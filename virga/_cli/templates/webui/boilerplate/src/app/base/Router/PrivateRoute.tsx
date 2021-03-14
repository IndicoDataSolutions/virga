import React, { useEffect } from 'react'
import { withRouter, Route, Redirect, RouteComponentProps } from 'react-router-dom'
import * as H from 'history'

import { PageContainer } from 'root/base/PageContainer'
import * as ROUTES from './routes'
import { Store as UserStore, useUser } from 'User/store'

// import LoginFailed from 'Auth/pages/LoginFailed/LoginFailed';

type Props = {
  resetRedirect: (path: string, history: H.History) => void
  location: H.Location
  history: H.History
  component: any
  loginError: boolean
  redirect: { url: string }
  exact: boolean
  path: string
}

const userSelector = (state: UserStore) => ({
  currentUser: state.user,
  verifyingUser: state.authenticating,
})

const PrivateRoute = (props: Props & RouteComponentProps) => {
  const { currentUser, verifyingUser } = useUser(userSelector)
  useEffect(() => {
    if (currentUser === null) {
      props.resetRedirect(props.location.pathname, props.history)
    }
  }, [])

  const { component: Component, loginError, redirect, ...rest } = props
  const scope = currentUser && currentUser.scopes.map((s) => s.scope.toUpperCase())
  const appAccess = scope && scope.includes('APP_ACCESS')

  return (
    <Route
      {...rest}
      render={(routeProps) => {
        if (loginError) {
          return (
            // <ConnectedBaseAppChrome>
            //   <LoginFailed />
            // </ConnectedBaseAppChrome>
            <div>Login Failed Error</div>
          )
        } else if (redirect.url && currentUser === null) {
          return <Redirect to={`/?redirect_url=${redirect.url}`} />
        } else if (verifyingUser || currentUser === null) {
          return <PageContainer />
        } else if (currentUser !== null && !appAccess) {
          // return <Redirect to={ROUTES.BASE_NO_ACCESS} />
          return <div>NO APP ACCESS</div>
        } else {
          return <Component {...routeProps} />
        }
      }}
    />
  )
}

export const RouterPrivateRoute = withRouter(PrivateRoute)
