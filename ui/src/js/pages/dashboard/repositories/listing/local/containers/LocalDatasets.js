import {
  createPaginationContainer,
  graphql,
} from 'react-relay';

// components
import LocalListing from '../LocalListing';

export default createPaginationContainer(
  LocalListing,
  {
    localDatasets: graphql`
      fragment LocalDatasets_localDatasets on DatasetList{
        localDatasets(first: $first, after: $cursor, orderBy: $orderBy, sort: $sort)@connection(key: "LocalDatasets_localDatasets", filters: []){
          edges {
            node {
              id
              name
              description
              owner
              createdOnUtc
              modifiedOnUtc
              overview {
                numFiles
                totalBytes
              }
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
      return props.localDatasets.localDatasets;
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
      cursor = props.localDatasets.localDatasets.pageInfo.endCursor;
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
      query LocalDatasetsPaginationQuery(
        $first: Int!
        $cursor: String
        $orderBy: String
        $sort: String
      ) {
        datasetList{
          ...LocalDatasets_localDatasets
        }
      }
    `,
  },
);
