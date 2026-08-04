import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: '',
      userInfo: null,
      permissions: [],
      menus: [],

      setToken: (token) => set({ token }),
      setUserInfo: (userInfo) => set({ userInfo }),
      setPermissions: (permissions) => set({ permissions }),
      setMenus: (menus) => set({ menus }),

      hasPermission: (code) => {
        const state = get()
        if (state.userInfo?.is_superuser) return true
        return state.permissions.includes(code)
      },

      logout: () =>
        set({ token: '', userInfo: null, permissions: [], menus: [] }),
    }),
    { name: 'admin-auth' }
  )
)
