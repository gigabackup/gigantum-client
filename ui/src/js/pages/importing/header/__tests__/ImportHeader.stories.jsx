// vendor
import React from 'react';
import { storiesOf } from '@storybook/react';
import { mount } from 'enzyme';
// css
import 'Styles/critical.scss';
// components
import ImportHeader from '../ImportHeader';

storiesOf('Pages/importing/ImportHeader', module)
  .addParameters({
    jest: ['ImportHeader'],
  })
  .add('ImportHeader Default', () => <ImportHeader />);

describe('ImportHeader Unit Tests:', () => {
  const output = mount(<ImportHeader />);

  test('ImportHeader loads', () => {
    const section = output.find('.ImportHeader');
    expect(section).toHaveLength(1);
  });
});
