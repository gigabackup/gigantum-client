// @flow
import { Machine } from 'xstate';
// container states
import {
  LOADING,
  LOGGED_IN,
  LOGGED_OUT,
  ERROR,
  BACK,
  IMPORTING,
} from './AuthMachineConstants';

const stateMachine = Machine({
  initial: LOADING,
  states: {
    [LOADING]: {
      meta: { message: '' },
      on: {
        LOGGED_IN,
        ERROR,
        LOGGED_OUT,
        IMPORTING,
      },
    },
    [LOGGED_IN]: {
      meta: { message: '' },
      on: {
        ERROR,
      },
    },
    [LOGGED_OUT]: {
      meta: { message: '' },
      on: {
        ERROR,
      },
    },
    IMPORTING: {
      meta: { message: '' },
      on: {
        LOGGED_IN,
      },
    },
    [ERROR]: {
      meta: { message: '' },
      on: {
        [BACK]: LOGGED_OUT,
      },
    },
  },
});

export default stateMachine;
