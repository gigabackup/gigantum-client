// @flow
// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
// components
import CustomAppsEditing from './editing/CustomAppsEditing';
import CustomAppsAction from './actions/CustomAppsActions';


type Props = {
  app: {
    appName: string,
    description: string,
    command: string,
    port: Number,
  },
  customAppsMutations: {
    deleteCustomApp: Function,
    uploadCustomApp: Function,
  },
  isLocked: boolean,
}


class CustomAppsRow extends Component<Props> {
  state = {
    addedFiles: new Map(),
    app: {
      ...this.props.app,
    },
    isEditing: false,
  }


  /**
    * @param {String} appName
    * @param {String} section
    * @param {Event} evt
    * sets editedCustomApps in state
    *
    * @return {}
  */
  _editCustomApp = (appName, section, evt) => {
    const { app } = this.state;
    const newProperties = section ? { [section]: evt.target.value } : {};
    const newApp = {
      ...app,
      ...newProperties,
    };
    this.setState({ app: newApp });
  }

  /**
  *  @param {String} filename
  *  @param {Object} file
  *  @param {Number} id
  *  @param {Boolean} isPresent
  * sets file in state
  */
  _setApp = (node, file) => {
    const { filename, id, isPresent } = node;
    const { addedFiles } = this.state;
    const newAddedFiles = new Map(addedFiles);
    newAddedFiles.set(filename, file);
    this.setState({ addedFiles: newAddedFiles }, () => {
      this._replaceApp(true);
    });
  }


  /**
  *  @param {String} filename
  *  @param {String} path
  *  calls insert and upload file mutations
  *  @calls {props.customAppsMutations.uploadCustomApp}
  *  @calls {props.customAppsMutations.deleteCustomApp}
  */
  _updateApp = (isPresent) => {
    const {
      app,
    } = this.state;
    const { customAppsMutations } = this.props;
    const uploadData = {
      ...app,
    };

    const data = {
      appName: this.props.app.appName,
      id: this.props.app.id,
    };
    this.setState({ isEditing: false });
    const callback = (response) => {
      console.log(response);
    };

    if (isPresent) {
      const removeCallback = () => {
        customAppsMutations.uploadCustomApp(uploadData, callback);
      };
      customAppsMutations.removeCustomApp(data, removeCallback);
      this._editCustomApp();
    } else {
      customAppsMutations.uploadCustomApp(uploadData, callback);
    }
  }

  /**
  * Method sets row to edit mode
  * @param {Boolean} isEditing
  * @return {}
  */
  _setEditingMode = (isEditing) => {
    this.setState({ isEditing });
  }

  render() {
    const {
      app,
      isLocked,
    } = this.props;
    const {
      addedFiles,
      isEditing,
    } = this.state;
    const {
      appName,
      description,
      command,
      port,
    } = app;
    const showEditApp = (isEditing && !isLocked);
    // css
    const nameCSS = classNames({
      'CustomAppsTable__row-file flex-1 break-word': true,
      'CustomAppsTable__row-file--editing': isEditing,
    });


    if (showEditApp) {
      return (
        <div className="Table__Row Table__Row--customApps flex flex-1 align-items--center">
          <CustomAppsEditing
            {...app}
            addedFiles={addedFiles}
            setApp={this._setApp}
            updateField={this._editCustomApp}
            editedCustomApps={this.state.app}
            setEditingMode={this._setEditingMode}
            updateApp={this._updateApp}
          />
        </div>
      );
    }


    return (
      <div className="Table__Row Table__Row--customApps flex flex-1 align-items--center">
        <div className={nameCSS}>
          <div className="flex">
            <div className="CustomAppsTable__name">
              {appName}
            </div>
          </div>
        </div>
        <div className="CustomAppsTable__row-path flex-2 break-word">
          {description}
        </div>
        <div className="CustomAppsTable__row-path flex-1 break-word">
          {port}
        </div>
        <div className="CustomAppsTable__row-path flex-3 break-word">
          {command}
        </div>

        <div className="CustomAppsTable__row-actions">
          <CustomAppsAction
            {...app}
            {...this.props}
            editCustomApp={this._editCustomApp}
            isEditing={isEditing}
            editedCustomApps={this.state.app}
            setEditingMode={this._setEditingMode}
            updateApp={this._updateApp}
          />
        </div>
      </div>
    );
  }
}


export default CustomAppsRow;
