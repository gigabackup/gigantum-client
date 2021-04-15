// vendor
import React from 'react';
import { storiesOf } from '@storybook/react';
import { mount } from 'enzyme';
// css
import 'Styles/critical.scss';
// components
import ImportFeedback from '../ImportFeedback';


const props = {
  feedback: 'This is some feedback \n That should render on 3 lines. \n STEP1/1 Step complete',
};

storiesOf('Pages/importing/ImportFeedback', module)
  .addParameters({
    jest: ['ImportFeedback'],
  })
  .add('ImportFeedback Default', () => <ImportFeedback {...props} />);

describe('ImportFeedback Unit Tests:', () => {
  const output = mount(<ImportFeedback {...props} />);

  test('ImportFeedback loads', () => {
    const section = output.find('.Importing__feedback');
    expect(section).toHaveLength(1);
  });
});
