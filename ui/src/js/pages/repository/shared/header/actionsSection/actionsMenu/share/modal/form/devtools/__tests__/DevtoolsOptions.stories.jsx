// vendor
import React from 'react';
import { storiesOf } from '@storybook/react';
import { mount } from 'enzyme';
// css
import 'Styles/critical.scss';
// components
import DevtoolsOptions from '../DevtoolsOptions';


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
  updateDevtoolUrl: jest.fn(),
};

const DevtoolsOptionsWrapped = () => (
  <DevtoolsOptions {...mainProps} />
);


storiesOf('Header/ShareLink/form/DevtoolsOptions', module)
  .addParameters({
    jest: ['DevtoolsOptions'],
  })
  .add('DevtoolsOptions Default', () => <DevtoolsOptionsWrapped />);

describe('DevtoolsOptions Unit Tests:', () => {
  const output = mount(<DevtoolsOptionsWrapped />);

  test('DevtoolsOptions loads', () => {
    const section = output.find('.DevtoolsOptions');
    expect(section).toHaveLength(1);
  });
});
