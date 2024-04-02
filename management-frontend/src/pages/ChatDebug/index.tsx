import userImg from '@/assets/images/user.png';
import LoadingDots from '@/components/LoadingDots';
import { INPCAllInfo, INPCInfo, NPCCharacterSexEnum } from '@/interfaces/game_npc';
import gameNpcService from '@/services/game_npc';
import { getHashParams } from '@/utils';
import { ClearOutlined, SendOutlined, UserOutlined } from '@ant-design/icons';
import { useMount, useRequest } from 'ahooks';
import { App, Avatar, Button, Col, Form, Image, Input, Radio, Row, Typography } from 'antd';
import React, { useState } from 'react';
import styles from './index.less';
import npcService from "@/services/game_npc";

const { TextArea } = Input;
const { Paragraph, Text } = Typography;

interface IChatItem {
  from: 'npc' | 'user';
  status?: 'wait' | 'success' | 'fail';
  content?: string | null;
  contentType?: 'text' | 'image' | null;
}

const ChatDebug = () => {
  const { message } = App.useApp();
  const [form] = Form.useForm();

  const [npcConfig, setNpcConfig] = useState<INPCInfo | null>(null);
  const [npcAllInfo, setNpcAllInfo] = useState<INPCAllInfo | null>(null);
  const [question, setQuestion] = useState('');
  const [chatList, setChatList] = useState<IChatItem[]>([]);

  const { runAsync: updateNPCRequest, loading: updateNPCLoading } = useRequest(
    npcService.UpdateNPC,
    { manual: true },
  );

  const { runAsync: getNPCInfoRequest, loading: getNPCInfoLoading } =
    useRequest(npcService.GetNPCInfo, { manual: true });

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
   * 获取NPC信息
   */
  const getNPCInfo = async () => {
    const result = await getNPCInfoRequest({ id: getHashParams()?.characterId });
    console.log(result, '查询结果');
    if (result?.data) {
      setNpcConfig(result.data);
      form.setFieldsValue({
        name: result.data.name,
        sex: result.data.sex,
        shortDescription: result.data.shortDescription,
        promptDescription: result.data.promptDescription,
      });
    }
  };

  /**
   * 获取NPC全部信息
   */
  const getNPCAllInfo = async () => {
    const result = await getNPCAllInfoRequest({
      npcId: getHashParams()?.characterId || '',
      userId: 'ace460f7-e6df-4b0c-8961-cfad6ab836b8',
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
      userId: 'ace460f7-e6df-4b0c-8961-cfad6ab836b8',
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
      userId: 'ace460f7-e6df-4b0c-8961-cfad6ab836b8',
      npcId: getHashParams()?.characterId || '',
    });

    if (result?.code === 0) {
      setChatList([]);
      message.success('重置对话成功');
    } else {
      message.warning(result?.msg);
    }
  };

  /**
   * 更新NPC配置
   */
  const updateConfig = async () => {
    form.validateFields().then(async (values) => {
      console.log(values);

      const result = await updateNPCRequest({
        ...values,
        id: getHashParams()?.characterId,
      });
      console.log(result, '更新结果');

      if (result?.code === 0) {
        message.success('更新成功');

        getNPCInfo().then();
        getNPCAllInfo().then();
      } else {
        message.warning(result?.msg);
      }
    });
  };

  useMount(() => {
      getNPCInfo().then();
      getNPCAllInfo().then();
  });

  return (
    <div
      style={{
        // backgroundImage: `url(${npcAllInfo?.chatBackground || ''})`,
      }}
      className={styles.container}
    >
      <div className={styles.left}>
        <Row justify={'space-between'} align={'middle'}>
          <Col>
            <Button
              type={'primary'}
              onClick={() => {
                history.back();
              }}
            >
              返回
            </Button>
          </Col>
          <Col>
            <Button
              type={'primary'}
              style={{ backgroundColor: '#F759AB' }}
              loading={updateNPCLoading}
              onClick={() => {
                updateConfig().then();
              }}
            >
              更新NPC配置
            </Button>
          </Col>
        </Row>

        <Form
          form={form}
          layout="vertical"
          style={{ marginTop: 20}}
          initialValues={{}}
        >
          <Form.Item label="角色名称" name="name">
            <Input style={{ width: '100%' }} placeholder="请输入" maxLength={12} />
          </Form.Item>

          <Form.Item label="角色性别" name={['sex']}>
            <Radio.Group>
              <Radio value={NPCCharacterSexEnum.NPCCharacterSexEnum_Male}>
                男
              </Radio>
              <Radio value={NPCCharacterSexEnum.NPCCharacterSexEnum_Female}>
                女
              </Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            label="简短描述"
            name="shortDescription"
            extra={
              <>
                （仅用于C端显示）
                <Button type={'link'}>根据简短描述生成角色描述</Button>
              </>
            }
          >
            <TextArea
              placeholder="请输入"
              maxLength={500}
              style={{ width: '100%' }}
              autoSize={{
                minRows: 3,
                maxRows: 4,
              }}
            />
          </Form.Item>
          <Form.Item
            label="角色描述"
            name="promptDescription"
            extra={<>（参与角色大模型调优）</>}
          >
            <TextArea
              placeholder="请输入"
              maxLength={1000}
              style={{ width: '100%' }}
              autoSize={{
                minRows: 8,
                maxRows: 10,
              }}
            />
          </Form.Item>
        </Form>

        <Col>
          <Row>
            <Button type={'link'}>查看完整Prompt描述</Button>
          </Row>
          <div className={styles.promptDesc}>暂无内容</div>
        </Col>
      </div>

      <div className={styles.chatContainer}>
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
            {
              npcAllInfo?.profile ? (
                <Avatar src={npcAllInfo?.profile || ''} size={48} />
              ) : (
                <Avatar icon={<UserOutlined />} size={48} />
              )
            }
          </Col>
          <Col style={{ marginLeft: 5 }}>{npcAllInfo?.name || '-'}</Col>
        </Row>

        <Row style={{ marginTop: 20 }}>
          <Image src={npcAllInfo?.chatBackground || ''} />
        </Row>
      </div>
    </div>
  );
};

export default ChatDebug;
