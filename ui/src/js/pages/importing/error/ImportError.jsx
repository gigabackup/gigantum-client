// vendor
import React from 'react';
// component
import Modal from 'Components/modal/Modal';
// css
import './ImportError.scss';

type Props = {
  devTool: String,
  isVisible: boolean,
  openProject: Function,
}

const ImportError = ({
  devTool,
  isVisible,
  openProject,
}: Props) => {
  if (!isVisible) {
    return null;
  }

  return (
    <Modal
      size="medium"
    >
      <div className="ImportError flex flex--column align-items--center">
        <div className="ImportError__header">
          <h2 className="ImportError__header-text">Devtool Failed to Launch</h2>
        </div>
        <div className="ImportError__message">
          <p>
            Gigantum failed to launch
            {` ${devTool} `}
            . This is most likely because the devtool or custom app does not exist.
          </p>
          <p>
            Please open the Project and select a valid devtool or custom application.
          </p>
        </div>
        <div className="ImportError__buttonContainer flex justify--right">
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

export default ImportError;
