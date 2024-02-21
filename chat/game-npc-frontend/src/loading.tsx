import logoImg from '@/assets/images/logo.png';
import styles from '@/global.less';
import { Image } from 'antd';

export default function InitDataLoading() {
  return (
    <div className={styles.loadingContainer}>
      <Image
        src={logoImg}
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: 64,
          height: 'auto',
          transform: 'translate(-50%,-50%)',
          imageRendering: 'pixelated',
        }}
      />
    </div>
  );
}
