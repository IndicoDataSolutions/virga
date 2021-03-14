import React, { useState } from 'react'

import { TextField, SmallLoadingIndicator } from '@indico-data/permafrost'

import { Store as UserStore, useUser } from 'User/store'

import { StyledEmailPassword } from './EmailPassword.styles'

const userSelector = (state: UserStore) => ({
  submitLogin: state.submitLogin,
  authenticating: state.authenticating,
})

export const EmailPassword = () => {
  const [email, setEmail] = useState<string>('')
  const [password, setPassword] = useState<string>('')
  const { submitLogin, authenticating } = useUser(userSelector)

  return (
    <StyledEmailPassword
      onSubmit={(e) => {
        e.preventDefault()
        submitLogin(email, password)
      }}
    >
      <TextField
        className="email"
        required={true}
        label="Email Address"
        autoFocus={true}
        onChange={(e) => {
          setEmail(e.target.value)
        }}
        value={email}
        inputProps={{
          'data-sel': 'LoginView--email',
        }}
      />

      <TextField
        className="password"
        required={true}
        type="password"
        label="Password"
        onChange={(e) => {
          setPassword(e.target.value)
        }}
        value={password}
        inputProps={{
          'data-sel': 'LoginView--password',
        }}
      />
      {authenticating ? (
        <SmallLoadingIndicator />
      ) : (
        <button
          type="submit"
          data-sel="LoginView--submit"
          className="cta blue full-width LoginView--submit"
          disabled={false}
        >
          Sign In to My Account
        </button>
      )}
    </StyledEmailPassword>
  )
}
