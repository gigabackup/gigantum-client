// @flow
// vendor
import React, { useState, useEffect } from 'react';
import { createFragmentContainer, graphql } from 'react-relay';
// components
import AutoComplete from './auto/AutoComplete';
// css
import './ShareFileInput.scss';

type Props = {
  devtool: string,
  labbook: {
    code: Object,
  },
  updateCodeFileUrl: Function,
};

/**
* Method finds the true modulus for a number
* @param {Number} number
* @param {Number} modulus
* @return {Number}
*/
const mod = (number, modulus) => {
  const remain = number % modulus;

  if (modulus === 0) return 0;

  return Math.floor(remain >= 0 ? remain : remain + modulus);
};

/**
* Method filters files by matching the input value
* @param {Array<Object>} allFiles
* @param {String} inputValue
* @return {Array<Object>}
*/
const filterList = (allFiles, inputValue) => {
  if (inputValue.length > 2) {
    const filteredFiles = allFiles.edges.filter((edge) => {
      const keyLowerCase = edge.node.key.toLowerCase();
      const inputLowerCase = inputValue.toLowerCase();
      if ((keyLowerCase.indexOf(inputLowerCase) > -1) && !edge.node.isDir) {
        return true;
      }
      return false;
    });
    return filteredFiles;
  }
  return [];
};

const ShareFileInput = ({
  devtool,
  labbook,
  updateCodeFileUrl,
}: Props) => {
  if (labbook && labbook.code) {
    // props
    const { code } = labbook;
    const { allFiles } = code;
    // state
    const [autoCompleteOpen, updateAutoCompleteOpen] = useState(true);
    const [autoCompleteIndex, updateAutoCompleteIndex] = useState(0);
    const [filePath, updateFilePath] = useState('');
    // vars
    const isInputDisabled = (devtool !== 'jupyterlab');
    const list = filterList(allFiles, filePath);
    // functions
    /**
    * Method updates file path from auto complete selection
    * @param {String} value
    * @fires updateFilePath
    * @fires updateCodeFileUrl
    */
    const updateFilePathState = (value) => {
      updateFilePath(value);
      updateCodeFileUrl(`code/${value}`);
    };

    /**
    * Method updates file path from event
    * @param {String} value
    * @fires updateFilePath
    * @fires updateCodeFileUrl
    */
    const updateFile = (evt) => {
      if (evt.target.value.length >= 0) {
        updateFilePath(evt.target.value);
        updateCodeFileUrl(`code/${evt.target.value}`);
      }
    };

    /**
    * Method handles window click to close autocomplete
    * @param {Object} evt
    * @fires updateAutoCompleteOpen
    * @return {}
    */
    const keyPressHandler = (evt) => {
      if (evt.key === 'ArrowDown') {
        const index = mod((autoCompleteIndex + 1), list.length);
        updateAutoCompleteIndex(index);
      }

      if (evt.key === 'ArrowUp') {
        const index = mod((autoCompleteIndex - 1), list.length);
        updateAutoCompleteIndex(index);
      }

      if (evt.key === 'Enter') {
        updateFilePathState(list[autoCompleteIndex].node.key);
        setTimeout(() => {
          updateAutoCompleteOpen(false);
        }, 100);
      }
    };

    // hooks
    useEffect(() => {
      if (isInputDisabled) {
        updateFilePathState('');
      }
    });

    return (
      <div
        className="ShareFileInput relative"
      >
        <h6 className="ShareFileInput__h6 relative">
          File Path
          <span
            className="Tooltip-data Tooltip-data--info"
            data-tooltip="The specified file will automically be opened. (Only available in JupyterLab)"
          />
        </h6>
        <div className="relative">
          <input
            className="ShareFileInput__input-text"
            disabled={isInputDisabled}
            onChange={updateFile}
            onKeyDown={(evt) => { keyPressHandler(evt); }}
            type="text"
            value={filePath}
          />
          <div className="ShareFileInput__overlay absolute">
            <p className="ShareFileInput__p">code/</p>
          </div>
        </div>

        <AutoComplete
          autoCompleteOpen={autoCompleteOpen}
          inputValue={filePath}
          list={list}
          overIndex={autoCompleteIndex}
          updateAutoCompleteOpen={updateAutoCompleteOpen}
          updateFilePath={updateFilePathState}
        />
      </div>
    );
  }

  return null;
};


export default createFragmentContainer(
  ShareFileInput,
  {
    labbook: graphql`
      fragment ShareFileInput_labbook on Labbook {
        code {
          id
          hasFiles
          allFiles(after: $cursor, first: $first) {
            edges{
              node{
                id
                isDir
                modifiedAt
                key
                size
              }
              cursor
            }
            pageInfo{
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }
          }
        }
      }
    `,
  },
);
