import { useEffect } from 'react'
import styles from './index.less';
import { useTheme } from 'antd-style';
import { Card, Col, Row } from "antd";
import claracterBg1 from '@/assets/images/character_bg_1.png';
import claracterBg2 from '@/assets/images/character_bg_2.png';
import claracterBg3 from '@/assets/images/character_bg_3.png';

const { Meta } = Card;

const Character = () => {
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
        justify={'center'}
        className={styles.title}
      >
        来跟我聊天吧!
      </Row>

      <Row gutter={16} justify={'space-evenly'} style={{ marginTop: 30 }}>
        <Col>
          <Card
            hoverable
            style={{ width: 300 }}
            cover={<img alt="example" src={claracterBg3} />}
          >
            <Meta title="萝莉" description="www.instagram.com" />
          </Card>
        </Col>
        <Col>
          <Card
            hoverable
            style={{ width: 300 }}
            cover={<img alt="example" src={claracterBg1} />}
          >
            <Meta title="御姐" description="www.instagram.com" />
          </Card>
        </Col>
        <Col>
          <Card
            hoverable
            style={{ width: 300 }}
            cover={<img alt="example" src={claracterBg2} />}
          >
            <Meta title="清纯" description="www.instagram.com" />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Character;
