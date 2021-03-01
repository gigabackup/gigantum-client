// @flow
// component
import React, { PureComponent } from 'react';
import classNames from 'classnames';
// images
import exclamationSVG from 'Images/icons/exclamation-orange.svg';
// components
import CollaboratorsRow from './CollaboratorsRow';
import NoCollaborators from './NoCollaborators';

// css
import './CollaboratorList.scss';

type Props = {
  currentServer: Object,
  collaborators: Array<Object>,
  overflow: boolean,
  toggleCollaborators: Function,
};

class CollaboratorList extends PureComponent<Props> {
  render() {
    const {
      currentServer,
      collaborators,
      overflow,
      toggleCollaborators,
    } = this.props;
    // declare css here
    const collaboratorList = classNames({
      CollaboratorsModal__list: true,
      'CollaboratorsModal__list--overflow': overflow,
    });

    if (currentServer.backupInProgress) {
      return (
        <div className="CollaboratorList__warning flex justify--center flex--column align-items--center">
          <img
            alt="warning"
            className="CollaboratorList__warning-icon"
            src={exclamationSVG}
          />
          <p>Backup is in progress, cannot add, modify or list collaborators at this time.</p>
        </div>
      );
    }

    if (collaborators && (collaborators.length > 0)) {
      return (
        <div className="CollaboratorsModal__listContainer">
          <ul className={collaboratorList}>
            { collaborators.map(collaborator => (
              <CollaboratorsRow
                {...this.props}
                key={collaborator.username}
                collaborator={collaborator}
              />
            ))}
          </ul>
        </div>
      );
    }

    return (
      <NoCollaborators
        collaborators={collaborators}
        currentServer={currentServer}
        toggleCollaborators={toggleCollaborators}
      />
    );
  }
}

export default CollaboratorList;
