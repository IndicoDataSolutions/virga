import React from 'react'
import { Redirect } from 'react-router-dom'

import { urlUtils } from '@indico-data/utils'

import * as ROUTES from 'root/base/Router/routes'

import { Panel } from 'Auth/components/Panel'
import { SSO } from 'Auth/components/SSO'
import { EmailPassword } from 'Auth/components/EmailPassword'

import logo from './indico-logo.svg'
import { StyledLoginView } from './Login.styles'
import { PageContainer } from 'root/base/PageContainer'

import { Store as UserStore, useUser } from 'User/store'

const userSelector = (state: UserStore) => ({
  user: state.user,
  authError: state.authError,
})

export const Login = () => {
  const { user: currentUser, authError } = useUser(userSelector)
  const redirect = urlUtils.parseRedirect(window.location.search)
  const renderLoginOption = (option: 'ALL' | 'SSO' | 'EMAIL') => {
    if (option === 'ALL') {
      return (
        <>
          {<SSO />}
          <hr />
          {<EmailPassword />}
        </>
      )
    } else if (option === 'SSO') {
      return <SSO />
    } else {
      return <EmailPassword />
    }
  }

  if (
    currentUser !== null &&
    !currentUser?.scopes?.map((s) => s.scope.toUpperCase()).includes('APP_ACCESS')
  ) {
    return <Redirect to={{ pathname: ROUTES.BASE_NO_ACCESS }} />
  } else if (currentUser !== null && redirect) {
    return <Redirect to={{ pathname: redirect }} />
  } else if (currentUser !== null) {
    return <Redirect to={{ pathname: ROUTES.AUTH_ACCOUNT }} />
  } else {
    return (
      <PageContainer module="Account">
        <StyledLoginView>
          <div className="App-Logo">
            <img src={logo} alt="indico logo" />
          </div>
          <Panel headerText="Sign In" className="sign-in">
            {authError ? (
              <p className="error" style={{ padding: '10px 15px' }}>
                {authError}
              </p>
            ) : null}
            <div className="login-method-container">
              {window.indico.features.loginOption
                ? renderLoginOption(window.indico.featuresConfig.loginOption)
                : renderLoginOption('EMAIL')}
            </div>
          </Panel>
        </StyledLoginView>
      </PageContainer>
    )
  }
}
