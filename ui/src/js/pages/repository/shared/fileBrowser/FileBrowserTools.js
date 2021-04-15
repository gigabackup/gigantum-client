// @flow
import React, { PureComponent } from 'react';
import classNames from 'classnames';
// context
import ServerContext from 'Pages/ServerContext';


class FileBrowserTools extends PureComponent {
  render() {
    const {
      updateVisibleFolder,
      updateSearchState,
      uploadFiles,
      handleDownloadAll,
      updateUnmanagedDatasetMutation,
      updateConfirmVisible,
      confirmUpdateVisible,
      downloadingAll,
      readOnly,
      allFilesLocal,
      section,
      mutations,
      uploadAllowed,
    } = this.props;

    // declare css here
    const updateCSS = classNames({
      'FileBrowser__update-modal': true,
      hidden: !confirmUpdateVisible,
    });
    const actionsContainerCSS = classNames({
      'flex justify--right': true,
      'FileBrowser__Primary-actions': !readOnly,
    })

    return (
      <div className="FileBrowser__tools flex justify--space-between">

        <div className="FileBrowser__search flex-1">
          <input
            className="FileBrowser__input search"
            type="text"
            placeholder="Search Files Here"
            onChange={(evt) => { updateSearchState(evt); }}
            onKeyUp={(evt) => { updateSearchState(evt); }}
          />
        </div>
        <div className={actionsContainerCSS}>
          {
          !readOnly
          && (
            <>
              <button
                className="Btn Btn--action Btn__FileBrowserAction Btn__FileBrowserAction--newFolder"
                data-click-id="addFolder"
                onClick={() => updateVisibleFolder()}
                type="button"
              >
                New Folder
              </button>
              <label
                htmlFor="browser_upload"
                className="FileBrowser__upload-label"
              >
                <div className="Btn__FileBrowserAction Btn__FileBrowserAction--upload inline-block Btn">
                  Add Files
                </div>
                <input
                  id="browser_upload"
                  className="hidden"
                  type="file"
                  multiple
                  onChange={evt => uploadFiles(Array.prototype.slice.call(evt.target.files))}
                />
              </label>
            </>
          )
          }
          { (section === 'data')
            && (
            <ServerContext.Consumer>
              {
                value => {
                  const { backupInProgress } = value.currentServer;
                  const tooltip = backupInProgress
                    ? 'Cannot download Dataset files while server backup is in progress'
                    : 'No files to download'
                  const downloadAllCSS = classNames({
                    'Btn__FileBrowserAction Btn--action': true,
                    'Btn__FileBrowserAction--download Btn__FileBrowserAction--download--data ': !downloadingAll,
                    'Btn__FileBrowserAction--loading Btn__FileBrowserAction--downloading': downloadingAll,
                    'Tooltip-data': allFilesLocal || backupInProgress,
                  });
                  return (
                    <button
                      className={downloadAllCSS}
                      disabled={allFilesLocal || downloadingAll || backupInProgress}
                      onClick={() => handleDownloadAll(allFilesLocal)}
                      data-tooltip={tooltip}
                      type="button"
                    >
                      Download All
                    </button>
                  );
                }
              }
            </ServerContext.Consumer>
            )}
        </div>
        {
          readOnly && uploadAllowed
          && (
          <div className="flex">
            <button
              className="Btn Btn__menuButton Btn--noShadow FileBrowser__newFolder"
              onClick={() => { mutations.verifyDataset({}, () => {}); }}
              type="button"
            >
              <div
                className="Btn--fileBrowser Btn--round Btn--bordered Btn__upArrow Btn"
              />
              Verify Dataset
            </button>
            <div>
              <button
                className="Btn Btn__menuButton Btn--noShadow FileBrowser__newFolder"
                onClick={() => { mutations.verifyDataset({}, () => {}); }}
                type="button"
              >
                <div
                  className="Btn--fileBrowser Btn--round Btn--bordered Btn__upArrow Btn"
                />
                Update from Remote
              </button>
              <div>
                <button
                  className="Btn Btn__menuButton Btn--noShadow FileBrowser__newFolder"
                  onClick={() => updateConfirmVisible()}
                  type="button"
                >
                  <div
                    className="Btn--fileBrowser Btn--round Btn--bordered Btn__upArrow Btn"
                  />
                  Update from Remote
                </button>
                <div className={updateCSS}>
                  <p>This will update the Dataset with the external source. Do you wish to continue?</p>
                  <div className="flex">
                    <button
                      type="button"
                      className="Btn--flat"
                      onClick={() => updateConfirmVisible()}
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      onClick={() => updateUnmanagedDatasetMutation()}
                    >
                      Confirm
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          )
        }
      </div>
    );
  }
}

export default FileBrowserTools;
