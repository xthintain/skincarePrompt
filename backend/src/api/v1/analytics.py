"""
Analytics API Endpoints
Provides dashboard metrics and trend data
"""
from flask import Blueprint, request, jsonify
from src.api.middleware.rate_limiter import rate_limit
from src.config import SessionLocal
from src.models import User, Product, Recommendation, UserRating, UserInteraction
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
import logging
import pickle
import os

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics/dashboard', methods=['GET'])
@rate_limit(limit=100)
def get_dashboard_metrics():
    """
    Get overview metrics for dashboard

    Query Parameters:
        skin_type (str): Filter by skin type

    Returns:
        JSON response with dashboard metrics
    """
    try:
        skin_type = request.args.get('skin_type')

        session = SessionLocal()

        try:
            # Total users
            user_query = session.query(func.count(User.user_id))
            if skin_type:
                user_query = user_query.filter(User.skin_type == skin_type)
            total_users = user_query.scalar()

            # Total products
            total_products = session.query(func.count(Product.product_id)).filter(
                Product.is_available == True
            ).scalar()

            # Total recommendations
            total_recommendations = session.query(func.count(Recommendation.recommendation_id)).scalar()

            # Total ratings
            total_ratings = session.query(func.count(UserRating.rating_id)).scalar()

            # Average rating
            avg_rating = session.query(func.avg(UserRating.rating)).scalar()
            avg_rating = float(avg_rating) if avg_rating else 0.0

            # User distribution by skin type
            skin_type_dist = session.query(
                User.skin_type,
                func.count(User.user_id)
            ).group_by(User.skin_type).all()

            skin_type_distribution = [
                {'skin_type': st, 'count': count}
                for st, count in skin_type_dist if st is not None
            ]

            # Product category distribution
            category_dist = session.query(
                Product.category,
                func.count(Product.product_id)
            ).filter(Product.is_available == True).group_by(Product.category).all()

            category_distribution = [
                {'category': cat, 'count': count}
                for cat, count in category_dist
            ]

            # Top rated products
            top_products = session.query(Product).filter(
                Product.is_available == True,
                Product.avg_rating.isnot(None)
            ).order_by(desc(Product.avg_rating)).limit(5).all()

            top_products_list = [
                {
                    'product_id': p.product_id,
                    'name': p.name,
                    'brand': p.brand,
                    'avg_rating': float(p.avg_rating),
                    'review_count': p.review_count,
                }
                for p in top_products
            ]

            return jsonify({
                'success': True,
                'metrics': {
                    'total_users': total_users,
                    'total_products': total_products,
                    'total_recommendations': total_recommendations,
                    'total_ratings': total_ratings,
                    'average_rating': round(avg_rating, 2),
                },
                'distributions': {
                    'skin_types': skin_type_distribution,
                    'categories': category_distribution,
                },
                'top_products': top_products_list,
            }), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/analytics/trends', methods=['GET'])
@rate_limit(limit=100)
def get_trends():
    """
    Get trending products and ingredients

    Query Parameters:
        days (int): Number of days to look back (default: 30)

    Returns:
        JSON response with trend data
    """
    try:
        days = min(request.args.get('days', 30, type=int), 365)

        session = SessionLocal()

        try:
            # Calculate date threshold
            threshold_date = datetime.utcnow() - timedelta(days=days)

            # Most viewed products (from interactions)
            trending_products = session.query(
                Product.product_id,
                Product.name,
                Product.brand,
                Product.category,
                func.count(UserInteraction.interaction_id).label('view_count')
            ).join(
                UserInteraction, Product.product_id == UserInteraction.product_id
            ).filter(
                UserInteraction.interaction_type == 'view',
                UserInteraction.timestamp >= threshold_date
            ).group_by(
                Product.product_id,
                Product.name,
                Product.brand,
                Product.category
            ).order_by(desc('view_count')).limit(10).all()

            trending_list = [
                {
                    'product_id': p.product_id,
                    'name': p.name,
                    'brand': p.brand,
                    'category': p.category,
                    'view_count': p.view_count,
                }
                for p in trending_products
            ]

            # Recent ratings trend (ratings per day)
            daily_ratings = session.query(
                func.date(UserRating.reviewed_at).label('date'),
                func.count(UserRating.rating_id).label('count'),
                func.avg(UserRating.rating).label('avg_rating')
            ).filter(
                UserRating.reviewed_at >= threshold_date
            ).group_by(
                func.date(UserRating.reviewed_at)
            ).order_by('date').all()

            ratings_trend = [
                {
                    'date': str(r.date),
                    'count': r.count,
                    'avg_rating': round(float(r.avg_rating), 2) if r.avg_rating else 0,
                }
                for r in daily_ratings
            ]

            return jsonify({
                'success': True,
                'period_days': days,
                'trending_products': trending_list,
                'ratings_trend': ratings_trend,
            }), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error getting trends: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/analytics/skincare-report', methods=['POST'])
