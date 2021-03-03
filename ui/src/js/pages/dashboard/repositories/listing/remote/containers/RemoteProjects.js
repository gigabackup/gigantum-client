import {
  createPaginationContainer,
  graphql,
} from 'react-relay';

// components
import RemoteListing from '../RemoteListing';

export default createPaginationContainer(
  RemoteListing,
  {
    remoteProjects: graphql`
      fragment RemoteProjects_remoteProjects on LabbookList{
        remoteLabbooks(first: $first, after: $cursor, orderBy: $orderBy, sort: $sort)@connection(key: "RemoteLabbooks_remoteLabbooks", filters: []){
          edges {
            node {
              name
              description
              visibility
              owner
              id
              isLocal
              creationDateUtc
              modifiedDateUtc
              importUrl
            }
            cursor
          }
          pageInfo {
            endCursor
            hasNextPage
            hasPreviousPage
            startCursor
          }
        }
      }
    `,
  },
  {
    direction: 'forward',
    getConnectionFromProps(props) {
      return props.remoteProjects.remoteLabbooks;
    },
    getFragmentVariables(prevVars, first) {
      return {
        ...prevVars,
        first,
      };
    },
    getVariables(props, {
      first, cursor, orderBy, sort,
    }, fragmentVariables) {
      first = 10;
      cursor = props.remoteProjects.remoteLabbooks.pageInfo.endCursor;
      orderBy = fragmentVariables.orderBy;
      sort = fragmentVariables.sort;
      return {
        first,
        cursor,
        orderBy,
        sort,
        // in most cases, for variables other than connection filters like
        // `first`, `after`, etc. you may want to use the previous values.
      };
    },
    query: graphql`
      query RemoteProjectsPaginationQuery(
        $first: Int!
        $cursor: String
        $orderBy: String
        $sort: String
      ) {
        labbookList{
          ...RemoteProjects_remoteProjects
        }
      }
    `,
  },
);
