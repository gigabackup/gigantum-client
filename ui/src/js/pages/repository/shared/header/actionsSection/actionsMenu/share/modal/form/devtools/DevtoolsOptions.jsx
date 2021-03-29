// @flow
// vendor
import React, { useState, useRef, useCallback } from 'react';
// hooks
import {
  useEventListener,
} from 'Hooks/hooks';
// components
import Dropdown from 'Components/dropdown/Dropdown';

type Props = {
  repository: {
    environment: {
      base: {
        developmentTools: Array,
      },
      bundledApps: Array,
    }
  },
  updateDevtoolUrl: Function,
}


const DevtoolsOptions = ({
  repository,
  updateDevtoolUrl,
}: Props) => {
  // props
  const { developmentTools } = repository.environment.base;
  const developmentToolsOptions = JSON.parse(JSON.stringify(developmentTools));
  const { bundledApps } = repository.environment;
  const customAppsOptions = bundledApps.map((item) => item.appName);
  // state
  const [selectedDevtool, setSelectedDevtools] = useState('none');
  const [dropdownVisible, setDropdownVisible] = useState(false);
  // refs
  const dropdownRef = useRef();

  const tools = ['none'].concat(developmentToolsOptions).concat(customAppsOptions);


  // functions
  /**
  * Method handles dropdown open and closing
  * @param {Object} evt
  * @fires evt#stopPropagation
  * @fires setDropdownVisible
  */
  const listAction = (evt) => {
    evt.stopPropagation();
    setDropdownVisible(!dropdownVisible);
  };

  /**
  * Method provides a way for child componts to update state
  * @param {string} devtool
  * @fires setSelectedDevtools
  * @fires updateDevtoolUrl
  * @fires setDropdownVisible
  */
  const itemAction = (devtool) => {
    setSelectedDevtools(devtool);
    updateDevtoolUrl(devtool);
    setDropdownVisible(false);
  };

  /**
  * Method provides a way for child componts to update state
  * @param {Object} evt
  * @fires updateCodeFileUrl
  */
  const handler = useCallback(
    (evt) => {
      if (dropdownRef.current && !dropdownRef.current.contains(evt.target)) {
        setDropdownVisible(false);
      }
    },
    [],
  );

  // Add event listener using our hook
  useEventListener('click', handler);

  return (
    <div className="DevtoolsOptions">
      <h6>Tool</h6>
      <div
        className="DevtoolsOptions__container"
        ref={dropdownRef}
      >
        <Dropdown
          itemAction={itemAction}
          label={selectedDevtool}
          listAction={listAction}
          listItems={tools}
          visibility={dropdownVisible}
        />
      </div>
    </div>
  );
};


export default DevtoolsOptions;
