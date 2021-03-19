// @flow
// vendor
import React from 'react';
// components
import Modal from 'Components/modal/Modal';
import ShareUrlInput from './input/ShareUrlInput';
import ShareForm from './form/ShareForm';
// css
import './ShareModal.scss';

type Props = {
  handleClose: Function,
  isVisible: boolean,
  repository: Object,
}

const ShareModal = ({
  handleClose,
  isVisible,
  repository,
}: Props) => {
  if (isVisible) {
    const baseUrl = window.location.origin;
    return (
      <Modal
        header="Share Link"
        handleClose={handleClose}
        size="large"
      >
        <ShareUrlInput
          baseUrl={baseUrl}
          repository={repository}
        />

        <ShareForm
          repository={repository}
        />
      </Modal>
    );
  }

  return null;
};


export default ShareModal;
