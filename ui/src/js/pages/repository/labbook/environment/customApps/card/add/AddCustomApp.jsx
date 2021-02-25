// vendor
import React, { Component } from 'react';
// assets
import './AddCustomApp.scss';
// utils

type Props = {
  customAppsMutations: Object,
  isLocked: boolean,
}

class AddCustomApp extends Component<Props> {
  state = {
    description: '',
    name: '',
    port: '',
    command: '',
  }

  /**
  *  @param {}
  *  calls insert and upload file mutations
  *  @calls {props.secretsMutations.uploadCustomApp}
  */
  _addCustomApp() {
    const {
      name,
      description,
      port,
      command,
    } = this.state;

    const { customAppsMutations } = this.props;
    const insertData = {
      appName: name,
      description,
      port,
      command,
    };

    const callback = (response, error) => {
      if (response && response.setBundledApp) {
        this._cancel();
      }
      if (error) {
        const displayedError = error[0].message
          || error[0].error.message;
        this.setState({ error: displayedError });
      }
    };

    customAppsMutations.uploadCustomApp(insertData, callback);
  }

  /**
  *  @param {evt} Object
  * updates field
  */
  _updateField(field, evt) {
    this.setState({ [field]: evt.target.value });
  }

  _cancel() {
    this.setState({
      description: '',
      name: '',
      port: '',
      command: '',
      error: '',
    });
  }

  _enforceMinMax = (evt) => {
    const element = evt.target;
    const { appName, updateField } = this.props;
    if (element.value !== '') {
      if (
        (parseInt(element.value, 10) < parseInt(element.min, 10))
        || (parseInt(element.value, 10) > parseInt(element.max, 10))
      ) {
        this.setState({ showError: true, error: 'Ports must be between 1024 & 65535' });
      } else {
        this.setState({ showError: false, error: null });
      }

      this._updateField('port', evt);
    }
  }


  render() {
    const {
      description,
      name,
      port,
      command,
      showError,
      error,
    } = this.state;
    const { isLocked } = this.props;
    const allowSave = description && name && port;
    const allowCancel = description || name || port || command;
    const commandtTooltip = `Optional. Enter a command that will be executed inside the Project container to start the application.
    Note, there are several important environment variables available:
      \n
      $APP_PREFIX: The prefix on which the app will be running through the Client's proxy. Often you can provide this prefix to an application.
      $PROJECT_CODE: The location of the Project's code directory
      $PROJECT_INPUT: The location of the Project's input directory
      $PROJECT_OUTPUT: The location of the Project's output directory
    `;
    return (
      <div className="AddCustomApp">
        <div className="AddCustomApp__form flex justify--space-between">
          <div className="AddCustomApp__field flex-1 flex flex--column justify--flex-start relative">
            <h6 className="AddCustomApps__h6 relative">
              <b>Name</b>
              <div
                className="Tooltip-data Tooltip-data--info"
                data-tooltip=" Enter a short name to identify this app. Max 10 characters."
              />
            </h6>
            <input
              className="AddCustomApp__input"
              type="text"
              value={name}
              onChange={evt => this._updateField('name', evt)}
              placeholder="My App"
            />
          </div>
          <div className="AddCustomApp__field flex flex-2 flex--column justify--flex-start relative">
            <h6 className="AddCustomApps__h6 relative">
              <b>Description</b>
              <div
                className="Tooltip-data Tooltip-data--top-offset Tooltip-data--info"
                data-tooltip="Enter a short description about what this app does"
              />
            </h6>
            <input
              className="AddCustomApp__input"
              type="text"
              value={description}
              onChange={evt => this._updateField('description', evt)}
              placeholder="My example dashboard"
            />
          </div>
          <div className="AddCustomApp__field flex flex-1 flex--column justify--flex-start relative">
            <h6 className="AddCustomApps__h6 relative">
              <b>Port</b>
              <div
                className="Tooltip-data Tooltip-data--top-offset Tooltip-data--info"
                data-tooltip="Enter a port that your app will run on. An EXPORT instruction will automatically be added to the environment's Dockerfile at build time."
              />
            </h6>
            <input
              className="AddCustomApp__input"
              type="number"
              min="1024"
              max="65535"
              value={port}
              onChange={evt => this._enforceMinMax(evt)}
              placeholder="9999"
            />

          </div>
          <div className="flex-1 AddCustomApp__field flex flex-3 flex--column justify--flex-start relative">
            <h6 className="AddCustomApps__h6 relative">
              <b>Command</b>
              <div
                className="Tooltip-data Tooltip-data--wide  Tooltip-data--top-offset Tooltip-data--info"
                data-tooltip={commandtTooltip}
              />
            </h6>
            <input
              className="AddCustomApp__input"
              type="text"
              value={command}
              placeholder="python3 $PROJECT_CODE/myapp.py --prefix $APP_PREFIX"
              onChange={evt => this._updateField('command', evt)}
            />
          </div>
        </div>
        <div className="AddCustomApp__actions flex justify--right">
          { error
            && <p className="AddCustomApps__paragraph AddCustomApps__paragraph--error error">{error}</p>}
          <button
            type="button"
            className="Btn Btn--flat AddCustomApps__btn"
            disabled={!allowCancel || isLocked}
            onClick={() => this._cancel()}
          >
            Cancel
          </button>
          <button
            disabled={!allowSave || showError || isLocked}
            type="button"
            className="Btn Btn--last"
            onClick={() => this._addCustomApp()}
          >
            Add
          </button>
        </div>
      </div>
    );
  }
}

export default AddCustomApp;
