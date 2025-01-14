// @flow
// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
import uuidv4 from 'uuid/v4';
import { connect } from 'react-redux';
// utilities
import JobStatus from 'JS/utils/JobStatus';
// mutations
import ExportLabbookMutation from 'Mutations/repository/export/ExportLabbookMutation';
import ExportDatasetMutation from 'Mutations/repository/export/ExportDatasetMutation';
import SyncLabbookMutation from 'Mutations/branches/SyncLabbookMutation';
import SyncDatasetMutation from 'Mutations/branches/SyncDatasetMutation';
import BuildImageMutation from 'Mutations/container/BuildImageMutation';
// store
import {
  setErrorMessage,
  setWarningMessage,
  setInfoMessage,
  setMultiInfoMessage,
} from 'JS/redux/actions/footer';
import store from 'JS/redux/store';
import { updateTransitionState } from 'JS/redux/actions/labbook/labbook';
import { setContainerMenuWarningMessage, setContainerMenuVisibility } from 'JS/redux/actions/labbook/environment/environment';
// queries
import UserIdentity from 'JS/Auth/UserIdentity';
import LinkedLocalDatasetsQuery from 'Pages/repository/shared/header/actionsSection/queries/LinkedLocalDatasetsQuery';
// components
import CreateBranch from 'Pages/repository/shared/modals/createBranch/CreateBranch';
import Tooltip from 'Components/tooltip/Tooltip';
import LoginPrompt from 'Pages/repository/shared/modals/LoginPrompt';
import DeleteLabbook from 'Pages/repository/shared/modals/DeleteLabbook';
import DeleteDataset from 'Pages/repository/shared/modals/DeleteDataset';
import ShareLink from './share/ShareLink';
import CopyUrl from './copy/CopyUrl';
import ChangeVisibility from './visibility/ChangeVisibility';
// assets
import './ActionsMenu.scss';

type Props = {
  currentServer: {
    baseUrl: string,
  },
  defaultRemote: string,
  description: string,
  history: Object,
  isExporting: boolean,
  isLocked: bool,
  name: string,
  owner: string,
  remoteUrl: string,
  sectionType: string,
  setExportingState: Function,
  setSyncingState: Function,
  toggleBranchesView: Function,
  visibility: string,
};


/**
  @param {Boolean} exporting
  @param {String} name
  @param {String} owner
  returns export text
  @return {string}
*/
const getExportText = (exporting, sectionType) => {
  if (!exporting) {
    return 'Export to Zip';
  }
  const exportType = (sectionType === 'dataset') ? 'Dataset' : 'Project';
  return `Exporting ${name} ${exportType}`;
};


class ActionsMenu extends Component<Props> {
  state = {
    addNoteEnabled: false,
    createBranchVisible: false,
    deleteModalVisible: false,
    exporting: false,
    exportPath: null,
    isValid: true,
    justOpened: true,
    name: this.props.owner,
    owner: this.props.owner,
    publishDisabled: false,
    publishWarningVisible: false,
    remoteUrl: this.props.remoteUrl,
    setPublic: false,
    showLoginPrompt: false,
    syncWarningVisible: false,
    visibilityModalVisible: false,
  };


  /**
   * attach window listener evetns here
  */
  componentDidMount() {
    window.addEventListener('click', this._closeMenu);
  }

  /**
   * detach window listener evetns here
  */
  componentWillUnmount() {
    window.removeEventListener('click', this._closeMenu);
  }

  /**
    @param {event} evt
    closes menu
  */
  _closeMenu = (evt) => {
    const {
      menuOpen,
      syncWarningVisible,
      publishWarningVisible,
    } = this.state;
    const isActionsMenu = (evt.target.className.indexOf('ActionsMenu') > -1)
      || (evt.target.className.indexOf('CollaboratorsModal') > -1)
      || (evt.target.className.indexOf('ActionsMenu__message') > -1)
      || (evt.target.className.indexOf('TrackingToggle') > -1);

    if (!isActionsMenu && menuOpen) {
      this.setState({ menuOpen: false, justOpened: true });
    }

    if (
      (evt.target.className.indexOf('ActionsMenu__btn--sync') === -1)
      && syncWarningVisible
    ) {
      this.setState({ syncWarningVisible: false });
    }

    if (
      (evt.target.className.indexOf('ActionsMenu__btn--remote') === -1)
      && publishWarningVisible
    ) {
      this.setState({ publishWarningVisible: false });
    }
  }

