// @flow
// vendor
import React, { Component } from 'react';
import uuidv4 from 'uuid/v4';
import { connect } from 'react-redux';
// context
import ServerContext from 'Pages/ServerContext';
// queries
import UserIdentity from 'JS/Auth/UserIdentity';
import LinkedLocalDatasetsQuery from 'Pages/repository/shared/header/actionsSection/queries/LinkedLocalDatasetsQuery';
// store
import {
  setWarningMessage,
  setMultiInfoMessage,
} from 'JS/redux/actions/footer';
import { setSidepanelVisible } from 'JS/redux/actions/labbook/labbook';
// components
// componenets
import ForceSync from 'Pages/repository/shared/modals/force/ForceSync';
import VisibilityModal from 'Pages/repository/shared/modals/visibility/VisibilityModal';
import PublishDatasetsModal from 'Pages/repository/shared/modals/publishDataset/PublishDatasetsModal';
import LoginPrompt from 'Pages/repository/shared/modals/LoginPrompt';
import SyncWarning from 'Pages/repository/shared/modals/syncWarning/SyncWarning';
import BranchMenu from './menu/BranchMenu';
import BranchesSidePanel from './panel/BranchesSidePanel';
import PublishSyncErrorModal from './modal/PublishSyncErrorModal';
// utils
import BranchMutations from '../../utils/BranchMutations';
// components
import {
  checkForWriteAccess,
  extractActiveBranch,
  getLocalDatasets,
  getSyncOrPublish,
  getSyncTooltip,
} from './utils/branchMenuUtils';


type Props = {
  branches: string,
  collaborators: Object,
  defaultRemote: string,
  isExporting: boolean,
  isLocked: boolean,
  isLockedSync: boolean,
  section: {
    name: string,
    owner: string,
    description: string,
  },
  sectionId: string,
  sectionType: string,
  setBranchUptodate: Function,
  setSyncingState: Function,
  setPublishingState: Function,
  updateMigationState: Function,
};

class Branches extends Component<Props> {
  state = {
    action: null,
    forceSyncModalVisible: false,
    isPublishSyncErroModalVisible: false,
    publishDatasetsModalVisible: false,
    publishDatasetsModalAction: 'Publish',
    publishModalVisible: false,
    publishSyncError: false,
    publishSyncErrorData: null,
    pullOnly: false,
    showLoginPrompt: false,
    showSyncWarning: false,
    switchingBranch: false,
    warningAction: '',
  };

  branchMutations = new BranchMutations({
    parentId: this.props.sectionId,
    name: this.props.section.name,
    owner: this.props.section.owner,
  });


  static getDerivedStateFromProps(props, state) {
    const { publishFromCollaborators } = props;
    const { publishModalVisible } = state;
    return {
      ...state,
      publishModalVisible: publishFromCollaborators || publishModalVisible,
    };
  }

  /**
  *  @param {}
  *  returns UserIdentityQeury promise
  *  @return {promise}
  */
  _checkSessionIsValid = () => (UserIdentity.getUserIdentity())

  /**
  *  @param {}
  *  closes login prompt modal
  *  @return {}
  */
  _closeLoginPromptModal = () => {
    this.setState({ showLoginPrompt: false });
  }


  /**
  *  @param {Boolean} - pullOnly
  *  @param {Boolean} - allowSync
  *  @param {Boolean} - allowSyncPull
  *  @param {Function} - passedSuccessCall
  *  @param {Boolean} - overrideLock
  *  handles syncing or publishing the project
  *  @return {}
  */
  _handleSyncButton = (
    pullOnly,
    allowSync,
    allowSyncPull,
    passedSuccessCall,
    overrideLock,
  ) => {
    // TODO refactor this function

    const {
      defaultRemote,
      isLocked,
      section,
      sectionType,
      setBranchUptodate,
      setSyncingState,
    } = this.props;
    const { owner } = section;
    const isDataset = sectionType === 'dataset';
    const { publishSyncError } = this.state;
    const { buildImage } = this.branchMutations;

    if (publishSyncError) {
      this.setState({ isPublishSyncErroModalVisible: true });
      return;
    }


    if (isLocked && (sectionType === 'labbook') && !overrideLock) {
      const warningAction = defaultRemote ? 'sync' : 'publish';
      this.setState({ showSyncWarning: true, warningAction });
      return;
    }
    this.setState({ syncMenuVisible: false, showSyncWarning: false });

    if (allowSync || (pullOnly && allowSyncPull)) {
      if (!defaultRemote) {
        this._togglePublishModal(!isDataset, false);
      } else {
        setSyncingState(true);
        const self = this;
        const data = {
          successCall: () => {
            if ((sectionType === 'labbook') && !isLocked) {
              buildImage((response, error) => {
                if (error) {
                  console.error(error);
                  const messageData = {
                    id: uuidv4(),
                    message: `ERROR: Failed to build ${section.name}`,
                    isLast: null,
                    error: true,
                    messageBody: error,
                  };
                  setMultiInfoMessage(owner, section.name, messageData);
                }
              });
              setBranchUptodate();
            }
            setSyncingState(false);
          },
          failureCall: (errorMessage, reportedFailureMessage) => {
            setSyncingState(false);
            if (errorMessage.indexOf('Merge conflict') > -1) {
              self._toggleSyncModal();
              this.setState({ pullOnly });
            } else {
              this._setPublishErrorState(errorMessage, reportedFailureMessage);
            }
          },
          pullOnly: pullOnly || false,
        };

        this._checkSessionIsValid().then((response) => {
          if (!navigator.onLine) {
            self.setState({ showLoginPrompt: true });
          } else if (!(response.data
              && response.data.userIdentity
              && response.data.userIdentity.isSessionValid)) {
            self.setState({ showLoginPrompt: true });
          } else if (sectionType !== 'labbook') {
            this._syncDataset(data);
          } else {
            this._syncLabbook(data, passedSuccessCall, pullOnly);
          }
        });
      }
    }
  }


