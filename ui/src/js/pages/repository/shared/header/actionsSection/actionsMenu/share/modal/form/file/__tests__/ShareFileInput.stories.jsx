// vendor
import React from 'react';
import { QueryRenderer } from 'react-relay';
import { storiesOf } from '@storybook/react';
import { mount } from 'enzyme';
import {
  createMockEnvironment,
  MockPayloadGenerator,
} from 'relay-test-utils';
// css
import 'Styles/critical.scss';
// query
import { shareFormQuery } from '../../ShareForm';
// resolver
import mockResolver from '../../../../__resolver__/MockResolver';
// components
import ShareFileInput from '../ShareFileInput';


const mainProps = {
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
  updateCodeFileUrl: () => {},
  updateDevtoolUrl: () => {},
};


const renderStory = ({ devtool, environment }) => (
  <QueryRenderer
    environment={environment}
    query={shareFormQuery}
    variables={{
      cursor: null,
      first: 100,
      name: 'projectname',
      owner: 'ownername',
      force: true,
    }}
    render={({ error, props }) => {
      if (props) {
        return (
          <ShareFileInput
            {...mainProps}
            {...props}
            devtool={devtool}
            environment={environment}
          />
        );
      }

      if (error) {
        return <div>error</div>;
      }
      return <div>Loading...</div>;
    }}
  />
);


storiesOf('Header/ShareLink/ShareFileInput', module)
  .addParameters({
    jest: ['ShareFileInput'],
  })
  .add('ShareFileInput Disabled', () => {
    const environment = createMockEnvironment();
    environment.mock.queueOperationResolver(operation => MockPayloadGenerator.generate(
      operation,
      mockResolver,
    ));
    return (renderStory({ devtool: null, environment }));
  })
  .add('ShareFileInput jupyterLab', () => {
    const environment = createMockEnvironment();
    environment.mock.queueOperationResolver(operation => MockPayloadGenerator.generate(
      operation,
      mockResolver,
    ));
    return renderStory({ devtool: 'jupyterlab', environment });
  });

describe('ShareFileInput Unit Tests:', () => {
  const environment = createMockEnvironment();
  environment.mock.queueOperationResolver(operation => MockPayloadGenerator.generate(
    operation,
    mockResolver,
  ));
  const output = mount(renderStory({ devtool: 'jupyterlab', environment }));
  test('ShareFileInput loads', () => {
    const section = output.text('.ShareFileInput');
    expect(section).toEqual('Loading...');
  });
});
