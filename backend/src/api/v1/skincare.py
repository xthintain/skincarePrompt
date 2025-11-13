"""
Skincare Products API
护肤品数据API端点
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc
from src.config import SessionLocal
import sys
import os

# Add the scripts directory to Python path to import the model
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../scripts'))
from parse_skincare_data import SkincareProduct

skincare_bp = Blueprint('skincare', __name__)


@skincare_bp.route('/skincare/products', methods=['GET'])
def get_skincare_products():
    """
    获取护肤品列表
    Query params:
        - platform: JD or TB (可选)
        - page: 页码,默认1
        - per_page: 每页数量,默认20
        - sort_by: 排序字段 (recommendation, price),默认recommendation
    """
    session = SessionLocal()
    try:
        # 获取参数
        platform = request.args.get('platform', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        sort_by = request.args.get('sort_by', 'recommendation', type=str)

        # 构建查询
        query = session.query(SkincareProduct)

        # 平台筛选
        if platform and platform in ['JD', 'TB']:
            query = query.filter(SkincareProduct.平台 == platform)

        # 排序
        if sort_by == 'price':
            query = query.order_by(desc(SkincareProduct.价格))
        elif sort_by == 'recommendation':
            query = query.order_by(SkincareProduct.序号)  # 序号小 = 推荐度高

        # 分页
        total = query.count()
        offset = (page - 1) * per_page
        products = query.offset(offset).limit(per_page).all()

        # 转换为字典
        products_data = []
        for p in products:
            products_data.append({
                '序号': p.序号,
                '平台': p.平台,
                '名称': p.名称,
                '价格': float(p.价格) if p.价格 else None,
                '用户评价数': p.用户评价数,
                '用户购买数': p.用户购买数,
                '推荐程度': float(p.推荐程度) if p.推荐程度 else None,
                '页数': p.页数,
                '页内序号': p.页内序号
            })

        return jsonify({
            'success': True,
            'data': products_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@skincare_bp.route('/skincare/analytics', methods=['GET'])
def get_skincare_analytics():
    """获取护肤品数据分析"""
    session = SessionLocal()
    try:
        # 总体统计
        total_count = session.query(func.count(SkincareProduct.序号)).scalar()
        jd_count = session.query(func.count(SkincareProduct.序号)).filter(
            SkincareProduct.平台 == 'JD'
        ).scalar()
        tb_count = session.query(func.count(SkincareProduct.序号)).filter(
            SkincareProduct.平台 == 'TB'
        ).scalar()

        # 价格统计
        avg_price = session.query(func.avg(SkincareProduct.价格)).filter(
            SkincareProduct.价格.isnot(None)
        ).scalar()
        max_price = session.query(func.max(SkincareProduct.价格)).filter(
            SkincareProduct.价格.isnot(None)
        ).scalar()
        min_price = session.query(func.min(SkincareProduct.价格)).filter(
            SkincareProduct.价格.isnot(None),
            SkincareProduct.价格 > 0
        ).scalar()

        # Top 10 推荐商品
        top_products = session.query(SkincareProduct).order_by(
            SkincareProduct.序号
        ).limit(10).all()

        top_products_data = []
        for p in top_products:
            top_products_data.append({
                '序号': p.序号,
                '平台': p.平台,
                '名称': p.名称,
                '价格': float(p.价格) if p.价格 else None,
                '推荐程度': float(p.推荐程度) if p.推荐程度 else None
            })

        # 价格分布
        price_ranges = [
            (0, 50, '0-50元'),
            (50, 100, '50-100元'),
            (100, 200, '100-200元'),
            (200, 500, '200-500元'),
            (500, 1000, '500-1000元'),
            (1000, 10000, '1000元以上')
        ]

        price_distribution = []
        for min_p, max_p, label in price_ranges:
            count = session.query(func.count(SkincareProduct.序号)).filter(
                SkincareProduct.价格 >= min_p,
                SkincareProduct.价格 < max_p
            ).scalar()
            price_distribution.append({
                'range': label,
                'count': count
            })

        return jsonify({
            'success': True,
            'analytics': {
                'total_count': total_count,
                'jd_count': jd_count,
                'tb_count': tb_count,
                'avg_price': float(avg_price) if avg_price else 0,
                'max_price': float(max_price) if max_price else 0,
                'min_price': float(min_price) if min_price else 0,
                'top_products': top_products_data,
                'price_distribution': price_distribution
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@skincare_bp.route('/skincare/search', methods=['GET'])
def search_skincare_products():
    """搜索护肤品"""
    session = SessionLocal()
    try:
        keyword = request.args.get('keyword', '', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        if not keyword:
            return jsonify({'success': False, 'error': '请提供搜索关键词'}), 400

        # 搜索
        query = session.query(SkincareProduct).filter(
            SkincareProduct.名称.like(f'%{keyword}%')
        ).order_by(SkincareProduct.序号)

        total = query.count()
        offset = (page - 1) * per_page
        products = query.offset(offset).limit(per_page).all()

        products_data = []
        for p in products:
            products_data.append({
                '序号': p.序号,
                '平台': p.平台,
                '名称': p.名称,
                '价格': float(p.价格) if p.价格 else None,
                '推荐程度': float(p.推荐程度) if p.推荐程度 else None
            })

        return jsonify({
            'success': True,
            'data': products_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()
