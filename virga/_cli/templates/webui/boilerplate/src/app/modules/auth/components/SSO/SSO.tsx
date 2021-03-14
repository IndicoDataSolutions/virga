import React from 'react'

import { Icon } from '@indico-data/permafrost'
import * as ROUTES from 'root/base/Router/routes'

import { StyledSSO } from './SSO.styles'

export const SSO = () => {
  return (
    <StyledSSO
      className="button blue cta"
      href={`${window.location.origin}${ROUTES.AUTH_SSO_LOGIN}`}
    >
      <Icon name="key" size={['20px']} className="sso-icon" />
      Sign In to Corporate Account
    </StyledSSO>
  )
}
