// vendor
import React from 'react';
import { storiesOf } from '@storybook/react';
import { mount } from 'enzyme';
// css
import 'Styles/critical.scss';
// components
import Importing from '../Importing';


const props = {
  currentServer: {
    currentServer: {
      baseUrl: 'gigantum.com',
      serverId: 'gigantum-com',
    },
  },
  transition: jest.fn,
};

storiesOf('Pages/importing/Importing', module)
  .addParameters({
    jest: ['ImportError'],
  })
  .add('ImportError Default', () => <Importing {...props} />);

describe('ImportError Unit Tests:', () => {
  const output = mount(<Importing {...props} />);

  test('ImportError loads', () => {
    const section = output.find('.Importing');
    expect(section).toHaveLength(1);
  });
});
