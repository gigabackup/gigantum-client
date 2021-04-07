// @flow
// vendor
import React, { Component } from 'react';
import queryString from 'querystring';
import classNames from 'classnames';
import { Route, Switch } from 'react-router-dom';
import { connect } from 'react-redux';
// components
import CreateModal from 'Pages/repository/shared/modals/create/CreateModal';
import Loader from 'Components/loader/Loader';

import LocalProjects from 'Pages/dashboard/repositories/listing/local/containers/LocalProjects';
import LocalListing from 'Pages/dashboard/repositories/listing/local/LocalListing';
import RemoteProjects from 'Pages/dashboard/repositories/listing/remote/containers/RemoteProjects';
import LocalDatasets from 'Pages/dashboard/repositories/listing/local/containers/LocalDatasets';
import RemoteDatasets from 'Pages/dashboard/repositories/listing/remote/containers/RemoteDatasets';

import LoginPrompt from 'Pages/repository/shared/modals/LoginPrompt';
import Tooltip from 'Components/tooltip/Tooltip';
import FilterByDropdown from 'Pages/dashboard/shared/filters/FilterByDropdown';
import SortByDropdown from 'Pages/dashboard/shared/filters/SortByDropdown';
// utils
import Validation from 'JS/utils/Validation';
// queries
import UserIdentity from 'JS/Auth/UserIdentity';
// context
import ServerContext from 'Pages/ServerContext';
// store
import { setErrorMessage } from 'JS/redux/actions/footer';
import { setFilterText } from 'JS/redux/actions/labbookListing/labbookListing';
// assets
import './Repositories.scss';

type Props = {
  diskLow: boolean,
  filterText: string,
  history: {
    location: {
      hash: string,
      pathname: string,
      search: string,
    },
    replace: Function,
  },
  projectList: Array<Object>,
  datasetList: Array<Object>,
  loading: boolean,
  orderBy: string,
  refetchSort: Function,
  section: string,
  sectionType: string,
  serverName: string,
  sort: boolean,
  sortBy: string,
}

class Repositories extends Component<Props> {
  constructor(props) {
    super(props);

    const {
      filter,
      orderBy,
      sort,
    } = queryString.parse(props.history.location.hash.slice(1));
    let { section } = props;
    if ((section !== 'cloud') && (section !== 'local')) {
      section = 'local';
    }

    this.state = {
      repositoryModalVisible: false,
      newRepositoryName: '',
      renameError: '',
      showNamingError: false,
      filter: filter || 'all',
      sortMenuOpen: false,
      refetchLoading: false,
      selectedSection: section,
      showLoginPrompt: false,
      orderBy: orderBy || props.orderBy,
      sort: sort || props.sort,
      filterMenuOpen: false,
    };
  }

  /**
    * @param {}
    * fires when a componet mounts
    * adds a scoll listener to trigger pagination
  */
  componentDidMount() {
    const {
      loading,
      projectList,
      project,
    } = this.props;
    document.title = 'Gigantum';

    window.addEventListener('scroll', this._captureScroll);
    window.addEventListener('click', this._hideSearchClear);
    window.addEventListener('click', this._closeSortMenu);
    window.addEventListener('click', this._closeFilterMenu);

    if (
        project
        && (projectList === null)
        && !loading
      ) {
      UserIdentity.getUserIdentity().then((response) => {
        if (response.data && response.data.userIdentity.isSessionValid) {
          setErrorMessage(null, null, 'Failed to fetch Projects.', [{ message: 'There was an error while fetching Projects. This likely means you have a corrupted Project directory.' }]);
          return;
        }
        this.setState({ showLoginPrompt: true });
      });
    }
  }

  /**
    * @param {}
    * fires when component unmounts
    * removes added event listeners
  */
  componentWillUnmount() {
    window.removeEventListener('click', this._closeSortMenu);
    window.removeEventListener('click', this._closeFilterMenu);
    window.removeEventListener('scroll', this._captureScroll);
    window.removeEventListener('click', this._hideSearchClear);
  }

  static getDerivedStateFromProps(props, state) {
    const paths = props.history.location.pathname.split('/');
    const selectedSection = paths.length > 2 ? paths[2] : 'local';

    return {
      ...state,
      selectedSection,
    };
  }

  /**
    * @param {}
    * fires when user identity returns invalid session
    * prompts user to revalidate their session
  */
  _closeLoginPromptModal = () => {
    this.setState({
      showLoginPrompt: false,
    });
  }

