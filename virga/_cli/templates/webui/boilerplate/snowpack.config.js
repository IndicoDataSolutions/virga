module.exports = {
  mount: {
    public: { url: '/', static: true },
    src: '/',
  },
  alias: {
    root: './src/app',
    Auth: './src/app/modules/auth',
    User: './src/app/modules/user',
  },
  devOptions: {
    secure: true,
    hostname: 'app.indico.local',
    port: 443
  },
  routes: [{ match: 'routes', src: '.*', dest: '/index.html' }],
}
