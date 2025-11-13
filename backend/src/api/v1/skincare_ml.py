"""
护肤品ML推荐API
使用训练好的TF-IDF和K-NN模型提供智能推荐
"""
from flask import Blueprint, request, jsonify
import pickle
import os
import sys
import jieba
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

skincare_ml_bp = Blueprint('skincare_ml', __name__)

# 全局变量存储模型
_model_cache = {
    'tfidf_vectorizer': None,
    'tfidf_matrix': None,
    'knn_model': None,
    'products_data': None
}


def load_models():
    """加载ML模型（懒加载）"""
    if _model_cache['tfidf_vectorizer'] is not None:
        return _model_cache

    model_dir = 'backend/models/skincare_ml'

    try:
        # 加载TF-IDF向量化器
        with open(f'{model_dir}/tfidf_vectorizer.pkl', 'rb') as f:
            _model_cache['tfidf_vectorizer'] = pickle.load(f)

        # 加载TF-IDF矩阵
        with open(f'{model_dir}/tfidf_matrix.pkl', 'rb') as f:
            _model_cache['tfidf_matrix'] = pickle.load(f)

        # 加载K-NN模型
        with open(f'{model_dir}/knn_model.pkl', 'rb') as f:
            _model_cache['knn_model'] = pickle.load(f)

        # 加载商品数据
        with open(f'{model_dir}/products_data.pkl', 'rb') as f:
            _model_cache['products_data'] = pickle.load(f)

        print(f"✅ ML模型加载成功 ({len(_model_cache['products_data'])} 个商品)")

    except Exception as e:
        print(f"❌ 加载ML模型失败: {e}")
        raise

    return _model_cache


def extract_features_from_name(name):
    """从商品名称中提取特征（与训练时相同）"""
    features = []

    # 1. 提取品牌关键词
    brands = [
        '欧莱雅', '谷雨', '海蓝之谜', 'LA MER', '妮维雅', 'NIVEA',
        '科颜氏', "Kiehl's", '自然堂', '兰蔻', '雅诗兰黛', '资生堂',
        '欧诗漫', '百雀羚', '大宝', '韩束', '珀莱雅', '袋鼠妈妈',
        '青蛙王子', '隆力奇', '蜜沐聆'
    ]
    for brand in brands:
        if brand in name:
            features.append(f'品牌_{brand}')

    # 2. 提取功效关键词
    effects = [
        '美白', '保湿', '补水', '抗皱', '紧致', '淡斑', '祛斑',
        '修护', '滋润', '提亮', '去黄', '抗氧化', '淡纹', '控油',
        '舒缓', '提拉', '焕肤', '嫩肤', '御龄'
    ]
    for effect in effects:
        if effect in name:
            features.append(f'功效_{effect}')

    # 3. 提取产品类型
    product_types = [
        '面霜', '乳液', '精华', '水乳', '套装', '礼盒', '洁面',
        '爽肤水', '晚霜', '日霜', '眼霜', '护手霜', '身体乳',
        '面膜', '精萃水', '凝露', '凝胶'
    ]
    for ptype in product_types:
        if ptype in name:
            features.append(f'类型_{ptype}')

    # 4. 提取适用人群
    targets = [
        '男士', '女', '孕妇', '儿童', '宝宝', '婴儿', '准孕妇'
    ]
    for target in targets:
        if target in name:
            features.append(f'人群_{target}')

    # 5. 提取规格相关
    specs = ['套装', '礼盒', '旅行装', '小样', '正装']
    for spec in specs:
        if spec in name:
            features.append(f'规格_{spec}')

    # 6. 使用jieba分词提取其他关键词
    words = jieba.cut(name)
    meaningful_words = [w for w in words if len(w) >= 2 and w not in ['的', '和', '与', '或']]
    features.extend(meaningful_words[:5])

    return ' '.join(features) if features else name


