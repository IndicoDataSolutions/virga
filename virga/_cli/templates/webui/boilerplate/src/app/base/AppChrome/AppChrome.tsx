import React from 'react'
import { Link } from 'react-router-dom'
import { Icon } from '@indico-data/permafrost'

import { StyledAppChrome } from './AppChrome.styles'

import { APP_CHROME_MENU } from './menu'

import { Store as AppStore, useApp } from '../store'

const fullLogo = (
  <svg viewBox="0 0 100 30">
    <path
      d="M59.6,20.1c0-5.5,4.5-9.9,9.9-9.9l0,0h7.2v3.5h-7.2c-3.5,0-6.2,2.9-6.2,6.2
	c0,3.5,2.9,6.2,6.2,6.2h7.2V30h-7.2l0,0C64.1,30,59.6,25.5,59.6,20.1z M0,30h3.6V10.3H0V30z M1.8,4.3C0.8,4.3,0,5,0,6
	s0.7,1.7,1.8,1.7S3.5,7,3.5,6C3.6,5,2.8,4.3,1.8,4.3z M6.8,20.3L6.8,20.3V30h3.6v-9.7c0-3.5,2.9-6.2,6.2-6.2c3.5,0,6.2,2.9,6.2,6.2
	V30h3.6v-9.7l0,0c0-5.5-4.5-9.9-9.9-9.9C11.3,10.3,6.8,14.8,6.8,20.3z M52.9,30h3.6V10.3h-3.6V30z M54.8,4.3C53.8,4.3,53,5,53,6
	s0.7,1.7,1.8,1.7c1,0,1.8-0.8,1.8-1.7S55.8,4.3,54.8,4.3z M100,20c0,5.5-4.5,10-10,10c-5.5,0-10-4.5-10-10s4.5-10,10-10
	C95.5,10,100,14.5,100,20z M83.9,20c0,3.4,2.8,6.1,6.1,6.1s6.1-2.8,6.1-6.1c0-3.4-2.8-6.1-6.1-6.1S83.9,16.6,83.9,20z M91.8,20
	c0,1-0.8,1.7-1.7,1.7S88.3,21,88.3,20s0.8-1.7,1.8-1.7S91.8,19,91.8,20z M49.8,0.4V20c0,0,0,0,0,0.1c0,5.5-4.5,9.9-10,9.9
	s-10-4.5-10-10s4.5-10,10-10c2.4,0,4.6,0.9,6.4,2.4V0.5h3.6V0.4z M33.6,20c0,3.4,2.7,6.1,6.1,6.1c3.4,0,6.1-2.8,6.1-6.1
	c0-3.4-2.7-6.1-6.1-6.1C36.4,13.9,33.6,16.6,33.6,20z"
    />
  </svg>
)

const markLogo = (
  <svg viewBox="0 0 100 100">
    <path
      d="M100,50c0,27.6-22.4,50-50,50S0,77.6,0,50S22.4,0,50,0S100,22.4,100,50z M50,19.4c-16.9,0-30.6,13.7-30.6,30.6
	S33.1,80.6,50,80.6S80.6,66.9,80.6,50S66.9,19.4,50,19.4z M50,41.1c-4.9,0-8.9,4-8.9,8.9s4,8.9,8.9,8.9s8.9-4,8.9-8.9
	S54.9,41.1,50,41.1z"
    />
  </svg>
)

const appSelector = (state: AppStore) => ({
  sidebarOpen: state.isSidebarOpen,
  toggleSidebar: state.toggleSidebar,
})

type Props = {
  selectedModule: string
  children: React.ReactNode
}

export const AppChrome = (props: Props) => {
  const { sidebarOpen, toggleSidebar } = useApp(appSelector)
  // const logoLink = this.props.logoLinkTo ? (
  //   <a href={this.props.logoLinkTo}>{fullLogo}</a>
  // ) : (
  //   fullLogo
  // );
  const icon = !sidebarOpen ? 'angle-right' : 'angle-left'

  return (
    <StyledAppChrome className={`${!sidebarOpen ? 'closed' : ''}`} data-sel="AppChrome--sidebar">
      <header className="AppNavigation">
        <div className="AppBranding">
          {sidebarOpen ? (
            <div className="AppLogo AppLogo--Full">{fullLogo}</div>
          ) : (
            <button
              className="AppLogo AppLogo--Small"
              data-sel="AppChrome--sidebar-open"
              onClick={toggleSidebar}
            >
              {markLogo}
            </button>
          )}
          <button
            data-sel="AppChrome--sidebar-close"
            className="AppChrome--Toggle"
            title="Toggle Sidebar"
            onClick={toggleSidebar}
          >
            <Icon name={icon} size={['17px', '32px']} />
          </button>
        </div>
        <nav>
          {APP_CHROME_MENU.map((s, i) => {
            return (
              <div key={i}>
                <ul className="LinkList">
                  {s.map((m, j) => {
                    if (m.anchor) {
                      return (
                        <li key={`app-chrome-anchor-${j}`}>
                          <a
                            target="_blank"
                            rel="noopener noreferrer"
                            href={m.destination}
                            title={m.text}
                            data-sel={`AppChrome--link-${m.text}`}
                            className={`AppChrome--link ${
                              m.text === props.selectedModule ? 'current' : ''
                            }`}
                          >
                            <span className="LinkList-Icon">{m.icon}</span>
                            <span className="LinkList-Text">{m.text}</span>
                          </a>
                        </li>
                      )
                    }
                    return (
                      <li key={`app-chrome-link-${j}`}>
                        <Link
                          to={m.destination}
                          title={m.text}
                          data-sel={`AppChrome--link-${m.text}`}
                          className={`AppChrome--link ${
                            m.text === props.selectedModule ? 'current' : ''
                          }`}
                        >
                          <span className="LinkList-Icon">{m.icon}</span>
                          <span className="LinkList-Text">{m.text}</span>
                        </Link>
                      </li>
                    )
                  })}
                </ul>
                {i < APP_CHROME_MENU.length - 1 && <hr />}
              </div>
            )
          })}
        </nav>
      </header>
      <div className="AppContents">{props.children}</div>
    </StyledAppChrome>
  )
}
