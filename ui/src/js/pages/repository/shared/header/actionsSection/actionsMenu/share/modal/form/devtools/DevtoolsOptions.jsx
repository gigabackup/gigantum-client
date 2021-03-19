// @flow
// vendor
import React, { useState } from 'react';
// components
import Dropdown from 'Components/dropdown/Dropdown';

type Props = {
  repository: {
    environment: {
      base: {
        developmentTools: Array,
      }
    }
  },
}

const DevtoolsOptions = ({
  repository,
}: Props) => {
  console.log(repository);
  const { developmentTools } = repository.environment.base;
  const [devtools, setSelectedDevtools] = useState(developmentTools);
  const [dropdownVisible, setDropdownVisible] = useState(false);
  console.log(devtools, dropdownVisible);
  return (
    <div className="DevtoolsOptions">
      <Dropdown
        itemAction={setSelectedDevtools}
        label="Development Tools"
        listAction={() => setDropdownVisible(!devtools)}
        listItems={devtools}
        visibility={dropdownVisible}
      />
    </div>
  );
};


export default DevtoolsOptions;
