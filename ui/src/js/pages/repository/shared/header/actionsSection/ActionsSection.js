// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
// context
import ServerContext from 'Pages/ServerContext';
// components
import LoginPrompt from 'Pages/repository/shared/modals/LoginPrompt';
import Collaborators from './collaborators/Collaborators';
import ActionsMenu from './actionsMenu/ActionsMenu';

import './ActionsSection.scss';

type Props = {
  isSticky: boolean,
}

class ActionsSection extends Component<Props> {
  state = {
    showLoginPrompt: false,
  }

  /**
   * @param {} -
   * sets login prompt to true
   * @return {}
   */
  _showLoginPrompt = () => {
    this.setState({ showLoginPrompt: true });
  }

  /**
   * @param {} -
   * sets login prompt to false
   * @return {}
   */
  _closeLoginPromptModal = () => {
    this.setState({ showLoginPrompt: false });
  }

  render() {
    const { isSticky } = this.props;
    const { showLoginPrompt } = this.state;
    // declare css here
    const actionsSectionCSS = classNames({
      ActionsSection: true,
      hidden: isSticky,
    });

    return (
      <ServerContext.Consumer>
        { value => (
          <div className={actionsSectionCSS}>
            <Collaborators
              {...this.props}
              showLoginPrompt={this._showLoginPrompt}
            />
            <ActionsMenu
              {...this.props}
              currentServer={value.currentServer}
              showLoginPrompt={this._showLoginPrompt}
            />

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

export default ActionsSection;
