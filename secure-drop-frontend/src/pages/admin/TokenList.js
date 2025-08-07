import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Space, Popconfirm, message, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, StopOutlined } from '@ant-design/icons';
import apiClient from '../../api';
import TokenForm from './TokenForm'; // 稍后创建

const TokenList = () => {
  const [tokens, setTokens] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingToken, setEditingToken] = useState(null);

  // fetchTokens 现在是一个纯粹的工具函数，不依赖任何组件状态
  const fetchTokens = useCallback(async (page, pageSize) => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/admin/tokens?page=${page}&limit=${pageSize}`);
      setTokens(response.data.items);
      // 直接使用返回的总数更新分页状态
      setPagination(prev => ({ ...prev, total: response.data.total, current: page, pageSize: pageSize }));
    } catch (error) {
      message.error('获取令牌列表失败');
    } finally {
      setLoading(false);
    }
  }, []); // 依赖项为空，此函数只创建一次

  // useEffect 只在分页的 current 或 pageSize 变化时触发
  useEffect(() => {
    fetchTokens(pagination.current, pagination.pageSize);
  }, [pagination.current, pagination.pageSize, fetchTokens]);

  // handleTableChange 只负责更新分页状态，useEffect 会自动响应变化
  const handleTableChange = (newPagination) => {
    setPagination(prev => ({
      ...prev,
      current: newPagination.current,
      pageSize: newPagination.pageSize,
    }));
  };

  const handleDelete = async (tokenId) => {
    try {
      await apiClient.delete(`/admin/tokens/${tokenId}`);
      message.success('令牌删除成功');
      // 操作成功后，重新获取当前页的数据
      fetchTokens(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleCreate = () => {
    setEditingToken(null);
    setIsModalVisible(true);
  };

  const handleEdit = (token) => {
    setEditingToken(token);
    setIsModalVisible(true);
  };
  
  const handleRevoke = async (tokenId) => {
    try {
      await apiClient.post(`/admin/tokens/${tokenId}/revoke`);
      message.success('令牌撤销成功');
      // 操作成功后，重新获取当前页的数据
      fetchTokens(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('撤销失败');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: '令牌字符串', dataIndex: 'token_string', key: 'token_string' },
    { title: '描述', dataIndex: 'description', key: 'description' },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        let color = 'geekblue';
        if (status === 'exhausted' || status === 'expired' || status === 'revoked') {
          color = 'volcano';
        } else if (status === 'active') {
          color = 'green';
        }
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      },
    },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at', render: (text) => new Date(text).toLocaleString() },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Popconfirm title="确定要撤销此令牌吗?" onConfirm={() => handleRevoke(record.id)}>
            <Button icon={<StopOutlined />} danger>撤销</Button>
          </Popconfirm>
          <Popconfirm title="确定要删除此令牌吗?" onConfirm={() => handleDelete(record.id)}>
            <Button icon={<DeleteOutlined />} danger type="dashed">删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Button
        type="primary"
        icon={<PlusOutlined />}
        style={{ marginBottom: 16 }}
        onClick={() => handleCreate()}
      >
        创建新令牌
      </Button>
      <Table
        columns={columns}
        dataSource={tokens}
        rowKey="id"
        loading={loading}
        pagination={pagination}
        onChange={handleTableChange}
      />
      <TokenForm
        visible={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingToken(null);
        }}
        onSuccess={() => {
          setIsModalVisible(false);
          setEditingToken(null);
          // 操作成功后，重新获取当前页的数据
          fetchTokens(pagination.current, pagination.pageSize);
        }}
        token={editingToken}
      />
    </>
  );
};

export default TokenList;