  /**
    * @param {event} evt
    * fires when sort menu is open and the user clicks elsewhere
    * hides the sort menu dropdown from the view
  */
  _closeSortMenu = (evt) => {
    const { sortMenuOpen } = this.state;
    const isSortMenu = evt && evt.target
      && evt.target.className
      && (evt.target.className.indexOf('Dropdown__sort-selector') > -1);

    if (!isSortMenu && sortMenuOpen) {
      this.setState({ sortMenuOpen: false });
    }
  }

  /**
    * @param {event} evt
    * fires when filter menu is open and the user clicks elsewhere
    * hides the filter menu dropdown from the view
  */
  _closeFilterMenu = (evt) => {
    const { filterMenuOpen } = this.state;
    const isFilterMenu = evt.target.className.indexOf('Dropdown__filter-selector') > -1;

    if (!isFilterMenu && filterMenuOpen) {
      this.setState({ filterMenuOpen: false });
    }
  }

  /**
    * @param {}
    * fires on window clock
    * hides search cancel button when clicked off
  */
  _hideSearchClear = (evt) => {
    const { showSearchCancel } = this.state;
    if (
      showSearchCancel
      && (evt.target.className !== 'Repositories__search-cancel')
      && (evt.target.className !== 'Repositories__search no--margin')
    ) {
      this.setState({ showSearchCancel: false });
    }
  }

  /**
   * @param {string} filter
   sets state updates filter
  */
  _setFilter = (filter) => {
    this.setState({ filterMenuOpen: false, filter });
    this._changeSearchParam({ filter });
  }

  /**
   sets state for filter menu
  */
  _toggleFilterMenu = () => {
    this.setState(state => ({ filterMenuOpen: !state.filterMenuOpen }));
  }

  /**
   sets state for sort menu
  */
  _toggleSortMenu = () => {
    this.setState(state => ({ sortMenuOpen: !state.sortMenuOpen }));
  }

  /**
   * @param {string} section
   replaces history and checks session
  */
  _setSection = (section) => {
    const { history, sectionType } = this.props;
    if (section === 'cloud') {
      this._viewRemote();
    } else {
      history.replace(`../${sectionType}s/${section}${history.location.search}`);
    }
  }

  /**
   * @param {object} repository
   * returns true if repository's name or description exists in filtervalue, else returns false
  */
  _filterSearch = (repository) => {
    const { filterText } = this.props;
    const hasNoFileText = (filterText === '');
    const nameMatches = repository.node
      && repository.node.name
      && (repository.node.name.toLowerCase().indexOf(filterText.toLowerCase()) > -1);
    const descriptionMatches = repository.node
      && repository.node.description
      && (repository.node.description.toLowerCase().indexOf(filterText.toLowerCase()) > -1);

    if (hasNoFileText
      || nameMatches
      || descriptionMatches) {
      return true;
    }
    return false;
  }

  /**
   * @param {Array} repositories
   * @param {String} filter
   * @return {Array} filteredRepositories
  */
  filterRepositories = (repositories = [], filter) => {
    const username = localStorage.getItem('username');
    const self = this;
    let filteredRepositories = [];


    if (filter === 'owner') {
      filteredRepositories = repositories.filter(
        repository => ((repository.node.owner === username)
        && self._filterSearch(repository)),
      );
    } else if (filter === 'others') {
      filteredRepositories = repositories.filter(
        repository => (repository.node.owner !== username
          && self._filterSearch(repository)),
      );
    } else {
      filteredRepositories = repositories.filter(repository => self._filterSearch(repository));
    }

    return filteredRepositories;
  }

  /**
    * @param {}
    * fires when handleSortFilter triggers refetch
    * references child components and triggers their refetch functions
  */
  _showModal = () => {
    // TODO remove refs this is deprecated
    this.createModal._showModal();
  }

  /**
    *  @param {string} selected
    * fires when setSortFilter validates user can sort
    * triggers a refetch with new sort parameters
  */
  _handleSortFilter = (orderBy, sort) => {
    const { refetchSort } = this.props;
    this.setState({ sortMenuOpen: false, orderBy, sort });
    this._changeSearchParam({ orderBy, sort });
    refetchSort(orderBy, sort);
  }

