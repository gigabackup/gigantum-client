// @flow
// vendor
import React, { useState } from 'react';
// conetxt
import RepositoryContext from 'Pages/repository/RepositoryContext';
// environment
import environment from 'JS/createRelayEnvironment';
// components
import ShareModal from './modal/ShareModal';
// css
import './ShareLink.scss';

type Props = {
  name: string,
  owner: string,
  repository: Object,
}


const ShareLink = ({
  name,
  owner,
  repository,
}: Props) => {
  const [isVisible, setIsVisible] = useState(false);

  const handleClose = (evt) => {
    evt.stopPropagation();
    setIsVisible(false);
  };
  return (
    <li
      className="ActionsMenu__item ShareLink"
      onClick={() => setIsVisible(true)}
      role="presentation"
    >
      <button
        className="ActionsMenu__btn--flat"
      >
        Share Link
      </button>

      <span
        className="Tooltip-data Tooltip-data--info Toolip-data--action"
        data-tooltip="Get a link to open or run this project."
      />
      <ShareModal
        environment={environment}
        handleClose={handleClose}
        isVisible={isVisible}
        name={name}
        owner={owner}
        repository={repository}
      />
    </li>
  );
};

const ShareLinkWrapper = () => (
  <RepositoryContext.Consumer>
    {
      value => (
        <ShareLink repository={value} />
      )
    }
  </RepositoryContext.Consumer>
);


export default ShareLinkWrapper;
