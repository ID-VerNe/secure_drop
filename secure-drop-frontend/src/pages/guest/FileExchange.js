import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layout,
  Typography,
  Alert,
  Upload,
  Button,
  List,
  message,
  Progress,
  Row,
  Col,
  Card,
  Divider,
} from 'antd';
import { InboxOutlined, DownloadOutlined } from '@ant-design/icons';
import apiClient from '../../api';

const { Content } = Layout;
const { Title, Text } = Typography;
const { Dragger } = Upload;

const FileExchange = () => {
  const navigate = useNavigate();
  const [policy, setPolicy] = useState(null);
  const [downloadableFiles, setDownloadableFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    const storedPolicy = localStorage.getItem('guest_policy');
    if (!storedPolicy) {
      message.error('无效的会话，请重新登录。');
      navigate('/guest/login');
      return;
    }
    const parsedPolicy = JSON.parse(storedPolicy);
    setPolicy(parsedPolicy);

    if (parsedPolicy.allow_download) {
      const fetchFiles = async () => {
        try {
          const response = await apiClient.get('/guest/files');
          setDownloadableFiles(response.data);
        } catch (error) {
          message.error('获取可下载文件列表失败。');
        }
      };
      fetchFiles();
    }
  }, [navigate]);

  const draggerProps = useMemo(() => {
    if (!policy) return {};
    
    const allowedFileTypes = policy.allowed_file_types ? policy.allowed_file_types.split(',').join(',') : '';

    return {
      name: 'file',
      multiple: true,
      action: `${apiClient.defaults.baseURL}/guest/upload`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('guest_session_token')}`,
      },
      beforeUpload: (file) => {
        if (policy.max_file_size_mb) {
          const isLtSize = file.size / 1024 / 1024 < policy.max_file_size_mb;
          if (!isLtSize) {
            message.error(`文件必须小于 ${policy.max_file_size_mb}MB!`);
            return Upload.LIST_IGNORE;
          }
        }
        return true;
      },
      onChange(info) {
        const { status } = info.file;
        setUploading(info.fileList.some(f => f.status === 'uploading'));
        if (status === 'done') {
          message.success(`${info.file.name} 文件上传成功。`);
        } else if (status === 'error') {
          message.error(`${info.file.name} 文件上传失败: ${info.file.response?.detail || '未知错误'}`);
        }
      },
      accept: allowedFileTypes,
    };
  }, [policy]);

  const handleDownload = (filename) => {
    // apiClient.defaults.baseURL 已经是 /api，所以我们拼接 guest/download/...
    const url = `/api/guest/download/${filename}`;
    const token = localStorage.getItem('guest_session_token');
    
    fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => {
      if (!res.ok) throw new Error('下载失败');
      return res.blob();
    })
    .then(blob => {
      const href = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = href;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(href);
    })
    .catch(err => message.error(err.message));
  };

  if (!policy) {
    return null; // 或者一个加载指示器
  }

  return (
    <Layout style={{ minHeight: '100vh', padding: '24px' }}>
      <Content style={{ maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <Title level={2}>{policy.page_title || '文件交换'}</Title>
        {policy.welcome_message && <Alert message={policy.welcome_message} type="info" showIcon style={{ marginBottom: 24 }} />}
        
        <Row gutter={24}>
          {policy.allow_upload && (
            <Col xs={24} md={policy.allow_download ? 12 : 24}>
              <Card title="上传文件">
                <Dragger {...draggerProps} disabled={uploading}>
                  <p className="ant-upload-drag-icon"><InboxOutlined /></p>
                  <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                  <p className="ant-upload-hint">
                    {policy.allowed_file_types ? `支持的文件类型: ${policy.allowed_file_types}` : '支持任何文件类型'}
                  </p>
                </Dragger>
              </Card>
            </Col>
          )}
          {policy.allow_download && (
            <Col xs={24} md={policy.allow_upload ? 12 : 24}>
              <Card title="下载文件">
                <List
                  dataSource={downloadableFiles}
                  renderItem={(item) => (
                    <List.Item
                      actions={[<Button icon={<DownloadOutlined />} onClick={() => handleDownload(item)}>下载</Button>]}
                    >
                      <List.Item.Meta title={item} />
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          )}
        </Row>
      </Content>
    </Layout>
  );
};

export default FileExchange;
