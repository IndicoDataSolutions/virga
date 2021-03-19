import styled from 'styled-components'

import { MEDIA_QUERIES } from '@indico-data/permafrost'

export const StyledPageContainer = styled.div`
  margin: 0 10px;

  @media ${MEDIA_QUERIES.mediumScreen} {
    margin: 20px 50px;
  }
`
