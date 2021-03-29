// vendor
import { graphql } from 'react-relay';
// environment
import { fetchQuery } from 'JS/createRelayEnvironment';

const importingUtilsQuery = graphql`
  query ImportingUtilsQuery($owner: String!, $name: String!){
    labbook(owner: $owner, name: $name){
      id
      owner
      name
      sizeBytes

      environment {
        id
        imageStatus
        containerStatus
      }
    }
  }
`;

const importingUtils = {
  /**
  * Method checks if a project exists before attempting to import it
  * @param {String} owner owner of project
    * @param {String} name name of the project
  * @fires fetchQuery
  * @return {}
  */
  projectExists: (owner, name) => {
    const variables = { owner, name };
    return new Promise((resolve, reject) => {
      const fetchData = () => {
        fetchQuery(
          importingUtilsQuery,
          variables,
          { force: true },
        ).then((response) => {
          resolve(response);
        }).catch((error) => {
          console.log(error);
          reject(error);
        });
      };

      fetchData();
    });
  },
};

export default importingUtils;
