// @flow
// vendor
import React, { Component } from 'react';
// context
import ServerContext from 'Pages/ServerContext';
// components
import Modal from 'Components/modal/Modal';
// styles
import './BackupInProgressModal.scss';

type Props = {
  currentServer: {
    backupInProgress: boolean,
    name: string,
  }
}


class BackupInProgressModal extends Component<Props> {
  state = {
    backupModalDismissed: false,
    checkboxValue: false,
    isVisible: false,
  }

  static getDerivedStateFromProps(props, state) {
    const { currentServer } = props;
    const { backupModalDismissed } = state;
    const { backupInProgress } = currentServer;
    const ignoreBackupModal = sessionStorage.getItem('ignoreBackupModal') === 'true';

    return {
      ...state,
      backupModalDismissed,
      isVisible: backupInProgress && !backupModalDismissed && !ignoreBackupModal,
    };
  }

  /**
    Method sets backup modal to be closed and dismissed
    @param {booelan} isDismiss
  */
  _handleClose = (isDismiss = false) => {
    const { checkboxValue } = this.state;
    if (isDismiss && checkboxValue) {
      sessionStorage.setItem('ignoreBackupModal', true);
    }

    this.setState({ isVisible: false, backupModalDismissed: true });
  }

  /**
    Method sets backup modal to be closed and dismissed
    @param {}
  */
  _updateCheckBox = (evt) => {
    const checkboxValue = evt.target.checked;
    this.setState({ checkboxValue });
  }


  render() {
    const { currentServer } = this.props;
    const { name } = currentServer;
    const { isVisible } = this.state;

    if (!isVisible) {
      return null;
    }

    return (
      <Modal
        handleClose={this._handleClose}
        header="Backup in Progress"
        icon="backup"
        size="large"
      >
        <div className="BackupInProgressModal flex-1">
          <h5 className="text-center">
            <b>
              Publish, sync, and other server-related operations are unavailable until
              <br />
              this process has completed.
            </b>
          </h5>
          <p className="BackupInProgressModal__p">
            The server
            {' '}
            <pre className="BackupInProgressModal__pre">
              <code>{name}</code>
            </pre>
            {' '}
            is currently backing up your data. During this time, access to the server is blocked to ensure backup integrity. Once the backup complete, these restrictions will automatically be removed and you will be able to interact with the server again.
          </p>
        </div>
        <div className="flex flex--row align-self--end">
          <label
            className="Checkbox"
            htmlFor="backupDontShow"
          >
            <input
              id="backupDontShow"
              onChange={(evt) => this._updateCheckBox(evt)}
              type="checkbox"
            />
            <span>
              Don't show me this again
            </span>
          </label>
          <button onClick={() => { this._handleClose(true); }}>
            Dismiss
          </button>
        </div>
      </Modal>
    );
  }
}

const BackupConsumeServer = () => (
  <ServerContext.Consumer>
    { value => (
      <BackupInProgressModal currentServer={value.currentServer} />
    )}
  </ServerContext.Consumer>
);

export default BackupConsumeServer;
