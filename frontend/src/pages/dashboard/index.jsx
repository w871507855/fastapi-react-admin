import { Card, Col, Row, Statistic } from 'antd'
import {
  UserOutlined,
  TeamOutlined,
  SafetyOutlined,
} from '@ant-design/icons'
import { useEffect, useState } from 'react'
import request from '../../api/request'
import { useAuthStore } from '../../store/auth'

export default function Dashboard() {
  const userInfo = useAuthStore((s) => s.userInfo)
  const [stats, setStats] = useState({ users: 0, roles: 0, permissions: 0 })

  useEffect(() => {
    request.get('/stats').then(setStats).catch(() => {})
  }, [])

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <h3>欢迎，{userInfo?.nickname || userInfo?.username}！</h3>
        <p style={{ color: '#999', marginBottom: 0 }}>
          这是一个基于 FastAPI + React + Ant Design 的通用后台管理系统。
        </p>
      </Card>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic title="用户总数" value={stats.users} prefix={<UserOutlined />} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="角色总数" value={stats.roles} prefix={<TeamOutlined />} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="权限数量" value={stats.permissions} prefix={<SafetyOutlined />} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
