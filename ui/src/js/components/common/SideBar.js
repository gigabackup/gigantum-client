import React, { Component } from 'react';
import classNames from 'classnames';
import { Link } from 'react-router-dom';
// components
import User from './User';
import ToolTip from 'Components/common/ToolTip';
// store
import { setCallbackRoute } from 'JS/redux/reducers/routes';
// config
import config from 'JS/config';

export default class SideBar extends Component {
  constructor(props) {
    super(props);
    this.state = {
      authenticated: null,
    };
  }
  /*
    sets authentication response to the state
  */
  componentDidMount() {
    this.props.auth.isAuthenticated().then((response) => {
      let isAuthenticated = response;
      if (isAuthenticated === null) {
        isAuthenticated = false;
      }
      if (isAuthenticated !== this.state.authenticated) {
        this.setState({ authenticated: isAuthenticated });
      }
    });
  }
  /**
    @param {}
    logout through Auth0
  */
  logout() {
    this.props.auth.logout();
  }
  render() {
    const isLabbooks = (window.location.href.indexOf('projects') > 0) || (window.location.href.indexOf('datasets') === -1);

    const sidebarCSS = classNames({
      'SideBar col-sm-1': this.state.authenticated || this.state.authenticated === null,
      hidden: !(this.state.authenticated || this.state.authenticated === null),
      'is-demo': window.location.hostname === config.demoHostName,
    });
    const projectsCSS = classNames({
      SideBar__icon: true,
      'SideBar__icon--labbooks-selected': isLabbooks,
      'SideBar__icon SideBar__icon--labbooks': !isLabbooks,
    }),
    datasetCSS = classNames({
      SideBar__icon: true,
      'SideBar__icon SideBar__icon--datasets': isLabbooks,
      'SideBar__icon SideBar__icon--datasets-selected': !isLabbooks,
    }),
    labbookSideBarItemCSS = classNames({
      'SideBar__nav-item SideBar__nav-item--labbooks': true,
      'SideBar__nav-item--selected': isLabbooks,
    }),
    datasetSideBarItemCSS = classNames({
      'SideBar__nav-item SideBar__nav-item--datasets': true,
      'SideBar__nav-item--selected': !isLabbooks,
    });
    return (
      <div className={sidebarCSS}>
        <div className="SideBar__inner-container">
          <div className="SideBar__logo" />
          <ul className="SideBar__nav">
            <li
              className="SideBar__list-item Tooltip-data Tooltip-data--right"
              data-tooltip="View Project listing page"
            >
              <Link
                onClick={() => setCallbackRoute('/projects/local')}
                className={labbookSideBarItemCSS}
                to={{ pathname: '/projects/local' }}
              >
                <div
                  className={projectsCSS}
                />
                Projects
              </Link>
              <ToolTip section="labbookListing" />
            </li>
            <li className="SideBar__list-item Tooltip-data Tooltip-data--right"
                data-tooltip="View Dataset listing page"
            >
              <Link
                onClick={() => setCallbackRoute('/datasets/local')}
                className={datasetSideBarItemCSS}
                to={{ pathname: '/datasets/local' }}
              >
                <div className={datasetCSS}
                />
                Datasets
              </Link>
              <ToolTip section="dataSets" />
            </li>
          </ul>

          {
            this.state.authenticated && (
            <User {...this.props} />
              )
          }
        </div>
      </div>
    );
  }
}
