// vendor
import React from 'react';
import { storiesOf } from '@storybook/react';
import { mount } from 'enzyme';
import path from 'path';
import { DragDropContext } from 'react-dnd';
import HTML5Backend from 'react-dnd-html5-backend';
// css
import 'Styles/critical.scss';
// components
import File from '../File';
// data
import fileBrowserData from '../../../__mock__/fileBrowser.json';

const edge = fileBrowserData.data.labbook.code.allFiles.edges[1];
const filename = path.basename(edge.node.key);
const file = {
  edge,
};

const backend = (manager: Object) => {
  const backend = HTML5Backend(manager),
      orgTopDropCapture = backend.handleTopDropCapture;

  backend.handleTopDropCapture = (e) => {
      if (backend.currentNativeSource) {
        orgTopDropCapture.call(backend, e);
      }
  };

  return backend;
};

const mutationData = {
  owner: 'uitest',
  labbookName: 'ui-test-project',
  section: 'code',
  connection: 'CodeBrowser_allFiles',
  favoriteConnection: 'CodeFavorite_favorites',
  parentId: fileBrowserData.data.labbook.id,
};

const mainProps = {
  connectDragSource: jsx => jsx,
  closeLinkModal: () => {},
  setState: () => {},
  updateChildState: () => {},
  codeDirUpload: () => {},
  isSelected: true,
  filename,
  key: file.edge.node.key,
  multiSelect: false,
  mutationData,
  fileData: file,
  mutations: {
    moveLabbookFile: () => {},
  },
  sort: 'all',
  reverse: true,
  childrenState: {},
  section: 'code',
  isDragging: false,
};

const Filecomponent = () => <File {...mainProps} />;
const FileWrapped = DragDropContext(backend)(Filecomponent);

storiesOf('FileBrowser/File Snapshots:', module)
  .addParameters({
    jest: ['File'],
  })
  .add('File Default', () => {
    return <FileWrapped />;
  });
