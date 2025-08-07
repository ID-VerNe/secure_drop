import axios from 'axios';

// 创建一个 Axios 实例
const apiClient = axios.create({
  baseURL: '/api', // 使用相对路径，因为前端和后端将由同一个服务提供
  headers: {
    'Content-Type': 'application/json',
  },
});

// 添加请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    let token = null;
    // 根据请求的 URL 判断应该使用哪个令牌
    if (config.url.startsWith('/admin')) {
      token = localStorage.getItem('admin_token');
    } else if (config.url.startsWith('/guest')) {
      token = localStorage.getItem('guest_session_token');
    } else {
      // 对于其他请求（例如 /auth），我们可能需要同时检查
      token = localStorage.getItem('admin_token') || localStorage.getItem('guest_session_token');
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // 对请求错误做些什么
    return Promise.reject(error);
  }
);

// 可以在这里添加响应拦截器，例如处理 401 未授权错误

export default apiClient;
