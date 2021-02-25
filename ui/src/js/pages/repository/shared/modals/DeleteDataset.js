// @flow
// vendor
import React, { Component } from 'react';
// utils
import { checkBackupMode } from 'JS/utils/checkBackupMode';
// store
import {
  setErrorMessage,
  setWarningMessage,
  setInfoMessage,
} from 'JS/redux/actions/footer';
// Mutations
import DeleteDatasetMutation from 'Mutations/repository/delete/DeleteDatasetMutation';
// components
import ButtonLoader from 'Components/buttonLoader/ButtonLoader';
import Modal from 'Components/modal/Modal';
// context
import ServerContext from 'Pages/ServerContext';
// assets
import './DeleteDataset.scss';

type Props = {
  history: {
    replace: Function,
  },
  name: string,
  remoteDelete: bool,
  owner: string,
  handleClose: Function,
  remoteId: string,
  datasetListId: string,
  remoteConnection: string,
  existsLocally: bool,
  remoteAdded: bool,
  toggleModal: Function,
}

class DeleteDataset extends Component<Props> {
  state = {
    userInputName: '',
    deletePending: false,
    deleteDatasetButtonState: '',
  };

  /**
    @param {String} name
    @param {String} owner
    @param {Boolean} deleteLocal
    @param {Boolean} deleteRemote
    @param {Boolean} forceImportLocal
    fires delete dataset mutation
  */
  _handleDatasetDelete = (
    name,
    owner,
    deleteLocal,
    deleteRemote,
  ) => {
    const {
      remoteId,
      datasetListId,
      remoteConnection,
      toggleModal,
      history,
    } = this.props;

    DeleteDatasetMutation(
      name,
      owner,
      remoteId,
      datasetListId,
      remoteConnection,
      deleteLocal,
      deleteRemote,
      (response, error) => {
        this.setState({ deletePending: false });

        if (error) {
          setErrorMessage(owner, name, `The was a problem deleting ${name}`, error);
          this.setState({ deleteDatasetButtonState: 'error' });

          setTimeout(() => {
            this.setState({
              userInputName: '',
              deletePending: false,
              deleteDatasetButtonState: '',
            });
            toggleModal();

            if (document.getElementById('deleteInput')) {
              document.getElementById('deleteInput').value = '';
            }
            checkBackupMode();
          }, 1000);
        } else if (deleteRemote) {
          setInfoMessage(owner, name, `${name} has been remotely deleted`);

          this.setState({ deleteDatasetButtonState: 'finished' });

          setTimeout(() => {
            this.setState({
              userInputName: '',
              deletePending: false,
              deleteDatasetButtonState: '',
            });

            toggleModal();

            if (document.getElementById('deleteInput')) {
              document.getElementById('deleteInput').value = '';
            }
          }, 1000);
        } else {
          setInfoMessage(owner, name, `${name} has been deleted`);
          this.setState({ deleteDatasetButtonState: 'finished' });
          setTimeout(() => {
            history.replace('/datasets/local');
          }, 2000);
        }
      },
    );
  }

  /**

  /**
    @param {object} evt
    sets state of name
  */
  _setDatasetName = (evt) => {
    this.setState({ userInputName: evt.target.value });
  }

  /**
  @param {}
  fires appropriate delete dataset mutation
  */
  _deleteDataset = () => {
    const { userInputName } = this.state;
    const {
      name,
      owner,
      remoteDelete,
    } = this.props;

    if (name === userInputName) {
      this.setState({
        deletePending: true,
        deleteDatasetButtonState: 'loading',
      });
      if (!remoteDelete) {
        this._handleDatasetDelete(name, owner, true, false);
      } else {
        this._handleDatasetDelete(name, owner, false, true);
      }
    } else {
      setWarningMessage(owner, name, 'Names do not match');
    }
  }

  /**
  *  @param {}
  *  determines the warning text to be displayed to the user
*/
  _getExplanationText() {
    const {
      existsLocally,
      name,
      owner,
      remoteAdded,
      remoteDelete,
    } = this.props;

    const { currentServer } = this.context;
    const { baseUrl } = currentServer;

    if (remoteDelete) {
      if (existsLocally) {
        return (
          <div>
            <p>
              This will delete
              {' '}
              <b>{name}</b>
              {' '}
              from the cloud.
            </p>
            <p>The Dataset will still exist locally.</p>
          </div>
        );
      }
      return (
        <p>
          This will delete
          {' '}
          <b>{name}</b>
          {' '}
          from the cloud.
          All data will be removed and can not be recovered.
        </p>
      );
    } if (remoteAdded) {
      return (
        <div>
          <p>
            This will delete
            {' '}
            <b>{name}</b>
            {' '}
            from this Gigantum client.
          </p>
          <p>{`You can still download it from ${baseUrl}${owner}/${name}.`}</p>
        </div>
      );
    }
    return (
      <p>
        This will delete
        {' '}
        <b>{name}</b>
        {' '}
        from this Gigantum instance. All data will be removed and can not be recovered.
      </p>
    );
  }

  static contextType = ServerContext;

  render() {
    const {
      userInputName,
      deleteDatasetButtonState,
      deletePending,
    } = this.state;
    const {
      name,
      remoteDelete,
      handleClose,
    } = this.props;
    const deleteText = remoteDelete ? 'Delete Remote Dataset' : 'Delete Dataset';
    const deleteDisabled = deletePending || (name !== userInputName);

    return (
      <Modal
        header={deleteText}
        handleClose={() => handleClose()}
        size="medium"
        icon="delete"
      >
        <div className="DeleteDataset">
          {this._getExplanationText()}
          <input
            id="deleteInput"
            placeholder={`Enter ${name} to delete`}
            onKeyUp={(evt) => { this._setDatasetName(evt); }}
            onChange={(evt) => { this._setDatasetName(evt); }}
            type="text"
          />
          <div className="Modal__button-container">
            <button
              type="button"
              className="Btn Btn--flat"
              onClick={() => handleClose()}
            >
              Cancel
            </button>
            <ButtonLoader
              buttonState={deleteDatasetButtonState}
              buttonText={deleteText}
              className="Btn Btn--wide Btn--last"
              params={{}}
              buttonDisabled={deleteDisabled}
              clicked={this._deleteDataset}
            />
          </div>
        </div>
      </Modal>
    );
  }
}

export default DeleteDataset;