@skincare_ml_bp.route('/skincare/ml/similar/<int:product_id>', methods=['GET'])
def get_similar_products(product_id):
    """
    获取相似商品推荐（基于K-NN）

    参数:
        product_id: 商品序号
        n: 推荐数量，默认10
    """
    try:
        models = load_models()
        n_recommendations = request.args.get('n', 10, type=int)
        n_recommendations = min(n_recommendations, 50)  # 最多50个

        # 查找商品索引
        product_idx = None
        for idx, product in enumerate(models['products_data']):
            if product['序号'] == product_id:
                product_idx = idx
                break

        if product_idx is None:
            return jsonify({
                'success': False,
                'error': f'商品ID {product_id} 不存在'
            }), 404

        # 使用K-NN找相似商品
        distances, indices = models['knn_model'].kneighbors(
            models['tfidf_matrix'][product_idx],
            n_neighbors=n_recommendations + 1
        )

        # 构建推荐列表（排除自己）
        recommendations = []
        for i, (dist, idx) in enumerate(zip(distances[0][1:], indices[0][1:])):
            similarity = 1 - dist
            product = models['products_data'][idx]
            recommendations.append({
                'rank': i + 1,
                'similarity': float(similarity),
                'product': {
                    '序号': product['序号'],
                    '平台': product['平台'],
                    '名称': product['名称'],
                    '价格': product['价格'],
                    '推荐程度': product['推荐程度'],
                    '用户评价数': product['用户评价数'],
                    '用户购买数': product['用户购买数']
                }
            })

        # 返回基准商品信息
        base_product = models['products_data'][product_idx]

        return jsonify({
            'success': True,
            'base_product': {
                '序号': base_product['序号'],
                '平台': base_product['平台'],
                '名称': base_product['名称'],
                '价格': base_product['价格'],
                '推荐程度': base_product['推荐程度']
            },
            'recommendations': recommendations,
            'algorithm': 'K-NN with cosine similarity',
            'total': len(recommendations)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@skincare_ml_bp.route('/skincare/ml/recommend', methods=['POST'])
def recommend_by_preferences():
    """
    基于用户偏好推荐（使用TF-IDF + 余弦相似度）

    请求体:
        {
            "preferences": "美白补水保湿 女士",
            "n": 10,
            "min_price": 0,
            "max_price": 10000,
            "platform": "all"  // all, JD, TB
        }
    """
    try:
        models = load_models()
        data = request.get_json()

        if not data or 'preferences' not in data:
            return jsonify({
                'success': False,
                'error': '请提供preferences参数'
            }), 400

        preferences = data.get('preferences', '')
        n_recommendations = min(data.get('n', 10), 50)
        min_price = data.get('min_price', 0)
        max_price = data.get('max_price', 100000)
        platform = data.get('platform', 'all')

        # 提取偏好特征
        preference_features = extract_features_from_name(preferences)
        preference_vector = models['tfidf_vectorizer'].transform([preference_features])

        # 计算与所有商品的相似度
        similarities = cosine_similarity(preference_vector, models['tfidf_matrix'])[0]

        # 结合推荐程度进行加权，并应用筛选条件
        candidates = []
        for i, sim in enumerate(similarities):
            product = models['products_data'][i]

            # 价格筛选
            if product['价格'] < min_price or product['价格'] > max_price:
                continue

            # 平台筛选
            if platform != 'all' and product['平台'] != platform:
                continue

            recommendation_score = product['推荐程度']
            # 加权: 70%相似度 + 30%平台推荐度
            weighted_score = 0.7 * sim + 0.3 * recommendation_score

            candidates.append({
                'index': i,
                'similarity': float(sim),
                'weighted_score': float(weighted_score),
                'product': product
            })

        # 按加权分数排序
        candidates.sort(key=lambda x: x['weighted_score'], reverse=True)

        # 返回Top N
        recommendations = []
        for i, candidate in enumerate(candidates[:n_recommendations]):
            recommendations.append({
                'rank': i + 1,
                'similarity': candidate['similarity'],
                'weighted_score': candidate['weighted_score'],
                'product': {
                    '序号': candidate['product']['序号'],
                    '平台': candidate['product']['平台'],
                    '名称': candidate['product']['名称'],
                    '价格': candidate['product']['价格'],
                    '推荐程度': candidate['product']['推荐程度'],
                    '用户评价数': candidate['product']['用户评价数'],
                    '用户购买数': candidate['product']['用户购买数']
                }
            })

        return jsonify({
            'success': True,
            'preferences': preferences,
            'extracted_features': preference_features,
            'recommendations': recommendations,
            'algorithm': 'TF-IDF + Cosine Similarity (70%) + Platform Score (30%)',
            'filters': {
                'min_price': min_price,
                'max_price': max_price,
                'platform': platform
            },
            'total': len(recommendations)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@skincare_ml_bp.route('/skincare/ml/model_info', methods=['GET'])
def get_model_info():
    """获取ML模型信息"""
    try:
        models = load_models()

        # 获取特征信息
        feature_names = models['tfidf_vectorizer'].get_feature_names_out()
        feature_scores = np.asarray(models['tfidf_matrix'].mean(axis=0)).ravel()
        top_indices = feature_scores.argsort()[-20:][::-1]

        top_features = []
        for idx in top_indices:
            top_features.append({
                'feature': feature_names[idx],
                'importance': float(feature_scores[idx])
            })

        return jsonify({
            'success': True,
            'model_info': {
                'total_products': len(models['products_data']),
                'tfidf_features': models['tfidf_matrix'].shape[1],
                'knn_neighbors': 10,
                'algorithm': 'K-NN with cosine similarity',
                'top_features': top_features
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
