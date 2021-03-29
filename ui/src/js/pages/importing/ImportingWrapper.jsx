// @flow
// vendor
import React from 'react';
import { graphql, QueryRenderer } from 'react-relay';
// componenets
import Interstitial from 'Components/interstitial/Interstitial';
import Importing from './Importing';

const ImportingWrapperQuery = graphql`
  query ImportingWrapperQuery {
    ...Importing_currentServer
  }
`;

type Props = {
  environment: Object,
  transition: Function,
}


const ImportingWrapper = ({
  environment,
  transition,
}: Props) => (
  <QueryRenderer
    environment={environment}
    variables={{}}
    query={ImportingWrapperQuery}
    render={({ props, error }) => {
      if (props) {
        return (
          <Importing
            {...props}
            currentServer={props}
            transition={transition}
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
);


export default ImportingWrapper;
