// @flow
// vendor
import React from 'react';
import classNames from 'classnames';
// components
import Modal from 'Components/modal/Modal';

type Props = {
  currentServer: Object,
  self: Object,
}

const ImportModal = ({ currentServer, self }: Props) => {
  const { props, state } = self;
  const owner = state.ready ? state.ready.owner : '';
  const name = state.ready ? state.ready.name : '';
  const section = props.section === 'labbook' ? 'Project' : 'Dataset';
  // declare css here
  const inputWrapperCSS = classNames({
    'Tooltip-data': currentServer.backupInProgress,
  });
  const dropBoxCSS = classNames({
    'Dropbox Dropbox--project ImportDropzone flex flex--column align-items--center': true,
    'Dropbox--project--hovered': state.isOver,
    'Dropbox--dropped': state.ready && state.files[0],
  });
  return (
    <div className="Import__main">
      { state.showImportModal && (
        <Modal
          header={`Import ${section}`}
          handleClose={() => self._closeImportModal()}
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
                defaultValue={state.remoteUrl}
                disabled={currentServer.backupInProgress}
                onChange={evt => self._updateRemoteUrl(evt)}
                placeholder={`Paste ${section} URL`}
                type="text"
              />
            </div>

            <div
              id="dropZone"
              className={dropBoxCSS}
              ref={div => self.dropZone = div}
              type="file"
              onDragEnd={evt => self._dragendHandler(evt, false)}
              onDrop={evt => self._dropHandler(evt)}
              onDragOver={evt => self._dragoverHandler(evt, true)}
              onDragLeave={evt => self._dragLeaveHandler(evt, false)}
              onDragEnter={evt => self._dragEnterHandler(evt, false)}
            >
              { (state.ready && state.files[0])
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
                      <h5>{`Drag and drop an exported ${section} here`}</h5>
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
                        onChange={evt => self._dropHandler(evt)}
                      />
                    </label>
                  </div>
                )}
            </div>

            <div className="Import__buttonContainer">
              <button
                type="button"
                onClick={() => self._closeImportModal()}
                className="Btn--flat"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => { self._import(); }}
                className="Btn--last"
                disabled={!self.state.ready || self.state.isImporting}
              >
                Import
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default ImportModal;
