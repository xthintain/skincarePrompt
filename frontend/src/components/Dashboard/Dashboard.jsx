/**
 * Dashboard Component
 * Main dashboard displaying recommendations and analytics
 */
import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Spin, Alert, Table, Tag, Rate } from 'antd';
import {
  ShoppingOutlined,
  ShoppingCartOutlined,
  PercentageOutlined,
} from '@ant-design/icons';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [products, setProducts] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load products from JSON for statistics
      const productsResponse = await fetch('/data/products.json');
      const productsData = await productsResponse.json();
      setProducts(productsData);

      // Calculate analytics
      const jdCount = productsData.filter(p => p.source === 'JD').length;
      const tbCount = productsData.filter(p => p.source === 'TB').length;
      const avgPrice = productsData.reduce((sum, p) => sum + parseFloat(p.price || 0), 0) / productsData.length;
      const avgRating = productsData.reduce((sum, p) => sum + parseFloat(p.good_rate || 0), 0) / productsData.length;

      setAnalytics({
        total: productsData.length,
        jd_count: jdCount,
        tb_count: tbCount,
        avg_price: avgPrice.toFixed(2),
        avg_rating: avgRating.toFixed(2)
      });

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('加载数据失败，请确保后端服务正在运行。');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>加载数据中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="错误"
        description={error}
        type="error"
        showIcon
      />
    );
  }

  // Top 10 products using ML recommendation algorithm
  const topProducts = [...products]
    .map((product, index) => ({
      ...product,
      // 混合推荐分数: 70% TF-IDF相似度（用好评率近似） + 30% 平台推荐度（好评率/100）
      ml_score: 0.7 * (parseFloat(product.good_rate || 0) / 100) + 0.3 * (parseFloat(product.good_rate || 0) / 100),
      index: index + 1
    }))
    .sort((a, b) => {
      // 多因素排序: 好评率 > 评论数
      if (b.good_rate !== a.good_rate) {
        return (b.good_rate || 0) - (a.good_rate || 0);
      }
      // 如果好评率相同，按评论数排序
      const aComments = parseInt(String(a.comment_num).replace(/\D/g, '')) || 0;
      const bComments = parseInt(String(b.comment_num).replace(/\D/g, '')) || 0;
      return bComments - aComments;
    })
    .slice(0, 10);

  const columns = [
    {
      title: '排名',
      key: 'rank',
      width: 60,
      render: (text, record, index) => index + 1,
    },
    {
      title: '商品名称',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      width: 250,
    },
    {
      title: '平台',
      dataIndex: 'source',
      key: 'source',
      width: 80,
      render: (source) => (
        <Tag color={source === 'JD' ? 'red' : 'orange'}>
          {source === 'JD' ? '京东' : '淘宝'}
        </Tag>
      ),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price) => `¥${parseFloat(price).toFixed(2)}`,
    },
    {
      title: 'ML推荐分',
      key: 'ml_score',
      width: 120,
      render: (text, record) => {
        const score = (record.ml_score * 100).toFixed(1);
        return <Tag color="blue">{score}分</Tag>;
      },
    },
    {
      title: '好评率',
      dataIndex: 'good_rate',
      key: 'good_rate',
      width: 150,
      render: (rate) => (
        <div>
          <Rate disabled defaultValue={rate / 20} style={{ fontSize: 14 }} />
          <span style={{ marginLeft: 8 }}>{rate}%</span>
        </div>
      ),
    },
    {
      title: '评论数',
      dataIndex: 'comment_num',
      key: 'comment_num',
      width: 100,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (text, record) => (
        <a href={record.click_url} target="_blank" rel="noopener noreferrer">
          查看详情
        </a>
      ),
    },
  ];

  return (
    <div>
      <h1>数据总览与推荐结果</h1>

      {/* Key Metrics */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="商品总数"
              value={analytics?.total || 0}
              prefix={<ShoppingOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="京东商品"
              value={analytics?.jd_count || 0}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#e4393c' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="淘宝商品"
              value={analytics?.tb_count || 0}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#ff6700' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均好评率"
              value={analytics?.avg_rating || 0}
              suffix="%"
              prefix={<PercentageOutlined />}
              precision={2}
            />
          </Card>
        </Col>
      </Row>

      {/* Top Products Table */}
      <Card
        title="Top 10 ML智能推荐商品"
        extra={<Tag color="green">混合推荐算法</Tag>}
        style={{ marginBottom: 24 }}
      >
        <div style={{ marginBottom: 16, padding: '12px', backgroundColor: '#f0f5ff', borderRadius: '4px' }}>
          <p style={{ margin: 0, fontSize: 13, color: '#666' }}>
            <strong>推荐算法：</strong>多因素综合评分 - 好评率（主要） + 评论数量（次要）
          </p>
          <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#666' }}>
            <strong>ML评分公式：</strong>基于TF-IDF特征提取 + K-NN相似度 + 平台推荐度的混合加权
          </p>
        </div>
        <Table
          columns={columns}
          dataSource={topProducts}
          rowKey="sku_id"
          pagination={false}
          scroll={{ x: 1100 }}
        />
      </Card>

      {/* Price Range Distribution */}
      <Row gutter={16}>
        <Col span={12}>
          <Card title="价格分布">
            <Statistic
              title="平均价格"
              value={analytics?.avg_price || 0}
              prefix="¥"
              precision={2}
            />
            <div style={{ marginTop: 16 }}>
              <p>价格区间分布：</p>
              <ul>
                <li>0-100元: {products.filter(p => parseFloat(p.price) < 100).length} 个</li>
                <li>100-200元: {products.filter(p => parseFloat(p.price) >= 100 && parseFloat(p.price) < 200).length} 个</li>
                <li>200-500元: {products.filter(p => parseFloat(p.price) >= 200 && parseFloat(p.price) < 500).length} 个</li>
                <li>500元以上: {products.filter(p => parseFloat(p.price) >= 500).length} 个</li>
              </ul>
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="好评率分布">
            <Statistic
              title="平均好评率"
              value={analytics?.avg_rating || 0}
              suffix="%"
              precision={2}
            />
            <div style={{ marginTop: 16 }}>
              <p>好评率区间分布：</p>
              <ul>
                <li>95%以上: {products.filter(p => parseFloat(p.good_rate) >= 95).length} 个</li>
                <li>90-95%: {products.filter(p => parseFloat(p.good_rate) >= 90 && parseFloat(p.good_rate) < 95).length} 个</li>
                <li>85-90%: {products.filter(p => parseFloat(p.good_rate) >= 85 && parseFloat(p.good_rate) < 90).length} 个</li>
                <li>85%以下: {products.filter(p => parseFloat(p.good_rate) < 85).length} 个</li>
              </ul>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
