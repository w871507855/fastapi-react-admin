import { Layout, Menu, Dropdown, Avatar, Spin } from 'antd'
import {
  DashboardOutlined,
  SettingOutlined,
  UserOutlined,
  TeamOutlined,
  SafetyOutlined,
  LogoutOutlined,
} from '@ant-design/icons'
import { useEffect, useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { authApi } from '../api'
import { useAuthStore } from '../store/auth'

const { Header, Sider, Content } = Layout

const iconMap = {
  DashboardOutlined,
  SettingOutlined,
  UserOutlined,
  TeamOutlined,
  SafetyOutlined,
}

function renderIcon(name) {
  const Comp = iconMap[name] || SettingOutlined
  return <Comp />
}

function buildMenuItems(menus) {
  return menus.map((m) => {
    const children = m.children && m.children.length ? m.children : null
    const item = {
      key: m.path || `perm-${m.id}`,
      icon: renderIcon(m.icon),
      label: m.name,
    }
    if (children) {
      item.children = children.map((c) => ({
        key: c.path || `perm-${c.id}`,
        icon: renderIcon(c.icon),
        label: c.name,
      }))
    }
    return item
  })
}

export default function BasicLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { token, userInfo, menus, permissions, logout } = useAuthStore()
  const [loading, setLoading] = useState(!userInfo)

  useEffect(() => {
    if (!token) return
    if (!userInfo) {
      Promise.all([authApi.me(), authApi.menus()])
        .then(([me, menuTree]) => {
          useAuthStore.setState({
            userInfo: me,
            permissions: me.permissions,
            menus: menuTree,
          })
        })
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [token, userInfo])

  const menuItems = buildMenuItems(menus)
  const selectedKeys = [location.pathname]

  const userMenu = {
    items: [
      { key: 'logout', icon: <LogoutOutlined />, label: '退出登录' },
    ],
    onClick: ({ key }) => {
      if (key === 'logout') {
        logout()
        navigate('/login', { replace: true })
      }
    },
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" collapsible breakpoint="lg">
        <div
          style={{
            height: 56,
            margin: 8,
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 18,
            fontWeight: 600,
          }}
        >
          后台管理
        </div>
        <Menu
          theme="dark"
          mode="inline"
          items={menuItems}
          selectedKeys={selectedKeys}
          onClick={({ key }) => {
            if (key.startsWith('/')) navigate(key)
          }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            boxShadow: '0 1px 4px rgba(0,21,41,0.08)',
          }}
        >
          <Dropdown menu={userMenu}>
            <span style={{ cursor: 'pointer' }}>
              <Avatar size="small" icon={<UserOutlined />} style={{ marginRight: 8 }} />
              {userInfo?.nickname || userInfo?.username || '用户'}
            </span>
          </Dropdown>
        </Header>
        <Content style={{ margin: 16 }}>
          {loading ? (
            <div style={{ textAlign: 'center', paddingTop: 100 }}>
              <Spin size="large" />
            </div>
          ) : (
            <Outlet />
          )}
        </Content>
      </Layout>
    </Layout>
  )
}
