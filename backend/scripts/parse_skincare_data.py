"""
Parse skincare product data from JD and TB HTML files
Extract product information and calculate recommendation scores
"""
import json
import re
import os
import sys
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Base, SessionLocal, engine


class SkincareProduct(Base):
    """护肤品数据表"""
    __tablename__ = 'skincare_products'

    序号 = Column(Integer, primary_key=True)
    平台 = Column(String(10), nullable=False)  # 'JD' or 'TB'
    页数 = Column(Integer, nullable=False)
    页内序号 = Column(Integer, nullable=False)
    名称 = Column(String(500), nullable=False)
    价格 = Column(Float, nullable=True)
    用户评价数 = Column(String(50), nullable=True)  # 京东
    用户购买数 = Column(String(50), nullable=True)  # 淘宝
    推荐程度 = Column(Float, nullable=True)  # 基于序号计算
    created_at = Column(DateTime, default=datetime.utcnow)


def parse_jd_html(file_path, page_num):
    """解析京东HTML文件"""
    products = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取pageData中的JSON数据
    match = re.search(r'var pageData = ({.*?"result":\[.*?\].*?});', content, re.DOTALL)
    if not match:
        print(f"Warning: No pageData found in {file_path}")
        return products

    try:
        data_str = match.group(1)
        data = json.loads(data_str)
        result = data.get('result', [])

        for idx, item in enumerate(result):
            # 提取价格
            price_str = item.get('sku_price', '0')
            try:
                price = float(price_str)
            except:
                price = 0.0

            # 提取评价数
            commentnum = item.get('commentnum', '')

            # 提取商品名称
            name = item.get('ad_title_text', '')
            if not name:
                name = item.get('ad_title', '')

            # 清理名称中的HTML标签
            name = re.sub(r'<[^>]+>', '', name)

            products.append({
                '页数': page_num,
                '页内序号': idx + 1,
                '名称': name.strip(),
                '价格': price,
                '用户评价数': commentnum,
                '用户购买数': None
            })

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")

    return products


def parse_tb_html(file_path, page_num):
    """解析淘宝HTML文件"""
    products = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # 淘宝使用doubleCard--gO3Bz6bu作为商品卡片的主容器
    items = soup.find_all('div', class_='doubleCard--gO3Bz6bu')

    print(f"  找到 {len(items)} 个商品卡片")

    for idx, item in enumerate(items):
        try:
            # 提取名称 - 使用title属性或span内容
            name = ''
            title_elem = item.find('div', class_=re.compile(r'title--'))
            if title_elem:
                name = title_elem.get('title', '')
                if not name:
                    # 尝试从span中提取
                    span_elem = title_elem.find('span')
                    if span_elem:
                        name = span_elem.get_text(strip=True)

            # 提取价格 - 整数和小数部分分开
            price = 0.0
            price_int_elem = item.find('div', class_=re.compile(r'priceInt--'))
            price_float_elem = item.find('div', class_=re.compile(r'priceFloat--'))

            if price_int_elem:
                price_int = price_int_elem.get_text(strip=True)
                price_float = ''
                if price_float_elem:
                    price_float = price_float_elem.get_text(strip=True)

                try:
                    price = float(price_int + price_float)
                except:
                    price = 0.0

            # 提取销量
            sales = ''
            sales_elem = item.find('span', class_=re.compile(r'realSales--'))
            if sales_elem:
                sales = sales_elem.get_text(strip=True)

            if name:
                products.append({
                    '页数': page_num,
                    '页内序号': idx + 1,
                    '名称': name.strip(),
                    '价格': price if price > 0 else None,
                    '用户评价数': None,
                    '用户购买数': sales if sales else None
                })

        except Exception as e:
            print(f"  解析商品 {idx+1} 出错: {e}")
            continue

    if not products:
        print(f"  Warning: No products found in {file_path}")

    return products


def calculate_recommendation_score(total_index, total_products=500):
    """
    计算推荐程度分数
    序号越小(排名越前)，推荐程度越高
    使用反向线性归一化: score = 1 - (index - 1) / (total - 1)
    """
    if total_products <= 1:
        return 1.0
    score = 1.0 - (total_index - 1) / (total_products - 1)
    return round(score, 4)


def main():
    """主函数"""
    print("开始解析护肤品数据...")

    # 创建表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据表创建成功")

    session = SessionLocal()

    try:
        # 清空现有数据
        session.query(SkincareProduct).delete()
        session.commit()

        all_products = []

        # 解析京东数据（使用相对路径）
        jd_dir = os.path.join('..', 'data', 'JD')
        print(f"\n解析京东数据 ({jd_dir})...")
        jd_count = 0
        for i in range(10):
            file_path = os.path.join(jd_dir, f'p{i}.html')
            if os.path.exists(file_path):
                products = parse_jd_html(file_path, i)
                print(f"  页{i}: 提取 {len(products)} 个商品")
                for p in products:
                    p['平台'] = 'JD'
                all_products.extend(products)
                jd_count += len(products)

        print(f"京东总计: {jd_count} 个商品")

        # 解析淘宝数据（使用相对路径）
        tb_dir = os.path.join('..', 'data', 'TB')
        print(f"\n解析淘宝数据 ({tb_dir})...")
        tb_count = 0
        for i in range(10):
            file_path = os.path.join(tb_dir, f'p{i}.html')
            if os.path.exists(file_path):
                products = parse_tb_html(file_path, i)
                print(f"  页{i}: 提取 {len(products)} 个商品")
                for p in products:
                    p['平台'] = 'TB'
                all_products.extend(products)
                tb_count += len(products)

        print(f"淘宝总计: {tb_count} 个商品")
        print(f"\n总计: {len(all_products)} 个商品")

        # 按平台分组计算序号和推荐程度
        jd_products = [p for p in all_products if p['平台'] == 'JD']
        tb_products = [p for p in all_products if p['平台'] == 'TB']

        # 京东商品编号
        for idx, product in enumerate(jd_products, start=1):
            product['序号'] = idx
            product['推荐程度'] = calculate_recommendation_score(idx, len(jd_products))

        # 淘宝商品编号(从京东之后开始)
        start_idx = len(jd_products) + 1
        for idx, product in enumerate(tb_products, start=start_idx):
            product['序号'] = idx
            product['推荐程度'] = calculate_recommendation_score(idx - start_idx + 1, len(tb_products))

        # 插入数据库
        print("\n插入数据到数据库...")
        for product in all_products:
            db_product = SkincareProduct(**product)
            session.add(db_product)

        session.commit()
        print(f"✅ 成功插入 {len(all_products)} 条数据")

        # 统计信息
        print("\n数据统计:")
        print(f"  京东商品: {len(jd_products)} 条")
        print(f"  淘宝商品: {len(tb_products)} 条")
        print(f"  总计: {len(all_products)} 条")

        # 显示示例数据
        print("\n示例数据(前5条):")
        samples = session.query(SkincareProduct).limit(5).all()
        for sample in samples:
            print(f"  [{sample.序号}] {sample.平台} - {sample.名称[:30]}... - ¥{sample.价格} - 推荐度:{sample.推荐程度}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


if __name__ == '__main__':
    main()
