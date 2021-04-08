// @flow
// vendor
import React, { Component } from 'react';
import uuidv4 from 'uuid/v4';
import Highlighter from 'react-highlight-words';
import classNames from 'classnames';
import Moment from 'moment';
// context
import ServerContext from 'Pages/ServerContext';
// components
import RepositoryTitle from 'Pages/dashboard/shared/title/RepositoryTitle';
import ImportButton from 'Pages/dashboard/shared/buttons/import/ImportButton';
// muations
import ImportRemoteProjectMutation from 'Mutations/repository/import/ImportRemoteLabbookMutation';
import ImportRemoteDatasetMutation from 'Mutations/repository/import/ImportRemoteDatasetMutation';
import BuildImageMutation from 'Mutations/container/BuildImageMutation';
// store
import { setWarningMessage, setMultiInfoMessage } from 'JS/redux/actions/footer';
// utils
import { checkBackupMode } from 'JS/utils/checkBackupMode';
// queries
import UserIdentity from 'JS/Auth/UserIdentity';
// components
import LoginPrompt from 'Pages/repository/shared/modals/LoginPrompt';
import Loader from 'Components/loader/Loader';
// assets
import './RemotePanel.scss';

type Props = {
  edge: {
    node: {
      creationDateUtc: string,
      description: string,
      modifiedDateUtc: string,
      importUrl: string,
      name: string,
      owner: string,
      visibility: string,
    }
  },
  existsLocally: boolean,
  toggleDeleteModal: Function,
  filterText: string,
  sectionType: string,
}

class RemotePanel extends Component<Props> {
  state = {
    isImporting: false,
    showLoginPrompt: false,
  };

  /**
    *  @param {}
    *  changes state of isImporting to false
  */
  _clearState = () => {
    if (document.getElementById('modal__cover')) {
      document.getElementById('modal__cover').classList.add('hidden');
    }
    if (document.getElementById('loader')) {
      document.getElementById('loader').classList.add('hidden');
    }
    this.setState({
      isImporting: false,
    });
  }

  /**
    *  @param {}
    *  changes state of isImporting to true
  */
  _importingState = () => {
    document.getElementById('modal__cover').classList.remove('hidden');
    document.getElementById('loader').classList.remove('hidden');
    this.setState({
      isImporting: true,
    });
  }

  /**
    *  @param {owner, name}
    *  imports project from remote url, builds the image, and redirects to imported project
    *  @return {}
  */
  _importRepository = (owner, name) => {
    // TODO break up this function
    const { edge, sectionType } = this.props;
    const capitalRepository = sectionType === 'project' ? 'Project' : 'Dataset';
    const self = this;
    const id = uuidv4();
    const remote = edge.node.importUrl;

    UserIdentity.getUserIdentity().then((response) => {
      if (navigator.onLine) {
        if (response.data) {
          if (response.data.userIdentity.isSessionValid) {
            this._importingState();
            const messageData = {
              id,
              message: `Importing ${capitalRepository} please wait`,
              isLast: false,
              error: false,
            };
            setMultiInfoMessage(owner, name, messageData);
            if (sectionType === 'project') {
              const successCall = () => {
                this._clearState();
                const mulitMessageData = {
                  id,
                  message: `Successfully imported remote ${capitalRepository} ${name}`,
                  isLast: true,
                  error: false,
                };
                setMultiInfoMessage(owner, name, mulitMessageData);

                BuildImageMutation(
                  owner,
                  name,
                  false,
                  (res, error) => {
                    if (error) {
                      const buildMessageData = {
                        id,
                        owner,
                        name,
                        message: `ERROR: Failed to build ${name}`,
                        isLast: null,
                        error: true,
                        messageBody: error,
                      };
                      setMultiInfoMessage(owner, name, buildMessageData);
                    }
                  },
                );

                self.props.history.replace(`/projects/${owner}/${name}`);
              };
              const failureCall = (error) => {
                this._clearState();
                const failureMessageData = {
                  id,
                  owner,
                  name,
                  message: 'ERROR: Could not import remote Project',
                  isLast: null,
                  error: true,
                  messageBody: error,
                };
                if (error.indexOf('backup in progress') > -1) {
                  checkBackupMode();
                } else {
                  setMultiInfoMessage(owner, name, failureMessageData);
                }
              };
              self.setState({ isImporting: true });

              ImportRemoteProjectMutation(
                owner,
                name,
                remote,
                successCall,
                failureCall,
                (res, error) => {
                  if (error) {
                    failureCall(error);
                  }
                  self.setState({ isImporting: false });
                },
              );
            } else {
              ImportRemoteDatasetMutation(
                owner,
                name,
                remote,
                (mutationResponse, error) => {
                  this._clearState();


                  if (error) {
                    console.error(error);
                    const failureMessageData = {
                      id,
                      owner,
                      name,
                      message: 'ERROR: Could not import remote Dataset',
                      isLast: null,
                      error: true,
                      messageBody: error,
                    };
                    if (error.indexOf('backup in progress') > -1) {
                      checkBackupMode();
                    } else {
                      setMultiInfoMessage(owner, name, failureMessageData);
                    }
                  } else if (mutationResponse) {
                    const successMessageData = {
                      id,
                      owner,
                      name,
                      message: `Successfully imported remote Dataset ${name}`,
                      isLast: true,
                      error: false,
                    };
                    setMultiInfoMessage(owner, name, successMessageData);

                    self.props.history.replace(`/datasets/${owner}/${name}`);
                  }
                },
              );
            }
          } else {
            this.setState({ showLoginPrompt: true });
          }
        }
      } else {
        this.setState({ showLoginPrompt: true });
      }
    });
  }

