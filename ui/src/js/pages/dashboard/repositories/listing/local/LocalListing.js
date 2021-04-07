// vendor
import React, { Component } from 'react';
// components
import LocalPanel from 'Pages/dashboard/repositories/listing/local/panel/LocalPanel';
import CardLoader from 'Pages/dashboard/shared/loaders/CardLoader';
import ImportModule from 'Pages/dashboard/shared/import/ImportModule';
import NoResults from 'Pages/dashboard/shared/NoResults';
// helpers
import ContainerLookup from '../lookups/ContainerLookup';
import VisibilityLookup from '../lookups/VisibilityLookup';
import DatasetVisibilityLookup from '../lookups/DatasetVisibilityLookup';

// assets
import './LocalListing.scss';


type Props = {
  filterRepositories: Function,
  filterState: string,
  filterText: string,
  history: Object,
  isVisible: Boolean,
  datasetList: Array,
  projectList: Array,
  loading: boolean,
  localDatasets: {
    localDatasets: {
      edges: Array<Object>,
      pageInfo: {
        hasNextPage: boolean,
      },
    },
  },
  localProjects: {
    localLabbooks: {
      edges: Array<Object>,
      pageInfo: {
        hasNextPage: boolean,
      },
    },
  },
  relay: {
    loadMore: Function,
    refetchConnection: Function,
  },
  section: string,
  sectionType: string,
  setFilterValue: Function,
  showModal: Function,
}

class LocalListing extends Component<Props> {
  state = {
    isPaginating: false,
    containerList: new Map(),
    visibilityList: new Map(),
  };

  /** *
  * @param {}
  * adds event listener for pagination and fetches container status
  */
  componentDidMount() {
    const {
      isVisible,
      datasetList,
      projectList,
      localDatasets,
      localProjects,
      loading,
      sectionType,
    } = this.props;
    this.mounted = true;
    if (!isVisible) {
      return;
    }
    if (!loading) {
      window.addEventListener('scroll', this._captureScroll);
      if (sectionType === 'project') {
        this._containerLookup();
      }

      this._visibilityLookup();

      const sectionList = (sectionType === 'project') ? projectList : datasetList;
      const listing = (sectionType === 'project') ? localProjects.localLabbooks : localDatasets.localDatasets;

      if (sectionList
         && listing
         && listing.edges
         && listing.edges.length === 0) {
        this._fetchDemo();
      }
    }
  }

  /** *
  * @param {}
  * removes event listener for pagination and removes timeout for container status
  */
  componentWillUnmount() {
    this.mounted = false;
    clearTimeout(this.containerLookup);

    window.removeEventListener('scroll', this._captureScroll);
  }

  /**
    *  @param {}
    *  loads more Projects using the relay pagination container
  */
  _loadMore = () => {
    const {
      localDatasets,
      localProjects,
      relay,
      sectionType,
    } = this.props;
    this.setState({
      isPaginating: true,
    });
    const listing = (sectionType === 'project') ? localProjects.localLabbooks : localDatasets.localDatasets;

    if (listing.pageInfo.hasNextPage) {
      relay.loadMore(
        10, // Fetch the next 10 items
        () => {
          this.setState({
            isPaginating: false,
          });

          this._visibilityLookup();
        },
      );
    }
  }

  /**
    *  @param {}
    *  fires when user scrolls
    *  if nextPage exists and user is scrolled down, it will cause loadmore to fire
  */
  _captureScroll = () => {
    const { isPaginating } = this.state;
    const {
      localDatasets,
      localProjects,
      sectionType,
    } = this.props;
    const root = document.getElementById('root');
    const distanceY = window.innerHeight + document.documentElement.scrollTop + 200;
    const expandOn = root.offsetHeight;
    const listing = (sectionType === 'project') ? localProjects.localLabbooks : localDatasets.localDatasets;

    if (listing) {
      if ((distanceY > expandOn) && !isPaginating
        && listing.pageInfo.hasNextPage) {
        this._loadMore();
      }
    }
  }

  /** *
  * @param {}
  * calls ContainerLookup query and attaches the returned data to the state
  */
  _containerLookup = () => {
    const { containerList } = this.state;
    const { localProjects } = this.props;
    const self = this;
    const idArr = localProjects.localLabbooks
      ? localProjects.localLabbooks.edges.map(edges => edges.node.id)
      : [];

    ContainerLookup.query(idArr).then((res) => {
      if (res && res.data
        && res.data.labbookList
        && res.data.labbookList.localById) {
        const containerListCopy = new Map(containerList);
        let brokenCount = 0;
        res.data.labbookList.localById.forEach((node) => {
          if (
            node.environment.imageStatus === null
            && node.environment.containerStatus === null
          ) {
            brokenCount += 1;
          }
          containerListCopy.set(node.id, node);
        });
        if (self.mounted) {
          const delay = (brokenCount !== res.data.labbookList.localById.length) ? 30000 : 10000;

          if (!brokenCount !== res.data.labbookList.localById.length) {
            self.setState({ containerList: containerListCopy });
          }
          this.containerLookup = setTimeout(() => {
            self._containerLookup();
          }, delay);
        }
      }
    });
  }

