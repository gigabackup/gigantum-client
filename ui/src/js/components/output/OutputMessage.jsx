// vendor
import React from 'react';

type Props = {
 message: string,
};

/**
  Method parses message and returns a cleaned up string with html
  @param {string} message
  @return {string}
*/
const getMessage = (message) => {
  const regex = /(Step [0-9]+\/[0-9]+)/g;
  const percentRegex = /[0-9]+\/[0-9]+/;
  const matches = message.match(regex);
  const lastMatchPct = matches ? matches[matches.length - 1].match(percentRegex)[0].split('/') : [];

  const regexMessage = message.replace(regex, '<span style="color:#fcd430">$1</span>')
  // Backspace (note funny syntax) deletes any previous character
    .replace(/.[\b]/g, '')
  // \r\n should be treated as a regular newline
    .replace(/\r\n/g, '\n')
  // Get rid of anything on a line before a carriage return
  // Using a group because Firefox still doesn't support ES2018 negative look-behind
    .replace(/(\n|^)[^\n]*\r/g, '$1');

  return regexMessage;
};

/**
  Method returns true if message has ansi chacters
  @param {string} message
  @return {boolean}
*/
const hasAnsi = (message) => message.indexOf('\n') > -1;

const OutputMessage = ({ message }: Props) => {
  if (hasAnsi(message)) {
    const html = getMessage(message).replace(/\n/g, '<br />');
    return (
      <div dangerouslySetInnerHTML={{ __html: html }} />
    );
  }

  return (
    <div dangerouslySetInnerHTML={{ __html: message }} />
  );
};

export default OutputMessage;
