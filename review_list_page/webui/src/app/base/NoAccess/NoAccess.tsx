import React from 'react'

// App
import { AppTitle, Card, CardBody, Shrug, Icon } from '@indico-data/permafrost'

import { Logout } from 'Auth/components/Logout'
import { PageContainer } from '../PageContainer'

export const NoAccess = () => {
  return (
    <PageContainer>
      <AppTitle icon="help" title="Help" actions={<Logout />} />
      <Card>
        <CardBody>
          <Shrug
            message={
              <p style={{ textAlign: 'center', maxWidth: '60ch' }}>
                Thank you for registering. Before you can access the platform, your administrator
                must grant you the “App Access” permission.
              </p>
            }
          />
        </CardBody>
      </Card>
    </PageContainer>
  )
}
