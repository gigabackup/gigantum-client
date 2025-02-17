// vendor
import { graphql } from 'react-relay';
// environment
import { fetchQuery } from 'JS/createRelayEnvironment';

const jobStatusQuery = graphql`
  query JobStatusQuery($jobKey: String!){
    jobStatus(jobId: $jobKey){
      id,
      jobKey
      status
      startedAt
      finishedAt
      jobMetadata
      failureMessage
      result
    }
  }
`;

const JobStatus = {
  getJobStatus: (owner, name, jobKey) => {
    const variables = { jobKey };
    return new Promise((resolve, reject) => {
      const fetchData = () => {
        fetchQuery(
          jobStatusQuery,
          variables,
          { force: true },
        ).then((response, error) => {
          if (
            (response.data.jobStatus.status === 'started')
            || (response.data.jobStatus.status === 'queued')
          ) {
            setTimeout(() => {
              fetchData();
            }, 250);
          } else if (response.data.jobStatus.status === 'finished') {
            resolve(response.data);
          } else if (response.data.jobStatus.status === 'failed') {
            reject(response.data);
          } else if (error) {
            reject(error);
          } else {
            reject(response.data);
          }
        }).catch((error) => {
          console.log(error);
          reject(error);
        });
      };

      fetchData();
    });
  },
  updateFooterStatus: (jobKey) => {
    const variables = { jobKey };

    return new Promise((resolve, reject) => {
      const fetchData = () => {
        fetchQuery(
          jobStatusQuery,
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
  getJobStatusUpdates: (jobKey, callback) => {
    const variables = { jobKey };
    return new Promise((resolve, reject) => {
      const fetchData = () => {
        fetchQuery(
          jobStatusQuery,
          variables,
          { force: true },
        ).then((response) => {
          callback(response);
          if (
            (response.data.jobStatus.status === 'started')
            || (response.data.jobStatus.status === 'queued')
          ) {
            setTimeout(() => {
              fetchData();
            }, 250);
          } else if (response.data.jobStatus.status === 'finished') {
            resolve(response.data);
          } else {
            reject(response.data);
          }
        }).catch((error) => {
          console.log(error);
          reject(error);
        });
      };

      fetchData();
    });
  },
};

export default JobStatus;
