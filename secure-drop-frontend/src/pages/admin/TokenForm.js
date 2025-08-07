import React, { useEffect, useState } from 'react';
import {
  Modal,
  Form,
  Input,
  DatePicker,
  InputNumber,
  Switch,
  Select,
  message,
  Row,
  Col,
} from 'antd';
import apiClient from '../../api';
import dayjs from 'dayjs';

const { TextArea } = Input;

const TokenForm = ({ visible, onCancel, onSuccess, token }) => {
  const [form] = Form.useForm();
  const isEditing = !!token;
  const [downloadableDirs, setDownloadableDirs] = useState([]);

  useEffect(() => {
    // 当模态框可见时，获取可下载的目录列表
    if (visible) {
      const fetchDirs = async () => {
        try {
          const response = await apiClient.get('/admin/tokens/downloadable-dirs');
          setDownloadableDirs(response.data);
        } catch (error) {
          message.error('无法加载可下载目录列表');
        }
      };
      fetchDirs();
    }
  }, [visible]);

  useEffect(() => {
    if (visible) {
      if (isEditing && token) {
        // 当编辑时，加载现有令牌数据
        form.setFieldsValue({
          ...token,
          expires_at: token.expires_at ? dayjs(token.expires_at) : null,
        });
      } else {
        // 创建新令牌时，设置默认值
        form.resetFields();
        form.setFieldsValue({
          description: '',
          expires_at: null,
          page_title: '',
          welcome_message: '',
          upload_path: '',
          allowed_file_types: '',
          max_file_size_mb: null,
          downloadable_path: null,
          max_usage_count: 1,
          delete_on_exhaust: false,
          filename_conflict_strategy: 'rename',
          allow_upload: false,
          allow_download: false,
          allow_resumable_download: true,
        });
      }
    }
  }, [visible, token, isEditing, form]);

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        ...values,
        // 将 dayjs 对象格式化为 ISO 字符串
        expires_at: values.expires_at ? values.expires_at.toISOString() : null,
      };

      if (isEditing) {
        await apiClient.put(`/admin/tokens/${token.id}`, payload);
        message.success('令牌更新成功');
      } else {
        await apiClient.post('/admin/tokens/', payload);
        message.success('令牌创建成功');
      }
      onSuccess();
    } catch (error) {
      message.error('操作失败');
    }
  };

  return (
    <Modal
      title={isEditing ? '编辑令牌' : '创建新令牌'}
      open={visible}
      onCancel={onCancel}
      onOk={handleOk}
      width={800}
      destroyOnClose
    >
      <Form form={form} layout="vertical" name="token_form">
        <Form.Item name="description" label="描述">
          <Input placeholder="例如：用于XX项目的临时上传" />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="expires_at" label="过期时间">
              <DatePicker showTime style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="max_usage_count" label="最大使用次数 (0为无限)" initialValue={1}>
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item name="delete_on_exhaust" label="用尽后自动删除" valuePropName="checked">
          <Switch />
        </Form.Item>
        <hr style={{ margin: '20px 0' }} />
        <Form.Item name="page_title" label="访客页面标题">
          <Input />
        </Form.Item>
        <Form.Item name="welcome_message" label="访客页面欢迎信息">
          <TextArea rows={2} />
        </Form.Item>
        <hr style={{ margin: '20px 0' }} />
        <Form.Item name="allow_upload" label="允许上传" valuePropName="checked">
          <Switch />
        </Form.Item>

        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) => prevValues.allow_upload !== currentValues.allow_upload}
        >
          {({ getFieldValue }) =>
            getFieldValue('allow_upload') ? (
              <>
                <Form.Item name="upload_path" label="上传路径 (相对路径)">
                  <Input placeholder="例如：project_alpha/uploads" />
                </Form.Item>
                <Form.Item name="allowed_file_types" label="允许的文件类型 (逗号分隔)">
                  <Input placeholder=".jpg,.pdf,.zip" />
                </Form.Item>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item name="max_file_size_mb" label="最大单文件大小 (MB)">
                      <InputNumber min={1} style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item name="filename_conflict_strategy" label="文件名冲突策略">
                      <Select>
                        <Select.Option value="rename">重命名</Select.Option>
                        <Select.Option value="overwrite">覆盖</Select.Option>
                        <Select.Option value="reject">拒绝</Select.Option>
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>
              </>
            ) : null
          }
        </Form.Item>

        <hr style={{ margin: '20px 0' }} />
        <Form.Item name="allow_download" label="允许下载" valuePropName="checked">
          <Switch />
        </Form.Item>

        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) => prevValues.allow_download !== currentValues.allow_download}
        >
          {({ getFieldValue }) =>
            getFieldValue('allow_download') ? (
              <Form.Item name="downloadable_path" label="可下载的文件夹">
                <Select placeholder="请选择一个文件夹">
                  {downloadableDirs.map(dir => (
                    <Select.Option key={dir} value={dir}>
                      {dir}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            ) : null
          }
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default TokenForm;
