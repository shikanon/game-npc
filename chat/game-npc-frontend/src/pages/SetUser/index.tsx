import { useEffect } from 'react'
import styles from './index.less';
import { useTheme } from 'antd-style';
import { Button, Col, Row, Space } from "antd";

const Login = () => {
  const theme = useTheme();

  useEffect(() => {

  }, [])

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
      }}
      className={styles.container}
    >
      <Row
        className={styles.title}
      >
        请选择你的性别
      </Row>

      <div className={styles.selectedSex}>
        <div>男</div>
        <div>女</div>
      </div>

      <Row justify={'center'} style={{ marginTop: 100 }}>
        <Button type={'primary'} style={{ background: 'linear-gradient(to right, #F8DA77, #ED6BC9)', border: 'none' }}>
          开始聊天!
        </Button>
      </Row>
    </div>
  );
};

export default Login;