  /**
    *  @param {Object} activeBranch
    *  @param {Boolean} hasWriteAccess
    *  @param {Boolean} upToDate
    *  returns tooltip info
    *  @return {string}
    */
  _getTooltipText = (activeBranch, hasWriteAccess) => {
    // destructure here
    const {
      collaborators,
      defaultRemote,
      isLocked,
      section,
      sectionType,
    } = this.props;
    const { currentServer } = this.context;

    const data = {
      activeBranch,
      collaborators,
      defaultRemote,
      hasWriteAccess,
      isLocked,
      section,
      sectionType,
    };
    const syncTooltip = getSyncTooltip(
      data,
      currentServer,
    );

    return syncTooltip;
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
    const { owner, labbookName } = this.state;
    const { currentServer } = this.context;
    const { baseUrl } = currentServer;
    this.setState({
      addedRemoteThisSession: true,
      remoteUrl: `${baseUrl}${owner}/${labbookName}`,
    });
  }


  /**
  *  @param {Array} branches
  *  filters array branhces and return the active branch node
  *  @return {Object} activeBranch
  */
  _setModalState = (key) => {
    const { state } = this;
    const { isLocked } = this.props;

    const value = !state[key];
    if (!isLocked && !state.isDataset) {
      this.setState({ [key]: value });
    }
  }


  /**
  * @param {Object} data
  * syncs dataset
  */
  _syncDataset = (data) => {
    const { branchMutations } = this;
    const { setSyncingState } = this.props;

    setSyncingState(true);
    branchMutations.syncDataset(data, (response, error) => {
      if (error) {
        data.failureCall(error);
      }
    });
  }

  /**
  * @param {Object} data
  * @param {function} passedSuccessCall
  * @param { Boolean} pullOnly
  * checks if project has a any published datasets and pops modal to sync them
  * or syncs project if none present
  */
  _syncLabbook = (data, passedSuccessCall, pullOnly) => {
    const { branchMutations } = this;
    const { section, setSyncingState } = this.props;
    const { syncLabbook } = branchMutations;
    const { owner, name } = section;

    setSyncingState(true);

    LinkedLocalDatasetsQuery.getLocalDatasets({
      owner,
      name,
    }).then((linkedQueryResponse) => {
      const localDatasets = getLocalDatasets(linkedQueryResponse);

      if ((localDatasets.length === 0) || pullOnly) {
        setSyncingState(true);

        syncLabbook(data, (response, error) => {
          if (error) {
            data.failureCall(error);
          }
          if (passedSuccessCall) {
            passedSuccessCall();
          }
        });
      } else {
        this.setState((state) => {
          const publishDatasetsModalVisible = !state.publishDatasetsModalVisible;
          return {
            localDatasets,
            publishDatasetsModalVisible,
            publishDatasetsModalAction: 'Sync',
          };
        });

        setSyncingState(false);
      }
    });
  }

  /**
    @param {String} action
    handles labbook cover toggle
    @return {}
  */
  _toggleCover = (action) => {
    // TODO don't use getElementById to set classNames
    if (action) {
      this.setState({ action });
      if (document.getElementById('labbook__cover')) {
        document.getElementById('labbook__cover').classList.remove('hidden');
      }
    } else {
      this.setState({ action: false });
      if (document.getElementById('labbook__cover')) {
        document.getElementById('labbook__cover').classList.add('hidden');
      }
    }
  }

