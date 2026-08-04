import { Button } from 'antd'
import { useAuthStore } from '../store/auth'

export default function AuthButton({ code, children, ...props }) {
  const hasPermission = useAuthStore((s) => s.hasPermission)
  if (!hasPermission(code)) return null
  return <Button {...props}>{children}</Button>
}
