import {
  Button,
  Card,
  Form,
  Input,
  Modal,
  Popconfirm,
  Space,
  Table,
  Tag,
  Tree,
  message,
} from 'antd'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import { permissionApi, roleApi } from '../../../api'
import AuthButton from '../../../components/AuthButton'
import dayjs from 'dayjs'

function buildTreeData(perms, onlyMenus = false) {
  return perms.map((p) => ({
    title: p.name,
    key: p.id,
    children: p.children?.length ? buildTreeData(p.children, onlyMenus) : undefined,
  }))
}

function collectAllIds(nodes, acc = []) {
  nodes.forEach((n) => {
    acc.push(n.id)
    if (n.children?.length) collectAllIds(n.children, acc)
  })
  return acc
}

export default function RoleManage() {
  const [form] = Form.useForm()
  const [list, setList] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState({ page: 1, page_size: 10, keyword: '' })
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [permTree, setPermTree] = useState([])
  const [checkedKeys, setCheckedKeys] = useState([])

  const fetchList = async () => {
    setLoading(true)
    try {
      const data = await roleApi.list(query)
      setList(data.items)
      setTotal(data.total)
    } finally {
      setLoading(false)
    }
  }

  const fetchPermTree = async () => {
    const data = await permissionApi.tree()
    setPermTree(data)
  }

  useEffect(() => {
    fetchList()
  }, [query])

  useEffect(() => {
    fetchPermTree()
  }, [])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setCheckedKeys([])
    setModalOpen(true)
  }

  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue({
      code: record.code,
      name: record.name,
      description: record.description,
    })
    setCheckedKeys(record.permission_ids || [])
    setModalOpen(true)
  }

  const handleSave = async () => {
    const values = await form.validateFields()
    const payload = {
      ...values,
      permission_ids: checkedKeys,
    }
    if (editing) {
      await roleApi.update(editing.id, payload)
      message.success('修改成功')
    } else {
      await roleApi.create(payload)
      message.success('新增成功')
    }
    setModalOpen(false)
    fetchList()
  }

  const handleDelete = async (id) => {
    await roleApi.remove(id)
    message.success('删除成功')
    fetchList()
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '角色编码', dataIndex: 'code' },
    { title: '角色名称', dataIndex: 'name' },
    { title: '描述', dataIndex: 'description', ellipsis: true },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (status) => <Tag color={status ? 'success' : 'default'}>{status ? '启用' : '禁用'}</Tag>,
    },
    { title: '创建时间', dataIndex: 'created_at', width: 170, render: (v) => dayjs(v).format('YYYY-MM-DD HH:mm') },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_, record) => (
        <Space>
          <AuthButton code="system:role:update" size="small" onClick={() => openEdit(record)}>
            编辑
          </AuthButton>
          <Popconfirm title="确定删除该角色？" onConfirm={() => handleDelete(record.id)}>
            <AuthButton code="system:role:delete" size="small" danger>
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
          placeholder="搜索角色名称/编码"
          allowClear
          onSearch={(v) => setQuery((q) => ({ ...q, page: 1, keyword: v }))}
          style={{ width: 280 }}
        />
        <Button icon={<ReloadOutlined />} onClick={fetchList}>
          刷新
        </Button>
        <AuthButton code="system:role:add" type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          新增角色
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
        title={editing ? '编辑角色' : '新增角色'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => setModalOpen(false)}
        destroyOnClose
        width={480}
      >
        <Form form={form} layout="vertical" initialValues={{ status: true }}>
          <Form.Item name="code" label="角色编码" rules={[{ required: true, message: '请输入角色编码' }]}>
            <Input placeholder="如 system_admin" />
          </Form.Item>
          <Form.Item name="name" label="角色名称" rules={[{ required: true, message: '请输入角色名称' }]}>
            <Input placeholder="角色名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} placeholder="描述" />
          </Form.Item>
          <Form.Item label="权限分配">
            <Tree
              checkable
              defaultExpandAll
              treeData={buildTreeData(permTree)}
              checkedKeys={checkedKeys}
              onCheck={(keys) => setCheckedKeys(Array.isArray(keys) ? keys : keys.checked)}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
