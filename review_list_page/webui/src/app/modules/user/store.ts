import { createStore } from 'root/utils/zustand'
import { fetchUtils } from '@indico-data/utils'

const token = '2|a911ae1a|4b2e5e2edc93617b040ce8d7e83978e9|1591963926'

export type AuthorizedUser = {
  id: number
  active: boolean
  apiRefreshToken: {
    createdAt: number
  } | null
  email: string
  name: string
  registeredDate: string
  sCity: string
  sCountry: string
  sState: string
  sStreet: string
  sStreet2: string
  sZip: string
  scopes: {
    scope: 'MANAGE_USERS' | 'APP_ACCESS' | 'GRAPHIQL'
  }[]
  logins: {
    logins: { loggedInAt: string; loginIp: string }[]
  }
}

export type Store = {
  authenticating: boolean
  user: AuthorizedUser
  verifyUser: any
  submitLogin: any
  authError: string
  submitLogout: any
}

const verifyUserAPI = () => {
  return fetchUtils
    .getCurrentUser()
    .then((json: any) => json)
    .catch((err: number) => {
      if (err === 401) {
        return Promise.reject(401)
      } else {
        return Promise.reject(err)
      }
    })
}

export const postUserLoginAPI = (authModel: { email: string; password: string }) => {
  return fetchUtils
    .postAuthJSON(`/users/authenticate`, token, {
      ...authModel,
      email: authModel.email.toLowerCase(),
    })
    .then((json: any) => json)
    .catch((err: string) => {
      return Promise.reject(err)
    })
}

export const userLogoutAPI = () => {
  return fetchUtils
    .postAuthJSON(`/users/logout`, token)
    .then((json: any) => {
      return json
    })
    .catch((err: string) => {
      return Promise.reject(err)
    })
}

const store = (set: (cb: (state: Store) => void) => void, get: () => Store): Store => ({
  authenticating: false,
  user: null,
  authError: '',
  verifyUser: () => {
    set((state: Store) => {
      state.authenticating = true
    })
    return verifyUserAPI()
      .then((user: AuthorizedUser) => {
        set((state: Store) => {
          state.authenticating = false
          state.user = user
        })
        return true
      })
      .catch((err: any) => {
        set((state: Store) => {
          state.authenticating = false
          state.user = null
        })
        return Promise.reject(err)
      })
  },
  submitLogin: (email: string, password: string) => {
    set((state: Store) => {
      state.authenticating = true
    })

    return postUserLoginAPI({ email, password })
      .then(() => {
        get().verifyUser()
        set((state: Store) => {
          state.authError = ''
        })
      })
      .catch((err: any) => {
        if (err.error_type === 'LoginRequired') {
          set((state: Store) => {
            state.authenticating = false
            state.authError = 'Invalid Email or Password'
          })
        } else if (err.error_type === 'AccountLocked') {
          set((state: Store) => {
            state.authenticating = false
            state.authError =
              'You have been locked out of your account due to unsuccessful login attempts. Please contact your site administrator or wait until your lockout expires.'
          })
        } else if (err.error_type === 'SessionLimit') {
          set((state: Store) => {
            state.authenticating = false
            state.authError =
              'You currently have another session open. Please log out before attempting to log in.'
          })
        } else {
          set((state: Store) => {
            state.authenticating = false
            state.authError = 'An error occurred while attempting to log you in. Please try again.'
          })
        }
      })
  },
  submitLogout: () => {
    set((state: Store) => {
      state.authenticating = true
    })

    return userLogoutAPI()
      .then(() => {
        set((state: Store) => {
          state.authenticating = false
          state.user = null
        })
      })
      .catch(() => {
        set((state: Store) => {
          state.authenticating = false
        })
      })
  },
})

export const useUser = createStore(store)
