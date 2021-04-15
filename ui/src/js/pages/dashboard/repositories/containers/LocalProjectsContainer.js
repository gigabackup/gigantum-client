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
      fragment LocalProjectsContainer_projectList on LabbookQuery{
        labbookList{
          id
          ...LocalProjects_localProjects
        }
      }
    `,
  },
);
