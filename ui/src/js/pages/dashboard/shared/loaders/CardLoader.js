// vendor
import React from 'react';
import classNames from 'classnames';
// assets
import './CardLoader.scss';

const CardLoader = ({ isLoadingMore, repeatCount }) => {

  return (
    <>
      {
        Array(repeatCount).fill(1).map((value, index) => {
          const loaderCSS = classNames({
            [`Card Card--225 column-4-span-3 flex flex--column justify--space-between CardLoader CardLoader--${index}`]: isLoadingMore,
            'CardLoader--hidden': !isLoadingMore,
          });
          return (
            <div
              key={`Card__loader--${index}`}
              className={loaderCSS}
            >
              <div />
            </div>
          );
        })
      }
    </>
  );
};

export default CardLoader;
