// @flow
// vendor
import React from 'react';


type Props = {
  filteredBranches: Array,
  modalVisible: Boolean,
  setModalVisible: Function
}

const NoOtherBranches = ({
  filteredBranches,
  modalVisible,
  setModalVisible,
}:Props) => {
  if (filteredBranches.length === 0) {
    return (
      <>
        <li
          className="BranchMenu__list-item BranchMenu__list-item--create"
          onClick={() => setModalVisible(!modalVisible)}
          role="presentation"
        >
          No other branches.
          <button
            type="button"
            className="Btn--flat"
          >
            Create a new branch?
          </button>
        </li>

      </>
    );
  }

  return null;
};

export default NoOtherBranches;
