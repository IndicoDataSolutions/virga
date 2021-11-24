import React, { useEffect } from 'react'

import { AppTitle } from '@indico-data/permafrost'

import { Logout } from 'Auth/components/Logout'
import { PageContainer } from 'root/base/PageContainer'

import { Store as UserStore, useUser } from 'User/store'
import { StyledListTable } from './ListTable.styles'
import { StyledReviewListTable, ResultsDescription } from './List.styles'
import { StyledSearchField, StyledSubmitButton, StyledStatusFilter } from './SearchField.styles'
import { useFetch } from 'Utils/hooks'
import { Select } from '@indico-data/permafrost';
import { useState } from 'react';

const userSelector = (state: UserStore) => ({
  user: state.user,
})

import { v4 as uuid } from 'uuid';

import {
    Shrug, 
    CardBody, 
    SearchField
    // Pagination,
    // Accordion, 
    // LoadingList
} from '@indico-data/permafrost';
import { max } from 'lodash'

// import { Header } from './Header';


type Props = {
  className?: string;
  title: string;
  accordion?: boolean;
  accordionDefaultOpen?: boolean;
  headerComponent?: React.ReactNode;
  sortBy?: {
    value: string;
    items: { name: string; value: string }[];
    descending: boolean;
    updateDescending: () => void;
    onSort: (value: string) => void;
  };
  subTitle?: string | React.ReactNode;
  listHeader: React.ReactNode;
  listItems: React.ReactNode[];
  pagination?: {
    pageInfo: {
      startCursor: number;
      endCursor: number;
      hasNextPage: boolean;
      aggregateCount: number;
    };
    limit: number;
    currentPage: number;
    getPage: (after: number, pageOffset: number) => void;
    getPreviousPage: (after: number) => void;
    getNextPage: (before: number) => void;
  };
  totalCount?: number;
//   loading?: any;
  error?: any;
  errorMessage?: any;
};

export const ListTable = (props: Props) => {
//   const header = (
//     <Header
//       title={props.title}
//       headerComponent={props.headerComponent}
//       sortBy={props.sortBy}
//       aggregateCount={props?.pagination?.pageInfo?.aggregateCount || props.totalCount}
//     />
//   );

  const RenderList = () => {
    // if (props.loading) {
    //   return <LoadingList />;
    // }
    if (props.error) {
      return (
        <CardBody className="error-shrug">
          <Shrug message={props.errorMessage || 'Sorry, there was an error retrieving this data'} />
        </CardBody>
      );
    }
    return (
      <>
        <ul className="list-container">
          {props.listItems.map((li) => {
            const key = uuid();
            return (
              <li className="list-item" key={key}>
                {li}
              </li>
            );
          })}
        </ul>
        {/* {props.pagination ? (
          <Pagination
            limit={props.pagination.limit}
            pageInfo={props.pagination.pageInfo}
            currentPage={props.pagination.currentPage}
            getPage={props.pagination.getPage}
            getPreviousPage={props.pagination.getPreviousPage}
            getNextPage={props.pagination.getNextPage}
            quantity={props.listItems.length}
          />
        ) : null} */}
      </>
    );
  };

  const list = (
    <StyledListTable>
      {props.subTitle ? (
        <div className="sub-title">
          {typeof props.subTitle === 'string' ? (
            <p style={{ maxWidth: '75%' }}>{props.subTitle}</p>
          ) : (
            props.subTitle
          )}
        </div>
      ) : null}
      <div className="list">
        {!props.error ? <div className="list-header-container">{props.listHeader}</div> : null}
        <RenderList />
      </div>
    </StyledListTable>
  );

  return props.accordion ? <div></div> 
    // <StyledListTable className={props.className}>
    //   <Accordion header={header} content={list} open={props.accordionDefaultOpen} />
    // </StyledListTable>
  : (
    <StyledListTable className={props.className}>
      {/* {header} */}
      {list}
    </StyledListTable>
  );
};

export default ListTable;

type SubmissionMeta = {
  id: number
  status: string
};


const options = [
  { name: 'Open', value: 'UNBLOCKED'},
  { name: 'Blocked', value: 'BLOCKED' }
];


const StatusSelector = (submission) => {
  console.log(submission);
  const [status, setStatus] = useState(submission.submission.blocked);
  const changeSubmissionStatus = (meta: SubmissionMeta) => {
    setStatus(meta.status);
    fetch(`/api/submission/${meta.id}/${meta.status}`, {credentials: 'include'}).then(
      (response) => {}
    );
  };

  return (
      <Select
        label=""
        horizontal
        value={status}
        onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
          changeSubmissionStatus({
            id: submission.submission.id,
            status: e.target.value,
          })
        }
        options={options}
      />
  );
};

export const StatusFilter = (props: {onChange: any}) => {

  const [statusFilter, setStatusFilter] = useState("");
  const allOptions = [{ name: 'Any', value: ''}, ...options];
  return (
      <Select
        label=""
        value={statusFilter}
        onChange={(e) => {setStatusFilter(e.target.value); props.onChange(e);}}
        options={allOptions}
      />
  );
};


export const WrappedList = (props: {query: string, statusFilter: string}) => {
  const { user } = useUser(userSelector);
  console.log(props);
  const { loading, error, data } = useFetch(`/api/list?q=${props.query}&statusFilter=${props.statusFilter}`);
  const listHeader = (
    <div className="list-header">
      <span>Submission ID</span>
      <span>Created At</span>
      <span>Status</span>
      <span>Submission Link</span>
    </div>
  );
  let listItems = [];

  if (!loading && !error && data) {
    listItems = data.map((submission) => {
        return (
          <div className="list-item-container" key="app-admin">
              <span>{submission.id}</span>
              <span>{submission.createdAt}</span>
              <span>
                <StatusSelector
                  submission={submission} 
                  options={options}
                />
              </span>
              <span><a href={submission.review_link}>{submission.inputFilename}</a></span>
          </div>
        )
      }
    )
  }
  const nResults = listItems ? listItems.length : 0;
  return (
    <StyledReviewListTable>
      <ResultsDescription>Showing {Math.min(1000, nResults)} of {nResults} results</ResultsDescription>
      <ListTable
        listItems={listItems}
        listHeader={listHeader}
        title="Review URLs"
      />
    </StyledReviewListTable>
  )
}


export const List = () => {
  const [typedQuery, setTypedQuery] = useState("");
  const [firedQuery, setFiredQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const filterChange = (e) => {
    setStatusFilter(e.target.value);
  };
  return (
    <div>
      <StyledSearchField
          onChange={(e) => {setTypedQuery(e.target.value)}}
          placeholder="Search for particular filename"
      />
      <StyledStatusFilter>
        <StatusFilter onChange={filterChange}/>
      </StyledStatusFilter>
      <StyledSubmitButton onClick={() => {setFiredQuery(typedQuery)}}>Search</StyledSubmitButton>
      <WrappedList query={firedQuery} statusFilter={statusFilter}/>
    </div>
  )
}
