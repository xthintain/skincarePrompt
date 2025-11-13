"""
训练护肤品ML推荐模型
使用scikit-learn的TF-IDF和K-NN算法
"""
import sys
import os
import pickle
import re
import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import SessionLocal
from scripts.parse_skincare_data import SkincareProduct


class SkincareMLRecommender:
    """护肤品机器学习推荐系统"""

    def __init__(self):
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.knn_model = None
        self.products_data = []
        self.feature_names = []

    def extract_features_from_name(self, name):
        """从商品名称中提取特征"""
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
        features.extend(meaningful_words[:5])  # 只取前5个词

        return ' '.join(features) if features else name

    def load_data(self):
        """从数据库加载数据"""
        print("从数据库加载护肤品数据...")
        session = SessionLocal()

        try:
            products = session.query(SkincareProduct).all()

            for product in products:
                self.products_data.append({
                    '序号': product.序号,
                    '平台': product.平台,
                    '名称': product.名称,
                    '价格': float(product.价格) if product.价格 else 0.0,
                    '推荐程度': float(product.推荐程度) if product.推荐程度 else 0.0,
                    '用户评价数': product.用户评价数,
                    '用户购买数': product.用户购买数,
                })

            print(f"✅ 成功加载 {len(self.products_data)} 个商品")

        finally:
            session.close()

    def train_tfidf(self):
        """训练TF-IDF模型"""
        print("\n训练TF-IDF向量化模型...")

        # 提取所有商品的特征文本
        feature_texts = []
        for product in self.products_data:
            features = self.extract_features_from_name(product['名称'])
            feature_texts.append(features)

        # 训练TF-IDF向量化器
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,      # 最多保留500个特征
            min_df=1,              # 至少出现1次
            max_df=0.8,            # 最多出现在80%的文档中
            ngram_range=(1, 2),    # 使用1-gram和2-gram
            token_pattern=r'(?u)\b\w+\b'  # 支持中文
        )

        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(feature_texts)
        self.feature_names = self.tfidf_vectorizer.get_feature_names_out()

        print(f"✅ TF-IDF矩阵形状: {self.tfidf_matrix.shape}")
        print(f"   - 商品数量: {self.tfidf_matrix.shape[0]}")
        print(f"   - 特征维度: {self.tfidf_matrix.shape[1]}")
        print(f"\n📊 Top 20 重要特征:")

        # 计算每个特征的平均TF-IDF值
        feature_scores = np.asarray(self.tfidf_matrix.mean(axis=0)).ravel()
        top_indices = feature_scores.argsort()[-20:][::-1]

        for idx in top_indices:
            print(f"   - {self.feature_names[idx]}: {feature_scores[idx]:.4f}")

    def train_knn(self):
        """训练K-NN相似度模型"""
        print("\n训练K-NN相似商品模型...")

        self.knn_model = NearestNeighbors(
            n_neighbors=11,        # 找11个邻居（包括自己，所以实际返回10个）
            metric='cosine',       # 使用余弦相似度
            algorithm='brute',     # 暴力搜索（数据量不大）
            n_jobs=-1              # 使用所有CPU核心
        )

        self.knn_model.fit(self.tfidf_matrix)

        print(f"✅ K-NN模型训练完成")
        print(f"   - 使用算法: brute force")
        print(f"   - 相似度度量: cosine")
        print(f"   - 邻居数量: 10")

    def find_similar_products(self, product_idx, n_recommendations=10):
        """找到相似商品"""
        if product_idx >= len(self.products_data):
            return []

        # 使用K-NN找相似商品
        distances, indices = self.knn_model.kneighbors(
            self.tfidf_matrix[product_idx],
            n_neighbors=n_recommendations + 1  # +1因为会包含自己
        )

        # 排除自己，返回相似商品
        similar_products = []
        for i, (dist, idx) in enumerate(zip(distances[0][1:], indices[0][1:])):
            similarity = 1 - dist  # 余弦距离转相似度
            similar_products.append({
                'product': self.products_data[idx],
                'similarity': float(similarity),
                'rank': i + 1
            })

        return similar_products

    def get_recommendations_by_preferences(self, preferences, n_recommendations=10):
        """基于用户偏好推荐"""
        # 将用户偏好转换为特征向量
        preference_features = self.extract_features_from_name(preferences)
        preference_vector = self.tfidf_vectorizer.transform([preference_features])

        # 计算与所有商品的相似度
        similarities = cosine_similarity(preference_vector, self.tfidf_matrix)[0]

        # 结合推荐程度进行加权
        weighted_scores = []
        for i, sim in enumerate(similarities):
            recommendation_score = self.products_data[i]['推荐程度']
            # 加权: 70%相似度 + 30%平台推荐度
            weighted_score = 0.7 * sim + 0.3 * recommendation_score
            weighted_scores.append((i, weighted_score, sim))

        # 按加权分数排序
        weighted_scores.sort(key=lambda x: x[1], reverse=True)

        # 返回Top N
        recommendations = []
        for i, (idx, weighted_score, similarity) in enumerate(weighted_scores[:n_recommendations]):
            recommendations.append({
                'product': self.products_data[idx],
                'similarity': float(similarity),
                'weighted_score': float(weighted_score),
                'rank': i + 1
            })

        return recommendations

    def save_model(self, model_dir='backend/models/skincare_ml'):
        """保存模型"""
        print(f"\n保存模型到 {model_dir}...")

        os.makedirs(model_dir, exist_ok=True)

        # 保存TF-IDF向量化器
        with open(f'{model_dir}/tfidf_vectorizer.pkl', 'wb') as f:
            pickle.dump(self.tfidf_vectorizer, f)

        # 保存TF-IDF矩阵
        with open(f'{model_dir}/tfidf_matrix.pkl', 'wb') as f:
            pickle.dump(self.tfidf_matrix, f)

        # 保存K-NN模型
        with open(f'{model_dir}/knn_model.pkl', 'wb') as f:
            pickle.dump(self.knn_model, f)

        # 保存商品数据
        with open(f'{model_dir}/products_data.pkl', 'wb') as f:
            pickle.dump(self.products_data, f)

        print("✅ 模型保存成功")
        print(f"   - tfidf_vectorizer.pkl")
        print(f"   - tfidf_matrix.pkl")
        print(f"   - knn_model.pkl")
        print(f"   - products_data.pkl")

    def test_recommendations(self):
        """测试推荐效果"""
        print("\n" + "="*60)
        print("测试推荐效果")
        print("="*60)

        # 测试1: 相似商品推荐
        print("\n【测试1】相似商品推荐")
        print(f"基准商品: {self.products_data[0]['名称']}")
        similar = self.find_similar_products(0, 5)

        for rec in similar:
            print(f"\n  排名 {rec['rank']}: 相似度 {rec['similarity']:.4f}")
            print(f"  名称: {rec['product']['名称']}")
            print(f"  价格: ¥{rec['product']['价格']}")

        # 测试2: 基于偏好推荐
        print("\n" + "-"*60)
        print("【测试2】基于用户偏好推荐")
        preferences = "美白补水保湿 女士"
        print(f"用户偏好: {preferences}")

        recs = self.get_recommendations_by_preferences(preferences, 5)

        for rec in recs:
            print(f"\n  排名 {rec['rank']}: 加权分数 {rec['weighted_score']:.4f} (相似度 {rec['similarity']:.4f})")
            print(f"  名称: {rec['product']['名称']}")
            print(f"  价格: ¥{rec['product']['价格']}")
            print(f"  平台推荐度: {rec['product']['推荐程度']:.4f}")


def main():
    """主函数"""
    print("="*60)
    print("护肤品ML推荐系统训练")
    print("="*60)

    # 创建推荐器
    recommender = SkincareMLRecommender()

    # 加载数据
    recommender.load_data()

    # 训练TF-IDF
    recommender.train_tfidf()

    # 训练K-NN
    recommender.train_knn()

    # 保存模型
    recommender.save_model()

    # 测试推荐
    recommender.test_recommendations()

    print("\n" + "="*60)
    print("✅ 训练完成!")
    print("="*60)


if __name__ == '__main__':
    main()
