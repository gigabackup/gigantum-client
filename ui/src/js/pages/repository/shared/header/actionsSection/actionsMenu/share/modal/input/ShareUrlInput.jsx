// @flow
// vendor
import React from 'react';
// css
import './ShareUrlInput.scss';


type Props = {
  baseUrl: string,
}

const ShareUrlInput = ({
  baseUrl,
}: Props) => {
  const value = baseUrl;
  return (
    <div className="ShareUrlInput">
      <input
        type="text"
        value={value}
      />
      <button
        type="button"
      >
        Copy
      </button>
    </div>
  );
};


export default ShareUrlInput;
