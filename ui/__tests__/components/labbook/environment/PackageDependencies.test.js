
      import React from 'react';
      import renderer from 'react-test-renderer';
      import { mount } from 'enzyme';
      import PackageDependencies from 'Pages/repository/labbook/environment/PackageDependencies';

      import relayTestingUtils from '@gigantum/relay-testing-utils';

      test('Test PackageDependencies', () => {
        const wrapper = renderer.create(

           <PackageDependencies />,

        );

        const tree = wrapper.toJSON();

        expect(tree).toMatchSnapshot();
      });
