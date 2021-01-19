// @flow
// vendor
import React, { Component } from 'react';
// context
import ServerContext from 'Pages/ServerContext';
// components
import Modal from 'Components/modal/Modal';
import CollaboratorsList from './list/CollaboratorList';
import CollaboratorSearch from './search/CollaboratorSearch';
// mutations
import CollaboratorMutations from './mutations/CollaboratorMutations';
// assets
import './CollaboratorsModal.scss';

type Props = {
  canManageCollaborators: boolean,
  collaborators: Array,
  name: string,
  owner: string,
  sectionType: string,
  toggleCollaborators: Function,
};

class CollaboratorsModal extends Component<Props> {
  mutations = new CollaboratorMutations(this.props);

  state = {
    overflow: false,
  }

  /**
    *  @param {boolean} overlfow
    *  sets of the menu should overflow
  */
  _setOverflow = (overflow) => {
    this.setState({ overflow });
  }

  /**
    *  @param {String} permission
    *  @param {String} CollaboratorName
    *  gets permissions value and displays it to the UI more clearly
  */
  _getPermissions = (permission, collaboratorName) => {
    const { owner } = this.props;
    if ((permission === 'readonly') || (permission === 'READ_ONLY')) {
      return 'Read';
    } if ((permission === 'readwrite') || (permission === 'READ_WRITE')) {
      return 'Write';
    } if ((permission === 'owner') || (permission === 'OWNER')) {
      return (collaboratorName === owner) ? 'Owner' : 'Admin';
    }
    return 'Read';
  }

  render() {
    const {
      canManageCollaborators,
      toggleCollaborators,
    } = this.props;
    const { overflow } = this.state;

    return (
      <Modal
        header="Manage Collaborators"
        icon="user"
        size="large-long"
        overflow="visible"
        handleClose={() => { toggleCollaborators(); }}
      >
        <ServerContext.Consumer>
          {value => (
            <div className="Modal__sizer">
              <CollaboratorSearch
                {...this.props}
                currentServer={value.currentServer}
                getPermissions={this._getPermissions}
                mutations={this.mutations}

              />

              <div className="CollaboratorsModal__collaborators">

                <h5 className="CollaboratorsModal__h5">Collaborators</h5>

                <CollaboratorsList
                  {...this.props}
                  canManageCollaborators={canManageCollaborators}
                  currentServer={value.currentServer}
                  getPermissions={this._getPermissions}
                  mutations={this.mutations}
                  overflow={overflow}
                  setOverflow={this._setOverflow}
                  toggleCollaborators={toggleCollaborators}
                />
              </div>
            </div>
          )}
        </ServerContext.Consumer>
      </Modal>
    );
  }
}

export default CollaboratorsModal;