  /**
    @param {string} value
    sets state on createBranchVisible and toggles modal cover
  */
  _toggleModal = (value) => {
    this.setState((state) => {
      const inverseValue = !state[value];
      return {
        [value]: inverseValue,
      };
    });
  }

  /**
  *  @param {}
  *  toggles open menu state
  *  @return {string}
  */
  _toggleMenu = () => {
    this.setState((state) => {
      const menuOpen = !state.menuOpen;
      return ({ menuOpen });
    });

    if (!this.state.menuOpen) {
      setTimeout(() => {
        this.setState({ justOpened: false });
      }, 500);
    } else {
      this.setState({ justOpened: true });
    }
  }

  /**
  *  @param {}
  *  remounts collaborators by updating key
  *  @return {}
  */
  _remountCollab = () => {
    this.setState({ collabKey: uuidv4() });
  }

  /**
  *  @param {string, boolean} action, containerRunning
  *  displays container menu message
  *  @return {}
  */
  _showContainerMenuMessage = (action, containerRunning) => {
    const dispatchMessage = containerRunning ? `Stop Project before ${action}. \n Be sure to save your changes.` : `Project is ${action}. \n Please do not refresh the page.`;

    this.setState({ menuOpen: false });

    setContainerMenuWarningMessage(dispatchMessage);
  }

  /**
  *  @param {Boolean} pullOnly
  *  pushes code to remote
  *  @return {string}
  */
  _sync = (pullOnly) => {
    const {
      owner,
      name,
      isExporting,
      setSyncingState,
      sectionType,
    } = this.props;

    if (isExporting) {
      this.setState({ syncWarningVisible: true });
    } else {
      const { status } = store.getState().containerStatus;
      this.setState({ pullOnly });

      if (owner !== 'gigantum-examples') {
        this.setState({ menuOpen: false });
      }

      if (
        (status === 'Stopped')
        || (status === 'Rebuild')
        || (sectionType !== 'labbook')
      ) {
        const id = uuidv4();
        const self = this;

        this._checkSessionIsValid().then((response) => {
          if (navigator.onLine) {
            if (response.data && response.data.userIdentity) {
              if (response.data.userIdentity.isSessionValid) {
                const failureCall = (errorMessage) => {
                  setSyncingState(false);
                  if (errorMessage.indexOf('Merge conflict') > -1) {
                    self._toggleSyncModal();
                  }
                };

                const successCall = () => {
                  setSyncingState(false);
                  if (sectionType === 'labbook') {
                    BuildImageMutation(
                      owner,
                      name,
                      false,
                      (response, error) => {
                        if (error) {
                          console.error(error);
                          const messageData = {
                            id,
                            message: `ERROR: Failed to build ${name}`,
                            isLast: null,
                            error: true,
                            messageBody: error,
                          };
                          setMultiInfoMessage(owner, name, messageData);
                        }
                      },
                    );
                  }

                  setContainerMenuVisibility(false);
                };
                if (sectionType === 'labbook') {
                  LinkedLocalDatasetsQuery.getLocalDatasets({
                    owner,
                    name,
                  }).then((res) => {
                    const localDatasets = res.data
                      && res.data.labbook.linkedDatasets.filter(linkedDataset => linkedDataset.defaultRemote && linkedDataset.defaultRemote.slice(0, 4) !== 'http');

                    if (localDatasets.length === 0) {
                      setSyncingState(true);

                      this._showContainerMenuMessage('syncing');
                      SyncLabbookMutation(
                        owner,
                        name,
                        null,
                        pullOnly,
                        successCall,
                        failureCall,
                        (error) => {
                          if (error) {
                            failureCall(error);
                          }
                        },
                      );
                    } else {
                      this.setState((state) => {
                        const publishDatasetsModalVisible = !state.publishDatasetsModalVisible;
                        return {
                          localDatasets,
                          publishDatasetsModalVisible,
                          publishDatasetsModalAction: 'Sync',
                        };
                      });
                    }
                  });
                } else {
                  setSyncingState(true);

                  this._showContainerMenuMessage('syncing');
                  SyncDatasetMutation(
                    owner,
                    name,
                    false,
                    successCall,
                    failureCall,
                    (error) => {
                      if (error) {
                        failureCall(error);
                      }
                    },
                  );
                }
              } else {
                self.setState({ showLoginPrompt: true });
              }
            }
          } else {
            self.setState({ showLoginPrompt: true });
          }
        });
      } else {
        this.setState({ menuOpen: false });

        setContainerMenuWarningMessage('Stop Project before syncing. \n Be sure to save your changes.');
      }
    }
  }

