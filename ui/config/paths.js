'use strict';

const path = require('path');
const fs = require('fs');
const url = require('url');

// Make sure any symlinks in the project folder are resolved:
// https://github.com/facebookincubator/create-react-app/issues/637
const appDirectory = fs.realpathSync(process.cwd());

const resolveApp = relativePath => path.resolve(appDirectory, relativePath);

const envPublicUrl = process.env.PUBLIC_URL;

function ensureSlash(path, needsSlash) {
  const hasSlash = path.endsWith('/');
  if (hasSlash && !needsSlash) {
    return path.substr(path, path.length - 1);
  } else if (!hasSlash && needsSlash) {
    return `${path}/`;
  } else {
    return path;
  }
}

const getPublicUrl = appPackageJson =>
  envPublicUrl || require(appPackageJson).homepage;

// We use `PUBLIC_URL` environment variable or "homepage" field to infer
// "public path" at which the app is served.
// Webpack needs to know it to put the right <script> hrefs into HTML even in
// single-page apps that may serve index.html for nested URLs like /todos/42.
// We can't use a relative path in HTML because we don't want to load something
// like /todos/42/static/js/bundle.7289d.js. We have to know the root.
function getServedPath(appPackageJson) {
  const publicUrl = getPublicUrl(appPackageJson);
  const servedUrl = envPublicUrl ||
    (publicUrl ? url.parse(publicUrl).pathname : '/');
  const needsSlash = process.env.BUILD_TYPE !== 'cloud';
  return ensureSlash(servedUrl, needsSlash);
}

const htmlPath = process.env.BUILD_TYPE === 'cloud' ? resolveApp('public/index.html') : resolveApp('public/indexLocal.html');

// config after eject: we're in ./config/
module.exports = {
  submodules: resolveApp('submodules'),
  dotenv: resolveApp('.env'),
  appBuild: resolveApp('build'),
  appPublic: resolveApp('public'),
  appHtml: htmlPath,
  appIndexJs: resolveApp('src/js/index.js'),
  cloudIndexJs: resolveApp('src/js/cloud/index.js'),
  dahshboardJs: resolveApp('src/js/pages/dashboard/Dashboard.js'),
  labbookJs: resolveApp('src/js/pages/repository/labbook/Labbook.js'),
  labbookActivityJs: resolveApp('src/js/pages/repository/shared/activity/Activity.jsx'),
  labbookEnvironmentJs: resolveApp('src/js/pages/repository/labbook/environment/Environment.js'),
  labbookOverviewJs: resolveApp('src/js/pages/repository/shared/overview/Overview.js'),
  mutationsJs: resolveApp('src/js/mutations'),
  appPackageJson: resolveApp('package.json'),
  appSrc: resolveApp('src'),
  appJs: resolveApp('src/js'),
  appCSS: resolveApp('src'),
  yarnLockFile: resolveApp('yarn.lock'),
  testsSetup: resolveApp('__tests__/setupTests.js'),
  appNodeModules: resolveApp('node_modules'),
  publicUrl: getPublicUrl(resolveApp('package.json')),
  servedPath: getServedPath(resolveApp('package.json')),
  uploadWorker: resolveApp('src/js/utils/upload.worker.js'),
};
