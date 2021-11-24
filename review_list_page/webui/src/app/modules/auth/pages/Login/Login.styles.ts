import styled from 'styled-components'
import { MEDIA_QUERIES, COLORS } from '@indico-data/permafrost'

export const StyledLoginView = styled.div`
  .App-Logo {
    width: 170px;
    margin: 0 auto 0;
    padding-top: 60px;
  }

  .sign-in {
    padding: 20px 15px 30px;
  }

  hr {
    border-bottom: 1px solid ${COLORS.ebony};
    margin: 30px 0;
  }

  .login-method-container {
    padding: 0 15px;
  }

  .full-width {
    width: 100%;
  }

  button + a {
    margin-top: 12px;
  }

  .cta {
    font-size: 14px;

    @media ${MEDIA_QUERIES.mediumScreen} {
      font-size: 16px;
    }
  }
`
