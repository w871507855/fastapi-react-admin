import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  TreeSelect,
  message,
} from 'antd'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import { permissionApi } from '../../../api'
import AuthButton from '../../../components/AuthButton'

const TYPE_MAP = {
  1: { label: '目录', color: 'blue' },
  2: { label: '菜单', color: 'green' },
  3: { label: '按钮', color: 'orange' },
}

function toTreeSelect(nodes) {
  return nodes.map((n) => ({
    value: n.id,
    title: n.name,
    children: n.children?.length ? toTreeSelect(n.children) : undefined,
  }))
}

function buildTree(list) {
  const map = {}
  list.forEach((item) => {
    map[item.id] = { ...item, children: [] }
  })
  const roots = []
  list.forEach((item) => {
    if (item.parent_id && map[item.parent_id]) {
      map[item.parent_id].children.push(map[item.id])
    } else {
      roots.push(map[item.id])
    }
  })
  return roots
}

export default function PermissionManage() {
  const [form] = Form.useForm()
  const [treeData, setTreeData] = useState([])
  const [flatList, setFlatList] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)

  const fetchTree = async () => {
    setLoading(true)
    try {
      const [tree, flat] = await Promise.all([permissionApi.tree(), permissionApi.list()])
      setTreeData(tree)
      setFlatList(flat)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTree()
  }, [])

  const openCreate = (parent) => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({
      parent_id: parent?.id || 0,
      type: parent ? 3 : 2,
      sort: 0,
      status: true,
    })
    setModalOpen(true)
  }

  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue({ ...record })
    setModalOpen(true)
  }

  const handleSave = async () => {
    const values = await form.validateFields()
    if (editing) {
      await permissionApi.update(editing.id, values)
      message.success('修改成功')
    } else {
      await permissionApi.create(values)
      message.success('新增成功')
    }
    setModalOpen(false)
    fetchTree()
  }

  const handleDelete = async (id) => {
    await permissionApi.remove(id)
    message.success('删除成功')
    fetchTree()
  }

  const renderTree = (nodes) =>
    nodes.map((n) => ({
      key: n.id,
      id: n.id,
      name: n.name,
      code: n.code,
      type: n.type,
      path: n.path,
      icon: n.icon,
      sort: n.sort,
      status: n.status,
      parent_id: n.parent_id,
      children: n.children?.length ? renderTree(n.children) : undefined,
    }))

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      render: (name, record) => (record.type === 1 ? <strong>{name}</strong> : name),
    },
    {
      title: '类型',
      dataIndex: 'type',
      width: 80,
      render: (t) => <Tag color={TYPE_MAP[t]?.color}>{TYPE_MAP[t]?.label}</Tag>,
    },
    { title: '权限编码', dataIndex: 'code' },
    { title: '路由', dataIndex: 'path' },
    { title: '组件', dataIndex: 'component' },
    { title: '图标', dataIndex: 'icon' },
    { title: '排序', dataIndex: 'sort', width: 70 },
    {
      title: '状态',
      dataIndex: 'status',
      width: 80,
      render: (s) => (s ? '启用' : '禁用'),
    },
    {
      title: '操作',
      key: 'action',
      width: 220,
      render: (_, record) => (
        <Space>
          <AuthButton
            code="system:permission:add"
            size="small"
            onClick={() => openCreate(record)}
          >
            新增子项
          </AuthButton>
          <AuthButton code="system:permission:update" size="small" onClick={() => openEdit(record)}>
            编辑
          </AuthButton>
          <Popconfirm title="确定删除该权限？" onConfirm={() => handleDelete(record.id)}>
            <AuthButton code="system:permission:delete" size="small" danger>
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
        <Button icon={<ReloadOutlined />} onClick={fetchTree}>
          刷新
        </Button>
        <AuthButton
          code="system:permission:add"
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => openCreate(null)}
        >
          新增根节点
        </AuthButton>
      </Space>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={renderTree(treeData)}
        loading={loading}
        pagination={false}
        expandable={{ defaultExpandAllRows: true }}
      />

      <Modal
        title={editing ? '编辑权限' : '新增权限'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => setModalOpen(false)}
        destroyOnClose
      >
        <Form form={form} layout="vertical" initialValues={{ parent_id: 0, type: 2, sort: 0, status: true }}>
          <Form.Item name="parent_id" label="父级" rules={[{ required: true }]}>
            <TreeSelect
              treeData={[{ value: 0, title: '顶级节点', children: toTreeSelect(buildTree(flatList)) }]}
              treeDefaultExpandAll
            />
          </Form.Item>
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
            <Input placeholder="名称" />
          </Form.Item>
          <Form.Item name="type" label="类型" rules={[{ required: true }]}>
            <Select
              options={[
                { value: 1, label: '目录' },
                { value: 2, label: '菜单' },
                { value: 3, label: '按钮' },
              ]}
            />
          </Form.Item>
          <Form.Item name="code" label="权限编码">
            <Input placeholder="如 system:user:list" />
          </Form.Item>
          <Form.Item name="path" label="路由">
            <Input placeholder="如 /system/user" />
          </Form.Item>
          <Form.Item name="component" label="组件">
            <Input placeholder="如 system/user" />
          </Form.Item>
          <Form.Item name="icon" label="图标">
            <Input placeholder="如 UserOutlined" />
          </Form.Item>
          <Form.Item name="sort" label="排序">
            <InputNumber min={0} />
          </Form.Item>
          <Form.Item name="status" label="状态" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
