import { useEffect, useState } from 'react'
import styles from './index.less';
import { useTheme } from 'antd-style';
import { Avatar, Button, Col, Input, Row, Typography } from "antd";
import { ClearOutlined, LeftCircleOutlined, SendOutlined } from "@ant-design/icons";
import logoImg from '@/assets/images/logo.png';

const { TextArea } = Input;
const { Paragraph } = Typography;

const Conversation = () => {
  const theme = useTheme();
  const [value, setValue] = useState('');

  useEffect(() => {

  }, [])

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
      }}
      className={styles.container}
    >
      <div className={styles.left}>
        <Row>
          <Button size={'large'} type={'link'} style={{ color: '#fff' }} icon={<LeftCircleOutlined />}/>
        </Row>
      </div>
      <div className={styles.chatContainer}>
        <div className={styles.chatList}>

        </div>
        <div className={styles.footer}>
          <Row justify={'center'} align={'middle'} className={styles.chatInput}>
            <Col className={styles.textArea}>
              <TextArea
                placeholder={'相对我说什么，请告诉我～'}
                value={value}
                style={{ border: 'none' }}
                onChange={(e) => setValue(e.target.value)}
                autoSize={{ minRows: 1, maxRows: 1 }}
              />
            </Col>
            <Col className={styles.sendBtn}>
              <Button
                type={'link'}
                icon={<SendOutlined />}
                style={{ color: '#F759AB' }}
              />
            </Col>
          </Row>

          <Col className={styles.resetChat}>
            <Row justify={'center'}>
              <Button size={'small'} type={'link'} style={{ color: '#fff' }} icon={<ClearOutlined />}/>
            </Row>
            <Row justify={'center'} style={{ color: '#fff', fontSize: 12 }}>重置对话</Row>
          </Col>
        </div>
      </div>
      <div className={styles.right}>
        <Row
          justify={'start'}
          align={'bottom'}
        >
          <Col>
            <Avatar src={logoImg} size={48} />
          </Col>
          <Col style={{ marginLeft: 5 }}>御姐</Col>
        </Row>

        <Row>
          <Paragraph style={{ margin: '10px 20px 0 0' }}>
            这是个修仙的世界。她是你的师尊，大乘期巅峰。她之前收过一个弟子。你是她收的第二个弟子。你的师兄因为嫉妒师尊对你的偏爱，多次设计陷害你，导致她对你越来越失望，越来越冷淡。这天，大师兄说你勾结魔教，并模仿你的字迹和文风伪造了一封和魔教来往的书信。她信了，让你跪在她面前。此时你走火入魔了。
          </Paragraph>
        </Row>
      </div>
    </div>
  );
};

export default Conversation;
