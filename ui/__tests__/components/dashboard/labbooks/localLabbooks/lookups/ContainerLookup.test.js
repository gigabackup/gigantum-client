import React from 'react';
import renderer from 'react-test-renderer';
import json from './../__relaydata__/LocalLabbooks.json';
import ContainerLookup from 'Pages/dashboard/labbooks/localLabbooks/lookups/ContainerLookup';

import relayTestingUtils from '@gigantum/relay-testing-utils';

test('Test ContainerLookup', async () => {
  let id = json.data.labbookList.localLabbooks.edges[0].node.id;
  ContainerLookup.query([id]).then((response) => {

    expect(response.data.ids.length).toEqual(0);
  });
});
