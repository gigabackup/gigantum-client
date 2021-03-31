// vendor
import React from 'react';
import { storiesOf } from '@storybook/react';
import { mount } from 'enzyme';
import {
  createMockEnvironment,
  MockPayloadGenerator,
} from 'relay-test-utils';
// context
import ServerContext from 'Pages/ServerContext';
import RepositoryContext from 'Pages/repository/RepositoryContext';
// resolver
import mockResolver from '../__resolver__/MockResolver';
// css
import 'Styles/critical.scss';
// components
import ShareLink from '../ShareLink';


const environment = createMockEnvironment();
environment.mock.queueOperationResolver(operation => MockPayloadGenerator.generate(
  operation,
  mockResolver,
));

const mainProps = {
  currentServer: {
    baseUrl: 'gigantum.com',
    name: 'gigantum',
    id: 'id_here',
  },
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
};

const ShareLinkWrapped = () => (
  <ServerContext.Provider value={mainProps}>
    <RepositoryContext.Provider value={mainProps.repository}>
      <ShareLink {...mainProps} environment={environment} />
    </RepositoryContext.Provider>
  </ServerContext.Provider>
);


storiesOf('Header/ShareLink/ShareLink', module)
  .addParameters({
    jest: ['ShareLink'],
  })
  .add('ShareLink Default', () => <ShareLinkWrapped />);

describe('ShareLink Unit Tests:', () => {
  const output = mount(<ShareLinkWrapped />);

  test('ShareLink loads', () => {
    const section = output.find('.ShareLink');
    expect(section).toHaveLength(1);
  });
});
