import { createStore } from 'root/utils/zustand'

export type Store = {
  isSidebarOpen: boolean
  toggleSidebar: () => void
}

const store = (set: (cb: (state: Store) => void) => void, get: () => Store): Store => ({
  isSidebarOpen: true,
  toggleSidebar: () => {
    const { isSidebarOpen } = get()
    set((state: Store) => {
      state.isSidebarOpen = !isSidebarOpen
    })
  },
})

export const useApp = createStore(store)
