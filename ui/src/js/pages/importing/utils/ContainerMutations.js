// mutations
import BuildImageMutation from 'Mutations/container/BuildImageMutation';
import StartContainerMutation from 'Mutations/container/StartContainerMutation';
import StartDevToolMutation from 'Mutations/container/StartDevToolMutation';
import ImportRemoteLabbookMutation from 'Mutations/repository/import/ImportRemoteLabbookMutation';

/**
* Method starts devtool for the project
* @param {String} owner
* @param {String} name
* @param {String} devtool
* @param {Function} callback
* @fires StartDevToolMutation
* @return {}
*/
const startDevtool = (
  owner,
  name,
  devtool,
  callback,
) => {
  const devtoolCallback = (response) => {
    callback(response);
  };

  StartDevToolMutation(
    owner,
    name,
    devtool,
    devtoolCallback,
  );
};

/**
* Method starts devtool container
* @param {String} owner
* @param {String} name
* @param {String} devtool
* @param {Function} callback
* @fires StartContainerMutation
* @fires startDevtool
* @return {}
*/
const launch = (
  owner,
  name,
  devtool,
  callback,
) => {
  const startCallback = (response) => {
    if (response.isArray) {
      callback({}, response);
    }
    startDevtool(
      owner,
      name,
      devtool,
      callback,
    );
  };
  StartContainerMutation(
    owner,
    name,
    startCallback,
  );
};

/**
* Method runs import job
* @param {Object} currentServer
* @param {Function} callback
* @fires StartContainerMutation
* @fires startDevtool
* @return {}
*/
const importJob = (
  currentServer,
  callback,
) => {
  const { baseUrl } = currentServer;
  const pathArray = window.location.pathname.split('/');
  const owner = pathArray[2];
  const name = pathArray[3];
  const remoteUrl = `${baseUrl}${owner}/${name}`;

  ImportRemoteLabbookMutation(
    owner,
    name,
    remoteUrl,
    callback,
    callback,
    callback,
  );
};

const buildAndLaunch = (owner, name, callback) => {
  BuildImageMutation(
    owner,
    name,
    {
      noCache: false,
    },
    callback,
  );
};


export {
  launch,
  buildAndLaunch,
  importJob,
};

export default {
  launch,
  buildAndLaunch,
  importJob,
};
