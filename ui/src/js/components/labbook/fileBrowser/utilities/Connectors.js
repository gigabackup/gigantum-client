import React from 'react';
import { DragSource } from 'react-dnd';
import uuidv4 from 'uuid/v4';
import FileBrowserMutations from './FileBrowserMutations';
// utilities
import CreateFiles from './../utilities/CreateFiles';
// store
import store from 'JS/redux/store';

const dragSource = {

 canDrag(props) {
   // You can disallow drag based on props
   return true;
 },

 isDragging(props, monitor) {
    return monitor.getItem().key === props.key;
 },

 beginDrag(props, monitor) {
  return {
    isDragging: true,
    data: props.data,
  };
 },

  endDrag(props, monitor, component) {
    if (!monitor.didDrop()) {
      return;
    }

    const item = monitor.getItem();
    const dropResult = monitor.getDropResult();

    let fileNameParts = props.data.edge.node.key.split('/');

    let fileName = fileNameParts[fileNameParts.length - 1];
    if (dropResult.data) {
      let pathArray = dropResult.data.edge.node.key.split('/');
      pathArray.pop();
      let path = pathArray.join('/');

      let newKey = path ? `${path}/${fileName}` : `${fileName}`;

      let newKeyArray = dropResult.data.edge.node.key.split('/');
      let fileKeyArray = props.data.edge.node.key.split('/');

      newKeyArray.pop();
      fileKeyArray.pop();

      let newKeyPath = newKeyArray.join('/');
      let fileKeyPath = fileKeyArray.join('/');
      newKeyPath = newKeyPath.replace(/\/\/\/g/, '/');
      const trimmedFilePath = fileKeyPath.split('/').slice(0, -1).join('/');

      if ((newKeyPath !== fileKeyPath) && (trimmedFilePath !== newKeyPath)) {
        if (newKey !== props.data.edge.node.key) {
          const moveLabbookFileData = {
            newKey,
            edge: props.data.edge,
          };

          if (props.mutations) {
            props.mutations.moveLabbookFile(moveLabbookFileData, (response) => {});
          } else {
            const {
              parentId,
              connection,
              favoriteConnection,
              section,
            } = props;
            const { owner, labbookName } = store.getState().routes;

            const mutationData = {
              owner,
              labbookName,
              parentId,
              connection,
              favoriteConnection,
              section,
            };

            const mutations = new FileBrowserMutations(mutationData);

            mutations.moveLabbookFile(moveLabbookFileData, (response) => {});
          }
        }
      }
    }
  },
};

function dragCollect(connect, monitor) {
  return {
    connectDragPreview: connect.dragPreview(),
    connectDragSource: connect.dragSource(),
    isDragging: monitor.sourceId === monitor.getSourceId(),
  };
}

const uploadDirContent = (dndItem, props, mutationData) => {
  let path;
  dndItem.dirContent.then((fileList) => {
      if (fileList.length) {
        let key = props.data ? props.data.edge.node.key : props.fileKey ? props.fileKey : '';
        path = key === '' ? '' : key.substr(0, key.lastIndexOf('/') || key.length);
        CreateFiles.createFiles(fileList.flat(), `${path}/`, mutationData);
      } else if (dndItem.files && dndItem.files.length) {
           // handle dragged files
           let key = props.newKey || props.fileKey;
           path = key.substr(0, key.lastIndexOf('/') || key.length);
           let item = monitor.getItem();

           if (item && item.files && props.browserProps.createFiles) {
             CreateFiles.createFiles(item.files, `${path}/`, mutationData);
           }
           newPath = null;
           fileKey = null;
      }
  });
};