  /**
  *  @param {}
  *  shows collaborators warning if user is not owner
  *  @return {}
  */
  _showCollaboratorsWarning = () => {
    const { owner, name } = this.props;
    const username = localStorage.getItem('username');

    if (owner !== username) {
      setWarningMessage(owner, name, `Only ${owner} can add and remove collaborators in this labbook.`);
    }
  }

  /**
  *  @param {}
  *  returns UserIdentityQeury promise
  *  @return {promise}
  */
  _checkSessionIsValid = () => (UserIdentity.getUserIdentity());

  /**
  *  @param {}
  *  closes login prompt modal
  *  @return {}
  */
  _closeLoginPromptModal = () => {
    this.setState({ showLoginPrompt: false });
  }

  /**
  *  @param {jobKey}
  *  polls jobStatus for export job message
  *  updates footer with a message
  *  @return {}
  */
  _jobStatus = (jobKey) => {
    const {
      setExportingState,
      owner,
      name,
    } = this.props;

    JobStatus.getJobStatus(owner, name, jobKey).then((data) => {
      setExportingState(false);
      updateTransitionState(owner, name, '');

      if (data.jobStatus.result) {
        this.setState({ exportPath: data.jobStatus.result });
        setInfoMessage(owner, name, `Export file ${data.jobStatus.result} is available in the export directory of your Gigantum working directory.`);
      }

      this.setState({ exporting: false });
    }).catch((error) => {
      updateTransitionState(owner, name, '');
      console.log(error);

      setExportingState(false);

      const errorArray = [{ message: 'Export failed.' }];

      setErrorMessage(owner, name, `${name} failed to export `, errorArray);

      this.setState({ exporting: false });
    });
  }

  /**
  *  @param {}
  *  runs export mutation if export has not been downloaded
  *  @return {}
  */
  _exportLabbook = () => {
    const {
      sectionType,
      setExportingState,
      owner,
      name,
      isLocked,
    } = this.props;

    if (!isLocked) {
      this.setState({
        exporting: true,
      });

      updateTransitionState(owner, name, 'Exporting');

      setExportingState(true);
      if (sectionType !== 'dataset') {
        ExportLabbookMutation(
          owner,
          name,
          (response, error) => {
            if (response.exportLabbook) {
              this._jobStatus(response.exportLabbook.jobKey);
            } else {
              console.log(error);

              setExportingState(false);

              setErrorMessage(owner, name, 'Export Failed', error);
            }
          },
        );
      } else {
        ExportDatasetMutation(
          owner,
          name,
          (response, error) => {
            if (response.exportDataset) {
              this._jobStatus(response.exportDataset.jobKey);
            } else {
              console.log(error);

              setExportingState(false);

              setErrorMessage(owner, name, 'Export Failed', error);
            }
          },
        );
      }
    } else {
      this._showContainerMenuMessage('exporting', true);
    }
  }

  /**
  *  @param {}
  *  toggle stat and modal visibility
  *  @return {}
  */
  _toggleDeleteModal = () => {
    this.setState((state) => {
      const deleteModalVisible = !state.deleteModalVisible;
      return {
        deleteModalVisible,
      };
    });
  }

  /**
  *  @param {}
  *  sets menu
  *  @return {}
  */
  _mergeFilter = () => {
    const { toggleBranchesView } = this.props;
    if (store.getState().containerStatus.status !== 'Running') {
      toggleBranchesView(true, true);

      this.setState({ menuOpen: false });

      window.scrollTo(0, 0);
    } else {
      this._showContainerMenuMessage('merging branches', true);
    }
  }

  /**
  *  @param {}
  *  sets menu
  *  @return {}
  */
  _switchBranch = () => {
    const { toggleBranchesView } = this.props;
    const { status } = store.getState().containerStatus;

    if (status !== 'Running') {
      window.scrollTo(0, 0);

      toggleBranchesView(true, false);

      this.setState({ menuOpen: false });
    } else {
      this._showContainerMenuMessage('switching branches', true);
    }
  }

  /**
  *  @param {string} modal
  *  passes modal to toggleModal if container is not running
  *  @return {}
  */
  _handleToggleModal = (modal) => {
    let action = '';

    if (store.getState().containerStatus.status !== 'Running') {
      this._toggleModal(modal);
    } else {
      switch (modal) {
        case 'createBranchVisible':
          action = 'creating branches';
          break;
        default:
          break;
      }

      this._showContainerMenuMessage(action, true);
    }
  }

  /**
  *  @param {}
  *  resets state after publish
  *  @return {}
  */
  _resetState = () => {
    this.setState({
      remoteUrl: '',
      showLoginPrompt: true,
    });
  }

