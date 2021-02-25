// @flow
// vendor
import React, { Component } from 'react';
// components
import CustomAppsRow from './row/CustomAppsRow';
// assets
import './CustomAppsTable.scss';

type Props = {
  customApps: {
    edges: Array<Object>,
  },
  customAppsMutations: {
    removeCustomApp: Function,
    uploadCustomApp: Function,
  },
  isLocked: boolean,
}

const CustomAppsTable = ({
  customApps,
  customAppsMutations,
  isLocked,
}: Props) => {
  const customAppsArray = customApps || [];

  return (
    <div className="Table Table--padded">
      <div className="Table__Header Table__Header--medium flex align-items--center">
        <div className="CustomAppsTable__header-file flex-1">Name</div>
        <div className="CustomAppsTable__header-path flex-2">Description</div>
        <div className="CustomAppsTable__header-file flex-1">Port</div>
        <div className="CustomAppsTable__header-path flex-3">Command</div>
        <div className="CustomAppsTable__header-actions">Actions</div>
      </div>
      <div className="Table__Body">
        { customAppsArray.map((app) => (
          <CustomAppsRow
            app={app}
            customAppsMutations={customAppsMutations}
            isLocked={isLocked}
            key={app.id}
          />
        ))}

        { (customAppsArray.length === 0)
          && <p className="text-center">No Custom Apps have been added to this project</p>}
      </div>
    </div>
  );
};

export default CustomAppsTable;
