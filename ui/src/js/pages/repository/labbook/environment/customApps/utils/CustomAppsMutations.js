// mutations
import SetBundledAppMutation from 'Mutations/environment/bundledApp/SetBundledAppMutation';
import RemoveBundledAppMutation from 'Mutations/environment/bundledApp/RemoveBundledAppMutation';

class CustomAppsMutations {
  /**
    * @param {Object} props
    *        {string} props.owner
    *        {string} props.name
    *        {string} props.connection
    *        {string} props.parentId
    * pass above props to state
    */
  constructor(props) {
    this.state = props;
  }

  /**
   *  @param {Object} data
   *         {string} data.filename
   *         {string} data.mountPath
   *  @param {function} callback
   *  calls insert secret mutation
   */
  uploadCustomApp(data, callback) {
    const {
      appName,
      description,
      port,
      command,
    } = data;

    const {
      owner,
      name,
    } = this.state;

    SetBundledAppMutation(
      owner,
      name,
      appName,
      description,
      port,
      command,
      callback,
    );
  }

  /**
   *  @param {Object} data
   *         {string} data.appName
   *  @param {function} callback
   *  calls remove customApp mutation
   */
  removeCustomApp(data, callback) {
    const {
      appName,
    } = data;

    const {
      owner,
      name,
    } = this.state;

    RemoveBundledAppMutation(
      owner,
      name,
      appName,
      callback,
    );
  }
}

export default CustomAppsMutations;
