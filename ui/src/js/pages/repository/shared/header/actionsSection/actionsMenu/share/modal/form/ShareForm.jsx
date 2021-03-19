// @flow
// vendor
import React from 'react';
import DevToolsOptions from './devtools/DevtoolsOptions.jsx';
import CustomAppsOptions from './customapps/CustomAppsOptions';
import ShareFileInput from './file/ShareFileInput';

type Props = {
  repository: Object,
}

const ShareForm = ({ repository }: Props) => (
  <div className="ShareForm">
    <DevToolsOptions repository={repository} />
    <CustomAppsOptions repository={repository} />
    <ShareFileInput repository={repository} />
  </div>
);

export default ShareForm;
