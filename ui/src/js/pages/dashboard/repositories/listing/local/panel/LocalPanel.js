// @flow
// vendor
import React, { Component } from 'react';
import Highlighter from 'react-highlight-words';
import { Link } from 'react-router-dom';
import Moment from 'moment';
import classNames from 'classnames';
// components
import RepositoryTitle from 'Pages/dashboard/shared/title/RepositoryTitle';
// muations
import StartContainerMutation from 'Mutations/container/StartContainerMutation';
import StopContainerMutation from 'Mutations/container/StopContainerMutation';
// store
import { setErrorMessage, setInfoMessage } from 'JS/redux/actions/footer';
// assets
import './LocalPanel.scss';

type Props = {
  edge: {
    node: {
      name: string,
      owner: string,
      description: string,
      creationDateUtc: string,
      modifiedOnUtc: string,
    }
  },
  panelSection: string,
  sectionType: string,
  visibility: string,
  filterText: string,
};

/**
*  project panel is to only render the edge passed to it
*/
class LocalPanel extends Component<Props> {
  state = {
    exportPath: '',
    status: 'loading',
    textStatus: '',
    name: this.props.edge.node.name,
    owner: this.props.edge.node.owner,
    cssClass: 'loading',
  };

  /** *
  * @param {Object} nextProps
  * processes container lookup and assigns container status to project card
  */
  static getDerivedStateFromProps(nextProps, state) {
    if (!nextProps.sectionType === 'project') {
      return;
    }
    const { environment } = nextProps.node;
    let status;
    let textStatus;
    if (environment) {
      const { containerStatus, imageStatus } = environment;
      status = 'Running';
      status = (containerStatus === 'NOT_RUNNING') ? 'Stopped' : status;
      status = (imageStatus === 'BUILD_IN_PROGRESS' || imageStatus === 'BUILD_QUEUED') ? 'Building' : status;
      status = (imageStatus === 'BUILD_FAILED') ? 'Rebuild' : status;
      status = ((imageStatus === 'DOES_NOT_EXIST') || (imageStatus === null)) ? 'Rebuild' : status;

      status = ((state.status === 'Starting') && (containerStatus !== 'RUNNING')) || (state.status === 'Stopping' && (containerStatus !== 'NOT_RUNNING')) ? state.status : status;

      textStatus = (status === 'Rebuild') ? 'Stopped' : status;
      textStatus = (state.textStatus === 'Start') ? 'Start' : textStatus;
      textStatus = (state.textStatus === 'Stop') ? 'Stop' : textStatus;
    }

    return {
      ...state,
      status,
      textStatus,
      cssClass: status,
    };
  }

  /** *
  * @param {string} status
  * fires when a componet mounts
  * adds a scoll listener to trigger pagination
  */
  _stopStartContainer = (evt, status) => {
    const { owner, name } = this.state;
    evt.preventDefault();
    evt.stopPropagation();
    evt.nativeEvent.stopImmediatePropagation();
    if (status === 'Stopped') {
      this._startContainerMutation();
    } else if (status === 'Running') {
      this._stopContainerMutation();
    } else if (status === 'loading') {
      setInfoMessage(owner, name, 'Container status is still loading. The status will update when it is available.');
    } else if (status === 'Building') {
      setInfoMessage(owner, name, 'Container is still building and the process may not be interrupted.');
    } else {
      this._rebuildContainer();
    }
  }

  /** *
  * @param {string} status
  * starts project conatainer
  */
  _startContainerMutation = () => {
    const self = this;
    const { owner, name } = this.state;

    setInfoMessage(owner, name, `Starting ${name} container`);

    this.setState({ status: 'Starting', textStatus: 'Starting' });

    StartContainerMutation(
      owner,
      name,
      (response, error) => {
        if (error) {
          setErrorMessage(owner, name, `There was a problem starting ${name}, go to Project and try again`, error);
        } else {
          self.props.history.replace(`../../projects/${owner}/${name}`);
        }
      },
    );
  }

