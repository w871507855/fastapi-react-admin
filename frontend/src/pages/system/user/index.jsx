import {
  Button,
  Card,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  message,
} from 'antd'
import { PlusOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import { roleApi, userApi } from '../../../api'
import AuthButton from '../../../components/AuthButton'
import dayjs from 'dayjs'

export default function UserManage() {
  const [form] = Form.useForm()
  const [pwdForm] = Form.useForm()
  const [list, setList] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState({ page: 1, page_size: 10, keyword: '' })
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [pwdOpen, setPwdOpen] = useState(false)
  const [pwdTarget, setPwdTarget] = useState(null)
  const [roleOptions, setRoleOptions] = useState([])

  const fetchList = async () => {
    setLoading(true)
    try {
      const data = await userApi.list(query)
      setList(data.items)
      setTotal(data.total)
    } finally {
      setLoading(false)
    }
  }

  const fetchRoles = async () => {
    const data = await roleApi.list({ page: 1, page_size: 100 })
    setRoleOptions(data.items || [])
  }

  useEffect(() => {
    fetchList()
  }, [query])

  useEffect(() => {
    fetchRoles()
  }, [])

  const handleSave = async () => {
    const values = await form.validateFields()
    const payload = {
      ...values,
      role_ids: values.role_ids || [],
    }
    if (editing) {
      await userApi.update(editing.id, payload)
      message.success('修改成功')
    } else {
      await userApi.create(payload)
      message.success('新增成功')
    }
    setModalOpen(false)
    fetchList()
  }

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setModalOpen(true)
  }

  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue({
      username: record.username,
      nickname: record.nickname,
      email: record.email,
      phone: record.phone,
      role_ids: record.roles.map((r) => r.id),
    })
    setModalOpen(true)
  }

  const handleDelete = async (id) => {
    await userApi.remove(id)
    message.success('删除成功')
    fetchList()
  }

  const handleStatus = async (record, checked) => {
    await userApi.updateStatus(record.id, checked)
    message.success('状态已更新')
    fetchList()
  }

  const handleResetPwd = async () => {
    const { password } = await pwdForm.validateFields()
    await userApi.resetPassword(pwdTarget.id, password)
    message.success('密码已重置')
    setPwdOpen(false)
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '用户名', dataIndex: 'username' },
    { title: '昵称', dataIndex: 'nickname' },
    { title: '邮箱', dataIndex: 'email' },
    { title: '手机号', dataIndex: 'phone' },
    {
      title: '角色',
      dataIndex: 'roles',
      render: (roles) =>
        roles.length ? (
          roles.map((r) => <Tag key={r.id}>{r.name}</Tag>)
        ) : (
          <span style={{ color: '#999' }}>-</span>
        ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (status, record) => (
        <Switch
          checked={status}
          disabled={record.is_superuser}
          onChange={(checked) => handleStatus(record, checked)}
        />
      ),
    },
    { title: '创建时间', dataIndex: 'created_at', width: 170, render: (v) => dayjs(v).format('YYYY-MM-DD HH:mm') },
    {
      title: '操作',
      key: 'action',
      width: 220,
      render: (_, record) => (
        <Space>
          <AuthButton code="system:user:update" size="small" onClick={() => openEdit(record)}>
            编辑
          </AuthButton>
          <AuthButton
            code="system:user:update"
            size="small"
            onClick={() => {
              setPwdTarget(record)
              pwdForm.resetFields()
              setPwdOpen(true)
            }}
          >
            重置密码
          </AuthButton>
          <Popconfirm title="确定删除该用户？" onConfirm={() => handleDelete(record.id)}>
            <AuthButton
              code="system:user:delete"
              size="small"
              danger
              disabled={record.is_superuser}
            >
              删除
            </AuthButton>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Card>
      <Space style={{ marginBottom: 16 }}>
        <Input.Search
          placeholder="搜索用户名/昵称/手机号"
          allowClear
          onSearch={(v) => setQuery((q) => ({ ...q, page: 1, keyword: v }))}
          style={{ width: 280 }}
          prefix={<SearchOutlined />}
        />
        <Button icon={<ReloadOutlined />} onClick={fetchList}>
          刷新
        </Button>
        <AuthButton code="system:user:add" type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          新增用户
        </AuthButton>
      </Space>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={list}
        loading={loading}
        pagination={{
          current: query.page,
          pageSize: query.page_size,
          total,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
          onChange: (page, pageSize) => setQuery((q) => ({ ...q, page, page_size: pageSize })),
        }}
      />

      <Modal
        title={editing ? '编辑用户' : '新增用户'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => setModalOpen(false)}
        destroyOnClose
      >
        <Form form={form} layout="vertical" initialValues={{ status: true }}>
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input disabled={!!editing} placeholder="用户名" />
          </Form.Item>
          {!editing && (
            <Form.Item
              name="password"
              label="密码"
              rules={[{ required: true, min: 6, message: '密码至少 6 位' }]}
            >
              <Input.Password placeholder="密码" />
            </Form.Item>
          )}
          <Form.Item name="nickname" label="昵称">
            <Input placeholder="昵称" />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input placeholder="邮箱" />
          </Form.Item>
          <Form.Item name="phone" label="手机号">
            <Input placeholder="手机号" />
          </Form.Item>
          <Form.Item name="role_ids" label="角色">
            <Select
              mode="multiple"
              placeholder="选择角色"
              options={roleOptions.map((r) => ({ label: r.name, value: r.id }))}
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`重置密码 - ${pwdTarget?.username || ''}`}
        open={pwdOpen}
        onOk={handleResetPwd}
        onCancel={() => setPwdOpen(false)}
        destroyOnClose
      >
        <Form form={pwdForm} layout="vertical">
          <Form.Item
            name="password"
            label="新密码"
            rules={[{ required: true, min: 6, message: '密码至少 6 位' }]}
          >
            <Input.Password placeholder="新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
