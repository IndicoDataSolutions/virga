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
    hostname: '0.0.0.0',
    port: +process.env.WEBUI_PORT,
  },
  routes: [{ match: 'routes', src: '.*', dest: '/index.html' }],
}
