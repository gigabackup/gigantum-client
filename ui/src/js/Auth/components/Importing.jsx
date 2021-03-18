// @flow
// vendor
import React, { Component } from 'react';
import { createFragmentContainer, graphql } from 'react-relay';
// components
import OutputMessage from 'Components/output/OutputMessage';
// mutations
import jobStatus from 'JS/utils/JobStatus';
import importingUtils from './utils/ImportingUtils';
import { launch, buildAndLaunch, importJob } from './utils/ContainerMutations';
// css
import './Importing.scss';


type Props = {
  currentServer: {
    currentServer: Object,
  },
  transition: Function,
};

type State = {
  feedback: string,
  failureMessage: string,
};


class Importing extends Component<Props, State> {
  state = {
    feedback: 'Importing...',
    failureMessage: null,
  }

  componentDidMount() {
    const pathArray = window.location.pathname.split('/');
    const owner = pathArray[2];
    const name = pathArray[3];
    importingUtils.projectExists(
      owner,
      name,
    ).then((response) => {
      if (response.data.labbook && response.data.labbook.sizeBytes) {
        const { environment } = response.data.labbook;
        const { imageStatus } = environment;
        if ((imageStatus !== 'EXISTS') && (imageStatus !== 'BUILD_IN_PROGRESS')) {
          this._buildAndLaunch();
        } else if ((imageStatus === 'EXISTS')) {
          this._launch();
        } else if (imageStatus === 'BUILD_IN_PROGRESS') {
          const buildKey = localStorage.getItem(`${owner}:${name}:buildkey`);
          this._jobStatus(buildKey);
        }
      } else {
        this._triggerImport();
      }
    });
  }

  /**
  * Method builds and triggers launch.
  * @param {}
  * @fires this#_launch
  * @fires this#_jobStatus
  * @fires buildAndLaunch
  * @return {}
  */
  _buildAndLaunch = () => {
    const pathArray = window.location.pathname.split('/');
    const owner = pathArray[2];
    const name = pathArray[3];
    const callback = (response) => {
      if (response.buildImage === null) {
        this._launch();
        return;
      }
      const { backgroundJobKey } = response.buildImage;
      localStorage.setItem(`${owner}:${name}:buildkey`, backgroundJobKey);
      this._jobStatus(
        backgroundJobKey,
      );
    };

    buildAndLaunch(owner, name, callback);
  }

  /**
  * Method launches project.
  * @param {}
  * @fires launch
  * @return {}
  */
  _launch = () => {
    const { feedback } = this.state;
    const pathArray = window.location.pathname.split('/');
    const owner = pathArray[2];
    const name = pathArray[3];
    const devtool = sessionStorage.getItem('devTool');
    const feedbackUpdated = `${feedback} <br /> Starting ${devtool} in '${owner}/${name}'`;

    this.setState({ feedback: feedbackUpdated });

    const callback = (response, error) => {
      if (error) {
        this.state({ failureMessage: error[0].message });
      }
      const tabName = `${devtool}-${owner}-${name}`;
      if (response.startDevTool) {
        let path = `${window.location.protocol}//${window.location.hostname}${response.startDevTool.path}`;
        const filePath = sessionStorage.getItem('filePath');
        if (filePath) {
          if (path.indexOf('/lab/tree/code') > -1) {
            path = path.replace('/lab/tree/code', `/lab/tree/${filePath}`);
          } else {
            path = path.replace('/lab/tree/', `/lab/tree/${filePath}`);
          }
        }

        window[tabName] = window.open(path, tabName);
        window[tabName].close();
        window[tabName] = window.open(path, tabName);


        window.location.hash = '';
        sessionStorage.removeItem('autoImport');
        sessionStorage.removeItem('devTool');
        sessionStorage.removeItem('filePath');
        window.location.reload();
      }
    };

    launch(owner, name, devtool, callback);
  }

  /**
  * Method triggers import process for projects.
  * @param {}
  * @fires importJob
  * @return {}
  */
  _triggerImport = () => {
    const { currentServer } = this.props.currentServer;

    const callback = (response, error) => {
      if (response) {
        const { jobKey } = response.importRemoteLabbook;

        this._jobStatus(jobKey);
      }
    };

    importJob(
      currentServer,
      callback,
      callback,
      callback,
    );
  }

  /**
  * Method calls a function that polls for status and returns on completion or failure.
  * @param {String} jobKey job key that corresponds to to a background job running on gigantum client server
  * @fires jobStatus#getJobStatusUpdates
  * @return {}
  */
  _jobStatus = (jobKey) => {
    const callback = (response) => {
      if (response.jobStatus && response.jobStatus.jobMetadata) {
        const { feedback } = JSON.parse(response.jobStatus.jobMetadata);

        this.setState({ feedback });
      }

      if (response.data && response.data.jobStatus && response.data.jobStatus.jobMetadata) {
        const { feedback } = JSON.parse(response.data.jobStatus.jobMetadata);

        if (feedback) {
          this.setState({ feedback });
        }
      }
    };

    jobStatus.getJobStatusUpdates(
      jobKey,
      callback,
    ).then(response => {
      const { jobMetadata, status } = response.jobStatus;
      const { feedback, method } = JSON.parse(jobMetadata);

      this.setState({ feedback });

      if ((status === 'finished') && (method === 'build_image')) {
        this._launch();
      }

      if ((status === 'finished') && (method === 'import_labbook_from_remote')) {
        this._buildAndLaunch();
      }
    }).catch((error) => {
      if (error.jobStatus) {
        const stateFeedback = this.state.feedback;
        const { jobMetadata, failureMessage } = error.jobStatus;
        const { feedback } = JSON.parse(jobMetadata);
        const feedbackAppened = `${stateFeedback} <br /> ${feedback}`;
        this.setState({ feedback: feedbackAppened, failureMessage });
      } else {
        this.setState({ failureMessage: error });
      }
    });
  }

  /**
  * Method cleans up importData for reloading and triggers a transition to load the application
  * @param {}
  * @fires transition
  * @return {}
  */
  _loadApp = () => {
    const { transition } = this.props;
    sessionStorage.removeItem('importData');
    transition('LOGGED_IN');
  }

  render() {
    const {
      feedback,
      failureMessage,
    } = this.state;
    const pathArray = window.location.pathname.split('/');
    const owner = pathArray[2];
    const project = pathArray[3];

    const header = `Importing ${owner}/${project}`;

    return (
      <div className="Importing">
        <h2 className="Importing__h2">{header}</h2>
        <div className="Importing__status">
          { failureMessage
            && <p>{failureMessage}</p>}
          <div className="Importing__feedback">
            <OutputMessage message={feedback} />
          </div>
        </div>
      </div>
    );
  }
}

const ImportingFragement = createFragmentContainer(
  Importing,
  {
    currentServer: graphql`
      fragment Importing_currentServer on LabbookQuery {
        currentServer {
          authConfig {
            audience
            id
            issuer
            loginType
            loginUrl
            logoutUrl
            publicKeyUrl
            serverId
            signingAlgorithm
            typeSpecificFields {
              id
              parameter
              serverId
              value
            }
          }
          baseUrl
          gitServerType
          gitUrl
          hubApiUrl
          id
          lfsEnabled
          name
          objectServiceUrl
          serverId
          userSearchUrl
        }
      }
    `,
  },
);


export default ImportingFragement;
