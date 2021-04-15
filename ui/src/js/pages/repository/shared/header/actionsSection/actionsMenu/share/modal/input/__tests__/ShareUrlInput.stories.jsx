// vendor
import React from 'react';
import { storiesOf } from '@storybook/react';
import { mount } from 'enzyme';

// context
import ServerContext from 'Pages/ServerContext';
// css
import 'Styles/critical.scss';
// components
import ShareUrlInput from '../ShareUrlInput';


const mainProps = {
  codeFile: 'code/batch.ipynb',
  currentServer: {
    baseUrl: 'gigantum.com',
    name: 'gigantum',
    id: 'id_here',
  },
  devTool: 'jupyterLab',
  repository: {
    name: 'projectname',
    owner: 'ownername',
    environment: {
      base: {
        developmentTools: ['jupyterLab', 'notebook'],
      },
      bundledApps: [{
        name: 'tensor-brd',
      }],
    },
  },
  labbook: {
    code: {
      allFiles: [
        {
          node: {
            key: 'code/Batch.ipynb',
          },
        },
        {
          node: {
            key: 'code/Match.ipynb',
          },
        },
        {
          node: {
            key: 'code/Clean.ipynb',
          },
        },
      ],
    },
  },
  urlOrigin: 'gigantum.com',
};

const ShareUrlInputWrapped = () => (
  <ServerContext.Provider value={mainProps}>
    <ShareUrlInput {...mainProps} />
  </ServerContext.Provider>
);


storiesOf('Header/ShareLink/ShareUrlInput', module)
  .addParameters({
    jest: ['ShareUrlInput'],
  })
  .add('ShareUrlInput Default', () => <ShareUrlInputWrapped />);

describe('ShareUrlInput Unit Tests:', () => {
  const output = mount(<ShareUrlInputWrapped />);

  test('ShareUrlInput loads', () => {
    const section = output.find('.ShareUrlInput');
    expect(section).toHaveLength(1);
  });
});
