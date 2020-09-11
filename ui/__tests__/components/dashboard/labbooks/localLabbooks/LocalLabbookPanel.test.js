import React from 'react';
import renderer from 'react-test-renderer';
import { shallow, mount } from 'enzyme';
import history from 'JS/history';
import { StaticRouter, Link } from 'react-router';
import LocalLabbookPanel from 'Pages/dashboard/labbooks/localLabbooks/LocalLabbookPanel';
import relayTestingUtils from '@gigantum/relay-testing-utils';
import { MemoryRouter } from 'react-router-dom';
import environment from 'JS/createRelayEnvironment';
import { BrowserRouter as Router } from 'react-router-dom';
import json from './__relaydata__/LocalLabbooks.json';

const variables = { first: 5 };
const goToLabbook = () => {

};

const fixtures = {
  edge: json.data.labbookList.localLabbooks.edges[0],
  node: json.data.labbookList.localLabbooks.edges[0],
  key: 'key',
  className: 'LocalLabbooks__panel',
  history,
  environment: false,
  goToLabbook,
};

test('Test LocalLabbooks rendering', () => {
  const localLabbooks = renderer.create(

     relayTestingUtils.relayWrap(
      <Router>
        <LocalLabbookPanel
          {...fixtures}
        />
      </Router>, {}, json.data.labbookList.localLabbooks.edges[0],
),

  );

  const tree = localLabbooks.toJSON();

  expect(tree).toMatchSnapshot();
});

export default variables;