  /**
    @param {} -
    sets state to toggle the switch dropdown
    @return {}
  */
  _toggleSidePanel = (sidePanelVisible) => {
    const { props } = this;
    const { isLocked, sectionType } = this.props;
    const { owner, name } = props[sectionType];
    const { isDataset } = this.state;

    if (!isLocked && !isDataset) {
      this.setState({ switchMenuVisible: false });
      setSidepanelVisible(owner, name, sidePanelVisible);
    }
  }

  /**
  *  @param {}
  *  toggles sync modal
  *  @return {string}
  */
 _toggleSyncModal = () => {
   this.setState((state) => {
     const forceSyncModalVisible = !state.forceSyncModalVisible;
     return {
       forceSyncModalVisible,
       publishDatasetsModalVisible: false,
     };
   });
 }

  /**
  *  @param {Boolean} queryForLocalDatasets
  *  @param {Boolean} closePublishDatasetsModal
  *  adds remote url to labbook
  *  @return {string}
  */
  _togglePublishModal = (queryForLocalDatasets, closePublishDatasetsModal) => {
    const { isExporting, section } = this.props;

    if (isExporting) {
      const { owner, name } = section;
      setWarningMessage(owner, name, 'Publishing is currently only available on the main workspace branch.');
      this.setState({ publishWarningVisible: true });
    } else if (queryForLocalDatasets && (typeof queryForLocalDatasets === 'boolean')) {
      LinkedLocalDatasetsQuery.getLocalDatasets({
        owner: section.owner,
        name: section.name,
      }).then((res) => {
        const localDatasets = res.data && res.data.labbook.linkedDatasets.filter(linkedDataset => linkedDataset.defaultRemote && linkedDataset.defaultRemote.slice(0, 4) !== 'http');
        if (localDatasets.length === 0) {
          this.setState((state) => {
            const publishModalVisible = !state.publishModalVisible;
            return { publishModalVisible };
          });
        } else {
          this.setState((state) => {
            const publishDatasetsModalVisible = !state.publishDatasetsModalVisible;
            return {
              localDatasets,
              publishDatasetsModalVisible,
              publishDatasetsModalAction: 'Publish',
            };
          });
        }
      });
    } else if (closePublishDatasetsModal) {
      this.setState((state) => {
        const publishDatasetsModalVisible = !state.publishDatasetsModalVisible;
        return { publishDatasetsModalVisible };
      });
    } else {
      this.setState((state) => {
        const publishModalVisible = !state.publishModalVisible;
        return { publishModalVisible };
      });
    }
  }


  /**
  * Method sets error state on button error state for the SyncErrorModal
  * @param {string} errorMessage
  * @param {string} reportedFailureMessage
  *
  */
  _setPublishErrorState = (errorMessage, reportedFailureMessage) => {
    this.setState({
      publishSyncError: true,
      publishSyncErrorData: {
        header: errorMessage,
        message: reportedFailureMessage,
      },
    });
  }

  /**
  * Method clears error state
  *
  */
  _clearSyncErorrState = () => {
    this.setState({
      isPublishSyncErroModalVisible: false,
      publishSyncError: false,
      publishSyncErrorData: null,
    });
  }

  /**
 * sets state for sync warning modal
 */
 _toggleSyncWarningModal = () => {
   this.setState({ showSyncWarning: false });
 }


  static contextType = ServerContext;

