import dispatcher from 'JS/redux/dispatcher';
import * as types from 'JS/redux/constants/constants';

/**
 * actions
 */
export const setErrorMessage = (
  owner,
  name,
  message,
  messageBody,
) => dispatcher(
  types.ERROR_MESSAGE,
  {
    owner,
    name,
    message,
    messageBody,
  },
);

export const setWarningMessage = (
  owner,
  name,
  message,
) => dispatcher(
  types.WARNING_MESSAGE,
  {
    owner,
    name,
    message,
  },
);

export const setInfoMessage = (
  owner,
  name,
  message,
) => dispatcher(
  types.INFO_MESSAGE,
  {
    owner,
    name,
    message,
  },
);

export const setMultiInfoMessage = (
  owner,
  name,
  messageData,
) => {
  messageData.owner = owner;
  messageData.name = name;
  dispatcher(
    types.MULTIPART_INFO_MESSAGE,
    messageData,
  );
};

// upload bar
export const setUploadMessageSetter = (
  uploadMessage,
  id,
  totalFiles,
) => dispatcher(
  types.UPLOAD_MESSAGE_SETTER,
  {
    uploadMessage,
    id,
    totalFiles,
  },
);

export const setUploadMessageUpdate = (
  uploadMessage,
  fileCount,
  progressBarPercentage,
  uploadError,
) => dispatcher(
  types.UPLOAD_MESSAGE_UPDATE,
  {
    uploadMessage,
    fileCount,
    progressBarPercentage,
    uploadError,
  },
);

export const setUploadMessageRemove = (
  uploadMessage,
  id,
  progressBarPercentage,
) => dispatcher(
  types.UPLOAD_MESSAGE_REMOVE,
  {
    uploadMessage,
    id,
    progressBarPercentage,
  },
);


export const setUpdateHistoryView = () => dispatcher(
  types.UPDATE_HISTORY_VIEW,
  {},
);

export const setResizeFooter = () => dispatcher(
  types.RESIZE_FOOTER,
  {},
);

export const setResetFooter = () => dispatcher(
  types.RESET_FOOTER_STORE,
  {},
);
export const setRemoveMessage = id => dispatcher(
  types.REMOVE_MESSAGE,
  { id },
);

// visibility toggles
export const setHelperVisible = helperVisible => dispatcher(
  types.HELPER_VISIBLE,
  { helperVisible },
);

export const setToggleMessageList = (
  messageListOpen,
  viewHistory,
) => dispatcher(
  types.TOGGLE_MESSAGE_LIST,
  {
    messageListOpen,
    viewHistory,
  },
);

export const setUpdateMessageStackItemVisibility = index => dispatcher(
  types.UPDATE_MESSAGE_STACK_ITEM_VISIBILITY,
  { index },
);
export const setUpdateHistoryStackItemVisibility = index => dispatcher(
  types.UPDATE_HISTORY_STACK_ITEM_VISIBILITY,
  { index },
);
