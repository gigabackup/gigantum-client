// @flow
// vendor
import React, { Component } from 'react';
import { createFragmentContainer, graphql } from 'react-relay';
// general utils
import jobStatus from 'JS/utils/JobStatus';
// components
import { ProgressLoader } from 'Components/loader/Loader';
import OutputMessage from 'Components/output/OutputMessage';
import PopupBlocked from 'Components/modal/popup/PopupBlocked';
import ImportFeedback from './feedback/ImportFeedback';
import ImportHeader from './header/ImportHeader';
import ImportError from './error/ImportError';
// mutations
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
    headerStep: 'Importing',
    importErrorVisible: false,
    showPopupBlocked: false,
    serverId: sessionStorage.getItem('serverId'),
    devTool: sessionStorage.getItem('devtool'),
    filePath: sessionStorage.getItem('filePath'),
  }

  componentDidMount() {
    const { currentServer } = this.props.currentServer;
    const { serverId } = this.state;
    const pathArray = window.location.pathname.split('/');
    const owner = pathArray[2];
    const name = pathArray[3];

    if (serverId !== currentServer.serverId) {
      this.setState({ importErrorVisible: true, headerStep: 'Server' });
      return;
    }

    importingUtils.projectExists(
      owner,
      name,
    ).then((response) => {
      if (response.data && response.data.labbook && response.data.labbook.sizeBytes) {
        const { environment } = response.data.labbook;
        const { imageStatus } = environment;
        if ((imageStatus !== 'EXISTS') && (imageStatus !== 'BUILD_IN_PROGRESS')) {
          this._buildAndLaunch();
          this.setState({ headerStep: 'Building' });
        } else if ((imageStatus === 'EXISTS')) {
          this._launch();
          this.setState({
            feedback: `Importing... \n${owner}/${name} already exists`,
            headerStep: 'Launching',
          });
        } else if (imageStatus === 'BUILD_IN_PROGRESS') {
          const buildKey = localStorage.getItem(`${owner}:${name}:buildkey`);
          this._jobStatus(buildKey);
          this.setState({ headerStep: 'Building' });
        }
      } else {
        this._triggerImport();
        this.setState({ headerStep: 'Importing' });
      }
    });
  }

  /**
   * sets state for popup modal
   */
  _togglePopupModal = () => {
    this.setState({ showPopupBlocked: false });
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
        this.setState({ headerStep: 'Launching' });
        return;
      }
      const { backgroundJobKey } = response.buildImage;
      localStorage.setItem(`${owner}:${name}:buildkey`, backgroundJobKey);
      this._jobStatus(
        backgroundJobKey,
      );
      this.setState({ headerStep: 'Building' });
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
    const devtool = sessionStorage.getItem('devtool');
    const feedbackUpdated = `${feedback} <br /> Starting ${devtool} in '${owner}/${name}'`;


    if (devtool === 'undefined') {
      const path = `${window.location.origin}/projects/${owner}/${name}`;
      window.location.hash = '';
      sessionStorage.removeItem('autoImport');
      sessionStorage.removeItem('devtool');
      sessionStorage.removeItem('filePath');
      window.open(path, '_self');
      return;
    }

    this.setState({
      feedback: feedbackUpdated,
      headerStep: 'Launching',
    });

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

        if (
          !window[tabName]
          || window[tabName].closed
          || typeof window[tabName].closed === 'undefined'
        ) {
          this.setState({ showPopupBlocked: true });
        } else {
          window.location.hash = '';
          sessionStorage.removeItem('autoImport');
          sessionStorage.removeItem('devtool');
          sessionStorage.removeItem('filePath');
          window.location.reload();
        }
      } else {
        this.setState({ importErrorVisible: true });
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
      if (response && response.importRemoteLabbook) {
        const { jobKey } = response.importRemoteLabbook;

        this._jobStatus(jobKey);
      }
    };

    this.setState({ headerStep: 'Importing' });

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
        this.setState({ headerStep: 'Launching' });
      }

      if ((status === 'finished') && (method === 'import_labbook_from_remote')) {
        this._buildAndLaunch();
        this.setState({ headerStep: 'Building' });
      }
    }).catch((error) => {
      if (error.jobStatus) {
        const stateFeedback = this.state.feedback;
        const { jobMetadata, failureMessage } = error.jobStatus;
        const { feedback } = JSON.parse(jobMetadata);
        const feedbackAppened = `${stateFeedback} <br /> ${feedback}`;
        this.setState({ feedback: feedbackAppened, failureMessage, importErrorVisible: true });
      } else {
        this.setState({ failureMessage: error, importErrorVisible: true });
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
    const pathArray = window.location.pathname.split('/');
    const owner = pathArray[2];
    const name = pathArray[3];
    const {
      devTool,
      headerStep,
      failureMessage,
      feedback,
      importErrorVisible,
      showPopupBlocked,
    } = this.state;
    const {
      isComplete,
      percentageComplete,
    } = importingUtils.getProgressLoaderData(feedback, name, owner);

    const header = `${headerStep} ${owner}/${name}`;


    return (
      <div className="Importing">
        <ImportHeader />
        <h4 className="Importing__h4">{header}</h4>

        <ProgressLoader
          error={failureMessage}
          isCanceling={false}
          isComplete={isComplete}
          percentageComplete={percentageComplete}
        />

        <PopupBlocked
          attemptRelaunch={this._launch}
          devTool={devTool}
          hideCancel
          togglePopupModal={this._togglePopupModal}
          isVisible={showPopupBlocked}
        />
        <ImportError
          devTool={devTool}
          headerStep={headerStep}
          isVisible={importErrorVisible}
        />
        <div className="Importing__status">
          <ImportFeedback feedback={feedback} />
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
