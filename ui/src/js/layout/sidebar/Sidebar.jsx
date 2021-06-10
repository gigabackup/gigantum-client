import React, { Component } from 'react';
import classNames from 'classnames';
import { Link } from 'react-router-dom';
// store
import { setCallbackRoute } from 'JS/redux/actions/routes';
// utils
import getApiURL from 'JS/utils/apiUrl';
// components
import Tooltip from 'Components/tooltip/Tooltip';
import User from './user/User';
// assets
import './Sidebar.scss';


type Props = {
  auth: {
    isAuthenticated: Function,
    logout: Function,
  },
  currentServer: Object,
  diskLow: boolean,
}

class Sidebar extends Component<Props> {
  constructor(props) {
    super(props);
    this.state = {
      authenticated: null,
      version: 'Loading...',
    };
  }

  /*
    sets authentication response to the state
  */
  componentDidMount() {
    const { auth } = this.props;
    const { authenticated } = this.state;
    const apiURL = getApiURL('ping');

    Promise.all([
      fetch(apiURL, { method: 'GET' }),
      auth.isAuthenticated(),
    ])
      .then(([pingResponse, authResponse]) => {
        if (pingResponse.status === 200 && (pingResponse.headers.get('content-type') === 'application/json')) {
          return Promise.all([pingResponse.json(), authResponse]);
        }
        return [{ version: 'Error Fetching Version', authResponse }];
      })
      .then(([pingData, responseData]) => {
        let isAuthenticated = responseData;
        if (isAuthenticated === null) {
          isAuthenticated = false;
        }
        if (isAuthenticated !== authenticated) {
          this.setState({ authenticated: isAuthenticated, version: pingData.version });
        } else {
          this.setState({ version: pingData.version });
        }
      });
  }

  /**
    Mehtod logs user out using session instance of auth
    @param {} -
  */
  logout = () => {
    const { auth } = this.props;
    auth.logout();
  }

  render() {
    const { authenticated, version } = this.state;
    const { diskLow } = this.props;
    const isLabbooks = (window.location.href.indexOf('projects') > 0) || (window.location.href.indexOf('datasets') === -1);
    // declare css here
    const sidebarCSS = classNames({
      'SideBar col-sm-1': authenticated || authenticated === null,
      hidden: !(authenticated || authenticated === null),
      'SideBar--disk-low': diskLow,
    });
    const projectsCSS = classNames({
      SideBar__icon: true,
      'SideBar__icon--labbooks': true,
    });
    const datasetCSS = classNames({
      SideBar__icon: true,
      'SideBar__icon SideBar__icon--datasets': true,
    });
    const labbookSideBarItemCSS = classNames({
      'SideBar__nav-item SideBar__nav-item--labbooks flex': true,
      'SideBar__nav-item--selected': isLabbooks,
    });
    const datasetSideBarItemCSS = classNames({
      'SideBar__nav-item SideBar__nav-item--datasets flex': true,
      'SideBar__nav-item--selected': !isLabbooks,
    });

    return (
      <aside className={sidebarCSS}>
        <div className="SideBar__inner-container">
          <div className="SideBar__logo" />
          <ul className="SideBar__nav">
            <li
              className="SideBar__list-item Tooltip-data Tooltip-data--right relative"
              data-tooltip="View Project listing page"
            >
              <Link
                onClick={() => setCallbackRoute('/projects/local')}
                className={labbookSideBarItemCSS}
                to={{ pathname: '/projects/local' }}
              >
                <div className={projectsCSS} />
                Projects
              </Link>
              <Tooltip section="labbookListing" />
            </li>
            <li
              className="SideBar__list-item Tooltip-data Tooltip-data--right relative"
              data-tooltip="View Dataset listing page"
            >
              <Link
                onClick={() => setCallbackRoute('/datasets/local')}
                className={datasetSideBarItemCSS}
                to={{ pathname: '/datasets/local' }}
              >
                <div className={datasetCSS} />
                Datasets
              </Link>
              <Tooltip section="datasetsTooltip" />
            </li>
          </ul>

          {
            authenticated && (<User {...this.props} />)
          }
          <div className="SideBar__version">
            <a
              className="SideBar__link"
              href={getApiURL('ping')}
              rel="noreferrer"
              target="_blank"
            >
              {`Version: ${version}`}
            </a>
          </div>
        </div>
      </aside>
    );
  }
}

export default Sidebar;
