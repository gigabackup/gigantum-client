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
import ImportRemoteLabbookMutation from 'Mutations/repository/import/ImportRemoteLabbookMutation';
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
import './RemoteLabbookPanel.scss';

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
}

class RemoteLabbookPanel extends Component<Props> {
  state = {
    isImporting: false,
    showLoginPrompt: false,
  };

  /**
    *  @param {}
    *  changes state of isImporting to false
  */
  _clearState = () => {
    if (document.getElementById('dashboard__cover')) {
      document.getElementById('dashboard__cover').classList.add('hidden');
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
    *  @param {owner, labbookName}
    *  imports labbook from remote url, builds the image, and redirects to imported labbook
    *  @return {}
  */
  _importLabbook = (owner, labbookName) => {
    // TODO break up this function
    const { edge } = this.props;
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
              message: 'Importing Project please wait',
              isLast: false,
              error: false,
            };
            setMultiInfoMessage(owner, labbookName, messageData);
            const successCall = () => {
              this._clearState();
              const mulitMessageData = {
                id,
                message: `Successfully imported remote Project ${labbookName}`,
                isLast: true,
                error: false,
              };
              setMultiInfoMessage(owner, labbookName, mulitMessageData);

              BuildImageMutation(
                owner,
                labbookName,
                false,
                (buildResponse, error) => {
                  if (error) {
                    const buildMessageData = {
                      id,
                      owner,
                      name: labbookName,
                      message: `ERROR: Failed to build ${labbookName}`,
                      isLast: null,
                      error: true,
                      messageBody: error,
                    };
                    setMultiInfoMessage(owner, labbookName, buildMessageData);
                  }
                },
              );

              self.props.history.replace(`/projects/${owner}/${labbookName}`);
            };
            const failureCall = (error) => {
              this._clearState();
              const failureMessageData = {
                id,
                owner,
                name: labbookName,
                message: 'ERROR: Could not import remote Project',
                isLast: null,
                error: true,
                messageBody: Array.isArray(error) ? error : [{ message: error }],
              };
              if (error.indexOf('backup in progress') > -1) {
                checkBackupMode();
              } else {
                setMultiInfoMessage(owner, labbookName, failureMessageData);
              }
            };
            self.setState({ isImporting: true });

            ImportRemoteLabbookMutation(
              owner,
              labbookName,
              remote,
              successCall,
              failureCall,
              (response, error) => {
                if (error) {
                  failureCall(error);
                }
                self.setState({ isImporting: false });
              },
            );
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
                remoteLabbookName: edge.node.name,
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
      'RemoteLabbooks__row RemoteLabbooks__row--text': true,
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
            <div className="RemoteLabbooks__row RemoteLabbooks__row--icon">
              { !(edge.node.visibility === 'local')
                && (
                <div
                  data-tooltip={`${edge.node.visibility}`}
                  className={`Tooltip-Listing RemoteLabbooks__${edge.node.visibility} Tooltip-data Tooltip-data--small`}
                />
                )}

              <ImportButton
                currentServer={value.currentServer}
                edge={edge}
                existsLocally={existsLocally}
                importRepository={this._importLabbook}
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

              <div className="RemoteLabbooks__row RemoteLabbooks__row--title">
                <RepositoryTitle
                  action={() => {}}
                  name={edge.node.name}
                  section="RemoteLabbooks"
                  filterText={filterText}
                />
              </div>

              <p className="RemoteLabbooks__paragraph RemoteLabbooks__paragraph--owner">{edge.node.owner}</p>
              <p className="RemoteLabbooks__paragraph RemoteLabbooks__paragraph--metadata">
                <span className="bold">Created:</span>
                {' '}
                {Moment(edge.node.creationDateUtc).format('MM/DD/YY')}
              </p>
              <p className="RemoteLabbooks__paragraph RemoteLabbooks__paragraph--metadata">
                <span className="bold">Modified:</span>
                {' '}
                {Moment(edge.node.modifiedDateUtc).fromNow()}
              </p>

              <p className="RemoteLabbooks__paragraph RemoteLabbooks__paragraph--description">
                { (edge.node.description && edge.node.description.length)
                  ? (
                    <Highlighter
                      highlightClassName="LocalLabbooks__highlighted"
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
                <div className="RemoteLabbooks__loader">
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

export default RemoteLabbookPanel;
