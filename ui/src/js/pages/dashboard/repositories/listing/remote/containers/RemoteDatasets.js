import {
  createPaginationContainer,
  graphql,
} from 'react-relay';

// components
import RemoteListing from '../RemoteListing';

export default createPaginationContainer(
  RemoteListing,
  {
    remoteDatasets: graphql`
      fragment RemoteDatasets_remoteDatasets on DatasetList{
        remoteDatasets(first: $first, after: $cursor, orderBy: $orderBy, sort: $sort)@connection(key: "RemoteDatasets_remoteDatasets", filters: []){
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
    getConnectionFromProps(props, error) {
      return props.remoteDatasets.remoteDatasets;
    },
    getFragmentVariables(prevVars, first, cursor) {
      return {
        ...prevVars,
        first,
      };
    },
    getVariables(props, {
      first, cursor, orderBy, sort,
    }, fragmentVariables) {
      first = 10;
      cursor = props.remoteDatasets.remoteDatasets.pageInfo.endCursor;
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
      query RemoteDatasetsPaginationQuery(
        $first: Int!
        $cursor: String
        $orderBy: String
        $sort: String
      ) {
        datasetList {
          ...RemoteDatasets_remoteDatasets
        }
      }
    `,
  },
);
