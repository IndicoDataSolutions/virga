;(function () {
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
      AuthURL: 'https://dev.indico.io/auth',
      DocsURL: 'https://indico.io/docs',
      HelpURL: 'https://indico.io/docs',
      FogURL: 'https://dev.indico.io/graph',
      CycloneURL: 'https://dev.indico.io/datasets',
      StorageURL: 'https://dev.indico.io/storage',
    },
  }
})()
