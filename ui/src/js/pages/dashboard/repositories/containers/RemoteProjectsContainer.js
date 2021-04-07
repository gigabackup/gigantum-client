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
    projectList: graphql`
      fragment RemoteProjectsContainer_projectList on LabbookQuery{
        labbookList{
          id
          ...RemoteProjects_remoteProjects
        }
      }
    `,
  },
);