@rate_limit(limit=50)
def generate_skincare_report():
    """
    生成护肤品推荐报告

    请求体:
        {
            "user_preferences": "美白补水保湿",  // 可选
            "skin_concerns": ["干燥", "暗沉"],   // 可选
            "budget_range": {                    // 可选
                "min": 0,
                "max": 500
            },
            "report_type": "comprehensive"  // comprehensive, budget, premium
        }

    返回:
        完整的护肤品推荐报告，包含：
        - 个性化推荐商品
        - 各价格区间推荐
        - 功效分类推荐
        - 平台对比分析
    """
    try:
        data = request.get_json() or {}

        # 解析参数
        user_preferences = data.get('user_preferences', '补水保湿')
        skin_concerns = data.get('skin_concerns', [])
        budget_range = data.get('budget_range', {'min': 0, 'max': 10000})
        report_type = data.get('report_type', 'comprehensive')

        session = SessionLocal()

        try:
            # 加载ML模型数据
            model_dir = 'models/skincare_ml'
            products_data = []

            if os.path.exists(f'{model_dir}/products_data.pkl'):
                with open(f'{model_dir}/products_data.pkl', 'rb') as f:
                    products_data = pickle.load(f)
            else:
                # 如果模型不存在，从数据库加载
                from scripts.parse_skincare_data import SkincareProduct
                products_query = session.query(SkincareProduct).all()
                products_data = [{
                    '序号': p.序号,
                    '平台': p.平台,
                    '名称': p.名称,
                    '价格': float(p.价格) if p.价格 else 0.0,
                    '推荐程度': float(p.推荐程度) if p.推荐程度 else 0.0,
                    '用户评价数': p.用户评价数,
                    '用户购买数': p.用户购买数
                } for p in products_query]

            # 构建搜索关键词
            search_keywords = user_preferences
            if skin_concerns:
                search_keywords += ' ' + ' '.join(skin_concerns)

            # 1. 筛选符合预算的商品
            budget_products = [
                p for p in products_data
                if budget_range['min'] <= p['价格'] <= budget_range['max']
            ]

            if not budget_products:
                budget_products = products_data

            # 2. 根据关键词匹配商品
            def calculate_relevance_score(product, keywords):
                """计算商品与关键词的相关性分数"""
                name = product['名称']
                score = product['推荐程度']

                # 关键词匹配加分
                for keyword in keywords.split():
                    if keyword in name:
                        score += 0.2

                return score

            # 为每个商品计算相关性分数
            for product in budget_products:
                product['relevance_score'] = calculate_relevance_score(product, search_keywords)

            # 3. 按相关性和推荐程度排序
            sorted_products = sorted(
                budget_products,
                key=lambda x: (x['relevance_score'], x['推荐程度']),
                reverse=True
            )

            # 4. 生成报告的各个部分

            # 4.1 Top推荐（前10名）
            top_recommendations = sorted_products[:10]

            # 4.2 价格区间分析
            price_ranges = {
                '经济实惠 (0-100元)': (0, 100),
                '中端选择 (100-300元)': (100, 300),
                '高端产品 (300-800元)': (300, 800),
                '奢华系列 (800元以上)': (800, 100000)
            }

            price_range_recommendations = {}
            for range_name, (min_p, max_p) in price_ranges.items():
                range_products = [
                    p for p in sorted_products
                    if min_p <= p['价格'] < max_p
                ]
                price_range_recommendations[range_name] = {
                    'count': len(range_products),
                    'top_picks': range_products[:3],
                    'avg_price': sum(p['价格'] for p in range_products) / len(range_products) if range_products else 0,
                    'avg_recommendation_score': sum(p['推荐程度'] for p in range_products) / len(range_products) if range_products else 0
                }

            # 4.3 功效分类推荐
            effects_categories = {
                '美白提亮': ['美白', '提亮', '去黄', '淡斑'],
                '补水保湿': ['补水', '保湿', '滋润', '水润'],
                '抗衰老': ['抗皱', '紧致', '提拉', '淡纹', '抗氧化'],
                '修护舒缓': ['修护', '舒缓', '修复', '镇静'],
                '控油清洁': ['控油', '清爽', '洁面', '去油']
            }

            effect_recommendations = {}
            for effect_name, keywords in effects_categories.items():
                effect_products = []
                for product in sorted_products:
                    if any(kw in product['名称'] for kw in keywords):
                        effect_products.append(product)

                effect_recommendations[effect_name] = {
                    'count': len(effect_products),
                    'top_picks': effect_products[:5]
                }

            # 4.4 平台对比分析
            jd_products = [p for p in sorted_products if p['平台'] == 'JD']
            tb_products = [p for p in sorted_products if p['平台'] == 'TB']

            platform_analysis = {
                '京东': {
                    'total_count': len(jd_products),
                    'avg_price': sum(p['价格'] for p in jd_products) / len(jd_products) if jd_products else 0,
                    'avg_recommendation_score': sum(p['推荐程度'] for p in jd_products) / len(jd_products) if jd_products else 0,
                    'top_picks': jd_products[:5]
                },
                '淘宝': {
                    'total_count': len(tb_products),
                    'avg_price': sum(p['价格'] for p in tb_products) / len(tb_products) if tb_products else 0,
                    'avg_recommendation_score': sum(p['推荐程度'] for p in tb_products) / len(tb_products) if tb_products else 0,
                    'top_picks': tb_products[:5]
                }
            }

            # 4.5 数据统计摘要
            statistics = {
                'total_products_analyzed': len(sorted_products),
                'budget_range': budget_range,
                'avg_price': sum(p['价格'] for p in sorted_products) / len(sorted_products) if sorted_products else 0,
                'price_range': {
                    'min': min(p['价格'] for p in sorted_products) if sorted_products else 0,
                    'max': max(p['价格'] for p in sorted_products) if sorted_products else 0
                },
                'avg_recommendation_score': sum(p['推荐程度'] for p in sorted_products) / len(sorted_products) if sorted_products else 0
            }

            # 4.6 智能建议
            smart_suggestions = []

            # 预算建议
            if budget_range['max'] < 100:
                smart_suggestions.append({
                    'type': 'budget',
                    'message': '您的预算偏低，建议关注经济实惠型产品，性价比更高',
                    'action': '查看0-100元区间商品'
                })
            elif budget_range['max'] > 800:
                smart_suggestions.append({
                    'type': 'budget',
                    'message': '您的预算充足，可以选择高端奢华系列，效果更佳',
                    'action': '查看800元以上商品'
                })

            # 平台建议
            if len(jd_products) > len(tb_products) * 1.5:
                smart_suggestions.append({
                    'type': 'platform',
                    'message': '京东平台有更多符合您需求的商品',
                    'action': '优先查看京东商品'
                })
            elif len(tb_products) > len(jd_products) * 1.5:
                smart_suggestions.append({
                    'type': 'platform',
                    'message': '淘宝平台有更多符合您需求的商品',
                    'action': '优先查看淘宝商品'
                })

            # 功效建议
            top_effect = max(effect_recommendations.items(), key=lambda x: x[1]['count'])
            if top_effect[1]['count'] > 0:
                smart_suggestions.append({
                    'type': 'effect',
                    'message': f'根据您的需求，我们找到{top_effect[1]["count"]}款{top_effect[0]}产品',
                    'action': f'查看{top_effect[0]}分类'
                })

            # 构建最终报告
            report = {
                'success': True,
                'report_metadata': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'user_preferences': user_preferences,
                    'skin_concerns': skin_concerns,
                    'budget_range': budget_range,
                    'report_type': report_type
                },
                'statistics': statistics,
                'top_recommendations': [
                    {
                        'rank': idx + 1,
                        'product': {
                            '序号': p['序号'],
                            '平台': p['平台'],
                            '名称': p['名称'],
                            '价格': p['价格'],
                            '推荐程度': p['推荐程度'],
                            '用户评价数': p.get('用户评价数'),
                            '用户购买数': p.get('用户购买数')
                        },
                        'relevance_score': round(p['relevance_score'], 4),
                        'recommendation_reason': _generate_recommendation_reason(p, search_keywords)
                    }
                    for idx, p in enumerate(top_recommendations)
                ],
                'price_range_analysis': price_range_recommendations,
                'effect_based_recommendations': effect_recommendations,
                'platform_comparison': platform_analysis,
                'smart_suggestions': smart_suggestions
            }

            return jsonify(report), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error generating skincare report: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _generate_recommendation_reason(product, keywords):
    """生成推荐理由"""
    reasons = []

    name = product['名称']

    # 检查关键词匹配
    matched_keywords = [kw for kw in keywords.split() if kw in name]
    if matched_keywords:
        reasons.append(f"包含您关注的功效: {', '.join(matched_keywords)}")

    # 推荐程度
    if product['推荐程度'] >= 0.95:
        reasons.append("平台高度推荐商品")
    elif product['推荐程度'] >= 0.90:
        reasons.append("平台推荐商品")

    # 价格合理性
    if product['价格'] < 100:
        reasons.append("价格实惠，性价比高")
    elif product['价格'] > 500:
        reasons.append("高端产品，品质保证")

    # 用户评价
    if product.get('用户评价数') and ('万+' in str(product['用户评价数']) or '万' in str(product['用户评价数'])):
        reasons.append("用户好评如潮")

    if product.get('用户购买数') and ('万+' in str(product['用户购买数']) or '万' in str(product['用户购买数'])):
        reasons.append("热销商品")

    return '; '.join(reasons) if reasons else "综合推荐"
