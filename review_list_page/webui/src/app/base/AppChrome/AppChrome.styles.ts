import styled from 'styled-components'

import { MEDIA_QUERIES, COLORS } from '@indico-data/permafrost'

const navWidthOpen = '240px'
const navWidthClosed = '50px'
const navTextColor = COLORS.baliHai
const navActiveTextColor = COLORS.hiliteFontColor
const navActiveIconColor = '#1e88e5'
const hrColor = '#2b3c4c'
const navDuration = '250ms'

export const StyledAppChrome = styled.div`
  width: 100%;

  .AppNavigation {
    width: ${navWidthOpen};
    overflow: hidden;
    transition: width ${navDuration} ease-out, padding ${navDuration} ease-out;
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    background: ${COLORS.ebony};
    padding: 30px;
    z-index: 500;

    .AppBranding {
      width: 180px;
      text-align: right;
      margin-bottom: 32px;
      transition: width ${navDuration} ease-out, opacity ${navDuration} ease-out;

      .AppLogo {
        float: left;
        overflow: hidden;
        height: 30px;

        path {
          fill: ${COLORS.white};
        }

        &.AppLogo--Full {
          width: 100px;
        }

        &.AppLogo--Small {
          width: 30px;
        }
      }

      .AppChrome--Toggle svg {
        font-size: 26px;
        color: ${navTextColor};
        margin-top: 2px;
      }
    }

    // Reset Core Element Styles Within Component
    button {
      background: none;
      border-width: 0;
      box-shadow: none;
      text-transform: uppercase;
      padding: 0;

      &:hover,
      &:active,
      &:focus {
        background: none;
        border-width: 0;
        box-shadow: none;
      }
    }

    hr {
      border-bottom: 2px solid ${hrColor};
    }

    .LinkList {
      li {
        margin-bottom: 20px;
        line-height: 0; // tightens up the space at the bottom of the container
      }

      .LinkList-Icon svg {
        width: 25px;
        height: 25px;

        path {
          fill: ${navTextColor};
        }
      }

      .LinkList-Text {
        display: inline-block;
        font-size: 14px;
        margin-left: 10px;
        color: ${navTextColor};
        opacity: 1;
        transition: width ${navDuration} ease-out, opacity ${navDuration} ease-out;
        vertical-align: top;
        padding-top: 5px;
        line-height: 1;
      }

      .AppChrome--link {
        display: inline-block;
        text-transform: uppercase;
        white-space: nowrap;
      }

      .AppChrome--link:hover,
      .AppChrome--link.current {
        .LinkList-Icon {
          path {
            fill: ${navActiveIconColor};
          }
        }

        .LinkList-Text {
          color: ${navActiveTextColor};
        }
      }
    }
  }

  .AppContents {
    display: block;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    padding-left: ${navWidthClosed};
    transition: padding ${navDuration} ease-out, transform ${navDuration} ease-out;
    transform: translateX(190px);

    @media ${MEDIA_QUERIES.largeScreen} {
      padding-left: ${navWidthOpen};
      transform: translate(0);
    }
  }

  &.closed {
    .AppNavigation {
      width: ${navWidthClosed};
      padding: 30px 13px;

      .AppLogo {
        margin-left: -3px;
      }

      .AppLogoCollapsed {
        display: inline-block;
      }

      .LinkList .LinkList-Text {
        opacity: 0;
      }
    }

    .AppContents {
      padding-left: ${navWidthClosed} !important;
      transform: translate(0);
    }
  }
`
