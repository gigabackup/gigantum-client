// @flow
// vendor
import React, { Component } from 'react';
// context
import ServerContext from 'Pages/ServerContext';
// component
import Modal from 'Components/modal/Modal';
import Complete from './status/Complete';
import Error from './status/Error';
import Publishing from './status/Publishing';
import VisibilityModalConent from './content/Content';
// utilities
import { publish, changeVisibility } from './utils/PublishMutations';
// Machine
import stateMachine from './machine/StateMachine';
import {
  CONTENT,
  PUBLISHING,
  ERROR,
  COMPLETE,
} from './machine/MachineConstants';
// assets
import './VisibilityModal.scss';

type Props = {
  buttonText: string,
  header: string,
  modalStateValue: Object,
  name: string,
  owner: string,
  resetState: Function,
  resetPublishState: Function,
  setPublishingState: Function,
  setRemoteSession: Function,
  setSyncingState: Function,
  toggleModal: Function,
  visibility: bool,
}

class VisibilityModal extends Component<Props> {
  state = {
    jobKey: null,
    isPublic: (this.props.visibility === 'public'),
    machine: stateMachine.initialState,
  }


  /**
    @param {object} state
    runs actions for the state machine on transition
  */
  _runActions = (state) => {
    if (state.actions.length > 0) {
      state.actions.forEach(f => this[f]());
    }
  };

  /**
    @param {string} eventType
    @param {object} nextState
    sets transition of the state machine
  */
  _transition = (eventType, nextState) => {
    const { state } = this;

    const newState = stateMachine.transition(
      state.machine.value,
      eventType,
      {
        state,
      },
    );

    this._runActions(newState);
    // TODO use category / installNeeded

    this.setState({
      machine: newState,
      message: nextState && nextState.message ? nextState.message : '',
      failureMessage: nextState && nextState.failureMessage ? nextState.failureMessage : '',
    });
  };

  /**
  *  @param {boolean}
  *  sets public state
  *  @return {string}
  */
  _setPublic = (isPublic) => {
    this.setState({
      isPublic,
    });
  }

  /**
  * Method handles publish callback.
  * @param {string} jobKey
  * @param {Object} error
  */
  _publishCallback = (jobKey, error) => {
    const {
      name,
      owner,
      resetPublishState,
      setPublishingState,
    } = this.props;
    if (jobKey) {
      this.setState({ jobKey });
    } else {
      this._transition(
        ERROR,
        {
          failureMessage: error[0].message,
        },
      );

      if (setPublishingState) {
        setPublishingState(owner, name, false);
      }

      resetPublishState(false);
    }
  };

  /**
  * Method handles modalVisibility callback.
  * @param {boolean} success
  * @param {Object} error
  */
  _modifyVisibilityCallback = (success, error) => {
    const {
      name,
      owner,
      resetPublishState,
      setPublishingState,
      toggleModal,
    } = this.props;
    if (success) {
      this._transition(
        COMPLETE,
        {},
      );

      setTimeout(() => {
        toggleModal();
      }, 1000)
    } else {
      this._transition(
        ERROR,
        {
          failureMessage: error[0].message,
        },
      );
    }
  };

  /**
  *  @param {} -
  *  triggers publish or change visibility
  *  @return {}
  */
  _modifyVisibility = () => {
    const { header } = this.props;
    const { isPublic } = this.state;

    if (header === 'Publish') {
      const { currentServer } = this.context;
      const { baseUrl } = currentServer;
      this._transition(
        PUBLISHING,
        {},
      );
      publish(baseUrl, this.props, isPublic, this._publishCallback);
    } else {
      this._transition(
        PUBLISHING,
        {},
      );
      changeVisibility(this.props, isPublic, this._modifyVisibilityCallback);
    }
  }

  static contextType = ServerContext;

  render() {
    const {
      buttonText,
      header,
      modalStateValue,
      name,
      owner,
      resetPublishState,
      resetState,
      setPublishingState,
      setRemoteSession,
      setSyncingState,
      toggleModal,
      visibility,
    } = this.props;
    const {
      failureMessage,
      isPublic,
      jobKey,
      machine,
    } = this.state;
    const { currentServer } = this.context;
    const icon = header === 'Publish' ? 'publish' : 'sync';


    const renderMap = {
      [CONTENT]: (
        <VisibilityModalConent
          buttonText={buttonText}
          currentServer={currentServer}
          header={header}
          isPublic={isPublic}
          modalStateValue={modalStateValue}
          modifyVisibility={this._modifyVisibility}
          setPublic={this._setPublic}
          toggleModal={this._toggleModal}
          visibility={visibility}
        />
      ),
      [PUBLISHING]: (
        <Publishing
          jobKey={jobKey}
          header={header}
          name={name}
          owner={owner}
          resetPublishState={resetPublishState}
          resetState={resetState}
          setPublishingState={setPublishingState}
          setRemoteSession={setRemoteSession}
          setSyncingState={setSyncingState}
          toggleModal={toggleModal}
          transition={this._transition}
        />
      ),
      [ERROR]: (
        <Error
          failureMessage={failureMessage}
          name={name}
          owner={owner}
        />
      ),
      [COMPLETE]: (
        <Complete
          name={name}
          owner={owner}
        />
      ),
    };

    if (stateMachine) {
      return (
        <Modal
          header={header}
          handleClose={() => toggleModal(modalStateValue)}
          size="large"
          icon={icon}
        >
          {renderMap[machine.value]}
        </Modal>
      );
    }

    return null;
  }
}

export default VisibilityModal;