  render() {
    const currentServer = this.context;
    const {
      branches,
      collaborators,
      defaultRemote,
      isLocked,
      isLockedSync,
      section,
      sectionId,
      sectionType,
      setSyncingState,
      updateMigationState,
    } = this.props;
    const {
      action,
      forceSyncModalVisible,
      isPublishSyncErroModalVisible,
      localDatasets,
      publishDatasetsModalAction,
      publishDatasetsModalVisible,
      publishModalVisible,
      publishSyncError,
      publishSyncErrorData,
      pullOnly,
      showLoginPrompt,
      showSyncWarning,
      warningAction,
    } = this.state;
    const {
      activeBranch,
    } = extractActiveBranch(branches);
    const { name, owner } = section;
    const syncOrPublish = getSyncOrPublish(defaultRemote, pullOnly);
    // declare vars here
    const isDataset = (sectionType !== 'labbook');
    const sectionCollabs = (collaborators && collaborators[name])
       || null;
    const waitingOnCollabs = !sectionCollabs;
    const hasWriteAccess = checkForWriteAccess(
      activeBranch,
      defaultRemote,
      collaborators,
      name,
    );
    const upToDate = (activeBranch.commitsAhead === 0)
      && (activeBranch.commitsBehind === 0);
    const allowSync = !((activeBranch.branchName !== 'master') && !defaultRemote)
      && hasWriteAccess && !isLockedSync;
    const allowSyncPull = !((activeBranch.branchName !== 'master') && !defaultRemote)
      && defaultRemote && !isLockedSync;
    const showPullOnly = defaultRemote && !hasWriteAccess && !waitingOnCollabs;
    const disableDropdown = !allowSyncPull || !defaultRemote || showPullOnly || publishSyncError;

    const syncTooltip = this._getTooltipText(activeBranch, hasWriteAccess, upToDate);
    return (
      <>
        <BranchMenu
          {...this.props}
          action={action}
          activeBranch={activeBranch}
          allowSync={allowSync}
          allowSyncPull={allowSyncPull}
          branchMutations={this.branchMutations}
          currentServer={currentServer}
          disableDropdown={disableDropdown}
          handleSyncButton={this._handleSyncButton}
          isableDropdown={disableDropdown}
          isDataset={isDataset}
          isLockedSync={isLockedSync}
          publishSyncError={publishSyncError}
          showLoginPrompt={showLoginPrompt}
          showPullOnly={showPullOnly}
          setModalState={this._setModalState}
          syncTooltip={syncTooltip}
          toggleCover={this._toggleCover}
          toggleSidePanel={this._toggleSidePanel}
          updateMigationState={updateMigationState}
          upToDate={upToDate}
        />
        <BranchesSidePanel
          {...this.props}
          activeBranch={activeBranch}
          allowSync={allowSync}
          allowSyncPull={allowSyncPull}
          branchMutations={this.branchMutations}
          defaultRemote={defaultRemote}
          disableDropdown={disableDropdown}
          isDataset={isDataset}
          handleSyncButton={this._handleSyncButton}
          labbookName={section.name}
          section={section}
          showPullOnly={showPullOnly}
          switchBranch={this._switchBranch}
          syncTooltip={syncTooltip}
          toggleCover={this._toggleCover}
          toggleModal={this._setModalState}
          toggleSidePanel={this._toggleSidePanel}
          updateMigrationState={updateMigationState}
          waitingOnCollabs={waitingOnCollabs}
        />

        <VisibilityModal
          {...this.props}
          isVisible={publishModalVisible}
          owner={owner}
          name={name}
          labbookId={sectionId}
          remoteUrl={defaultRemote}
          buttonText="Publish"
          header="Publish"
          modalStateValue="visibilityModalVisible"
          checkSessionIsValid={this._checkSessionIsValid}
          toggleModal={this._togglePublishModal}
          resetState={this._resetState}
          resetPublishState={this._resetPublishState}
          setPublishErrorState={this._setPublishErrorState}
          setRemoteSession={this._setRemoteSession}
          setSyncingState={setSyncingState}
        />

        <PublishDatasetsModal
          {...this.props}
          isVisible={publishDatasetsModalVisible}
          owner={owner}
          name={name}
          labbookId={sectionId}
          buttonText="Publish All"
          header={publishDatasetsModalAction}
          pullOnly={pullOnly}
          modalStateValue="visibilityModalVisible"
          toggleSyncModal={this._toggleSyncModal}
          checkSessionIsValid={this._checkSessionIsValid}
          toggleModal={this._togglePublishModal}
          resetState={this._resetState}
          resetPublishState={this._resetPublishState}
          setRemoteSession={this._setRemoteSession}
          handleSync={this._handleSyncButton}
          localDatasets={localDatasets || []}
          setPublishErrorState={this._setPublishErrorState}
        />

        <ForceSync
          {...this.props}
          isVisible={forceSyncModalVisible}
          name={name}
          owner={owner}
          pullOnly={pullOnly}
          toggleSyncModal={this._toggleSyncModal}
          setPublishErrorState={this._setPublishErrorState}
        />

        <LoginPrompt
          showLoginPrompt={showLoginPrompt}
          closeModal={this._closeLoginPromptModal}
        />

        <PublishSyncErrorModal
          closeModal={this._clearSyncErorrState}
          data={publishSyncErrorData}
          isVisible={isPublishSyncErroModalVisible}
          remoteOperationPerformed={syncOrPublish}
        />

        <SyncWarning
          allowSync={allowSync}
          allowSyncPull={allowSyncPull}
          handleSync={this._handleSyncButton}
          isLocked={isLocked}
          isVisible={showSyncWarning}
          showPullOnly={showPullOnly}
          toggleSyncWarningModal={this._toggleSyncWarningModal}
          warningAction={warningAction}
        />
      </>
    );
  }
}


const mapStateToProps = state => ({
  collaborators: state.collaborators.collaborators,
  publishFromCollaborators: state.collaborators.publishFromCollaborators,
});

const mapDispatchToProps = () => ({});

export default connect(mapStateToProps, mapDispatchToProps)(Branches);