  /**
    *  @param {string, boolean} orderBy sort
    * fires when user selects a sort option
    * checks session and selectedSection state before handing off to handleSortFilter
  */
  _setSortFilter = (orderBy, sort) => {
    const {
      selectedSection,
      showLoginPrompt,
    } = this.state;

    if (
      selectedSection === 'remoteProjects'
      || selectedSection === 'remoteDatasets'
      ) {
      UserIdentity.getUserIdentity().then((response) => {
        if (navigator.onLine) {
          if (response.data) {
            if (response.data.userIdentity.isSessionValid) {
              this._handleSortFilter(orderBy, sort);
            } else {
              this.setState({ showLoginPrompt: true });
            }
          }
        } else if (!showLoginPrompt) {
          this.setState({ showLoginPrompt: true });
        }
      });
    } else {
      this._handleSortFilter(orderBy, sort);
    }
  }

  /**
    * @param {}
    * fires when user selects remote repository view
    * checks user auth before changing selectedSection state
  */
  _viewRemote = () => {
    const { history, sectionType } = this.props;
    const { showLoginPrompt } = this.state;
    UserIdentity.getUserIdentity().then((response) => {
      if (navigator.onLine) {
        if (response.data && response.data.userIdentity.isSessionValid) {
          history.replace(`../${sectionType}s/cloud${history.location.search}`);
          this.setState({ selectedSection: 'cloud' });
        } else {
          this.setState({ showLoginPrompt: true });
        }
      } else if (!showLoginPrompt) {
        this.setState({ showLoginPrompt: true });
      }
    });
  }

  /**
  *  @param {evt}
  *  sets the filterValue in state
  */
  _setFilterValue = (evt) => {
    setFilterText(evt.target.value);
    // TODO remove refs
    if (this.repositorySearch.value !== evt.target.value) {
      this.repositorySearch.value = evt.target.value;
    }
  }

  /**
    *  @param {object} newValues
    *  changes the query params to new sort and filter values
  */
  _changeSearchParam = (newValues) => {
    const { history } = this.props;
    const searchObj = Object.assign(
      {},
      queryString.parse(history.location.hash.slice(1)),
      newValues,
    );
    const urlParameters = queryString.stringify(searchObj);

    history.replace(`..${history.location.pathname}#${urlParameters}`);
  }

  /**
    *  @param {} -
    *  forces state update ad sets to local view
  */
  _forceLocalView = () => {
    this.setState({
      selectedSection: 'local',
      showLoginPrompt: true,
    });
  }

  static contextType = ServerContext;

