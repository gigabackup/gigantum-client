// @flow
// vendor
import React, { Component } from 'react';
import ReactMarkdown from 'react-markdown';
import classNames from 'classnames';
// mutations
import WriteLabbookReadmeMutation from 'Mutations/repository/readme/WriteLabbookReadmeMutation';
import WriteDatasetReadmeMutation from 'Mutations/repository/readme/WriteDatasetReadmeMutation';
// store
import { setErrorMessage } from 'JS/redux/actions/footer';
// components
import MarkdownEditor from 'Components/markdownEditor/MarkdownEditor';
import Base from 'Pages/repository/labbook/environment/Base';
import Type from 'Pages/repository/dataset/overview/type/Type';
import RecentActivity from 'Pages/repository/labbook/overview/RecentActivity';
import Loader from 'Components/loader/Loader';
import CodeBlock from 'Pages/repository/labbook/renderers/CodeBlock';
import Tooltip from 'Components/tooltip/Tooltip';
import Summary from 'Pages/repository/dataset/overview/summary/Summary';
import EmptyReadme from './EmptyReadme';

// assets
import './Overview.scss';

/**
  @param {}
  sets element to expand
 */
const checkOverflow = (element) => {
  const curOverflow = element.style.overflow;
  const isOverflowing = element.clientWidth < element.scrollWidth
     || element.clientHeight < element.scrollHeight;

  if (!curOverflow || curOverflow === 'visible') {
    element.style.overflow = 'hidden';
  }

  element.style.overflow = curOverflow;

  return isOverflowing;
};


type Props = {
  datasetType: string,
  history: {
    push: Function,
  },
  isManaged: boolean,
  name: string,
  owner: string,
  sectionType: string,
  refetch: Function,
  scrollToTop: Function,
}


class Overview extends Component<Props> {
  state = {
    editingReadme: false,
    readmeExpanded: false,
    overflowExists: false,
    editorFullscreen: false,
    markdown: '',
  };

  /*
    runs state check when component mounts
  */
  componentDidMount() {
    const { refetch } = this.props;
    this._setExpand();
    refetch('overview');
  }

  /*
    runs state check when component updates
  */
  componentDidUpdate() {
    this._setExpand();
  }

  /**
   @param {} -
     sets to toggle fullscreen
   */
  _fullscreen = () => {
    this.setState((state) => {
      const editorFullscreen = !state.editorFullscreen;
      return { editorFullscreen };
    });
  }

  /**
   @param {} -
     sets to toggle fullscreen
   */
  _openEditor = () => {
    this.setState({ editorFullscreen: true });
  }

  /**
   @param {}
   sets element to expand
   */
  _setExpand = () => {
    const { state } = this;
    const element = document.getElementsByClassName('ReadmeMarkdown')[0];

    if (element && checkOverflow(element) && !state.overflowExists) {
      this.setState({ overflowExists: true });
    } else if (element && !checkOverflow(element) && state.overflowExists) {
      this.setState({ overflowExists: false });
    }
  }

  /**
   @param {}
   reverts readme to have a max size
   resets vertical scroll
   */
  _toggleReadme = (readmeExpanded) => {
    if (!readmeExpanded) {
      if (window.pageYOffset > 345) {
        window.scrollTo(0, 345);
      }
    }
    this.setState({ readmeExpanded: !readmeExpanded });

    this._setExpand();
  }

  /**
   @param {Boolean} editingReadme
   sets state for editing readme
   */
  _setEditingReadme = (editingReadme) => {
    this.setState({ editingReadme });
  }

  /**
   @param {}
   sets readme state to false
   */
  _closeReadme = () => {
    this.setState({ editingReadme: false });
  }

  /**
   @param {String} owner
   @param {String} name
   calls mutation to save labbook readme
   */
  _saveLabbookReadme = (owner, name) => {
    const { markdown } = this.state;
    WriteLabbookReadmeMutation(
      owner,
      name,
      markdown,
      (res, error) => {
        if (error) {
          console.log(error);
          setErrorMessage(owner, name, 'Readme was not set: ', error);
        } else {
          this.setState({ editingReadme: false });
        }
      },
    );
  }

  /**
   @param {String} owner
   @param {String} name
   calls mutation to save dataset readme
   */
  _saveDatasetReadme = (owner, name) => {
    const { markdown } = this.state;
    WriteDatasetReadmeMutation(
      owner,
      name,
      markdown,
      (res, error) => {
        if (error) {
          console.log(error);
          setErrorMessage(owner, name, 'Readme was not set: ', error);
        } else {
          this.setState({ editingReadme: false });
        }
      },
    );
  }

  /**
   @param {}
   handles calling mutation functions to save readme
   */
  _saveReadme = () => {
    const {
      owner,
      name,
      sectionType,
    } = this.props;

    if (sectionType === 'labbook') {
      this._saveLabbookReadme(owner, name);
    } else {
      this._saveDatasetReadme(owner, name);
    }
  }

  /**
    @param {String} section
    handles redirect and scrolling to top
  */
  _handleRedirect = (section) => {
    const {
      owner,
      name,
      history,
      scrollToTop,
    } = this.props;
    scrollToTop();
    history.push(`/projects/${owner}/${name}/${section}`);
  }

