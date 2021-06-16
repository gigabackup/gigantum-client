// @flow
// vendor
import React, { useState } from 'react';
import classNames from 'classnames';
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
  // declare STATE
  const [isVisible, setIsVisible] = useState(false);
  // declare VARS
  const isPublished = repository.defaultRemote !== null;
  const tooltipText = isPublished
    ? 'Get a link to open or run this project.'
    : 'Project has not been published. Publish the project to enable share links.';

  // declare css here
  const shareLinkCSS = classNames({
    'ActionsMenu__item ShareLink': true,
    'ShareLink--disabled': !isPublished,
  });

  // declare event functions here

  /**
  * Method handles click for closing and stops stops propagation to prevent odd closing behaviour
  * @param {Object} evt
  * @fires #evt.stopPropagation();
  * @fires #setIsVisible
  */
  const handleClose = (evt) => {
    evt.stopPropagation();
    setIsVisible(false);
  };

  /**
  * Method handles opening of share link modal on the condition that the project is published
  * @param {}
  * @fires #setIsVisible
  */
  const handleOpen = () => {
    if (isPublished) {
      setIsVisible(true);
    }
  };

  return (
    <li
      className={shareLinkCSS}
      onClick={() => handleOpen()}
      role="presentation"
    >
      <button
        className="ActionsMenu__btn--flat"
        disabled={!isPublished}
        type="button"
      >
        Share Link
      </button>

      <span
        className="Tooltip-data Tooltip-data--info Toolip-data--action Tooltip-data--top-offset"
        data-tooltip={tooltipText}
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
