; (function () {
  window.indico = {
    features: {
      inactivityTimeout: false,
      loginOption: true,
    },
    featuresConfig: {
      inactivityTimeout: 1000 * 60 * 10, // defaults to 10 minutes
      loginOption: 'ALL', // 'ALL' | 'SSO' | 'EMAIL'
    },
    appURLs: {
      AuthURL: 'https://app.indico.io/auth',
      DocsURL: 'https://indico.io/docs',
      HelpURL: 'https://indico.io/docs'
    },
  }
})()
