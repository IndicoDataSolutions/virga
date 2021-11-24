import React, { useState, useEffect } from 'react'
import { BrowserRouter, Switch, Route } from 'react-router-dom'

// App
import * as ROUTES from './routes'
import { Store as UserStore, useUser } from 'User/store'

// Routing
import { RouterPrivateRoute } from './PrivateRoute'

// Auth
import { Login } from 'Auth/pages/Login'
import { Account } from 'Auth/pages/Account'
import { FourOhFour } from 'root/base/FourOhFour'
import { NoAccess } from 'root/base/NoAccess'
import { List } from 'Review/pages/List'

const routeMap = [
  { path: ROUTES.AUTH_ACCOUNT, component: Account, type: 'PRIVATE' },
  { path: ROUTES.BASE_NO_ACCESS, component: NoAccess, type: 'REGULAR' },
  { path: ROUTES.REVIEW_LIST_PAGE, component: List, type: 'PRIVATE'},
  { path: '*', component: FourOhFour, type: 'REGULAR' },
]

const userSelector = (state: UserStore) => ({
  verifyUser: state.verifyUser,
})

export const Router = () => {
  const [loginError, setLoginError] = useState<boolean>(false)
  const [redirect, setRedirect] = useState<{ url: string }>({ url: '' })
  const { verifyUser } = useUser(userSelector)

  useEffect(() => {
    verifyUser().catch((err) => {
      if (err.status !== 401) {
        setLoginError(true)
      }
    })
  }, [])

  const resetRedirect = (location, history) => {
    if (location) {
      setRedirect({ url: location })
      history.push(`/?redirect_url=${location}`)
    } else {
      setRedirect({ url: '' })
    }
  }

  return (
    <BrowserRouter>
      <main style={{ height: '100%' }}>
        <Switch>
          <Route exact path="/" component={Login} />
          <Route
            exact
            path="/"
            component={() => {
              return <div>Login Goes Here</div>
            }}
          />
          <Route exact path={ROUTES.BASE_AUTH} component={Login} />
          {routeMap.map((route, i) => {
            if (route.type === 'PRIVATE') {
              return (
                <RouterPrivateRoute
                  exact
                  key={i}
                  path={route.path}
                  component={route.component}
                  loginError={loginError}
                  redirect={redirect}
                  resetRedirect={resetRedirect}
                />
              )
            } else {
              return <Route exact key={i} path={route.path} component={route.component} />
            }
          })}
        </Switch>
      </main>
    </BrowserRouter>
  )
}