  /** *
  * @param {string} status
  * stops project container
  */
  _stopContainerMutation = () => {
    const { owner, name } = this.state;

    const self = this;
    setInfoMessage(owner, name, `Stopping ${name} container`);
    this.setState({ status: 'Stopping', textStatus: 'Stopping' });

    StopContainerMutation(
      owner,
      name,
      (response, error) => {
        if (error) {
          console.log(error);
          setErrorMessage(owner, name, `There was a problem stopping ${name} container`, error);
          self.setState({ textStatus: 'Running', status: 'Running' });
        } else {
          // this.setState({ status: 'Stopped', textStatus: 'Stopped' });
        }
      },
    );
  }

  /** *
  * @param {object,string} evt,status
  * stops labbbok conatainer
  ** */
  _updateTextStatusOver = (evt, isOver, status) => {
    if (isOver) {
      if (status === 'Running') {
        this.setState({ textStatus: 'Stop' });
      } else if (status === 'Stopped') {
        this.setState({ textStatus: 'Start' });
      }
    } else {
      this.setState({ textStatus: status });
    }
  }

  /** *
  * @param {objectstring} evt,status
  * stops labbbok conatainer
  ** */
  _updateTextStatusOut = (evt, status) => {
    if (status !== 'loading') {
      this.setState({ textStatus: status });
    }
  }

  render() {
    const { state } = this;
    const {
      edge,
      panelSection,
      sectionType,
      visibility,
      filterText,
    } = this.props;
    const {
      name,
      owner,
      description,
      creationDateUtc,
      modifiedOnUtc,
    } = edge.node;
    const {
      status,
      textStatus,
      cssClass,
    } = state;

    const containerCSS = classNames({
      [`ContainerStatus__container-state ContainerStatus__containerStatus--state ${cssClass} box-shadow`]: true,
      'Tooltip-data': cssClass === 'Rebuild',
    });

    return (
      <Link
        to={`/${sectionType}s/${owner}/${name}`}
        key={`local${name}`}
        className="Card Card--225 Card--text column-4-span-3 flex flex--column justify--space-between"
      >

        <div className="LocalPanel__row--icons">
          <div
            data-tooltip={`${visibility}`}
            className={`Tooltip LocalPanel__visibility LocalPanel__visibility--${visibility} Tooltip-data Tooltip-data--small`}
          />
          <div className={`LocalPanel__${sectionType}-icon`} />
          {
            (sectionType === 'project')
            && (
              <div className="LocalPanel__containerStatus">

                <div
                  role="presentation"
                  type="button"
                  data-tooltip="Rebuild Required, container will attempt to rebuild before starting."
                  onClick={evt => this._stopStartContainer(evt, cssClass)}
                  onMouseOver={evt => this._updateTextStatusOver(evt, true, status)}
                  onMouseOut={evt => this._updateTextStatusOut(evt, false, status)}
                  onFocus={() => {}}
                  onBlur={() => {}}
                  className={containerCSS}
                >
                  <div className="ContainerStatus__text">{ textStatus }</div>
                  <div className="ContainerStatus__toggle">
                    <div className="ContainerStatus__toggle-btn" />
                  </div>
                </div>
              </div>
            )
          }
        </div>

        <div className="LocalPanel__row--text">
          <div>
            <RepositoryTitle
              name={name}
              section={panelSection}
              filterText={filterText}
            />
          </div>
          <p className="LocalPanel__paragraph LocalPanel__paragraph--owner">{owner}</p>
          <p className="LocalPanel__paragraph LocalPanel__paragraph--metadata">
            <span className="bold">Created:</span>
            {' '}
            {Moment(creationDateUtc).format('MM/DD/YY')}
          </p>
          <p className="LocalPanel__paragraph LocalPanel__paragraph--metadata">
            <span className="bold">Modified:</span>
            {' '}
            {Moment(modifiedOnUtc).fromNow()}
          </p>

          <p className="LocalPanel__paragraph LocalPanel__paragraph--description">
            {
              description && description.length
                ? (
                  <Highlighter
                    highlightClassName="LocalPanel__highlighted"
                    searchWords={[filterText]}
                    autoEscape={false}
                    caseSensitive={false}
                    textToHighlight={description}
                  />
                )
                : (
                  <span> No description provided</span>
                )
            }
          </p>

        </div>
      </Link>
    );
  }
}

export default LocalPanel;