const targetSource = {
  canDrop(props, monitor) {
     // You can disallow drop based on props or item
     const item = monitor.getItem();
     return monitor.isOver({ shallow: true });
  },
  drop(props, monitor, component) {
    const dndItem = monitor.getItem();

    let newPath,
        fileKey,
        path,
        files;
    if (dndItem && props.data) {
          if (!dndItem.dirContent) {
              fileKey = props.data.edge.node.key;

              const fileNameParts = fileKey.split('/');
              const fileName = fileNameParts[fileNameParts.length - 1];
              let newKey = props.newKey || props.fileKey;
              newPath = newKey + fileName;
              fileKey = props.fileKey;
          } else {
              uploadDirContent(dndItem, props, props.mutationData);
          }
      } else {
          const {
            parentId,
            connection,
            favoriteConnection,
            section,
          } = props;
          const { owner, labbookName } = store.getState().routes;

          const mutationData = {
            owner,
            labbookName,
            parentId,
            connection,
            favoriteConnection,
            section,
          };
          // uploads to root directory
          let item = monitor.getItem();
          if (item.files) {
            if (dndItem.dirContent) {
               uploadDirContent(dndItem, props, mutationData);
            } else {
              CreateFiles.createFiles(item.files, '', component.state.mutationData);
            }
          } else {
            const dropResult = monitor.getDropResult();

            if (dropResult) {
              let currentKey = item.data.edge.node.key;
              let splitKey = currentKey.split('/');
              let newKeyTemp = (splitKey[splitKey.length - 1] !== '') ? splitKey[splitKey.length - 1] : splitKey[splitKey.length - 2];
              let splitFolder = dropResult.data ? dropResult.data.edge.node.key.split('/') : '';
              if (splitFolder !== '') {
                splitFolder.pop();
              }

              let dropFolderKey = splitFolder.join('/');

              let newKey = item.data && item.data.edge.node.isDir ? `${dropFolderKey}/${newKeyTemp}/` : `${dropFolderKey}/${newKeyTemp}`;
              newKey = dropResult.data ? newKey : `${newKeyTemp}`;

              if ((newKey !== item.data.edge.node.key)) {
                const moveLabbookFileData = {
                  newKey,
                  edge: item.data.edge,
                };

                if (props.mutations) {
                  props.mutations.moveLabbookFile(moveLabbookFileData, (response) => {});
                } else {
                  const {
                    parentId,
                    connection,
                    favoriteConnection,
                    section,
                  } = props;
                  const { owner, labbookName } = store.getState().routes;

                  const mutationData = {
                    owner,
                    labbookName,
                    parentId,
                    connection,
                    favoriteConnection,
                    section,
                  };

                  const mutations = new FileBrowserMutations(mutationData);

                  mutations.moveLabbookFile(moveLabbookFileData, (response) => {});
                }
              }
            }
          }
      }

      return {
       data: props.data,
      };
  },
};

function targetCollect(connect, monitor) {
  let currentTargetId = monitor.targetId;
  let isOverCurrent = monitor.isOver({ shallow: true });
  let isOver = monitor.isOver({});
  let currentTarget = monitor.internalMonitor.registry.dropTargets.get(currentTargetId);
  let canDrop = monitor.canDrop();
  let newLastTarget;

  let targetIds = monitor.internalMonitor.getTargetIds();

  let targets = targetIds.map(id => monitor.internalMonitor.registry.dropTargets.get(id));
  if (targets.length > 0) {
    let lastTarget = targets[targets.length - 1];
    if (lastTarget.props.data && !lastTarget.props.data.edge.node.isDir) {
      targets.pop();
    }
    newLastTarget = targets[targets.length - 1];
    isOver = (currentTargetId === newLastTarget.monitor.targetId);
  } else {
    isOver = false;
  }

  let dragItem;
  monitor.internalMonitor.registry.dragSources.forEach((item) => {
    if (item.ref && item.ref.current && item.ref.current.props.isDragging) {
      dragItem = item.ref.current;
    }
  });

  if (dragItem && newLastTarget) {
    let dragKeyArray = dragItem.props.data.edge.node.key.split('/');
    dragKeyArray.pop();

    let dragKeyPruned = dragKeyArray.join('/') === '' ? '' : `${dragKeyArray.join('/')}/`;

    let dropKey = newLastTarget.props.files ? '' : newLastTarget.props.data.edge.node.key;
    canDrop = (dragKeyPruned !== dropKey);
    isOver = isOver && canDrop;
  }
  return {
    connectDropTarget: connect.dropTarget(),
		canDrop,
    isOver,
    isOverCurrent,
  };
}

const Connectors = {
  dragSource,
  dragCollect,
  targetSource,
  targetCollect,
};

export default Connectors;
