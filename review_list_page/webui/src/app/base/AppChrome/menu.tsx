import React from 'react'

import { Icon } from '@indico-data/permafrost'

import * as ROUTES from 'root/base/Router/routes'

export const APP_CHROME_MENU = [
  [
    {
      text: 'Account',
      icon: <Icon name="account" />,
      destination: ROUTES.BASE_AUTH,
      anchor: false,
    },
  ],
  [
    {
      text: 'API Documentation',
      icon: <Icon name="api-doc" />,
      destination: window?.indico?.appURLs?.DocsURL,
      anchor: true,
    },
    {
      text: 'Help',
      icon: <Icon name="help" />,
      destination: window?.indico?.appURLs?.HelpURL,
      anchor: true,
    },
  ],
]
