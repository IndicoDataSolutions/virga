import React from 'react'

import { AppChrome } from '../AppChrome'

import { StyledPageContainer } from './PageContainer.styles'

type Props = {
  children?: React.ReactNode
  module?: string
}

export const PageContainer = (props: Props) => {
  return (
    <AppChrome selectedModule={props.module}>
      <StyledPageContainer>{props.children}</StyledPageContainer>
    </AppChrome>
  )
}
