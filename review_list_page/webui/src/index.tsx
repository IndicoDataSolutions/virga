import React from 'react'
import { render } from 'react-dom'
import { GlobalStyles } from '@indico-data/permafrost'

import { Router } from './app/base/Router'

const App = () => {
  return (
    <>
      <GlobalStyles />
      <Router />
    </>
  )
}
render(<App />, document.getElementById('root'))
