// @flow
// vendor
import React, { useState } from 'react';
import classNames from 'classnames';
// context
import ServerContext from 'Pages/ServerContext';
// css
import './ShareUrlInput.scss';


type Props = {
  codeFile: string,
  currentServer: {
    baseUrl: string,
  },
  devtool: string,
  repository: {
    name: string,
    owner: string,
  },
  urlOrigin: string,
}

const ShareUrlInput = ({
  codeFile,
  currentServer,
  devtool,
  repository,
  urlOrigin,
}: Props) => {
  // props
  const { name, owner } = repository;
  const { baseUrl } = currentServer;
  // state
  const [isTooltipVisible, setTooltipVisible] = useState(false);
  // other variables
  const filePathUrl = (codeFile !== null) && (codeFile !== 'code/') ? `&filePath=${codeFile}` : '';
  const devtoolUrl = (devtool !== null) && (devtool !== 'none') ? `&devtool=${devtool}` : '';
  const value = `${urlOrigin}/projects/${owner}/${name}/#autoImport=true&baseUrl=${baseUrl}${devtoolUrl}${filePathUrl}`;

  // css
  const copyButtonCSS = classNames({
    'ShareUrlInput__button ShareUrlInput__button--copy fa fa-clone': true,
    'Tooltip-data': isTooltipVisible,
  });

  // functions
  /**
  * Method copies link to clipboard and shows a tooltip notifying the user that link was copied
  * @fires setTooltipVisible
  * @return {}
  */
  const copyUrl = () => {
    setTooltipVisible(true);
    document.getElementById('ShareUrlInput__textarea').select();
    document.execCommand('copy');

    setTimeout(() => {
      setTooltipVisible(false);
    }, 3000);
  };

  return (
    <div className="ShareUrlInput relative">
      <textarea
        className="ShareUrlInput__textarea"
        id="ShareUrlInput__textarea"
        onChange={() => {}}
        type="text"
        value={value}
      />
      <button
        className={copyButtonCSS}
        data-tooltip="Copied to clipboard!"
        onClick={() => { copyUrl(); }}
        type="button"
      />
    </div>
  );
};


const ShareInputUrlWrapper = (props) => (
  <ServerContext.Consumer>
    { value => (
      <ShareUrlInput
        {...props}
        currentServer={value.currentServer}
      />
    )}
  </ServerContext.Consumer>
);


export default ShareInputUrlWrapper;
