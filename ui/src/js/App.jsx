// @flow
// vendor
import React, { Component } from 'react';
import { Router } from 'react-router-dom';
import queryString from 'querystring';
import { fetchAuthServerState } from 'JS/Auth/AuthHandler';
import { graphql, QueryRenderer } from 'react-relay';
// environment
import environment from 'JS/createRelayEnvironment';
// history
import history from 'JS/history';
// auth
import Auth from 'JS/Auth/Auth';
import stateMachine from 'JS/Auth/machine/AuthStateMachine';
import {
  LOADING,
  ERROR,
  LOGGED_IN,
  LOGGED_OUT,
  IMPORTING,
} from 'JS/Auth/machine/AuthMachineConstants';
// assets
import gigantumLogo from 'Images/logos/gigantum-client.svg';
// components
import Login from 'Pages/login/Login';
import Routes from 'Pages/Routes';
import Importing from 'Pages/importing/ImportingWrapper';
import Interstitial from 'Components/interstitial/Interstitial';
// css
import './App.scss';

const AppQuery = graphql`
  query AppQuery {
    ...Routes_currentServer
  }
`;
// todo fix state not being recognized
// type State = {
//   availableServers: Array,
//   errors: Array,
//   isLoggedIn: boolean | null,
//   machine: string,
// }

class App extends Component {
  state = {
    availableServers: [],
    errors: [],
    isLoggedIn: null,
    machine: stateMachine.initialState,
  }

  auth = new Auth();

  componentDidMount() {
    const hash = queryString.parse(document.location.hash.slice(1));
    const promise = new Promise((resolve, reject) => fetchAuthServerState(
      resolve,
      reject,
      hash,
      this.auth,
    ));

    if (hash.autoImport) {
      sessionStorage.setItem('autoImport', true);
      sessionStorage.setItem('devtool', hash.devtool);
      sessionStorage.setItem('route', window.location.pathname);
      sessionStorage.setItem('serverId', hash.serverId);

      if (hash.filePath) {
        sessionStorage.setItem('filePath', hash.filePath);
      }
    }

    promise.then((data) => {
      if (data.isLoggedIn) {
        const autoImport = JSON.parse(sessionStorage.getItem('autoImport'));
        const { pathname } = window.location;
        const pathArray = pathname.split('/');
        if (autoImport && (pathArray.length > 3)) {
          this.transition(IMPORTING, {
            availableServers: data.availableServers,
            isLoggedIn: data.isLoggedIn,
            data,
          });
        } else {
          this.transition(LOGGED_IN, {
            availableServers: data.availableServers,
            isLoggedIn: data.isLoggedIn,
          });
        }
      } else {
        this.transition(LOGGED_OUT, {
          availableServers: data.availableServers,
          isLoggedIn: data.isLoggedIn,
        });
      }
    }).catch((data) => {
      if (data && data.availableServers && (data.availableServers.length > 0)) {
        this.transition(LOGGED_OUT, {
          isLoggedIn: false,
          availableServers: data.availableServers,
          errors: data && data.errors ? data.errors : [],
        });
      } else if (data && data.errors) {
        const errors = (typeof data.errors === 'string')
          ? [{ message: data.errors }]
          : data.errors;
        this.transition(ERROR, {
          errors,
        });
      } else {
        this.transition(ERROR, {
          errors: [{ message: 'There was a problem fetching your data.' }],
        });
      }
    });
  }


  /**
    @param {object} state
    runs actions for the state machine on transition
  */
  runActions = state => {
    if (state.actions.length > 0) {
      state.actions.forEach(f => this[f]());
    }
  };

  /**
    @param {string} eventType
    @param {object} nextState
    sets transition of the state machine
  */
  transition = (eventType, nextState) => {
    const { state } = this;
    const { availableServers, machine } = this.state;

    const newState = stateMachine.transition(machine.value, eventType, {
      state,
    });

    this.runActions(newState);
    // TODO use category / installNeeded

    this.setState({
      machine: newState,
      availableServers: nextState && nextState.availableServers ? nextState.availableServers : availableServers,
      errors: nextState && nextState.errors ? nextState.errors : [],
    });
  };


  render() {
    const {
      availableServers,
      errors,
      isLoggedIn,
      machine,
    } = this.state;


    const renderMap = {
      [LOADING]: (
        <Interstitial
          message="Please wait. Loading server options..."
          messageType="loader"
        />
      ),
      [ERROR]: (
        <Interstitial
          message="There was problem loading app data. Refresh to try again, if the problem persists you may need to restart GigantumClient"
          messageType="error"
        />
      ),
      [IMPORTING]: (
        <Importing
          environment={environment}
          transition={this.transition}
        />
      ),
      [LOGGED_IN]: (
        <QueryRenderer
          environment={environment}
          variables={{}}
          query={AppQuery}
          render={({ props, error }) => {
            if (props) {
              return (
                <Routes
                  auth={this.auth}
                  currentServer={props}
                  isLoggedIn={isLoggedIn}
                />
              );
            }

            if (error) {
              return (
                <Interstitial
                  message="There was problem loading app data. Refresh to try again, if the problem persists you may need to restart GigantumClient"
                  messageType="error"
                />
              );
            }

            return (
              <Interstitial
                message="Please wait. Gigantum Client is starting…"
                messageType="loader"
              />
            );
          }}
        />
      ),
      [LOGGED_OUT]: (
        <Router history={history} basename={this.basename}>
          <div className="App">
            <header className="App__header">
              <img
                alt="Gigantum"
                width="515"
                src={gigantumLogo}
              />
            </header>
            <Login
              auth={this.auth}
              history={history}
              availableServers={availableServers}
              errors={errors}
            />
          </div>
        </Router>
      ),
    };

    return (renderMap[machine.value]);
  }
}

export default App;
