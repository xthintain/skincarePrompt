/**
 * ProductsGrid Component
 * 展示推荐商品网格
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Tag, Rate, Spin, Empty, Pagination } from 'antd';
import { ShoppingCartOutlined } from '@ant-design/icons';

const { Meta } = Card;

const ProductsGrid = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20; // 每页显示20个商品

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      // 从本地JSON文件加载商品数据
      const response = await fetch('/data/products.json');
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      console.error('加载商品数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>加载商品中...</p>
      </div>
    );
  }

  if (products.length === 0) {
    return <Empty description="暂无商品数据" />;
  }

  // 分页处理
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentProducts = products.slice(startIndex, endIndex);

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>推荐商品 (共{products.length}个)</h2>

      <Row gutter={[16, 16]}>
        {currentProducts.map((product, index) => (
          <Col xs={24} sm={12} md={8} lg={6} xl={4} key={product.sku_id || index}>
            <Card
              hoverable
              cover={
                <div style={{
                  height: 200,
                  overflow: 'hidden',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: '#f0f5ff',
                  flexDirection: 'column'
                }}>
                  <ShoppingCartOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
                  <div style={{ fontSize: 12, color: '#999', textAlign: 'center', padding: '0 16px' }}>
                    {product.source === 'JD' ? '京东商品' : '淘宝商品'}
                  </div>
                </div>
              }
              actions={[
                <a
                  href={product.click_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: '#1890ff' }}
                >
                  <ShoppingCartOutlined /> 查看详情
                </a>
              ]}
            >
              <Meta
                title={
                  <div style={{
                    height: 44,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    fontSize: 14
                  }}>
                    {product.title}
                  </div>
                }
                description={
                  <div>
                    <div style={{ marginBottom: 8 }}>
                      <Tag color={product.source === 'JD' ? 'red' : 'orange'}>
                        {product.source === 'JD' ? '京东' : '淘宝'}
                      </Tag>
                    </div>
                    <div style={{ fontSize: 18, color: '#ff4d4f', fontWeight: 'bold' }}>
                      ¥{parseFloat(product.price).toFixed(2)}
                    </div>
                    {product.good_rate && (
                      <div style={{ marginTop: 8 }}>
                        <Rate disabled defaultValue={product.good_rate / 20} style={{ fontSize: 12 }} />
                        <span style={{ marginLeft: 8, fontSize: 12, color: '#999' }}>
                          {product.good_rate}%
                        </span>
                      </div>
                    )}
                    {product.comment_num && (
                      <div style={{ marginTop: 4, fontSize: 12, color: '#999' }}>
                        {product.comment_num} 条评价
                      </div>
                    )}
                  </div>
                }
              />
            </Card>
          </Col>
        ))}
      </Row>

      <div style={{ marginTop: 32, textAlign: 'center' }}>
        <Pagination
          current={currentPage}
          pageSize={pageSize}
          total={products.length}
          onChange={(page) => {
            setCurrentPage(page);
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
          showSizeChanger={false}
          showTotal={(total) => `共 ${total} 个商品`}
        />
      </div>
    </div>
  );
};

export default ProductsGrid;
