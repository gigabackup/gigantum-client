// vendor
import React from 'react';
// component
import Modal from 'Components/modal/Modal';
// css
import './ImportingError.scss';

type Props = {
  devTool: String,
  isVisible: boolean,
  openProject: Function,
  toggleDevtoolFailedModal: Function,
}

const ImportingError = ({
  devTool,
  isVisible,
  openProject,
  toggleDevtoolFailedModal,
}: Props) => {
  if (!isVisible) {
    return null;
  }

  return (
    <Modal
      handleClose={() => toggleDevtoolFailedModal()}
      size="medium"
    >
      <div className="ImportingError flex flex--column align-items--center">
        <div className="ImportingError__header">
          <h2 className="ImportingError__header-text">Devtool Failed to Launch</h2>
        </div>
        <div className="ImportingError__message">
          <p>
            Gigantum failed to launch
            {` ${devTool} `}
            . This is most likely because the devtool or custom app does not exist.
          </p>
          <p>
            Please open the Project and select a valid devtool or custom application.
          </p>
        </div>
        <div className="ImportingError__buttonContainer flex justify--right">
          <button
            className="Btn Btn--inverted Btn--popup-blocked"
            onClick={openProject}
            type="button"
          >
            Open Project
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default ImportingError;
