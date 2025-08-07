import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Layout, Typography, message } from 'antd';
import { KeyOutlined } from '@ant-design/icons';
import apiClient from '../../api';

const { Content } = Layout;
const { Title } = Typography;

const GuestLogin = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await apiClient.post('/guest/login', {
        token_string: values.token,
      });
      
      // 将会话令牌和策略存储起来，以便下一页使用
      localStorage.setItem('guest_session_token', response.data.session_token);
      localStorage.setItem('guest_policy', JSON.stringify(response.data.policy));
      
      message.success('令牌验证成功！');
      navigate('/guest/exchange'); // 验证成功后跳转到文件交换页
    } catch (error) {
      message.error(error.response?.data?.detail || '令牌无效或已过期。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Content>
        <Card style={{ width: 400 }}>
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <Title level={2}>安全文件交换</Title>
            <Typography.Text>请输入访问令牌</Typography.Text>
          </div>
          <Form
            name="guest_login"
            onFinish={onFinish}
          >
            <Form.Item
              name="token"
              rules={[{ required: true, message: '请输入访问令牌!' }]}
            >
              <Input prefix={<KeyOutlined />} placeholder="访问令牌" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} style={{ width: '100%' }}>
                进 入
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </Content>
    </Layout>
  );
};

export default GuestLogin;
