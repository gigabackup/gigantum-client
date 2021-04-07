// @flow
// vendor
import React from 'react';
// images
import gigantumLogo from 'Images/logos/gigantum-client.svg';
// css
import './ImportHeader.scss';

const ImportHeader = () => (
  <div className="ImportHeader flex justify--center">
    <img
      alt="Gigantum Logo"
      src={gigantumLogo}
    />
  </div>
);

export default ImportHeader;