  render() {
    const {
      datasetList,
      diskLow,
      filterText,
      projectList,
      sectionType,
      loading,
    } = this.props;

    const {
      filter,
      filterMenuOpen,
      selectedSection,
      showLoginPrompt,
    } = this.state;
    const { currentServer } = this.context;
    const repositoryTitle = sectionType === 'project' ? 'Project' : 'Dataset';
    const currentServerName = currentServer && currentServer.name ? currentServer.name : 'gigantum';
    const projectListId = projectList && projectList.labbookList.id;
    const datasetListId = datasetList && datasetList.datasetList.id;
    const projectListingData = projectList && projectList.labbookList;
    const datasetListingData = datasetList && datasetList.datasetList;

    // declare css
    const repositoriesCSS = classNames({
      Repositories: true,
      'Repositories--disk-low': diskLow,
    });

    if (
        (projectList !== null)
        || (datasetList !== null)
        || loading
      ) {
      const localNavItemCSS = classNames({
        Tab: true,
        'Tab--local': true,
        'Tab--selected': selectedSection === 'local',
      });
      const cloudNavItemCSS = classNames({
        Tab: true,
        'Tab--cloud': true,
        'Tab--selected': selectedSection === 'cloud',
      });

      return (

        <div className={repositoriesCSS}>

          <CreateModal
            {...this.props}
            ref={(modal) => { this.createModal = modal; }}
            datasets={sectionType === 'dataset'}
            handler={this.handler}
          />

          <div className="Repositories__panel-bar">
            <h6 className="Repositories__username">{localStorage.getItem('username')}</h6>
            <h1>{`${repositoryTitle}s`}</h1>

          </div>
          <div className="Repositories__menu  mui-container flex-0-0-auto">
            <ul className="Tabs">
              <li className={localNavItemCSS}>
                <button
                  className="Btn--noStyle"
                  type="button"
                  onClick={() => this._setSection('local')}
                >
                  Local
                </button>
              </li>
              <li className={cloudNavItemCSS}>
                <button
                  className="Btn--noStyle"
                  type="button"
                  onClick={() => this._setSection('cloud')}
                >
                  {currentServerName}
                </button>
              </li>

              <Tooltip section="cloudLocal" />
            </ul>

          </div>
          <div className="Repositories__subheader grid">
            <div className="Repositories__search-container column-2-span-6 padding--0">
              <div className="Input Input--clear">
                { (filterText.length !== 0)
                    && (
                      <button
                        type="button"
                        className="Btn Btn--flat"
                        onClick={() => this._setFilterValue({ target: { value: '' } })}
                      >
                        Clear
                      </button>
                    )
                  }
                <input
                  type="text"
                  ref={(modal) => { this.repositorySearch = modal; }}
                  className="margin--0"
                  placeholder={`Filter ${repositoryTitle}s by name or description`}
                  defaultValue={filterText}
                  onKeyUp={evt => this._setFilterValue(evt)}
                  onFocus={() => this.setState({ showSearchCancel: true })}
                />
              </div>
            </div>

            <FilterByDropdown
              {...this.state}
              type={repositoryTitle}
              toggleFilterMenu={() => this.setState({ filterMenuOpen: !filterMenuOpen })}
              setFilter={this._setFilter}
            />
            <SortByDropdown
              {...this.state}
              toggleSortMenu={this._toggleSortMenu}
              setSortFilter={this._setSortFilter}
            />

          </div>
          {
            !loading
            && (
              <Switch>
                <Route path="/datasets/cloud">
                  <RemoteDatasets
                    {...this.props}
                    datasetListId={datasetListId}
                    isVisible={(!loading) && (selectedSection === 'cloud')}
                    remoteDatasets={datasetListingData}
                    showModal={this._showModal}
                    filterRepositories={this.filterRepositories}
                    filterState={filter}
                    setFilterValue={this._setFilterValue}
                    forceLocalView={() => { this._forceLocalView(); }}
                    changeRefetchState={bool => this.setState({ refetchLoading: bool })}
                  />
                </Route>
                <Route path="/datasets/local">
                  <LocalDatasets
                    {...this.props}
                    datasetListId={datasetListId}
                    isVisible={(!loading) && (selectedSection === 'local')}
                    localDatasets={datasetListingData}
                    showModal={this._showModal}
                    filterRepositories={this.filterRepositories}
                    filterState={filter}
                    setFilterValue={this._setFilterValue}
                    changeRefetchState={bool => this.setState({ refetchLoading: bool })}
                  />
                </Route>
                <Route path="/projects/cloud">
                  <RemoteProjects
                    {...this.props}
                    projectListId={projectListId}
                    remoteProjects={projectListingData}
                    showModal={this._showModal}
                    isVisible={(!loading) && (selectedSection === 'cloud')}
                    filterRepositories={this.filterRepositories}
                    filterState={filter}
                    setFilterValue={this._setFilterValue}
                    forceLocalView={() => { this._forceLocalView(); }}
                    changeRefetchState={bool => this.setState({ refetchLoading: bool })}
                  />
                </Route>
                <Route path="/projects/local">
                  <LocalProjects
                    {...this.props}
                    projectListId={projectListId}
                    isVisible={(!loading) && (selectedSection === 'local')}
                    localProjects={projectListingData}
                    showModal={this._showModal}
                    filterRepositories={this.filterRepositories}
                    filterState={filter}
                    setFilterValue={this._setFilterValue}
                    changeRefetchState={bool => this.setState({ refetchLoading: bool })}
                  />
                </Route>
              </Switch>
            )
          }
          {
            loading
            && (
              <LocalListing
                {...this.props}
                isVisible={loading}
                filterRepositories={this.filterRepositories}
                loading
                showModal={this._showModal}
              />
            )
          }

          <LoginPrompt
            closeModal={this._closeLoginPromptModal}
            showLoginPrompt={showLoginPrompt}
          />

        </div>
      );
    }
    if ((projectList === null) && !loading) {
      return (
        <div className="Repositories__fetch-error">
          There was an error attempting to fetch Projects.
          <br />
          Try restarting Gigantum and refresh the page.
          <br />
          If the problem persists
          <a
            target="_blank"
            href="https://spectrum.chat/gigantum"
            rel="noopener noreferrer"
          >
            request assistance here.
          </a>
        </div>
      );
    }

    return (<Loader />);
  }
}

const mapStateToProps = state => ({
  filterText: state.labbookListing.filterText,
});

const mapDispatchToProps = () => ({});

export default connect(mapStateToProps, mapDispatchToProps)(Repositories);
