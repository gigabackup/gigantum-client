// @flow
// vendor
import React from 'react';


type Props = {
  currentServer: {
    backupInProgress: boolean,
  },
  edge: {
    node: {
      name: string,
      owner: string,
    }
  },
  existsLocally: boolean,
  importRepository: Function,
  isImporting: boolean,
}

const ImportButton = ({
  currentServer,
  edge,
  existsLocally,
  importRepository,
  isImporting,
}: Props) => {
  if (existsLocally) {
    return (
      <button
        type="button"
        className="Btn__dashboard Btn--action Btn__dashboard--cloud Btn__Tooltip-data"
        data-tooltip="This Project has already been imported"
        disabled
      >
        Imported
      </button>
    );
  }
  return (
    <button
      type="button"
      disabled={isImporting || currentServer.backupInProgress}
      className="Btn__dashboard Btn--action Btn__dashboard--cloud-download"
      onClick={() => importRepository(edge.node.owner, edge.node.name)}
    >
      Import
    </button>
  );
};


export default ImportButton;
