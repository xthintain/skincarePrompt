"""
使用products.json数据训练ML推荐模型
"""
import json
import pickle
import os
import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


class SkincareMLRecommender:
    """护肤品机器学习推荐系统"""

    def __init__(self):
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.knn_model = None
        self.products_data = []

    def extract_features_from_name(self, name):
        """从商品名称中提取特征"""
        features = []

        # 1. 提取品牌关键词
        brands = [
            '欧莱雅', '谷雨', '海蓝之谜', 'LA MER', '妮维雅', 'NIVEA',
            '科颜氏', "Kiehl's", '自然堂', '兰蔻', '雅诗兰黛', '资生堂',
            '欧诗漫', '百雀羚', '大宝', '韩束', '珀莱雅', '袋鼠妈妈',
            '青蛙王子', '隆力奇', '蜜沐聆', 'ALORM', 'Losok', 'ORGINESE'
        ]
        for brand in brands:
            if brand in name:
                features.append(f'品牌_{brand}')

        # 2. 提取功效关键词
        effects = [
            '美白', '保湿', '补水', '抗皱', '紧致', '淡斑', '祛斑',
            '修护', '滋润', '提亮', '去黄', '抗氧化', '淡纹', '控油',
            '舒缓', '提拉', '焕肤', '嫩肤', '御龄', '收缩毛孔', '改善'
        ]
        for effect in effects:
            if effect in name:
                features.append(f'功效_{effect}')

        # 3. 提取产品类型
        product_types = [
            '面霜', '乳液', '精华', '水乳', '套装', '礼盒', '洁面',
            '爽肤水', '晚霜', '日霜', '眼霜', '护手霜', '身体乳',
            '面膜', '精萃水', '凝露', '凝胶', '洗面奶', '精华液'
        ]
        for ptype in product_types:
            if ptype in name:
                features.append(f'类型_{ptype}')

        # 4. 提取适用人群
        targets = ['男士', '女', '孕妇', '儿童', '宝宝', '婴儿', '准孕妇']
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

    def load_data_from_json(self, json_path):
        """从JSON文件加载数据"""
        print(f"从 {json_path} 加载商品数据...")

        with open(json_path, 'r', encoding='utf-8') as f:
            products = json.load(f)

        for i, product in enumerate(products):
            # 将good_rate转换为推荐程度（0-1之间）
            good_rate = float(product.get('good_rate', 0))
            recommendation_score = good_rate / 100.0  # 转换为0-1

            self.products_data.append({
                '序号': i + 1,
                '平台': product.get('source', 'JD'),
                '名称': product.get('title', ''),
                '价格': float(product.get('price', 0)),
                '推荐程度': recommendation_score,
                '用户评价数': product.get('comment_num', '0'),
                '用户购买数': product.get('comment_num', '0'),  # 使用评论数作为购买数
                'sku_id': product.get('sku_id', ''),
                'image_url': product.get('image_url', ''),
                'click_url': product.get('click_url', ''),
                'good_rate': good_rate
            })

        print(f"✅ 成功加载 {len(self.products_data)} 个商品")

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
            max_features=500,
            min_df=1,
            max_df=0.8,
            ngram_range=(1, 2),
            token_pattern=r'(?u)\b\w+\b'
        )

        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(feature_texts)
        feature_names = self.tfidf_vectorizer.get_feature_names_out()

        print(f"✅ TF-IDF矩阵形状: {self.tfidf_matrix.shape}")
        print(f"   - 商品数量: {self.tfidf_matrix.shape[0]}")
        print(f"   - 特征维度: {self.tfidf_matrix.shape[1]}")
        print(f"\n📊 Top 10 重要特征:")

        # 计算每个特征的平均TF-IDF值
        feature_scores = np.asarray(self.tfidf_matrix.mean(axis=0)).ravel()
        top_indices = feature_scores.argsort()[-10:][::-1]

        for idx in top_indices:
            print(f"   - {feature_names[idx]}: {feature_scores[idx]:.4f}")

    def train_knn(self):
        """训练K-NN相似度模型"""
        print("\n训练K-NN相似商品模型...")

        n_neighbors = min(11, len(self.products_data))  # 确保不超过商品总数

        self.knn_model = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric='cosine',
            algorithm='brute',
            n_jobs=-1
        )

        self.knn_model.fit(self.tfidf_matrix)

        print(f"✅ K-NN模型训练完成")
        print(f"   - 使用算法: brute force")
        print(f"   - 相似度度量: cosine")
        print(f"   - 邻居数量: {n_neighbors - 1}")

    def save_model(self, model_dir='models/skincare_ml'):
        """保存模型（相对于backend目录）"""
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
        print(f"   - products_data.pkl ({len(self.products_data)} 个商品)")


def main():
    """主函数"""
    print("="*60)
    print("护肤品ML推荐系统训练（基于products.json）")
    print("="*60)

    # 创建推荐器
    recommender = SkincareMLRecommender()

    # 加载数据
    json_path = 'data/products.json'
    recommender.load_data_from_json(json_path)

    # 训练TF-IDF
    recommender.train_tfidf()

    # 训练K-NN
    recommender.train_knn()

    # 保存模型
    recommender.save_model()

    print("\n" + "="*60)
    print("✅ 训练完成!")
    print("="*60)


if __name__ == '__main__':
    main()
