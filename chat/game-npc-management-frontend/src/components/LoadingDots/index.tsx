/**
 * 消息加载中Loading动画
 */

import React from 'react';
import styles from './index.less';

interface IProps {
  size?: number;
}

const LoadingDots: React.FC<IProps> = ({ size = 7 }) => {
  return (
    <div className={styles.loadingDotsContainer}>
      {new Array(3).fill(null).map((item, index) => (
        <span
          key={index}
          className={styles.loadingDot}
          style={{ width: size, height: size }}
        />
      ))}
    </div>
  );
};

export default LoadingDots;
