import styled from 'styled-components';

import { COLORS } from '@indico-data/permafrost';

export const StyledListTable = styled.div`
  margin-left: 20px; 
  
  .list {
    .list-header-container,
    .list-container .list-item {
      border-bottom: solid ${COLORS.blueBayoux} 1px;
      padding: 0 20px 10px 20px;
      margin-bottom: 10px;
    }

    .list-container .list-item {
      font-size: 14px;

      & > * div {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
    }
  }

  .sub-title {
    margin-bottom: 20px;
  }

  summary,
  summary h2 {
    width: 100%;
  }

  summary .header-container {
    svg {
      margin-top: 2px;
    }

    .header-component div {
      padding: 0;
    }
  }

  summary .title-container {
    margin-bottom: 2px;

    .title {
      align-items: flex-start;

      h2 {
        margin-left: 0;
      }
    }

    .count {
      color: ${COLORS.defaultFontColor};
    }
  }

  summary .sort-by .button-sort-direction svg {
    bottom: 5px;
  }

  .content {
    margin-top: 0 !important;
  }

  .error-shrug {
    margin: 0 20px;
    background-color: ${COLORS.oxfordBlue};
  }
`;