  /**
  *  @param {}
  *  resets state after publish
  *  @return {}
  */
  _resetPublishState = (publishDisabled) => {
    this.setState({
      menuOpen: false,
      publishDisabled,
    });
  }

  /**
  *  @param {}
  *  resets state after publish
  *  @return {}
  */
  _setRemoteSession = () => {
    const { currentServer } = this.props;
    const { baseUrl } = currentServer;
    const {
      name,
      owner,
    } = this.props;
    this.setState({
      addedRemoteThisSession: true,
      remoteUrl: `${baseUrl}${owner}/${name}`,
    });
  }

  render() {
    const {
      currentServer,
      defaultRemote,
      description,
      history,
      isLocked,
      name,
      owner,
      sectionType,
    } = this.props;
    const {
      deleteModalVisible,
      exporting,
      exportPath,
      justOpened,
      menuOpen,
      remoteUrl,
      showLoginPrompt,
    } = this.state;
    const deleteText = (sectionType === 'labbook') ? 'Delete Project' : 'Delete Dataset';
    const exportText = getExportText(exporting, name, sectionType);
    const isShareLinkEnabled = (sectionType === 'labbook')
      && (window.location.host !== 'localhost:10000')
      && (window.location.host !== 'client.gtm-dev.cloud')
      && (window.location.host !== 'client.gigantum.com');
    // declare css here
    const exportCSS = classNames({
      ActionsMenu__item: true,
      'ActionsMenu__item--export': !exporting,
      'ActionsMenu__item--loading': exporting,
    });
    const branchMenuCSS = classNames({
      'ActionsMenu__menu--animation': justOpened, // this is needed to stop animation from breaking position flow when collaborators modal is open
      hidden: !menuOpen,
      'ActionsMenu__menu box-shadow': true,
    });

    return (
      <div className="ActionsMenu flex flex--column'">

        <LoginPrompt
          showLoginPrompt={showLoginPrompt}
          closeModal={this._closeLoginPromptModal}
        />

        { (deleteModalVisible && (sectionType === 'labbook'))
          && (
            <DeleteLabbook
              handleClose={() => this._toggleDeleteModal()}
              history={history}
              name={name}
              owner={owner}
              remoteAdded={defaultRemote}
              remoteDelete={false}
            />
          )}

        { (deleteModalVisible && (sectionType === 'dataset'))
          && (
            <DeleteDataset
              handleClose={() => this._toggleDeleteModal()}
              history={history}
              name={name}
              owner={owner}
              remoteAdded={defaultRemote}
            />
          )}

        <CreateBranch
          description={description}
          modalVisible={this.state.createBranchVisible}
          toggleModal={this._toggleModal}
        />

        <button
          onClick={() => { this._toggleMenu(); }}
          className="ActionsMenu__btn Btn--last"
          type="button"
        />

        <div className={branchMenuCSS}>

          <ul className="ActionsMenu__list">

            <li className={exportCSS}>
              <button
                onClick={evt => this._exportLabbook(evt)}
                disabled={exporting || isLocked}
                className="ActionsMenu__btn--flat"
                type="button"
                data-tooltip="Cannot export Project while in use"
              >
                {exportText}
              </button>

              <div
                className="Tooltip-data Tooltip-data--top-offset Tooltip-data--info"
                data-tooltip="Export as a zip file to your gigantum working directory"
              />

            </li>
            {
              exportPath
              && (
                <CopyUrl
                  showExport
                  defaultRemote={exportPath}
                  name={name}
                  owner={owner}
                  remoteUrl={exportPath}
                />
              )
            }


            <li className="ActionsMenu__item ActionsMenu__item--delete">

              <button
                onClick={() => this._toggleDeleteModal()}
                className="ActionsMenu__btn--flat"
                type="button"
              >
                {deleteText}
              </button>

            </li>

            <ChangeVisibility
              {...this.props}
              checkSessionIsValid={this._checkSessionIsValid}
              currentServer={currentServer}
              defaultRemote={defaultRemote}
              resetState={this._resetState}
            />
            { isShareLinkEnabled
              && <ShareLink />}
            <CopyUrl
              defaultRemote={defaultRemote}
              name={name}
              owner={owner}
              remoteUrl={remoteUrl}
            />

          </ul>

        </div>

        <Tooltip section="actionMenu" />

      </div>
    );
  }
}

const mapStateToProps = state => state.packageDependencies;

const mapDispatchToProps = () => ({
  setContainerMenuWarningMessage,
});

export default connect(mapStateToProps, mapDispatchToProps)(ActionsMenu);
