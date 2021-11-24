import styled, { css } from 'styled-components';

import { CardSection } from '@indico-data/permafrost';

const gridDefinition = css`
  display: grid;
  grid-template-columns: 1fr 2fr 2fr 2fr 1fr;
`;

export const StyledReviewListTable = styled(CardSection)`
  padding-top: 20px;

  .list-header,
  .list-item-container {
    ${gridDefinition}
  }

  .list-item-container {
    align-content: center;
    height: 25px;
  }
`;

export const ResultsDescription = styled.div`
  padding: 20px;
`