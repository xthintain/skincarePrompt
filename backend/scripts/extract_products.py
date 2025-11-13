#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从HTML文件中提取商品信息
"""
import os
import re
import json
from bs4 import BeautifulSoup


def extract_jd_products(html_file):
    """从京东HTML文件中提取商品信息"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取pageData中的商品信息
    pattern = r'var pageData = ({.*?});'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        try:
            page_data = json.loads(match.group(1))
            products = []

            for item in page_data.get('result', []):
                product = {
                    'sku_id': item.get('sku_id', ''),
                    'title': item.get('ad_title_text', ''),
                    'image_url': 'https://img14.360buyimg.com/' + item.get('image_url', ''),
                    'price': item.get('sku_price', '0.00'),
                    'click_url': item.get('click_url', ''),
                    'shop_id': item.get('shop_id', ''),
                    'comment_num': item.get('commentnum', '0'),
                    'good_rate': item.get('good_rate_show', 0),
                    'source': 'JD'
                }
                products.append(product)

            return products
        except json.JSONDecodeError as e:
            print(f"解析JSON失败: {e}")
            return []

    return []


def extract_tb_products(html_file):
    """从淘宝HTML文件中提取商品信息"""
    # 淘宝HTML结构不同,需要用BeautifulSoup解析
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    products = []

    # 这里需要根据实际的淘宝HTML结构来解析
    # 暂时返回空列表,后续可以补充

    return products


def extract_all_products():
    """提取所有商品信息"""
    all_products = []

    # 提取data目录下的JD商品
    jd_dir = '/home/xthintain/code/LLL/data/JD'
    if os.path.exists(jd_dir):
        for filename in os.listdir(jd_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(jd_dir, filename)
                products = extract_jd_products(filepath)
                all_products.extend(products)
                print(f"从 {filename} 提取了 {len(products)} 个商品")

    # 提取data目录下的TB商品
    tb_dir = '/home/xthintain/code/LLL/data/TB'
    if os.path.exists(tb_dir):
        for filename in os.listdir(tb_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(tb_dir, filename)
                products = extract_tb_products(filepath)
                all_products.extend(products)
                print(f"从 {filename} 提取了 {len(products)} 个商品")

    # 提取data目录下的商品(直接在data下的p*.html文件)
    data_dir = '/home/xthintain/code/LLL/data'
    for filename in os.listdir(data_dir):
        if filename.startswith('p') and filename.endswith('.html'):
            filepath = os.path.join(data_dir, filename)
            products = extract_jd_products(filepath)
            all_products.extend(products)
            print(f"从 {filename} 提取了 {len(products)} 个商品")

    return all_products


def save_products_to_json(products, output_file):
    """保存商品信息到JSON文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(products)} 个商品到 {output_file}")


if __name__ == '__main__':
    # 提取所有商品
    products = extract_all_products()

    # 取前100个商品
    top_100 = products[:100] if len(products) >= 100 else products

    # 保存到JSON文件
    output_file = '/home/xthintain/code/LLL/data/products.json'
    save_products_to_json(top_100, output_file)

    print(f"\n总共提取了 {len(products)} 个商品")
    print(f"已保存前 {len(top_100)} 个商品到 products.json")
