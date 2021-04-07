// @flow
// vendor
import React from 'react';
import classNames from 'classnames';

// css
import './ProgressLoader.scss';


type Props = {
  isCanceling: boolean,
  isComplete: boolean,
  error: string,
  percentageComplete: Number,
  text: string,
}

const ProgressLoader = ({
  isCanceling,
  isComplete,
  error,
  percentageComplete,
  text,
}:Props) => {
  // declare css here
  const progressCSS = classNames({
    ProgressLoader__progress: true,
    'ProgressLoader__progress--completed': isComplete,
    'ProgressLoader__progress--failed': isCanceling || error,
  });
  const progressTextCSS = classNames({
    ProgressLoader__text: true,
    'ProgressLoader__text--completed': isComplete,
    'ProgressLoader__text--failed': isCanceling || error,
  });

  return (
    <div className="ProgressLoader">
      <div className={progressCSS}>
        {percentageComplete}
      </div>
      <p className={progressTextCSS}>
        {text}
      </p>
    </div>
  );
};


export default ProgressLoader;
