/**
 * FunctionModules Component
 * 功能模块管理中心 - 运行和管理项目的各个功能模块
 */
import React, { useState } from 'react';
import { Card, Row, Col, Button, Badge, Statistic, Space, Tag, Modal, message } from 'antd';
import {
  PlayCircleOutlined,
  DatabaseOutlined,
  ExperimentOutlined,
  LineChartOutlined,
  ShoppingOutlined,
  RobotOutlined,
  ApiOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';

const FunctionModules = () => {
  const [loadingModule, setLoadingModule] = useState(null);
  const [moduleStatus, setModuleStatus] = useState({
    database: 'idle',      // idle, running, success, error
    dataImport: 'idle',
    mlTraining: 'idle',
    apiServer: 'running',  // 后端默认运行中
    analytics: 'idle',
    recommendation: 'idle',
  });

  // 模块配置
  const modules = [
    {
      id: 'database',
      title: '数据库初始化',
      description: '创建数据库表结构，准备数据存储环境',
      icon: <DatabaseOutlined style={{ fontSize: 48, color: '#1890ff' }} />,
      endpoint: '/api/v1/admin/init-database',
      color: '#1890ff',
      actions: ['初始化表结构', '创建索引', '设置约束'],
    },
    {
      id: 'dataImport',
      title: '数据导入',
      description: '从HTML文件解析并导入护肤品数据到数据库',
      icon: <ShoppingOutlined style={{ fontSize: 48, color: '#52c41a' }} />,
      endpoint: '/api/v1/admin/import-data',
      color: '#52c41a',
      actions: ['解析HTML', '提取商品信息', '写入数据库'],
    },
    {
      id: 'mlTraining',
      title: 'ML模型训练',
      description: '训练TF-IDF和K-NN推荐模型',
      icon: <RobotOutlined style={{ fontSize: 48, color: '#722ed1' }} />,
      endpoint: '/api/v1/admin/train-model',
      color: '#722ed1',
      actions: ['TF-IDF特征提取', 'K-NN模型训练', '保存模型文件'],
    },
    {
      id: 'analytics',
      title: '数据分析',
      description: '分析商品数据，生成统计报告',
      icon: <LineChartOutlined style={{ fontSize: 48, color: '#fa8c16' }} />,
      endpoint: '/api/v1/skincare/analytics',
      color: '#fa8c16',
      actions: ['统计分析', '生成图表', '导出报告'],
    },
    {
      id: 'recommendation',
      title: '推荐系统测试',
      description: '测试ML推荐算法的准确性',
      icon: <ExperimentOutlined style={{ fontSize: 48, color: '#eb2f96' }} />,
      endpoint: '/api/v1/skincare/ml/model_info',
      color: '#eb2f96',
      actions: ['相似度计算', '推荐结果生成', '性能评估'],
    },
    {
      id: 'apiServer',
      title: 'API服务器',
      description: '后端API服务运行状态监控',
      icon: <ApiOutlined style={{ fontSize: 48, color: '#13c2c2' }} />,
      endpoint: '/api/v1/health',
      color: '#13c2c2',
      actions: ['健康检查', '性能监控', '日志查看'],
    },
  ];

  // 获取状态徽章
  const getStatusBadge = (status) => {
    const statusConfig = {
      idle: { status: 'default', text: '未运行' },
      running: { status: 'processing', text: '运行中' },
      success: { status: 'success', text: '成功' },
      error: { status: 'error', text: '失败' },
    };
    return statusConfig[status] || statusConfig.idle;
  };

  // 获取状态图标
  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <SyncOutlined spin style={{ color: '#1890ff' }} />;
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return null;
    }
  };

  // 运行模块
  const runModule = async (module) => {
    setLoadingModule(module.id);
    setModuleStatus(prev => ({ ...prev, [module.id]: 'running' }));

    try {
      // 对于不同的模块，调用不同的API
      let response;

      if (module.id === 'apiServer') {
        // API服务器状态检查
        response = await fetch('http://localhost:5000/api/v1/skincare/analytics');
      } else if (module.id === 'analytics') {
        // 数据分析
        response = await fetch(`http://localhost:5000${module.endpoint}`);
      } else if (module.id === 'recommendation') {
        // 推荐系统测试
        response = await fetch(`http://localhost:5000${module.endpoint}`);
      } else {
        // 其他模块（需要后端实现相应的管理API）
        message.info(`${module.title}功能需要在后端实现管理API`);
        setModuleStatus(prev => ({ ...prev, [module.id]: 'idle' }));
        setLoadingModule(null);
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setModuleStatus(prev => ({ ...prev, [module.id]: 'success' }));

        // 显示结果
        Modal.success({
          title: `${module.title} - 执行成功`,
          content: (
            <div>
              <p>模块已成功运行</p>
              {module.id === 'analytics' && data.data && (
                <div>
                  <p>总商品数: {data.data.total_products}</p>
                  <p>京东商品: {data.data.jd_count}</p>
                  <p>淘宝商品: {data.data.tb_count}</p>
                </div>
              )}
              {module.id === 'recommendation' && data.model_info && (
                <div>
                  <p>商品总数: {data.model_info.total_products}</p>
                  <p>特征维度: {data.model_info.tfidf_features}</p>
                  <p>算法: {data.model_info.algorithm}</p>
                </div>
              )}
            </div>
          ),
          width: 600,
        });
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('模块运行失败:', error);
      setModuleStatus(prev => ({ ...prev, [module.id]: 'error' }));
      message.error(`${module.title}运行失败: ${error.message}`);
    } finally {
      setLoadingModule(null);
    }
  };

  // 重置模块状态
  const resetModule = (moduleId) => {
    setModuleStatus(prev => ({ ...prev, [moduleId]: 'idle' }));
    message.info('模块状态已重置');
  };

  // 运行所有模块（按顺序）
  const runAllModules = () => {
    Modal.confirm({
      title: '确认运行所有模块',
      content: '这将按顺序运行: 数据库初始化 → 数据导入 → ML训练 → 数据分析',
      okText: '开始运行',
      cancelText: '取消',
      onOk: async () => {
        const sequence = ['database', 'dataImport', 'mlTraining', 'analytics'];
        for (const moduleId of sequence) {
          const module = modules.find(m => m.id === moduleId);
          if (module) {
            await runModule(module);
            // 等待2秒再运行下一个
            await new Promise(resolve => setTimeout(resolve, 2000));
          }
        }
        message.success('所有模块运行完成！');
      },
    });
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <h1>功能模块管理中心</h1>
            <p style={{ color: '#666', margin: 0 }}>
              管理和运行护肤品推荐系统的各个功能模块
            </p>
          </Col>
          <Col>
            <Space>
              <Button
                type="primary"
                size="large"
                icon={<PlayCircleOutlined />}
                onClick={runAllModules}
              >
                运行全部模块
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => window.location.reload()}
              >
                刷新页面
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 系统状态概览 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃模块"
              value={Object.values(moduleStatus).filter(s => s === 'running' || s === 'success').length}
              suffix={`/ ${modules.length}`}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="成功执行"
              value={Object.values(moduleStatus).filter(s => s === 'success').length}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="运行中"
              value={Object.values(moduleStatus).filter(s => s === 'running').length}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="失败"
              value={Object.values(moduleStatus).filter(s => s === 'error').length}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 功能模块卡片 */}
      <Row gutter={[16, 16]}>
        {modules.map((module) => {
          const status = moduleStatus[module.id];
          const badge = getStatusBadge(status);
          const isLoading = loadingModule === module.id;

          return (
            <Col xs={24} sm={12} lg={8} key={module.id}>
              <Badge.Ribbon text={badge.text} color={badge.status}>
                <Card
                  hoverable
                  style={{
                    borderLeft: `4px solid ${module.color}`,
                    height: '100%',
                  }}
                >
                  <div style={{ textAlign: 'center', marginBottom: 16 }}>
                    {module.icon}
                  </div>

                  <h3 style={{ textAlign: 'center', marginBottom: 8 }}>
                    {module.title}
                    {getStatusIcon(status) && (
                      <span style={{ marginLeft: 8 }}>
                        {getStatusIcon(status)}
                      </span>
                    )}
                  </h3>

                  <p style={{
                    textAlign: 'center',
                    color: '#666',
                    minHeight: 40,
                    fontSize: 13,
                  }}>
                    {module.description}
                  </p>

                  <div style={{ marginBottom: 16 }}>
                    <Tag color={module.color}>
                      功能模块
                    </Tag>
                    {status === 'running' && (
                      <Tag color="processing">运行中</Tag>
                    )}
                    {status === 'success' && (
                      <Tag color="success">已完成</Tag>
                    )}
                  </div>

                  <div style={{
                    background: '#f5f5f5',
                    padding: 12,
                    borderRadius: 4,
                    marginBottom: 16,
                  }}>
                    <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>
                      <strong>执行步骤：</strong>
                    </div>
                    <ul style={{
                      margin: 0,
                      paddingLeft: 20,
                      fontSize: 12,
                      color: '#666',
                    }}>
                      {module.actions.map((action, idx) => (
                        <li key={idx}>{action}</li>
                      ))}
                    </ul>
                  </div>

                  <Space style={{ width: '100%' }} direction="vertical">
                    <Button
                      type="primary"
                      block
                      icon={<PlayCircleOutlined />}
                      onClick={() => runModule(module)}
                      loading={isLoading}
                      disabled={status === 'running'}
                      style={{ backgroundColor: module.color, borderColor: module.color }}
                    >
                      {isLoading ? '运行中...' : '运行模块'}
                    </Button>

                    {status !== 'idle' && (
                      <Button
                        block
                        icon={<ReloadOutlined />}
                        onClick={() => resetModule(module.id)}
                        disabled={isLoading}
                      >
                        重置状态
                      </Button>
                    )}
                  </Space>
                </Card>
              </Badge.Ribbon>
            </Col>
          );
        })}
      </Row>

      {/* 使用说明 */}
      <Card
        title="使用说明"
        style={{ marginTop: 24 }}
        type="inner"
      >
        <Row gutter={16}>
          <Col span={12}>
            <h4>首次部署流程</h4>
            <ol>
              <li>运行"数据库初始化"创建表结构</li>
              <li>运行"数据导入"导入护肤品数据</li>
              <li>运行"ML模型训练"训练推荐模型</li>
              <li>运行"数据分析"查看统计信息</li>
              <li>运行"推荐系统测试"验证模型效果</li>
            </ol>
          </Col>
          <Col span={12}>
            <h4>注意事项</h4>
            <ul>
              <li>确保后端服务已启动（http://localhost:5000）</li>
              <li>数据库PostgreSQL必须正在运行</li>
              <li>按顺序运行模块以避免依赖问题</li>
              <li>部分功能需要后端实现管理API</li>
              <li>模型训练可能需要几分钟时间</li>
            </ul>
          </Col>
        </Row>
      </Card>

      {/* API状态监控 */}
      <Card
        title="后端API状态"
        style={{ marginTop: 16 }}
        extra={
          <Tag color={moduleStatus.apiServer === 'running' ? 'success' : 'error'}>
            {moduleStatus.apiServer === 'running' ? '在线' : '离线'}
          </Tag>
        }
      >
        <Row gutter={16}>
          <Col span={8}>
            <Statistic
              title="API服务器"
              value="localhost:5000"
              prefix={<ApiOutlined />}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="数据库"
              value="PostgreSQL"
              prefix={<DatabaseOutlined />}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="ML模型"
              value="TF-IDF + K-NN"
              prefix={<RobotOutlined />}
            />
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default FunctionModules;