  /**
    * Method updates markdown in state
     @param {Object} event
   */
   _updateMarkdownText = (value) => {
     if (value) {
       this.setState({ markdown: value });
     }
   }

   render() {
     // destructure here
     const {
       datasetType,
       name,
       owner,
       sectionType,
       scrollToTop,
       history,
       isManaged,
     } = this.props;
     const {
       editingReadme,
       editorFullscreen,
       markdown,
       overflowExists,
       readmeExpanded,
     } = this.state;
     // declare variables here
     const sectionProps = this.props[sectionType];
     const isLabbook = (sectionType === 'labbook');
     const typeText = isLabbook ? 'Environment' : 'Type';
     const showLoadMoreButton = overflowExists
      || (readmeExpanded && !overflowExists);
     const overViewComponent = (isLabbook && sectionProps.overview)
       ? (
         <RecentActivity
           name={name}
           owner={owner}
           recentActivity={sectionProps.overview.recentActivity}
           scrollToTop={scrollToTop}
           history={history}
         />
       )
       : (
         <Summary
           name={name}
           owner={owner}
           isManaged={isManaged}
           {...sectionProps.overview}
         />
       );

     // decalre css here
     const overviewCSS = classNames({
       Overview: true,
       'Overview--fullscreen': editorFullscreen,
     });
     const readmeCSS = classNames({
       'ReadmeMarkdown Markdown': true,
       'ReadmeMarkdown--collapsed': !readmeExpanded,
       'ReadmeMarkdown--expanded': readmeExpanded,

     });
     const overviewReadmeCSS = classNames({
       'Overview__readme Readme Card Card--auto Card--no-hover column-1-span-12': !editingReadme,
       hidden: editingReadme,
     });
     const overviewReadmeButtonCSS = classNames({
       'Btn Btn--feature Btn__edit Btn__edit--featurePosition': true,
       hidden: editingReadme,
     });

     const loadMoreCSS = classNames({
       'Btn Btn__expandadble': true,
       'Btn__expandadble--expand': !readmeExpanded,
       'Btn__expandadble--collapse': readmeExpanded,
     });

     if (sectionProps && sectionProps.overview) {
       return (

         <div className={overviewCSS}>
           { overViewComponent }

           <div className="Overview__container">

             <h4 className="Overview__title">
               Readme
               <Tooltip section="readMe" />
             </h4>

           </div>

           { editingReadme
            && (
              <div className="Overview__readme--editing Markdown column-1-span-12">
                <MarkdownEditor
                  {...this.props}
                  markdown={sectionProps.overview.readme || markdown}
                  updateMarkdownText={this._updateMarkdownText}
                />
                <div className="Overview__readme--editing-buttons">
                  <button
                    type="button"
                    className="Overview__readme-cancel Btn--flat"
                    onClick={() => { this._closeReadme(); }}
                  >
                    Cancel
                  </button>

                  <button
                    type="button"
                    className="Overview__readme-save Btn--last"
                    disabled={false}
                    onClick={() => { this._saveReadme(); }}
                  >
                    Save
                  </button>
                </div>
              </div>
            )}
           { sectionProps.overview.readme
             ? (
               <div className="grid">
                 <div className={overviewReadmeCSS}>
                   <button
                     type="button"
                     className={overviewReadmeButtonCSS}
                     onClick={() => this._setEditingReadme(true)}
                   >
                     <span>Edit Readme</span>
                   </button>
                   <ReactMarkdown
                     className={readmeCSS}
                     source={sectionProps.overview.readme}
                     renderers={{ code: props => <CodeBlock {...props} /> }}
                   />

                   { (overflowExists && !readmeExpanded)
                      && <div className="Overview__readme-fadeout" />}
                   { showLoadMoreButton
                    && (
                      <div className="Overview__readme-buttons">
                        <div className="Overview__readme-bar-less">
                          <button
                            type="button"
                            className={loadMoreCSS}
                            onClick={() => this._toggleReadme(readmeExpanded)}
                          />
                        </div>
                      </div>
                    )}
                 </div>
               </div>
             )
             : !editingReadme
              && (
                <EmptyReadme
                  sectionType={sectionType}
                  editingReadme={editingReadme}
                  setEditingReadme={this._setEditingReadme}
                />
              )}

           <div className="Overview__container">
             <h4>
               {typeText}
               <Tooltip section="environmentOverview" />
             </h4>
           </div>

           { isLabbook
             ? (
               <div className="grid">
                 <div className="Overview__environment column-1-span-12">
                   <button
                     type="button"
                     className="Btn Btn--feature Btn__redirect Btn__redirect--featurePosition Btn__overview"
                     onClick={() => this._handleRedirect('environment')}
                   >
                     <span>View Environment Details</span>
                   </button>
                   <Base
                     environment={sectionProps.environment}
                     blockClass="Overview"
                     overview={sectionProps.overview}
                   />

                 </div>
               </div>
             )
             : (
               <div className="Overview__environment">
                 <Type
                   type={datasetType}
                   isManaged={isManaged}
                 />
               </div>
             )}
         </div>
       );
     }

     return (<Loader />);
   }
}

export default Overview;
