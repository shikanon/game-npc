import logoImg from '@/assets/images/logo.png';
import styles from '@/global.less';

export default function InitDataLoading() {
  return (
    <div className={styles.container}>
      <div className={styles.loadingContainer}>
        <div className={styles.loadingLayer}/>
        <img
          src={logoImg}
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: 64,
            height: 'auto',
            transform: 'translate(-50%,-50%)',
            objectFit: 'contain',
            imageRendering: 'pixelated',
          }}
          alt=''
        />
      </div>
    </div>
  );
}