  /**
   * @param {}
   * fires when user identity returns invalid session
   * prompts user to revalidate their session
   */
  _closeLoginPromptModal = () => {
    this.setState({
      showLoginPrompt: false,
    });
  }

  /**
   * @param {object} edge
   * validates user's session and then triggers toggleDeleteModal
   * which passes parameters to the DeleteLabbook component
  */
  _handleDelete = (edge) => {
    // TODO: move toggleDeleteModal
    const { existsLocally, toggleDeleteModal } = this.props;
    if (localStorage.getItem('username') !== edge.node.owner) {
      const { owner, name } = edge.node;
      setWarningMessage(owner, name, 'You can only delete remote Projects that you have created.');
    } else {
      UserIdentity.getUserIdentity().then((response) => {
        if (navigator.onLine) {
          if (response.data) {
            if (response.data.userIdentity.isSessionValid) {
              toggleDeleteModal({
                remoteId: edge.node.id,
                remoteUrl: edge.node.remoteUrl,
                remoteOwner: edge.node.owner,
                remoteName: edge.node.name,
                existsLocally,
              });
            } else {
              this.setState({ showLoginPrompt: true });
            }
          }
        } else {
          this.setState({ showLoginPrompt: true });
        }
      });
    }
  }


  render() {
    // variables declared here
    const { isImporting, showLoginPrompt } = this.state;
    const { edge, existsLocally, filterText } = this.props;
    const deleteDisabled = isImporting || (localStorage.getItem('username') !== edge.node.owner);
    const deleteTooltipText = (localStorage.getItem('username') !== edge.node.owner) ? 'Only owners and admins can delete a remote Project' : '';

    // css declared here
    const descriptionCss = classNames({
      'RemotePanel__row RemotePanel__row--text': true,
      blur: isImporting,
    });
    const deleteCSS = classNames({
      'Btn__dashboard Btn--action': true,
      'Tooltip-data Tooltip-data--wide': localStorage.getItem('username') !== edge.node.owner,
      'Btn__dashboard--delete': localStorage.getItem('username') === edge.node.owner,
      'Btn__dashboard--delete-disabled': localStorage.getItem('username') !== edge.node.owner,
    });

    return (
      <ServerContext.Consumer>
        {value => (
          <div
            key={edge.node.name}
            className="Card Card--225 column-4-span-3 flex flex--column justify--space-between"
          >
            <div className="RemotePanel__row RemotePanel__row--icon">
              { !(edge.node.visibility === 'local')
                && (
                <div
                  data-tooltip={`${edge.node.visibility}`}
                  className={`Tooltip-Listing RemotePanel__${edge.node.visibility} Tooltip-data Tooltip-data--small`}
                />
                )}

              <ImportButton
                currentServer={value.currentServer}
                edge={edge}
                existsLocally={existsLocally}
                importRepository={this._importRepository}
                isImporting={isImporting}
              />

              <button
                type="button"
                className={deleteCSS}
                data-tooltip={deleteTooltipText}
                disabled={deleteDisabled || value.currentServer.backupInProgress}
                onClick={() => this._handleDelete(edge)}
              >
                Delete
              </button>
            </div>

            <div className={descriptionCss}>

              <div className="RemotePanel__row RemotePanel__row--title">
                <RepositoryTitle
                  action={() => {}}
                  name={edge.node.name}
                  section="RemoteProjects"
                  filterText={filterText}
                />
              </div>

              <p className="RemotePanel__paragraph RemotePanel__paragraph--owner">{edge.node.owner}</p>
              <p className="RemotePanel__paragraph RemotePanel__paragraph--metadata">
                <span className="bold">Created:</span>
                {' '}
                {Moment(edge.node.creationDateUtc).format('MM/DD/YY')}
              </p>
              <p className="RemotePanel__paragraph RemotePanel__paragraph--metadata">
                <span className="bold">Modified:</span>
                {' '}
                {Moment(edge.node.modifiedDateUtc).fromNow()}
              </p>

              <p className="RemotePanel__paragraph RemotePanel__paragraph--description">
                { (edge.node.description && edge.node.description.length)
                  ? (
                    <Highlighter
                      highlightClassName="LocalProjects__highlighted"
                      searchWords={[filterText]}
                      autoEscape={false}
                      caseSensitive={false}
                      textToHighlight={edge.node.description}
                    />
                  )
                  : 'No description provided'}
              </p>
            </div>

            { isImporting
              && (
                <div className="RemotePanel__loader">
                  <Loader />
                </div>
              )}

            <LoginPrompt
              showLoginPrompt={showLoginPrompt}
              closeModal={this._closeLoginPromptModal}
            />
          </div>
        )}
      </ServerContext.Consumer>
    );
  }
}

export default RemotePanel;
