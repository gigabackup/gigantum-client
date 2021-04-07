// @flow
// vendor
import React, { Component } from 'react';
// components
import RemotePanel from 'Pages/dashboard/repositories/listing/remote/panel/RemotePanel';
import DeleteLabbook from 'Pages/repository/shared/modals/DeleteLabbook';
import DeleteDataset from 'Pages/repository/shared/modals/DeleteDataset';
import CardLoader from 'Pages/dashboard/shared/loaders/CardLoader';
import NoResults from 'Pages/dashboard/shared/NoResults';
import LoginPrompt from 'Pages/repository/shared/modals/LoginPrompt';
// queries
import UserIdentity from 'JS/Auth/UserIdentity';
// store
import store from 'JS/redux/store';
// assets
import './RemoteListing.scss';


type Props = {
  datasetListId: string,
  filterRepositories: Function,
  filterState: string,
  forceLocalView: Function,
  isVisible: Boolean,
  projectListId: string,
  relay: {
    isLoading: Function,
    loadMore: Function,
  },
  remoteDatasets: {
    remoteDatasets: {
      edges: Array<Object>,
      pageInfo: {
        hasNextPage: boolean,
      }
    }
  },
  remoteProjects: {
    remoteLabbooks: {
      edges: Array<Object>,
      pageInfo: {
        hasNextPage: boolean,
      }
    }
  },
  sectionType: string,
  setFilterValue: Function,
};

class RemoteListing extends Component<Props> {
  state = {
    deleteData: {
      remoteId: null,
      remoteOwner: null,
      remoteName: null,
      remoteUrl: null,
      existsLocally: null,
    },
    deleteModalVisible: false,
    showLoginPrompt: false,
  };

  /*
    loads more remote projects on mount
  */
  componentDidMount() {
    const {
      forceLocalView,
      isVisible,
      remoteDatasets,
      remoteProjects,
      sectionType,
    } = this.props;
    if (!isVisible) {
      return;
    }
    const list = sectionType === 'project' ? remoteProjects.remoteLabbooks : remoteDatasets.remoteDatasets;
    if (
      list
      && list.pageInfo.hasNextPage
    ) {
      this._loadMore();
    }

    UserIdentity.getUserIdentity().then((response) => {
      if (navigator.onLine) {
        if (response.data) {
          if (!response.data.userIdentity.isSessionValid) {
            forceLocalView();
          }
        }
      } else {
        forceLocalView();
      }
    });
  }

  /**
    *  @param {}
    *  loads more projects using the relay pagination container
  */
  _loadMore = () => {
    const {
      forceLocalView,
      relay,
      remoteDatasets,
      remoteProjects,
      sectionType,
    } = this.props;

    if (relay.isLoading()) {
      return;
    }
    const list = sectionType === 'project' ? remoteProjects.remoteLabbooks : remoteDatasets.remoteDatasets;
    UserIdentity.getUserIdentity().then((response) => {
      if (navigator.onLine) {
        if (response.data) {
          if (response.data.userIdentity.isSessionValid) {
            if (list.pageInfo.hasNextPage) {
              relay.loadMore(
                8, // Fetch the next 8 items
                () => {
                  const newProps = this.props;
                  const newList = sectionType === 'project' ? newProps.remoteProjects.remoteLabbooks : newProps.remoteDatasets.remoteDatasets;

                  if (
                    newList
                    && newList.pageInfo.hasNextPage
                  ) {
                    this._loadMore();
                  }
                },
              );
            }
          } else {
            forceLocalView();
          }
        }
      } else {
        forceLocalView();
      }
    });
  }

  /**
   *  @param {} -
   *  hides login prompt
  */
  _closeLoginPromptModal = () => {
    this.setState({ showLoginPrompt: false });
  }

  /**
    *  @param {object} deleteData
    *  changes the delete modal's visibility and changes the data passed to it
  */
  _toggleDeleteModal = (deleteData) => {
    if (deleteData) {
      this.setState({
        deleteData,
        deleteModalVisible: true,
      });
    } else {
      this.setState({
        deleteData: {
          remoteId: null,
          remoteOwner: null,
          remoteUrl: null,
          remoteName: null,
          existsLocally: null,
        },
        deleteModalVisible: false,
      });
    }
  }

  render() {
    const {
      isVisible,
      filterRepositories,
      filterState,
      remoteDatasets,
      datasetListId,
      remoteProjects,
      projectListId,
      relay,
      sectionType,
      setFilterValue,
    } = this.props;
    const {
      deleteData,
      deleteModalVisible,
      showLoginPrompt,
    } = this.state;
    if (!isVisible) {
      return null;
    }
    const list = (sectionType === 'project') ? remoteProjects.remoteLabbooks : remoteDatasets.remoteDatasets;
    const { hasNextPage } = list.pageInfo;

    if (
      list
    ) {
      const repositories = filterRepositories(
        list.edges,
        filterState,
      );

      return (
        <div className="Labbooks__listing">
          <div className="grid">
            {
            repositories.length
              ? repositories.map(edge => (
                <RemotePanel
                  {...this.props}
                  toggleDeleteModal={this._toggleDeleteModal}
                  key={edge.node.owner + edge.node.name}
                  edge={edge}
                  existsLocally={edge.node.isLocal}
                />
              ))
              : !relay.isLoading()
            && store.getState().labbookListing.filterText
            && <NoResults setFilterValue={setFilterValue} />
            }
            <CardLoader
              isLoadingMore={hasNextPage}
              repeatCount={5}
            />

          </div>
          {/* TODO: Reuse delete modal */}
          { (deleteModalVisible && (sectionType === 'project'))
            && (
              <DeleteLabbook
                {...deleteData}
                {...this.props}
                labbookListId={projectListId}
                owner={deleteData.remoteOwner}
                name={deleteData.remoteName}
                handleClose={() => { this._toggleDeleteModal(); }}
                remoteConnection="RemoteLabbooks_remoteLabbooks"
                toggleModal={this._toggleDeleteModal}
                remoteDelete
              />
            )}
          { (deleteModalVisible && (sectionType === 'dataset'))
            && (
              <DeleteDataset
                {...deleteData}
                {...this.props}
                datasetListId={datasetListId}
                sectionType="dataset"
                handleClose={() => { this._toggleDeleteModal(); }}
                remoteConnection="RemoteDatasets_remoteDatasets"
                toggleModal={this._toggleDeleteModal}
                owner={deleteData.remoteOwner}
                name={deleteData.remoteName}
                remoteDelete
              />
            )}

          <LoginPrompt
            showLoginPrompt={showLoginPrompt}
            closeModal={this._closeLoginPromptModal}
          />
        </div>
      );
    }

    return (<div />);
  }
}

export default RemoteListing;
