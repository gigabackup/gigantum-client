// vendor
import React from 'react';
import { storiesOf } from '@storybook/react';
import { mount } from 'enzyme';
// css
import 'Styles/critical.scss';
// components
import ImportError from '../ImportError';


const props = {
  devTool: 'jarpyter',
  isVisible: true,
  openProject: jest.fn,
  toggleDevtoolFailedModal: jest.fn,
};

storiesOf('Pages/importing/ImportError', module)
  .addParameters({
    jest: ['ImportError'],
  })
  .add('ImportError Default', () => <ImportError {...props} />);

describe('ImportError Unit Tests:', () => {
  const output = mount(<ImportError {...props} />);

  test('ImportError loads', () => {
    const section = output.find('.ImportError');
    expect(section).toHaveLength(1);
  });
});
