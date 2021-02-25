// @flow
// vendor
import React, { PureComponent } from 'react';
// Assets
import './CustomAppsEditing.scss';

type Props = {
  appName: String,
  command: String,
  description: String,
  editCustomApp: Function,
  editedCustomApps: {
    appName: String,
    command: String,
    description: String,
    port: String,
  },
  port: String,
  setEditingMode: Function,
  updateApp: Function,
  updateField: Function,
};


class CustomAppsEditing extends PureComponent<Props> {
  state = {
    portError: false,
  }

  _enforceMinMax = (evt) => {
    const element = evt.target;
    const { appName, updateField } = this.props;
    if (element.value !== '') {
      if (
        (parseInt(element.value, 10) < parseInt(element.min, 10))
        || (parseInt(element.value, 10) > parseInt(element.max, 10))
      ) {
        this.setState({ portError: true });
      } else {
        this.setState({ portError: false });
      }

      updateField(appName, 'port', evt);
    }
  }

  render() {
    const {
      appName,
      command,
      description,
      editCustomApp,
      editedCustomApps,
      port,
      setEditingMode,
      updateApp,
      updateField,
    } = this.props;
    const {
      portError,
    } = this.state;
    const canReplace = editedCustomApps;
    return (
      <div className="CustomAppsEditing flex flex--column">
        <div className="CustomAppsEditing__row flex relative">
          <div className="CustomAppsTable__form flex flex-1 justify--space-between">
            <div className="CustomAppsTable__row-file flex-1 flex flex--column justify--flex-start">
              <input
                className="AddCustomApp__input"
                type="text"
                value={editedCustomApps.appName}
                defaultValue={appName}
                onChange={evt => updateField(appName, 'appName', evt)}
              />
            </div>
            <div className="CustomAppsTable__row-path flex flex-2 flex--column justify--flex-start">
              <input
                className="AddCustomApp__input"
                type="text"
                value={editedCustomApps.description}
                onChange={evt => updateField(appName, 'description', evt)}
              />
            </div>
            <div className="CustomAppsTable__row-file flex flex-1 flex--column justify--flex-start">
              <input
                className="AddCustomApp__input"
                type="number"
                min="1024"
                max="65535"
                value={editedCustomApps.port}
                onChange={evt => this._enforceMinMax(evt)}
              />
            </div>
            <div className="CustomAppsTable__row-path flex flex-3 flex--column justify--flex-start">
              <input
                className="AddCustomApp__input"
                type="text"
                value={editedCustomApps.command}
                onChange={evt => updateField(appName, 'command', evt)}
              />
            </div>
          </div>
          <div className="CustomAppsTable__row-actions">
            <button
              className="CustomApps__btn--round CustomApps__btn--cancel"
              onClick={() => setEditingMode(false)}
              type="button"
            />
            <button
              className="CustomApps__btn--round CustomApps__btn--add"
              disabled={!canReplace}
              onClick={() => updateApp(true)}
              type="button"
            />
          </div>
        </div>

        { portError
          && <p className="CustomAppsEditing__error">Ports must be between 1024 & 65535 </p>}
      </div>
    );
  }
}

export default CustomAppsEditing;
