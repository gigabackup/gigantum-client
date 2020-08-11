// vendor
import React, { PureComponent, Fragment } from 'react';
import { detect } from 'detect-browser';
// component
import Modal from 'Components/common/Modal';
// assets
import firefoxSrc from 'Images/logos/Firefox-popup.png';
import chromeSrc from 'Images/logos/Chrome-popup.png';
import './PopupBlocked.scss';

type Props = {
  attemptRelaunch: Function,
  devTool: String,
  togglePopupModal: Function,
}

class PopupBlocked extends PureComponent<Props> {
  render() {
    const {
      togglePopupModal,
      devTool,
      attemptRelaunch,
    } = this.props;

    const browser = detect();
    const isChrome = browser.name === ('chrome');

    const icon = isChrome ? chromeSrc : firefoxSrc;

    return (
      <Modal
        handleClose={() => togglePopupModal()}
        size="large-full"
        renderContent={() => (
          <div className="PopupBlocked flex flex--column align-items--center">
            <div className="PopupBlocked__header">
              <h2 className="PopupBlocked__header-text">Pop-up Blocked</h2>
            </div>
            <div className="PopupBlocked__message">
              <p>
                Gigantum opens
                {` ${devTool} `}
                in a new tab, which was blocked by your browser.
              </p>
              <p>
                Please modify your browser settings to allow pop-ups, as shown below.
              </p>
            </div>
            {
              isChrome
              && (
                <img
                  alt="browser"
                  width="362"
                  height="225"
                  src={chromeSrc}
                />
              )
            }
            <img
              alt="firefox"
              width="362"
              height="225"
              src={icon}
            />
            <div className="PopupBlocked__buttonContainer flex justify--right">
              <button
                className="Btn Btn--flat"
                onClick={() => { togglePopupModal(); }}
                type="button"
              >
                Cancel
              </button>
              <button
                className="Btn Btn--inverted Btn--popup-blocked"
                onClick={attemptRelaunch}
                type="button"
              >
                Launch Again
              </button>
            </div>
          </div>
        )
        }
      />
    );
  }
}

export default PopupBlocked;
