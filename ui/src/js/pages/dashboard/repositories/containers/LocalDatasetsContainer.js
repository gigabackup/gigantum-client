// vendor
import {
  createFragmentContainer,
  graphql,
} from 'react-relay';
// components
import Repositories from '../Repositories';

export default createFragmentContainer(
  Repositories,
  {
    datasetList: graphql`
      fragment LocalDatasetsContainer_datasetList on LabbookQuery{
        datasetList{
          id
          ...LocalDatasets_localDatasets
        }
      }
    `,
  },
);
