import React from 'react'

// App
import { PageContainer } from '../PageContainer'
import { Logout } from 'Auth/components/Logout'
import { AppTitle, Card, CardBody, Shrug } from '@indico-data/permafrost'

export const FourOhFour = () => {
  return (
    <PageContainer>
      <AppTitle icon="help" title="Help" actions={<Logout />} />
      <Card>
        <CardBody>
          <Shrug message="Whoops... we don't have anything here...." />
        </CardBody>
      </Card>
    </PageContainer>
  )
}
