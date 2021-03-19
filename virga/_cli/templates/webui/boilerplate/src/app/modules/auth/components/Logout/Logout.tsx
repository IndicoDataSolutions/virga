import React from 'react'
import { withRouter } from 'react-router-dom'
import * as H from 'history'

import { Button, Icon } from '@indico-data/permafrost'

import { Store as UserStore, useUser } from 'User/store'

type Props = {
  history: H.History
}

const userSelector = (state: UserStore) => ({
  submitLogout: state.submitLogout,
})

const LogoutButton = (props: Props) => {
  const { submitLogout } = useUser(userSelector)

  return (
    <Button
      variant="link-style"
      style={{ color: 'white' }}
      onClick={() => {
        submitLogout().then(() => {
          props.history.push('/')
        })
      }}
    >
      Sign Out of indico{' '}
      <Icon name="fa-sign-out-alt" style={{ position: 'relative', top: '3px' }} />
    </Button>
  )
}

export const Logout = withRouter(LogoutButton)
