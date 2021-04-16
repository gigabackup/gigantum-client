// @flow
// vendor
import React from 'react';
import classNames from 'classnames';
// components
import Modal from 'Components/modal/Modal';

type Props = {
  closeImportModal: Function,
  currentServer: {
    backupInProgress: boolean,
  },
  dragendHandler: Function,
  dragEnterHandler: Function,
  dragLeaveHandler: Function,
  dragoverHandler: Function,
  dropHandler: Function,
  dropZone: Object,
  files: Array,
  importRepository: Function,
  isImporting: boolean,
  isOver: boolean,
  isVisible: boolean,
  ready: {
    name: string,
    owner: string,
  },
  remoteUrl: string,
  sectionType: string,
  updateRemoteUrl: Function,
}

const ImportModal = ({
  closeImportModal,
  currentServer,
  dragendHandler,
  dragEnterHandler,
  dragLeaveHandler,
  dragoverHandler,
  dropHandler,
  dropZone,
  files,
  importRepository,
  isImporting,
  isOver,
  isVisible,
  ready,
  remoteUrl,
  sectionType,
  updateRemoteUrl,
}: Props) => {
  const owner = ready ? ready.owner : '';
  const name = ready ? ready.name : '';
  const section = sectionType === 'labbook' ? 'Project' : 'Dataset';
  // declare css here
  const inputWrapperCSS = classNames({
    'Tooltip-data': currentServer.backupInProgress,
  });
  const dropBoxCSS = classNames({
    'Dropbox Dropbox--project ImportDropzone flex flex--column align-items--center': true,
    'Dropbox--project--hovered': isOver,
    'Dropbox--dropped': ready && files[0],
  });

  if (!isVisible) {
    return null;
  }

  return (
    <Modal
      header={`Import ${section}`}
      handleClose={() => closeImportModal()}
      size="large"
      icon="add"
    >
      <div className="ImportModal">
        <p>{`Import a ${section} by either pasting a URL or drag & dropping below`}</p>
        <div
          className={inputWrapperCSS}
          data-tooltip={`Remote ${section}s cannot be imported while server backup is in progress.`}
        >
          <input
            className="Import__input"
            defaultValue={remoteUrl}
            disabled={currentServer.backupInProgress}
            onChange={evt => updateRemoteUrl(evt)}
            placeholder={`Paste ${section} URL`}
            type="text"
          />
        </div>

        <div
          id="dropZone"
          className={dropBoxCSS}
          ref={div => dropZone = div}
          type="file"
          onDragEnd={evt => dragendHandler(evt, false)}
          onDrop={evt => dropHandler(evt)}
          onDragOver={evt => dragoverHandler(evt, true)}
          onDragLeave={evt => dragLeaveHandler(evt, false)}
          onDragEnter={evt => dragEnterHandler(evt, false)}
        >
          { (ready && files[0])
            ? (
              <div className="Import__ready">
                <div>{`Select Import to import the following ${section}`}</div>
                <hr />
                <div>{`${section} Owner: ${owner}`}</div>
                <div>{`${section} Name: ${name}`}</div>
              </div>
            )
            : (
              <div className="DropZone">
                <div className="Dropbox--menu">
                  <h5 className="ImportModal__h5">{`Drag and drop an exported ${section} here`}</h5>
                  <span>or</span>
                </div>
                <label
                  className="flex justify--center"
                  htmlFor="zip__dropzone"
                >
                  <div
                    className="Btn Btn--allStyling"
                  >
                    Choose Files...
                  </div>
                  <input
                    id="zip__dropzone"
                    className="hidden"
                    type="file"
                    onChange={evt => dropHandler(evt)}
                  />
                </label>
              </div>
            )}
        </div>

        <div className="Import__buttonContainer">
          <button
            type="button"
            onClick={() => closeImportModal()}
            className="Btn--flat"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => { importRepository(); }}
            className="Btn--last"
            disabled={!ready || isImporting}
          >
            Import
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default ImportModal;
