// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
// store
import { setErrorMessage, setInfoMessage } from 'JS/redux/actions/footer';
// mutations
import ModifyDatasetLinkMutation from 'Mutations/ModifyDatasetLinkMutation';
// config
import config from 'JS/config';
// components
import DatasetBody from './DatasetBody';
// assets
import './DatasetCard.scss';

export default class DatasetCard extends Component {
  state = {
    expanded: false,
    popupVisible: false,
    unlinkPending: false,
    downloadPending: false,
  }

  /**
  *  @param {Obect} evt
  *  @param {Boolean} expanded
  *  toggles expanded in state
  *  @return {}
  */
  _toggleExpanded = (evt, expanded) => {
    if (evt.target.nodeName !== 'BUTTON') {
      this.setState({ expanded });
    }
  }

  /**
  *  @param {Obect} evt
  *  unlinks a dataset
  *  @return {}
  */
  _unlinkDataset = (evt) => {
    const { props } = this;
    const labbookOwner = props.owner;
    const labbookName = props.name;
    const datasetOwner = props.dataset.owner;
    const datasetName = props.dataset.name;
    this.setState({ unlinkPending: true });
    this._togglePopup(evt, false);
    ModifyDatasetLinkMutation(
      labbookOwner,
      labbookName,
      datasetOwner,
      datasetName,
      'unlink',
      null,
      (response, error) => {
        if (error) {
          this.setState({ unlinkPending: false });
          setErrorMessage('Unable to unlink dataset', error);
        } else {
          setInfoMessage(`Dataset ${datasetName} has been succesfully unlinked`);
        }
      },
    );
  }

  /**
  *  @param {}
  *  downloads a dataset
  *  @return {}
  */
  _downloadDataset = () => {
    const { props } = this;
    const labbookOwner = props.owner;
    const labbookName = props.name;
    const { owner } = props.dataset;
    const datasetName = props.dataset.name;
    const data = {
      labbookOwner,
      datasetName,
      labbookName,
      owner,
      allKeys: true,
    };

    data.successCall = () => {
      this.setState({ downloadPending: false });
    };
    data.failureCall = () => {
      this.setState({ downloadPending: false });
    };
    const callback = (response, error) => {
      if (error) {
        this.setState({ downloadPending: false });
      }
    };
    this.setState({ downloadPending: true });
    props.mutations.downloadDatasetFiles(data, callback);
  }

  /**
  *  @param {Obect} evt
  *  @param {boolean} popupVisible - boolean value for hiding and showing popup state
  *  triggers favoirte unfavorite mutation
  *  @return {}
  */
  _togglePopup(evt, popupVisible) {
    if (!popupVisible) {
      evt.stopPropagation(); // only stop propagation when closing popup, other menus won't close on click if propagation is stopped
    }
    this.setState({ popupVisible });
  }

  render() {
    const { props, state } = this;
    const numFilesText = `${props.dataset.overview.numFiles} file${(props.dataset.overview.numFiles === 1) ? '' : 's'}`
    const sizeText = config.humanFileSize(props.dataset.overview.totalBytes);
    const cardCSS = classNames({
      'DatasetCard Card': true,
      'DatasetCard--expanded': state.expanded,
      'DatasetCard--collapsed': !state.expanded,
    });
    const popupCSS = classNames({
      DatasetCard__popup: true,
      hidden: !state.popupVisible || props.isLocked,
      Tooltip__message: true,
    });
    const unlinkCSS = classNames({
      'Btn Btn__FileBrowserAction Btn__FileBrowserAction--unlink': true,
      'Btn__FileBrowserAction--loading': state.unlinkPending,

    });
    const downloadCSS = classNames({
      'Btn Btn__FileBrowserAction Btn__FileBrowserAction--download': true,
      'Btn__FileBrowserAction--loading': state.downloadPending,
      'Tooltip-data': props.isLocal,
    });
    const unlinkDisabled = props.isLocked || state.unlinkPending;
    const downloadDisabled = props.isLocked || state.downloadPending || props.isLocal;
    const onDiskBytes = props.dataset.overview.localBytes;
    const onDiskFormatted = config.humanFileSize(onDiskBytes);
    const toDownloadBytes = props.dataset.overview.totalBytes - props.dataset.overview.localBytes;
    const toDownloadFormatted = config.humanFileSize(toDownloadBytes);


    return (
      <div className={cardCSS}>
        <div
          className="DatasetCard__summary flex justify--space-between"
          onClick={evt => this._toggleExpanded(evt, !state.expanded)}
        >
          <div className="DatasetCard__info flex flex-1">
            <div className="DatasetCard__icon" />
            <div className="flex flex--column justify--space-between">
              <div className="DatasetCard__name">{props.dataset.name}</div>
              <div className="DatasetCard__owner">{`by ${props.dataset.owner}`}</div>
              <div className="DatasetCard__details flex justify--space-between">
                <span>{sizeText}</span>
                <span>{numFilesText}</span>
              </div>
            </div>
          </div>
          <div className="flex flex--column">
            <progress
              value={onDiskBytes}
              max={props.dataset.overview.totalBytes}
            />
            <div className="flex justify--space-between">
              <div className="DatasetCard__onDisk flex flex--column">
                <div className="DatasetCard__onDisk--primary">{onDiskFormatted}</div>
                <div className="DatasetCard__onDisk--secondary">on disk</div>
              </div>
              <div className="DatasetCard__toDownload flex flex--column">
                <div className="DatasetCard__toDownload--primary">{toDownloadFormatted}</div>
                <div className="DatasetCard__toDownload--secondary">to download</div>
              </div>
            </div>
          </div>
          <div className="flex flex--column justify--space-between align-items--end flex-1">
            <div className="relative">
              <button
                className={unlinkCSS}
                type="button"
                onClick={(evt) => { this._togglePopup(evt, true); }}
                disabled={unlinkDisabled}
              >
                Unlink Dataset
              </button>
              <div className={popupCSS}>
                <div className="Tooltip__pointer" />
                <p className="margin-top--0">Are you sure?</p>
                <div className="flex justify--space-around">
                  <button
                    className="Secrets__btn--round Secrets__btn--cancel"
                    onClick={(evt) => { this._togglePopup(evt, false); }}
                    type="button"
                  />
                  <button
                    className="Secrets__btn--round Secrets__btn--add"
                    onClick={evt => this._unlinkDataset(evt)}
                    type="button"
                  />
                </div>
              </div>
            </div>
            <button
              className={downloadCSS}
              type="button"
              data-tooltip="All files for this dataset have been downloaded"
              onClick={() => this._downloadDataset()}
              disabled={downloadDisabled}
            >
              Download All
            </button>
          </div>
        </div>
        {
          state.expanded
          && (
          <DatasetBody
            files={props.formattedFiles.children}
            mutationData={props.mutationData}
            checkLocal={props.checkLocal}
            downloadPending={state.downloadPending}
            mutations={props.mutations}
          />
          )
        }
      </div>
    );
  }
}