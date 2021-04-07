// @flow
// vendor
import React, {
  useCallback,
  useEffect,
  useState,
} from 'react';
// custom hooks
import {
  useEventListener,
} from 'Hooks/hooks';
// components
import AutoCompleteItem from './item/AutoCompleteItem';
// css
import './AutoComplete.scss';

type Props = {
  autoCompleteOpen: Boolean,
  inputValue: string,
  list: Array,
  repository: {
    name: string,
    owner: string,
  },
  overIndex: Number,
  updateAutoCompleteOpen: Function,
  updateFilePath: Function,
};


const AutoComplete = ({
  autoCompleteOpen,
  inputValue,
  list,
  overIndex,
  updateFilePath,
  updateAutoCompleteOpen,
}: Props) => {
  // state
  const [obeservedInputValue, updateObservedInputValue] = useState(inputValue);

  /**
  * Method handles window click to close autocomplete
  * @param {Object} evt
  * @fires updateAutoCompleteOpen
  * @return {}
  */
  const handler = useCallback(
    (evt) => {
      updateAutoCompleteOpen(false);
    },
    [],
  );
  // hooks
  useEffect(() => {
    if (inputValue !== obeservedInputValue) {
      updateObservedInputValue(inputValue);
      updateAutoCompleteOpen(true);
    }
  });
  // Add event listener using our hook
  useEventListener('click', handler);

  if ((list.length > 0) && (autoCompleteOpen)) {
    return (
      <div className="AutoComplete absolute">
        <ul>
          {
            list.map((edge, index) => (
              <AutoCompleteItem
                edge={edge}
                index={index}
                overIndex={overIndex}
                updateFilePath={updateFilePath}
              />
            ))
          }
        </ul>
      </div>
    );
  }

  return null;
};

export default AutoComplete;
