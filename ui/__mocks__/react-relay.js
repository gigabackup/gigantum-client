
import { XMLHttpRequest } from 'xmlhttprequest';
import relayTestingUtils from '@gigantum/relay-testing-utils';
import { commitMutation, graphql, QueryRenderer } from 'react-relay';
import React, { Component } from 'react';
global.XMLHttpRequest = XMLHttpRequest;

const relay = jest.genMockFromModule('react-relay');

const RelayPaginationProps = {
      hasMore: jest.fn(),
      loadMore: jest.fn(),
      isLoading: jest.fn(),
      refetchConnection: jest.fn(),
};

const makeRelayWrapper = (Comp) => {
  class Container extends Component {
    constructor(props, context) {
    	super(props);

    	this.state = { ...props };
    }

    render() {
      return React.createElement(Comp, {
        ...this.props,
        ...this.state,
        relay: RelayPaginationProps,
      });
    }
  }

  return Container;
};

relay.createFragmentContainer = c => c;
relay.createPaginationContainer = Comp => makeRelayWrapper(Comp);
relay.createRefetchContainer = c => c;
relay.refetchConnection = jest.fn();

relay.Component = Component;
relay.commitMutation = commitMutation;
relay.graphql = graphql;


const loadMore = (props, value, ha) => {
  // let labbooks = json.data.labbookList.localLabbooks
  // labbooks.edges = labbooks.edges.slice(0, 5)
  return 'labbooks';
};

relay.loadMore = loadMore

class ReactRelayQueryRenderer extends React.Component<Props, State, Data> {
  constructor(props: Props, context: Object, data: Data) {

    super(props, context);
    this._pendingFetch = true;
    this._rootSubscription = null;
    this._selectionReference = null;

    let name = props.query.operation.name;

    this.state = {
      readyState: {
        props: (name !== false) ? global.data[name] : global.data,
      }
    }
  }


  render() {
    return this.props.render((this.state.readyState))
  }
}

relay.QueryRenderer = ReactRelayQueryRenderer

//relay.QueryRendererMock = ReactRelayQueryRenderer

module.exports = relay
