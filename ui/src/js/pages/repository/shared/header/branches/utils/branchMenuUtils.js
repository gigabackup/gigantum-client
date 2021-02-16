/**
  @param {Array} branches
  filters array branhces and return the active branch node
  @return {Object} activeBranch
*/
const extractActiveBranch = (branches) => {
  const activeBranch = branches.filter(branch => branch.isActive)[0] || {};

  return ({
    activeBranch,
  });
};

/**
  Method returns sync/publish button state based on,
  if there is a remote available or user only has pull access
  @param {String} defaultRemote
  @param {Boolean} isPullOnly
  @return {String}
*/
const getSyncOrPublish = (defaultRemote, isPullOnly) => {
  if (defaultRemote) {
    return 'Sync';
  }

  if (isPullOnly) {
    return 'Pull';
  }

  return 'Publish';
};

/**
  @param {Object} props
  @param {Object} data
  Gets sync tooltip
  @return {String}
*/
const getSyncTooltip = (data, currentServer) => {
  const {
    activeBranch,
    collaborators,
    defaultRemote,
    hasWriteAccess,
    isLocked,
    section,
    sectionType,
  } = data;

  const isDataset = (sectionType !== 'labbook');
  const sectionCollabs = (collaborators && collaborators[section.name]) || null;
  const isPullOnly = defaultRemote && !hasWriteAccess && sectionCollabs;

  const syncOrPublish = getSyncOrPublish(defaultRemote, syncOrPublish);
  const { backupInProgress, name } = currentServer;
  const repositoryType = isDataset ? 'Dataset' : 'Project';

  let syncTooltip = !hasWriteAccess ? 'Pull changes from Gignatum Hub' : `Sync changes to ${name}`;
  syncTooltip = !defaultRemote
    ? `Click Publish to push branch to ${name}`
    : syncTooltip;
  syncTooltip = isLocked
    ? `Cannot ${syncOrPublish} while ${repositoryType} is in use`
    : syncTooltip;
  syncTooltip = (activeBranch.branchName !== 'master' && !defaultRemote)
    ? 'Must publish Master branch first'
    : syncTooltip;
  syncTooltip = defaultRemote && !sectionCollabs
    ? `Please wait while ${repositoryType} data is being fetched`
    : syncTooltip;
  syncTooltip = backupInProgress
    ? `Cannot  ${syncOrPublish} while ${repositoryType} back up is in progress`
    : syncTooltip;

  return syncTooltip;
};


/**
  @param {Object} result
  @param {Object} data
  Gets managed tooltip
  @return {String}
*/
const getLocalDatasets = (result) => {
  const { data } = result;
  let localDataset = [];

  if (data && data.labbook) {
    const { linkedDatasets } = data.labbook;
    localDataset = linkedDatasets.filter((linkedDataset) => {
      const { defaultRemote } = linkedDataset;
      return (defaultRemote && (defaultRemote.slice(0, 4) !== 'http'));
    });
  }

  return localDataset;
};


/**
*  @param {Object} - activeBranch
*  determines whether or not user has write access
*  @return {}
*/
const checkForWriteAccess = (
  activeBranch,
  defaultRemote,
  collaborators,
  sectionName,
) => {
  const username = localStorage.getItem('username');

  if (!defaultRemote) {
    return true;
  }

  if (!collaborators
    || (collaborators && !collaborators[sectionName])
  ) {
    return false;
  }
  const collaboratorsSection = collaborators[sectionName];
  const filteredArr = collaboratorsSection.filter(
    collaborator => (collaborator.collaboratorUsername === username),
  );

  if (filteredArr.length === 0) {
    return false;
  }

  if (
    (filteredArr[0].permission === 'READ_ONLY')
    || ((filteredArr[0].permission === 'READ_WRITE')
    && (activeBranch.branchName === 'master'))
  ) {
    return false;
  }

  return true;
};

export {
  checkForWriteAccess,
  extractActiveBranch,
  getLocalDatasets,
  getSyncOrPublish,
  getSyncTooltip,
};

export default {
  checkForWriteAccess,
  extractActiveBranch,
  getLocalDatasets,
  getSyncOrPublish,
  getSyncTooltip,
};
