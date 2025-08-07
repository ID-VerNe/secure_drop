import React from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { Layout, Menu, Button, message } from 'antd';
import { KeyOutlined, LogoutOutlined } from '@ant-design/icons';
import TokenList from './TokenList'; // 我们稍后会创建这个组件

const { Header, Content, Sider } = Layout;

const AdminLayout = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    message.success('您已成功退出。');
    navigate('/admin/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider>
        <div style={{ height: '32px', margin: '16px', color: 'white', fontSize: '18px', textAlign: 'center' }}>
          SecureDrop
        </div>
        <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline">
          <Menu.Item key="1" icon={<KeyOutlined />}>
            <Link to="/admin/tokens">令牌管理</Link>
          </Menu.Item>
        </Menu>
      </Sider>
      <Layout>
        <Header style={{ padding: '0 24px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', background: '#fff' }}>
          <Button type="primary" icon={<LogoutOutlined />} onClick={handleLogout}>
            退出登录
          </Button>
        </Header>
        <Content style={{ margin: '24px' }}>
          <div style={{ padding: 24, minHeight: 360, background: '#fff' }}>
            <Routes>
              <Route path="tokens" element={<TokenList />} />
              {/* 可以在这里添加其他管理页面的路由 */}
            </Routes>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default AdminLayout;
