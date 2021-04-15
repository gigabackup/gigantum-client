// vendor
import React, { PureComponent } from 'react';
import { detect } from 'detect-browser';
// component
import Modal from 'Components/modal/Modal';
// assets
import firefoxSrc from 'Images/logos/Firefox-popup.png';
import chromeSrc from 'Images/logos/Chrome-popup.png';
import safariSrc from 'Images/logos/safari-popup.png';
// css
import './PopupBlocked.scss';

const getIcon = (browserName) => {
  if (browserName === 'firefox') {
    return firefoxSrc;
  }
  if (browserName === 'safari') {
    return safariSrc;
  }
  return chromeSrc;
};

type Props = {
  attemptRelaunch: Function,
  devTool: String,
  hideCancel: boolean,
  isVisible: boolean,
  togglePopupModal: Function,
}

class PopupBlocked extends PureComponent<Props> {
  render() {
    const {
      attemptRelaunch,
      devTool,
      hideCancel,
      isVisible,
      togglePopupModal,
    } = this.props;

    const browser = detect();

    if (!browser || !isVisible) {
      return null;
    }
    const icon = getIcon(browser.name);

    return (
      <Modal
        handleClose={() => togglePopupModal()}
        size="large-full"
      >
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
          <img
            alt="browser"
            src={icon}
            className="PopupBlocked__image"
          />
          <div className="PopupBlocked__buttonContainer flex justify--right">
            {
              !hideCancel
              && (
                <button
                  className="Btn Btn--flat"
                  onClick={() => { togglePopupModal(); }}
                  type="button"
                >
                  Cancel
                </button>
              )
            }
            <button
              className="Btn Btn--inverted Btn--popup-blocked"
              onClick={attemptRelaunch}
              type="button"
            >
              Launch Again
            </button>
          </div>
        </div>
      </Modal>
    );
  }
}

export default PopupBlocked;
