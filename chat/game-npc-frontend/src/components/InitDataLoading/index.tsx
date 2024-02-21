import React from 'react'
import loadingImg from '@/assets/images/logo.png';
import styles from '@/global.less';

export default function InitDataLoading() {
  return (
    <div className={styles.container}>
      <div className={styles.loadingContainer}>
        <div className={styles.loadingLayer}/>
        <img
          src={loadingImg}
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: 64,
            height: 'auto',
            transform: 'translate(-50%,-50%)',
            objectFit: 'contain',
          }}
        />
      </div>
    </div>
  )
}
