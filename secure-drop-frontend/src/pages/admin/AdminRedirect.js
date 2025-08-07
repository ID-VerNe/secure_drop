import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AdminRedirect = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const isAdminLoggedIn = !!localStorage.getItem('admin_token');
    if (isAdminLoggedIn) {
      // 如果已登录，重定向到令牌管理页面
      navigate('/admin/tokens', { replace: true });
    } else {
      // 如果未登录，重定向到登录页面
      navigate('/admin/login', { replace: true });
    }
  }, [navigate]);

  // 这个组件只负责重定向，不渲染任何内容
  return null; 
};

export default AdminRedirect;
