import React, { Component } from 'react';
import { graphql, QueryRenderer } from 'react-relay';
import { Route, Switch } from 'react-router-dom';
import queryString from 'querystring';
// redux
import { setCallbackRoute } from 'JS/redux/actions/routes';
// components
import environment from 'JS/createRelayEnvironment';
import Loader from 'Components/loader/Loader';
import LocalProjectsContainer from './repositories/containers/LocalProjectsContainer';
import LocalDatasetsContainer from './repositories/containers/LocalDatasetsContainer';
import RemoteDatasetsContainer from './repositories/containers/RemoteDatasetsContainer';
import RemoteProjectsContainer from './repositories/containers/RemoteProjectsContainer';
// assets
import './Dashboard.scss';


const LocalListingQuery = graphql`query DashboardLocalQuery($first: Int!, $cursor: String, $orderBy: String $sort: String){
  ...LocalProjectsContainer_projectList
}`;

const LocalDatasetListingQuery = graphql`query DashboardDatasetLocalQuery($first: Int!, $cursor: String, $orderBy: String $sort: String){
  ...LocalDatasetsContainer_datasetList
}`;
const RemoteDatasetListingQuery = graphql`query DashboardDatasetRemoteQuery($first: Int!, $cursor: String, $orderBy: String $sort: String){
  ...RemoteDatasetsContainer_datasetList
}`;

const RemoteListingQuery = graphql`query DashboardRemoteQuery($first: Int!, $cursor: String, $orderBy: String $sort: String){
  ...RemoteProjectsContainer_projectList
}`;

type Props = {
  auth: Object,
  diskLow: boolean,
  hash: Object,
  history: Object,
  match: Object,
  serverName: string,
}

export default class DashboardContainer extends Component<Props> {
  constructor(props) {
    super(props);
    const { orderBy, sort } = queryString.parse(props.history.location.hash.slice(1));

    this.state = {
      selectedComponent: props.match && props.match.path,
      orderBy: orderBy || 'modified_on',
      sort: sort || 'desc',
    };
  }

  static getDerivedStateFromProps(props, state) {
    setCallbackRoute(props.history.location.pathname);
    return {
      ...state,
      selectedComponent: props.match.path,
    };
  }

  componentDidMount() {
    const { history } = this.props;
    window.location.hash = '';
    setCallbackRoute(history.location.pathname);
  }

  /**
    * @param {string, string} orderBy, sort
    * sets state of orderBy and sort, passed to child components
  */
  _refetchSort = (orderBy, sort) => {
    const { state } = this;
    if (state.orderBy !== orderBy || state.sort !== sort) {
      this.setState({ orderBy, sort });
    }
  }


  /**
  *  @param {}
  *  returns jsx of selected component
  *  @return {jsx}
  */
  _displaySelectedComponent = () => {
    const {
      orderBy,
      sort,
      selectedComponent,
    } = this.state;
    const {
      auth,
      diskLow,
      hash,
      history,
      match,
      serverName,
    } = this.props;
    const sectionRoute = match
      && match.params
      && match.params.labbookSection;
    let query;

    if ((sectionRoute !== 'cloud') && (sectionRoute !== 'local')) {
      history.replace('/projects/local');
    }
    if (selectedComponent === '/datasets/:labbookSection') {
      query = sectionRoute === 'cloud' ? RemoteDatasetListingQuery : LocalDatasetListingQuery;
    } else if (sectionRoute === 'cloud') {
      query = RemoteListingQuery;
    } else {
      query = LocalListingQuery;
    }

    return (
      <QueryRenderer
        environment={environment}
        query={query}
        variables={{
          first: sectionRoute === 'cloud' ? 10 : 100,
          cursor: null,
          orderBy,
          sort,
        }}
        render={(response) => {
          const { error } = this;
          const queryProps = response.props;
          if (error) {
            console.log(error);
            return null;
          }

          if (queryProps) {
            return (
              <Switch>
                <Route path="/datasets/cloud">
                  <RemoteDatasetsContainer
                    auth={auth}
                    datasetList={queryProps}
                    diskLow={diskLow}
                    history={history}
                    orderBy={orderBy}
                    refetchSort={this._refetchSort}
                    section={sectionRoute}
                    sectionType="dataset"
                    serverName={serverName}
                    sort={sort}
                  />
                </Route>
                <Route path="/datasets/local">
                  <LocalDatasetsContainer
                    auth={auth}
                    datasetList={queryProps}
                    diskLow={diskLow}
                    hash={hash}
                    history={history}
                    orderBy={orderBy}
                    refetchSort={this._refetchSort}
                    section={sectionRoute}
                    sectionType="dataset"
                    serverName={serverName}
                    sort={sort}
                  />
                </Route>
                <Route path="/projects/cloud">
                  <RemoteProjectsContainer
                    auth={auth}
                    diskLow={diskLow}
                    history={history}
                    projectList={queryProps}
                    orderBy={orderBy}
                    refetchSort={this._refetchSort}
                    section={sectionRoute}
                    sectionType="project"
                    serverName={serverName}
                    sort={sort}
                  />
                </Route>
                <Route path="/projects/local">
                  <LocalProjectsContainer
                    auth={auth}
                    diskLow={diskLow}
                    hash={hash}
                    history={history}
                    project
                    projectList={queryProps}
                    orderBy={orderBy}
                    refetchSort={this._refetchSort}
                    section={sectionRoute}
                    sectionType="project"
                    serverName={serverName}
                    sort={sort}
                  />
                </Route>
              </Switch>
            );
          }
          return (
            <Switch>
              <Route path="/projects">
                <LocalProjectsContainer
                  auth={auth}
                  diskLow={diskLow}
                  history={history}
                  hash={hash}
                  project
                  projectList={queryProps}
                  loading
                  orderBy={orderBy}
                  refetchSort={this._refetchSort}
                  section={sectionRoute}
                  sectionType="project"
                  serverName={serverName}
                  sort={sort}
                />
              </Route>
              <Route path="/datasets">
                <LocalDatasetsContainer
                  auth={auth}
                  datasetList={queryProps}
                  diskLow={diskLow}
                  hash={hash}
                  history={history}
                  loading
                  orderBy={orderBy}
                  refetchSort={this._refetchSort}
                  section={sectionRoute}
                  sectionType="dataset"
                  serverName={serverName}
                  sort={sort}
                />
              </Route>
            </Switch>
          );
        }}
      />
    );
  }

  render() {
    return (
      <div className="Dashboard flex flex-column">

        <div className="Dashboard__view flex-1-0-auto">
          <div id="dashboard__cover" className="Dashboard__cover hidden">
            <Loader />
          </div>
          {
            this._displaySelectedComponent()
          }
        </div>
      </div>
    );
  }
}
