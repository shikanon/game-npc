import leaveImg from '@/assets/images/leave.png';
import userImg from '@/assets/images/user.png';
import LoadingDots from '@/components/LoadingDots';
import { INPCAllInfo } from '@/interfaces/game_npc';
import gameNpcService from '@/services/game_npc';
import { getHashParams } from '@/utils';
import { ClearOutlined, LeftOutlined, SendOutlined } from '@ant-design/icons';
import { history, useModel } from '@umijs/max';
import { useRequest } from 'ahooks';
import { App, Avatar, Button, Col, Image, Input, Row, Typography } from 'antd';
import { useTheme } from 'antd-style';
import { useEffect, useState } from 'react';
import styles from './index.less';

const { TextArea } = Input;
const { Paragraph, Text } = Typography;

interface IChatItem {
  from: 'npc' | 'user';
  status?: 'wait' | 'success' | 'fail';
  content?: string | null;
  contentType?: 'text' | 'image' | null;
}

const Conversation = () => {
  const theme = useTheme();
  const { message } = App.useApp();
  const { userInfo } = useModel('user');

  const [npcAllInfo, setNpcAllInfo] = useState<INPCAllInfo | null>(null);
  const [question, setQuestion] = useState('');
  const [chatList, setChatList] = useState<IChatItem[]>([]);

  // 获取NPC全部信息
  const {
    // loading: getNPCAllInfoLoading,
    runAsync: getNPCAllInfoRequest,
  } = useRequest(gameNpcService.GetNPCAllInfo, { manual: true });

  // NPC聊天
  const { loading: npcChatLoading, runAsync: npcChatRequest } = useRequest(
    gameNpcService.NPCChat,
    { manual: true },
  );

  // 清除NPC聊天历史
  const { loading: clearNPCHistoryLoading, runAsync: clearNPCHistoryRequest } =
    useRequest(gameNpcService.ClearNPCHistory, { manual: true });

  /**
   * 滚动到底部
   */
  const scrollToBottom = () => {
    const chatListScroll = document.getElementById('chatListScroll');
    setTimeout(() => {
      if (chatListScroll) {
        chatListScroll.scrollTop = chatListScroll.scrollHeight;
      }
    }, 300);
  };

  /**
   * 获取NPC全部信息
   */
  const getNPCAllInfo = async () => {
    const result = await getNPCAllInfoRequest({
      npcId: getHashParams()?.characterId || '',
      userId: userInfo?.id || '',
    });
    console.log(result, '当前NPC全部信息');

    if (result?.data) {
      setNpcAllInfo(result.data);

      if (result?.data?.dialogueContext?.length) {
        const chatList: IChatItem[] =
          result?.data?.dialogueContext?.map((item) => {
            return {
              from: item?.roleTo?.includes(result?.data?.npcId)
                ? 'user'
                : 'npc',
              status: 'success',
              content: item?.content || null,
              contentType: item?.contentType || null,
            };
          }) || [];
        console.log(chatList, '对话列表');
        setChatList(chatList);

        // 滚动到底部
        scrollToBottom();
      }
    }
  };

  /**
   * 发起NPC聊天
   */
  const sendNPCChat = async () => {
    // 组装我发送的信息
    const waitChatList = JSON.parse(JSON.stringify(chatList));
    waitChatList.push({ from: 'user', content: question });
    waitChatList.push({ from: 'npc', status: 'wait', content: '' });
    setChatList(waitChatList);
    setQuestion('');

    scrollToBottom();

    const result = await npcChatRequest({
      question: question,
      userId: userInfo?.id || '',
      npcId: getHashParams()?.characterId || '',
      scene: npcAllInfo?.scene || '',
      contentType: 'text',
    });
    console.log(result, '对话信息');

    // 更新waitChatList中最后一项NPC发送的信息
    if (result?.data?.message) {
      waitChatList[waitChatList.length - 1].status = 'success';
      waitChatList[waitChatList.length - 1].content = result.data.message;
      setChatList(waitChatList);
    } else {
      waitChatList[waitChatList.length - 1].status = 'fail';
      waitChatList[waitChatList.length - 1].content = '回答失败，请重试';
      setChatList(waitChatList);
    }
  };

  /**
   * 清空NPC聊天记录
   */
  const clearNPCHistory = async () => {
    const result = await clearNPCHistoryRequest({
      userId: userInfo?.id || '',
      npcId: getHashParams()?.characterId || '',
    });

    if (result?.code === 0) {
      setChatList([]);

      message.success('重置对话成功');
    } else {
      message.warning(result?.msg);
    }
  };

  useEffect(() => {
    if (userInfo) {
      getNPCAllInfo().then();
    }
  }, [userInfo]);

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
        backgroundImage: `url(${npcAllInfo?.chatBackground || ''})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
      className={styles.container}
    >
      <div className={styles.left}>
        <Row style={{ marginTop: 20 }}>
          <Button
            shape={'circle'}
            size={'large'}
            style={{ color: '#ff7875', border: '2px solid #ff7875' }}
            icon={<LeftOutlined />}
            onClick={() => {
              history.push('/character');
            }}
          />
        </Row>
      </div>
      <div
        className={styles.chatContainer}
        style={{
          backgroundColor: theme.colorBgLayout,
          backgroundImage: `url(${npcAllInfo?.chatBackground || ''})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center center',
          backgroundRepeat: 'no-repeat',
        }}
      >
        <div id="chatListScroll" className={styles.chatList}>
          {chatList.map((item, index) => {
            if (item.from === 'user') {
              return (
                <Row
                  key={index}
                  justify={'end'}
                  align={'top'}
                  wrap={false}
                  style={{ marginBottom: 10, paddingLeft: 40 }}
                >
                  <Col className={styles.userChatItem}>
                    <Text className={styles.content}>{item.content}</Text>
                  </Col>
                  <Col>
                    <Avatar src={userImg} size={32} />
                  </Col>
                </Row>
              );
            } else {
              return (
                <Row
                  key={index}
                  justify={'start'}
                  align={'top'}
                  wrap={false}
                  style={{ marginBottom: 10, paddingRight: 40 }}
                >
                  <Col>
                    <Avatar src={npcAllInfo?.profile || ''} size={32} />
                  </Col>
                  <Col className={styles.npcChatItem}>
                    {item?.status === 'wait' ? <LoadingDots /> : null}
                    {item?.status === 'success' ? (
                      <Text className={styles.content}>{item.content}</Text>
                    ) : null}
                    {item?.status === 'fail' ? (
                      <Text className={styles.content}>{item.content}</Text>
                    ) : null}
                  </Col>
                </Row>
              );
            }
          })}
        </div>
        <div className={styles.footer}>
          <Row justify={'start'} align={'middle'} className={styles.chatInput}>
            <Col className={styles.textArea}>
              <TextArea
                placeholder={
                  '想对我说什么，请告诉我～ 😊'
                  // 按"Enter"键发送，按"Shift+Enter"换行
                }
                value={question}
                style={{
                  border: 'none',
                  outline: 'none',
                  boxShadow: 'none',
                  textAlign: 'center',
                }}
                autoFocus
                tabIndex={0}
                maxLength={500}
                autoSize={{ minRows: 1, maxRows: 5 }}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(event) => {
                  const target = event.target as HTMLInputElement;
                  if (event.key === 'Enter' && event.shiftKey) {
                    setQuestion(target.value);
                  } else if (event.key === 'Enter') {
                    event.preventDefault();

                    // 发送聊天
                    if (!npcChatLoading) {
                      sendNPCChat().then();
                    }
                  }
                }}
              />
            </Col>
            <Col className={styles.sendBtn}>
              <Button
                type={'link'}
                icon={<SendOutlined />}
                style={
                  question === '' ? { color: '#8c8c8c' } : { color: '#F759AB' }
                }
                disabled={npcChatLoading}
                loading={npcChatLoading}
                onClick={() => {
                  // 发送聊天
                  sendNPCChat().then();
                }}
              />
            </Col>
          </Row>

          <Col
            className={styles.resetChat}
            onClick={() => {
              clearNPCHistory().then();
            }}
          >
            <Row justify={'center'}>
              <Button
                size={'small'}
                type={'link'}
                // style={{ color: '#fff' }}
                icon={<ClearOutlined />}
                loading={clearNPCHistoryLoading}
              />
            </Row>
            <Row justify={'center'} style={{ fontSize: 12 }}>
              重置对话
            </Row>
          </Col>
        </div>
      </div>
      <div className={styles.right}>
        <Row justify={'start'} align={'bottom'}>
          <Col>
            <Avatar src={npcAllInfo?.profile || ''} size={48} />
          </Col>
          <Col style={{ marginLeft: 5 }}>{npcAllInfo?.name || '-'}</Col>
        </Row>

        <Row>
          <Paragraph style={{ margin: '10px 20px 0 0' }}>
            {npcAllInfo?.shortDescription || '-'}
          </Paragraph>
        </Row>
      </div>
    </div>
  );
};

export default Conversation;
