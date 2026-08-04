import request from './request'

export const authApi = {
  login: (data) => request.post('/auth/login', data),
  me: () => request.get('/auth/me'),
  menus: () => request.get('/auth/menus'),
}

export const userApi = {
  list: (params) => request.get('/users', { params }),
  create: (data) => request.post('/users', data),
  update: (id, data) => request.put(`/users/${id}`, data),
  remove: (id) => request.delete(`/users/${id}`),
  updateStatus: (id, status) => request.put(`/users/${id}/status`, { status }),
  resetPassword: (id, password) => request.put(`/users/${id}/password`, { password }),
}

export const roleApi = {
  list: (params) => request.get('/roles', { params }),
  create: (data) => request.post('/roles', data),
  update: (id, data) => request.put(`/roles/${id}`, data),
  remove: (id) => request.delete(`/roles/${id}`),
}

export const permissionApi = {
  tree: () => request.get('/permissions/tree'),
  list: () => request.get('/permissions'),
  create: (data) => request.post('/permissions', data),
  update: (id, data) => request.put(`/permissions/${id}`, data),
  remove: (id) => request.delete(`/permissions/${id}`),
}
