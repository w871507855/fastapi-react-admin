import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from './store/auth'
import Login from './pages/login'
import BasicLayout from './layouts/BasicLayout'
import Dashboard from './pages/dashboard'
import UserManage from './pages/system/user'
import RoleManage from './pages/system/role'
import PermissionManage from './pages/system/permission'
import NotFound from './pages/NotFound'

function RequireAuth({ children }) {
  const token = useAuthStore((s) => s.token)
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <RequireAuth>
              <BasicLayout />
            </RequireAuth>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="system/user" element={<UserManage />} />
          <Route path="system/role" element={<RoleManage />} />
          <Route path="system/permission" element={<PermissionManage />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
