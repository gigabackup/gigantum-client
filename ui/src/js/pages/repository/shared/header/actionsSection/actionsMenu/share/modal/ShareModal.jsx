// @flow
// vendor
import React, { useState } from 'react';
// components
import Modal from 'Components/modal/Modal';
import ShareUrlInput from './input/ShareUrlInput';
import ShareForm from './form/ShareForm';
// css
import './ShareModal.scss';

type Props = {
  environment: Object,
  handleClose: Function,
  isVisible: boolean,
  repository: Object,
}

const ShareModal = ({
  environment,
  handleClose,
  isVisible,
  repository,
}: Props) => {
  if (isVisible) {
    const urlOrigin = window.location.origin;
    const [devtool, setDevtool] = useState('none');
    const [codeFile, setCodeFile] = useState(null);

    /**
    * Method provides a way for child componts to update state
    * @param {string} newCodeFile
    * @fires updateCodeFileUrl
    */
    const updateCodeFileUrl = (newCodeFile) => {
      setCodeFile(newCodeFile);
    };

    /**
    * Method provides a way for child componts to update state
    * @param {string} newDevtool
    * @fires updateDevtoolUrl
    */
    const updateDevtoolUrl = (newDevtool) => {
      setDevtool(newDevtool);
    };

    return (
      <Modal
        handleClose={handleClose}
        header="Share Link"
        icon="share"
        overflow="visible"
        size="large"
      >
        <p>Create a share link to automatically import and open this Project. You can also automatically start a tool and even open a notebook in Jupyterlab.  </p>
        <p><b><i>Note, this link is specific to this Client instance and will create a unique copy in a user's workspace.</i></b></p>
        <ShareUrlInput
          urlOrigin={urlOrigin}
          codeFile={codeFile}
          devtool={devtool}
          repository={repository}
        />

        <ShareForm
          environment={environment}
          devtool={devtool}
          repository={repository}
          setCodeFile={setCodeFile}
          setDevtool={setDevtool}
          updateCodeFileUrl={updateCodeFileUrl}
          updateDevtoolUrl={updateDevtoolUrl}
        />
      </Modal>
    );
  }

  return null;
};


export default ShareModal;
