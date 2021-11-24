import React from 'react'

import { AppTitle } from '@indico-data/permafrost'

import { Logout } from 'Auth/components/Logout'
import { PageContainer } from 'root/base/PageContainer'

import { Store as UserStore, useUser } from 'User/store'

import { StyledAccount } from './Account.styles'

const userSelector = (state: UserStore) => ({
  user: state.user,
})

export const Account = () => {
  const { user } = useUser(userSelector)
  return (
    <PageContainer module="Account">
      <AppTitle icon="account" title="Account" actions={<Logout />} />
      <StyledAccount>
        <h2>
          {user.id}: {user.name}
        </h2>
        <h3>{user.email}</h3>
      </StyledAccount>
    </PageContainer>
  )
}
