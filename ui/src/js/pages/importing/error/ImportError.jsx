// vendor
import React from 'react';
// component
import Modal from 'Components/modal/Modal';
// css
import './ImportError.scss';

type Props = {
  devTool: String,
  headerStep: String,
  isVisible: boolean,
}

const ImportError = ({
  devTool,
  headerStep,
  isVisible,
}: Props) => {
  if (!isVisible) {
    return null;
  }

  /**
  * Opens the project
  * @param {}
  * @return {}
  */
  const clearState = () => {
    window.location.hash = '';
    sessionStorage.removeItem('autoImport');
    sessionStorage.removeItem('devTool');
    sessionStorage.removeItem('filePath');
  };

  /**
  * Opens the project
  * @param {}
  * @return {}
  */
  const openProject = () => {
    clearState();
    window.location.reload();
  };

  /**
  * Opens project listing
  * @param {}
  * @return {}
  */
  const viewProjects = () => {
    clearState();
    window.location.pathname = '/projects/local';
  };

  /**
  * Opens project environment
  * @param {}
  * @return {}
  */
  const viewEnvironment = () => {
    clearState();
    window.location.pathname = `${window.location.pathname}environment`;
  };

  const errorState = {
    Importing: {
      headerText: 'Project Failed to Launch',
      bodyText: 'Gigantum failed to import the Project. This is most likely because you do not have access to the Project or it does not exist.',
      subText: 'Please select a valid Project to launch.',
      buttonText: 'View My Projects',
      buttonAction: viewProjects,
    },
    Building: {
      headerText: 'Gigantum Failed to Build',
      bodyText: 'Gigantum failed to build the Project. This is most likely due to an issue with the Project\'s environment.',
      subText: 'Please modify the environment and try again.',
      buttonText: 'View Project Environment',
      buttonAction: viewEnvironment,

    },
    Launching: {
      headerText: 'Devtool Failed to Launch',
      bodyText: `Gigantum failed to launch ${devTool}. This is most likely because the devtool or custom app does not exist.`,
      subText: 'Please open the Project and select a valid devtool or custom application.',
      buttonText: 'Open Project',
      buttonAction: openProject,
    },
    Server: {
      headerText: 'Server Mismatch',
      bodyText: 'You are currently logged in to a different server than specified in the import link.',
      subText: 'Please logout and login to the specified server and try again.',
      buttonText: 'View My Projects',
      buttonAction: viewProjects,
    },
  };

  const {
    headerText,
    bodyText,
    subText,
    buttonText,
    buttonAction,
  } = errorState[headerStep];

  return (
    <Modal
      size="medium"
    >
      <div className="ImportError flex flex--column align-items--center">
        <div className="ImportError__header">
          <h2 className="ImportError__header-text">{headerText}</h2>
        </div>
        <div className="ImportError__message">
          <p>
            {bodyText}
          </p>
          <p>
            {subText}
          </p>
        </div>
        <div className="ImportError__buttonContainer flex justify--right">
          <button
            className="Btn Btn--inverted Btn--popup-blocked ImportError__button"
            onClick={buttonAction}
            type="button"
          >
            {buttonText}
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default ImportError;