  /** *
    * @param {integer} count
    * attempts to fetch a demo if no projects are present, 3 times
  */
  _fetchDemo = (count = 0) => {
    const {
      project,
      localDatasets,
      localProjects,
      relay,
      sectionType,
    } = this.props;
    if (count < 3) {
      const self = this;
      setTimeout(() => {
        relay.refetchConnection(20, () => {
          const list = (sectionType === 'project') ? localProjects.localLabbooks : localDatasets.localDatasets;
          if (list.edges.length > 0) {
            if (project) {
              self._containerLookup();
            }
            self._visibilityLookup();
          } else {
            self._fetchDemo(count + 1);
          }
        });
      }, 3000);
    }
  }

  /** *
  * @param {} -
  * calls VisibilityLookup query and attaches the returned data to the state
  */
  _visibilityLookup = () => {
    const {
      localDatasets,
      localProjects,
      sectionType,
    } = this.props;
    const self = this;
    const list = (sectionType === 'project') ? localProjects.localLabbooks : localDatasets.localDatasets;
    const idArr = list
      ? list.edges.map(edges => edges.node.id)
      : [];
    let index = 0;

    function query(ids) {
      const subsetIds = idArr.slice(index, index + 10);
      const lookup = (sectionType === 'project') ? VisibilityLookup : DatasetVisibilityLookup;
      lookup.query(subsetIds).then((res) => {
        const listName = (sectionType === 'project') ? 'labbookList' : 'datasetList';
        if (res && res.data
          && res.data[listName]
          && res.data[listName].localById) {
          const visibilityListCopy = new Map(self.state.visibilityList);

          res.data[listName].localById.forEach((node) => {
            visibilityListCopy.set(node.id, node);
          });


          if (index < idArr.length) {
            index += 10;

            query(ids, index);
          }
          if (self.mounted) {
            self.setState({ visibilityList: visibilityListCopy });
          }
        }
      });
    }

    query(idArr, index);
  }

  render() {
    const {
      filterRepositories,
      filterState,
      filterText,
      history,
      isVisible,
      loading,
      localDatasets,
      localProjects,
      section,
      sectionType,
      setFilterValue,
      showModal,
    } = this.props;
    const {
      isPaginating,
      visibilityList,
      containerList,
    } = this.state;

    if (!isVisible) {
      return null;
    }
    const sectionList = (sectionType === 'project')
      ? localProjects && localProjects.localLabbooks
      : localDatasets && localDatasets.localDatasets;

    if (
      (sectionList && sectionList.edges)
      || loading
    ) {
      const repositories = !loading
        ? filterRepositories(sectionList.edges, filterState)
        : [];
      const importVisible = (section === 'local' || !loading) && !filterText;
      const isLoadingMore = isPaginating || loading;
      const importTitle = (sectionType === 'project') ? 'Add Project' : 'Add Dataset';
      const importSection = (sectionType === 'project') ? 'labbook' : 'dataset';
      const panelSection = (sectionType === 'project') ? 'LocalProjects' : 'LocalDatasets';
      return (

        <div className="Repositories__listing">

          <div className="grid">
            { importVisible
                && (
                <ImportModule
                  {...this.props}
                  section={importSection}
                  title={importTitle}
                  showModal={showModal}
                  history={history}
                />
                )}
            { repositories.length ? repositories.map((edge) => {
              const visibility = visibilityList.has(edge.node.id)
                ? visibilityList.get(edge.node.id).visibility
                : 'loading';
              const node = containerList.has(edge.node.id)
                && containerList.get(edge.node.id);

              return (
                <LocalPanel
                  key={`${edge.node.owner}/${edge.node.name}`}
                  className="LocalListing__panel"
                  edge={edge}
                  history={history}
                  panelSection={panelSection}
                  node={node}
                  sectionType={sectionType}
                  visibility={visibility}
                  filterText={filterText}
                />
              );
            })
              : !loading && filterText
                && <NoResults setFilterValue={setFilterValue} />}

            <CardLoader
              isLoadingMore={isLoadingMore}
              repeatCount={5}
            />
          </div>
        </div>
      );
    }
    return (<div />);
  }
}

export default LocalListing;
