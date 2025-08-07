import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import AdminLayout from './pages/admin/AdminLayout';
import AdminLogin from './pages/admin/AdminLogin';
import GuestLogin from './pages/guest/GuestLogin';
import FileExchange from './pages/guest/FileExchange';

// 一个简单的私有路由组件，用于保护需要登录的页面
const PrivateRoute = ({ children }) => {
  const isAdminLoggedIn = !!localStorage.getItem('admin_token');
  return isAdminLoggedIn ? children : <Navigate to="/admin/login" />;
};

function App() {
  return (
    <ConfigProvider
      theme={{
        // 移除暗色主题，使用默认的日间主题
        token: {
          // 在这里可以覆盖主题的 token，例如主色调
          colorPrimary: '#1677ff',
        },
      }}
    >
      <Router>
        <Routes>
          {/* 根路径重定向到访客登录页 */}
          <Route path="/" element={<Navigate to="/guest/login" />} />

          {/* 访客路由 */}
          <Route path="/guest/login" element={<GuestLogin />} />
          <Route path="/guest/exchange" element={<FileExchange />} />

          {/* 管理员路由 */}
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route 
            path="/admin/*" 
            element={
              <PrivateRoute>
                <AdminLayout />
              </PrivateRoute>
            } 
          />
        </Routes>
      </Router>
    </ConfigProvider>
  );
}

export default App;
