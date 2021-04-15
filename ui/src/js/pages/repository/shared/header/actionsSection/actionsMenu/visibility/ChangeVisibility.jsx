// @flow
// vendor
import React, { Component } from 'react';
import ReactTooltip from 'react-tooltip';
import classNames from 'classnames';
// components
import VisibilityModal from 'Pages/repository/shared/modals/visibility/VisibilityModal';
// css
import './ChangeVisibility.scss';

type Props = {
  currentServer: {
    backupInProgress: boolean,
  },
  defaultRemote: string,
  name: string,
  owner: string,
  isLocked: boolean,
  remoteUrl: string,
  visibility: string,
};

class ChangeVisibility extends Component<Props> {
  state ={
    visibilityModalVisible: false,
  }

  /**
  *  @param {}
  *  copies remote
  *  @return {}
  */
  _toggleModal = (value) => {
    this.setState((state) => {
      const visibilityModalVisible = !state.visibilityModalVisible;

      const newVisibilityModalVisible = value === undefined ? visibilityModalVisible : value;
      return { visibilityModalVisible: newVisibilityModalVisible };
    });
  }

  render() {
    const {
      currentServer,
      defaultRemote,
      remoteUrl,
      visibility,
      isLocked,
    } = this.props;
    const { backupInProgress } = currentServer;
    const { visibilityModalVisible } = this.state;

    const doesNotHaveRemote = (defaultRemote === null) && (remoteUrl === null);

    // declare css here
    const visibilityButtonCSS = classNames({
      'ActionsMenu__btn--flat': true,
      'Tooltip-data': backupInProgress,
    });

    return (
      <li
        className="ChangeVisibility"
        data-tip="Project needs to be published before its visibility can be changed"
        data-for="Tooltip--noCache"
      >
        <div className={`ActionsMenu__item ChangeVisibility--visibility-${visibility}`}>

          <button
            className={visibilityButtonCSS}
            data-tooltip="Visibility cannot be modified when backup is in progress."
            disabled={doesNotHaveRemote || isLocked || backupInProgress}
            onClick={() => this._toggleModal('visibilityModalVisible')}
            type="button"
          >
            Change Visibility
          </button>

          <VisibilityModal
            {...this.props}
            isVisible={visibilityModalVisible}
            toggleModal={this._toggleModal}
            buttonText="Save"
            header="Change Visibility"
            modalStateValue="visibilityModalVisible"
          />

        </div>

        { doesNotHaveRemote
          && (
            <ReactTooltip
              place="top"
              id="Tooltip--noCache"
              delayShow={500}
            />
          )}
      </li>
    );
  }
}

export default ChangeVisibility;
