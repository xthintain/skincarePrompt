/**
 * Recommendation Panel Component
 * Displays personalized product recommendations with ML predictions
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button, Spin, Alert, Tag, Rate } from 'antd';
import { ReloadOutlined, LikeOutlined, DislikeOutlined } from '@ant-design/icons';
import apiClient, { getErrorMessage } from '../../services/api';

const RecommendationPanel = ({ userId }) => {
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRecommendations();
  }, [userId]);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get('/recommendations', {
        params: {
          user_id: userId,
          n: 6,
        },
      });

      if (response.data.success) {
        setRecommendations(response.data.recommendations);
      }
    } catch (err) {
      console.error('Error loading recommendations:', err);
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (recommendationId, feedback) => {
    try {
      await apiClient.post('/recommendations/feedback', {
        recommendation_id: recommendationId,
        feedback: feedback,
      });

      // Reload recommendations after feedback
      loadRecommendations();
    } catch (err) {
      console.error('Error submitting feedback:', err);
    }
  };

  if (loading) {
    return (
      <Card title="Personalized Recommendations">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
          <p>Generating predictions...</p>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Personalized Recommendations">
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={loadRecommendations}>
              Retry
            </Button>
          }
        />
      </Card>
    );
  }

  return (
    <Card
      title="Personalized Recommendations (ML-Powered)"
      extra={
        <Button
          icon={<ReloadOutlined />}
          onClick={loadRecommendations}
          loading={loading}
        >
          Refresh
        </Button>
      }
    >
      <Row gutter={[16, 16]}>
        {recommendations.map((rec, index) => {
          const product = rec.product;
          const reasoning = rec.reasoning || {};

          return (
            <Col span={8} key={index}>
              <Card
                hoverable
                style={{ height: '100%' }}
                cover={
                  <div
                    style={{
                      height: 200,
                      background: '#f0f0f0',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {product.image_url ? (
                      <img
                        alt={product.name}
                        src={product.image_url}
                        style={{ maxHeight: '100%', maxWidth: '100%' }}
                      />
                    ) : (
                      <span style={{ color: '#999' }}>No Image</span>
                    )}
                  </div>
                }
              >
                <Card.Meta
                  title={product.name}
                  description={
                    <div>
                      <p style={{ fontSize: '12px', color: '#888' }}>
                        {product.brand}
                      </p>
                      <Tag color="blue">{product.category}</Tag>
                      {product.price && (
                        <Tag color="green">${product.price}</Tag>
                      )}
                      <div style={{ marginTop: 8 }}>
                        <Rate
                          disabled
                          value={product.avg_rating || 0}
                          style={{ fontSize: 14 }}
                        />
                        <span style={{ marginLeft: 8, fontSize: 12 }}>
                          ({product.review_count} reviews)
                        </span>
                      </div>
                    </div>
                  }
                />

                {/* Prediction Score */}
                <div style={{ marginTop: 12, padding: 8, background: '#f5f5f5', borderRadius: 4 }}>
                  <p style={{ margin: 0, fontSize: 12, fontWeight: 'bold' }}>
                    Match Score: {(rec.relevance_score * 100).toFixed(1)}%
                  </p>
                  <p style={{ margin: '4px 0 0', fontSize: 11, color: '#666' }}>
                    Algorithm: {reasoning.algorithm || 'hybrid'}
                  </p>
                </div>

                {/* Reasoning */}
                {reasoning.cf_reasoning && (
                  <div style={{ marginTop: 8, fontSize: 11 }}>
                    <strong>Why recommended:</strong>
                    <p style={{ margin: '4px 0' }}>
                      Similar to products you liked
                    </p>
                  </div>
                )}

                {/* Feedback Buttons */}
                <div style={{ marginTop: 12, textAlign: 'center' }}>
                  <Button
                    size="small"
                    icon={<LikeOutlined />}
                    onClick={() => handleFeedback(rec.recommendation_id, 'helpful')}
                    style={{ marginRight: 8 }}
                  >
                    Helpful
                  </Button>
                  <Button
                    size="small"
                    icon={<DislikeOutlined />}
                    onClick={() => handleFeedback(rec.recommendation_id, 'not_helpful')}
                  >
                    Not Helpful
                  </Button>
                </div>
              </Card>
            </Col>
          );
        })}
      </Row>

      {recommendations.length === 0 && (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <p>No recommendations available.</p>
          <p style={{ fontSize: 12, color: '#888' }}>
            This may be due to insufficient data. Try seeding the database.
          </p>
        </div>
      )}
    </Card>
  );
};

export default RecommendationPanel;
