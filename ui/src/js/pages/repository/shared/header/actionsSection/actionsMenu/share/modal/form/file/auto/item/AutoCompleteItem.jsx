// @flow
// vendor
import React from 'react';
import classNames from 'classnames';


type Props = {
  edge: {
    node: {
      key: string,
    }
  },
  index: Number,
  overIndex: Number,
  updateFilePath: Function,
}


const AutomCompleteItem = ({
  edge,
  index,
  overIndex,
  updateFilePath,
}: Props) => {
  // css
  const itemCSS = classNames({
    AutoComplete__li: true,
    'AutoComplete__li--highlighted': index === overIndex,
  });
  return (
    <li
      className={itemCSS}
      onClick={() => updateFilePath(edge.node.key)}
      role="presentation"
    >
      {edge.node.key}
    </li>
  );
};


export default AutomCompleteItem;
