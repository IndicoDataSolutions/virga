import styled from 'styled-components';

import { MEDIA_QUERIES, COLORS } from '@indico-data/permafrost';

export const StyledPanel = styled.div`
  width: 100%;
  background: none;

  @media ${MEDIA_QUERIES.mediumScreen} {
    width: 380px;
    margin: 30px auto 0;
    background-color: ${COLORS.clay};
    border: solid 1px ${COLORS.oxfordBlue};
    border-radius: 4px;
  }

  .Panel-Header {
    text-align: center;
    padding-top: 20px;

    h4 {
      color: ${COLORS.lightFontColor};
      letter-spacing: -0.5px;
      margin: 0;
    }
  }

  .Panel-Body {
    padding: 10px 30px 30px;
  }
`;
