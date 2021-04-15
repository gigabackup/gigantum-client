// @flow
// vendor
import React from 'react';
import { QueryRenderer, graphql } from 'react-relay';
// components
import DevToolsOptions from './devtools/DevtoolsOptions';
import ShareFileInput from './file/ShareFileInput';
// css
import './ShareForm.scss';

type Props = {
  environment: Object,
  devtool: string,
  repository: {
    name: string,
    owner: string,
  },
  updateCodeFileUrl: Function,
  updateDevtoolUrl: Function,
}


const shareFormQuery = graphql`
  query ShareFormQuery($name: String!, $owner: String!, $first: Int!, $cursor: String){
    labbook(name: $name, owner: $owner){
      ...ShareFileInput_labbook
    }
  }`;

const ShareForm = ({
  environment,
  devtool,
  repository,
  updateCodeFileUrl,
  updateDevtoolUrl,
}: Props) => {
  const { name, owner } = repository;
  return (
    <QueryRenderer
      environment={environment}
      variables={{
        cursor: null,
        first: 1000, // induce pagination and refactor with relay hooks
        name,
        owner,
      }}
      query={shareFormQuery}
      render={({ props, error }) => {
        if (props) {
          return (
            <div className="ShareForm flex">

              <DevToolsOptions
                repository={repository}
                updateDevtoolUrl={updateDevtoolUrl}
              />

              <ShareFileInput
                {...props}
                devtool={devtool}
                repository={repository}
                updateCodeFileUrl={updateCodeFileUrl}
              />

            </div>
          );
        }
        return (
          <div className="ShareForm">
            <DevToolsOptions
              repository={repository}
              updateDevtoolUrl={updateDevtoolUrl}
            />
            <ShareFileInput
              devtool={devtool}
              repository={repository}
              updateCodeFileUrl={updateCodeFileUrl}
            />
          </div>
        );
      }}
    />
  );
};

export { shareFormQuery };

export default ShareForm;
