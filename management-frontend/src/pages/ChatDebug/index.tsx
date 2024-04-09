import userImg from '@/assets/images/user.png';
import LoadingDots from '@/components/LoadingDots';
import { INPCAllInfo, INPCInfo, IUpdateNPCCharacterRequest, NPCCharacterStatusEnum } from '@/interfaces/game_npc';
import gameNpcService from '@/services/game_npc';
import npcService from '@/services/game_npc';
import { getHashParams } from '@/utils';
import {
  CheckCircleOutlined, CheckOutlined,
  ClearOutlined,
  ClockCircleOutlined, CompressOutlined, ExclamationCircleOutlined, ExpandOutlined,
  FormOutlined,
  LeftOutlined, LoadingOutlined, OpenAIOutlined,
  SendOutlined
} from '@ant-design/icons';
import { useMount, useRequest } from 'ahooks';
import { App, Avatar, Button, Col, Collapse, Divider, Input, Popconfirm, Row, Typography } from 'antd';
import React, { useEffect, useState } from 'react';
import styles from './index.less';
import { useModel, history } from "@umijs/max";
import { USER_ID_KEY } from "@/constants";
import userService from "@/services/user";
import PromptModal from "@/components/PromptModal";
import { Timeout } from "ahooks/es/useRequest/src/types";
import ReactJson from "react-json-view";

const { TextArea } = Input;
const { Text } = Typography;
let debounceTimeout: Timeout | null = null;

interface IChatItem {
  from: 'npc' | 'user' | 'clear';
  status?: 'wait' | 'success' | 'fail';
  content?: string | null;
  contentType?: 'text' | 'image' | null;
  debugMessage?: object | null;
  totalTime?: number;
  isClear?: boolean;
}

const ChatDebug = () => {
  const { message } = App.useApp();
  const { userInfo, setUserInfo, openPromptModal, setOpenPromptModal } = useModel('user');

  const [activeKey, setActiveKey] = useState<string|string[]>(['1']);
  const [editName, setEditName] = useState<string>('');
  const [editShortDesc, setEditShortDesc] = useState<string>('');
  const [editTrait, setEditTrait] = useState<string>('');
  const [npcConfig, setNpcConfig] = useState<INPCInfo | null>(null);
  const [npcAllInfo, setNpcAllInfo] = useState<INPCAllInfo | null>(null);
  const [question, setQuestion] = useState('');
  const [chatList, setChatList] = useState<IChatItem[]>([]);

  const { runAsync: updateNPCRequest, loading: updateNPCLoading } = useRequest(
    npcService.UpdateNPC,
    { manual: true },
  );

  const {
    runAsync: getNPCInfoRequest,
    // loading: getNPCInfoLoading,
  } =
    useRequest(npcService.GetNPCInfo, { manual: true });

  // 获取NPC全部信息
  const {
    // loading: getNPCAllInfoLoading,
    runAsync: getNPCAllInfoRequest,
  } = useRequest(gameNpcService.GetNPCAllInfo, { manual: true });

  const { runAsync: updateNPCStatusRequest, loading: updateNPCStatusLoading } =
    useRequest(npcService.UpdateNPCStatus, { manual: true });

  // NPC聊天
  const { loading: npcDebugChatLoading, runAsync: npcDebugChatRequest } = useRequest(
    gameNpcService.NPCDebugChat,
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

      setEditName(result.data.name);
      setEditShortDesc(result.data.shortDescription);
      setEditTrait(result.data.trait);
    }
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

    const result = await npcDebugChatRequest({
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
      waitChatList[waitChatList.length - 1].debugMessage = result?.data?.debugMessage || null;
      waitChatList[waitChatList.length - 1].totalTime = result?.data?.totalTime || null;

      setChatList(waitChatList);
      scrollToBottom();
    } else {
      waitChatList[waitChatList.length - 1].status = 'fail';
      waitChatList[waitChatList.length - 1].content = '回答失败，请重试';
      waitChatList[waitChatList.length - 1].debugMessage = result?.data?.debugMessage || null;
      waitChatList[waitChatList.length - 1].totalTime = result?.data?.totalTime || null;

      setChatList(waitChatList);
      scrollToBottom();
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
      const clearChatList: IChatItem[] = chatList.map((item) => {
        return {
          ...item,
          isClear: true,
        };
      });
      clearChatList.push({
        from: 'clear',
      });
      setChatList(clearChatList);
      message.success('重置对话成功');
    } else {
      message.warning(result?.msg);
    }
  };

  /**
   * 更新NPC配置
   */
  const updateConfig = async (config?: IUpdateNPCCharacterRequest) => {
    const result = await updateNPCRequest({
      id: getHashParams()?.characterId,
      name: config?.name || npcConfig?.name,
      shortDescription: config?.shortDescription || npcConfig?.shortDescription,
      trait: config?.trait || npcConfig?.trait,
    });
    console.log(result, '更新结果');

    if (result?.code === 0) {
      message.success('更新成功');

      if (npcConfig) {
        setNpcConfig({
          ...npcConfig,
          name: editName,
          shortDescription: editShortDesc,
          trait: editTrait,
          status: result?.data?.status,
          updatedAt: result?.data?.updatedAt,
        });
      }
    } else {
      message.warning(result?.msg);
    }
  };

  /**
   * 更新NPC状态
   * @param id
   * @param status
   */
  const updateNPCStatus = async (
    id: string | null,
    status: NPCCharacterStatusEnum,
  ) => {
    if (!userInfo?.id) {
      return false;
    }

    const result = await updateNPCStatusRequest({
      id: id,
      status: status,
    });
    console.log(result, '更新状态结果');

    if (result.code === 0) {
      message.success('发布成功');
      if (npcConfig) {
        setNpcConfig({
          ...npcConfig,
          status: result.data.status,
          updatedAt: result.data.updatedAt,
        });
      }
    }
  };

  useMount(async () => {
    const storageUserId = localStorage.getItem(USER_ID_KEY);
    if (storageUserId) {
      const userResult = await userService.UserQuery({
        id: storageUserId || '',
      });
      console.log('用户信息：', userResult?.data);
      if (userResult?.data?.id) {
        window.localStorage.setItem(USER_ID_KEY, userResult.data.id);
        setUserInfo(userResult.data || null);
      }
    }

    getNPCInfo().then();
  });

  useEffect(() => {
    if (userInfo?.id) {
      getNPCAllInfo().then();
    }
  }, [userInfo]);

  return (
    <div
      style={{
        // backgroundImage: `url(${npcAllInfo?.chatBackground || ''})`,
      }}
      className={styles.container}
    >
      <Row justify={'space-between'} align={'middle'} className={styles.top}>
        <Col>
          <Row align={'middle'}>
            <Col style={{ marginRight: 10 }}>
              <Button
                icon={<LeftOutlined />}
                type={'text'}
                size={'small'}
                onClick={() => {
                  history.push('/characterList');
                }}
              >
                返回
              </Button>
            </Col>
            <Col>
              <Row align={'middle'}>
                <Col style={{ marginRight: 5 }}>
                  {npcConfig?.name}
                </Col>
                <Col>
                  <Popconfirm
                    title={null}
                    description={(
                      <Input
                        value={editName}
                        onChange={(e) => {
                          setEditName(e.target.value);
                        }}
                      />
                    )}
                    onConfirm={() => {
                      updateConfig({ name: editName }).then();
                    }}
                    okText="确定"
                    cancelText="取消"
                    okButtonProps={{ loading: updateNPCLoading }}
                  >
                    <Button loading={updateNPCLoading} size={'small'} type={'link'} icon={<FormOutlined />} />
                  </Popconfirm>
                </Col>
              </Row>
              <Row>
                {
                  npcConfig?.status === NPCCharacterStatusEnum.NPCCharacterStatusEnum_Save ? (
                    <Text style={{ color: '#8c8c8c' }}><ClockCircleOutlined style={{ color: '#389e0d', marginRight: 3 }} />未发布</Text>
                  ) : null
                }
                {
                  npcConfig?.status === NPCCharacterStatusEnum.NPCCharacterStatusEnum_Publish ? (
                    <Text style={{ color: '#8c8c8c' }}><CheckCircleOutlined style={{ color: '#389e0d', marginRight: 3 }} />已发布</Text>
                  ) : null
                }
                <Text style={{ marginLeft: 20, color: '#8c8c8c' }}>自动保存 {npcConfig?.updatedAt}</Text>
              </Row>
            </Col>
          </Row>
        </Col>
        <Col>
          <Popconfirm
            placement="leftTop"
            title={'角色发布'}
            description={(
              <Text>
                发布角色到线上，用户将实时看到最新角色信息，如果此前角色已发布，<br/>
                则最新角色信息会覆盖旧信息（可能会影响用户体验，请谨慎发布）。
              </Text>
            )}
            okText="发布"
            cancelText="取消"
            onConfirm={() => {
              updateNPCStatus(getHashParams()?.characterId, NPCCharacterStatusEnum.NPCCharacterStatusEnum_Publish).then();
            }}
            okButtonProps={{ loading: updateNPCStatusLoading }}
          >
            <Button
              style={{ backgroundColor: '#F759AB', color: '#fff' }}
              loading={updateNPCStatusLoading}
            >
              发布
            </Button>
          </Popconfirm>
        </Col>
      </Row>

      <div className={styles.main}>
        <div className={styles.left}>
          <Collapse
            style={{ height: '100%' }}
            accordion
            bordered={false}
            expandIconPosition={'end'}
            collapsible={'icon'}
            expandIcon={(panelProps) => {
              if (panelProps.isActive) {
                return <CompressOutlined />
              } else {
                return <ExpandOutlined />
              }
            }}
            activeKey={activeKey}
            onChange={(key) => {
              setActiveKey(key);
            }}
            items={[
              {
                key: '1',
                label: (
                  <Row align={'middle'}>
                    <Col>角色描述</Col>
                    <Col>
                      <Button
                        style={{ color: '#EB2F96' }}
                        size={'small'}
                        type={'link'}
                        icon={<OpenAIOutlined />}
                        onClick={() => {
                          setOpenPromptModal(true);
                        }}
                      >
                        生成
                      </Button>
                    </Col>
                  </Row>
                ),
                children: (
                  <TextArea
                    style={{ width: '100%' }}
                    placeholder="请输入"
                    maxLength={1000}
                    showCount
                    autoSize={{
                      minRows: 20,
                      maxRows: 30,
                    }}
                    value={editTrait}
                    onChange={(e) => {
                      setEditTrait(e.target.value);

                      // 简单防抖处理
                      if (debounceTimeout) {
                        clearTimeout(debounceTimeout);
                      }

                      debounceTimeout = setTimeout(() => {
                        updateConfig({
                          trait: e.target.value,
                        }).then()
                      }, 2000);
                    }}
                  />
                ),
              },
              {
                key: '2',
                label: '简短描述',
                children: (
                  <TextArea
                    style={{ width: '100%' }}
                    placeholder="请输入"
                    maxLength={1000}
                    showCount
                    autoSize={{
                      minRows: 20,
                      maxRows: 30,
                    }}
                    value={editShortDesc}
                    onChange={(e) => {
                      setEditShortDesc(e.target.value);

                      // 简单防抖处理
                      if (debounceTimeout) {
                        clearTimeout(debounceTimeout);
                      }

                      debounceTimeout = setTimeout(() => {
                        updateConfig({
                          shortDescription: e.target.value,
                        }).then()
                      }, 2000);
                    }}
                  />
                ),
              },
              // {
              //   key: '3',
              //   label: '完整Prompt',
              //   children: (
              //     <TextArea
              //       placeholder="请输入"
              //       maxLength={1000}
              //       style={{ width: '100%' }}
              //       autoSize={{
              //         minRows: 8,
              //         maxRows: 10,
              //       }}
              //     />
              //   ),
              // },
            ]}
          />
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
                    <Col>
                      <Row justify={'end'} style={{ marginBottom: 5, marginRight: 10, color: '#595959' }}>{userInfo?.name || '-'}</Row>
                      <Row className={styles.userChatItem} style={item?.isClear ? { opacity: 0.7 } : {}}>
                        <Text className={styles.content}>{item.content}</Text>
                      </Row>
                    </Col>
                    <Col>
                      <Avatar src={userImg} size={32}/>
                    </Col>
                  </Row>
                );
              } else if (item.from === 'npc') {
                return (
                  <Row
                    key={index}
                    justify={'start'}
                    align={'top'}
                    wrap={false}
                    style={{ marginBottom: 10, paddingRight: 40 }}
                  >
                    <Col>
                      <Avatar src={npcAllInfo?.profile || ''} size={32}/>
                    </Col>
                    <Col>
                      <Row style={{ marginBottom: 5, marginLeft: 5, color: '#595959' }}>{npcConfig?.name || '-'}</Row>
                      {
                        item?.status === 'success' && item?.debugMessage ? (
                          <Row style={{ marginBottom: 10 }}>
                            <Collapse
                              size={'small'}
                              expandIconPosition={'end'}
                              items={[
                                {
                                  key: '1',
                                  label: (
                                    <Text style={{ color: '#389e0d' }}><CheckCircleOutlined /> 运行完毕</Text>
                                  ),
                                  children: (
                                    <ReactJson
                                      src={item.debugMessage}
                                      theme={'monokai'}
                                      displayDataTypes={true}
                                      displayObjectSize={true}
                                      name={false}
                                      style={{ padding: '10px' }}
                                    />
                                  )
                                }
                              ]}
                              defaultActiveKey={[]}
                            />
                          </Row>
                        ) : null
                      }
                      {
                        item?.status === 'wait' ? (
                          <Row style={{ marginBottom: 10 }}>
                            <Collapse
                              size={'small'}
                              expandIconPosition={'end'}
                              items={[
                                {
                                  key: '1',
                                  label: (
                                    <Text style={{ color: '#ff9c6e' }}><LoadingOutlined /> 运行中</Text>
                                  ),
                                  children: null
                                }
                              ]}
                              defaultActiveKey={[]}
                            />
                          </Row>
                        ) : null
                      }
                      {
                        item?.status === 'fail' ? (
                          <Row style={{ marginBottom: 10 }}>
                            <Collapse
                              size={'small'}
                              expandIconPosition={'end'}
                              items={[
                                {
                                  key: '1',
                                  label: (
                                    <Text style={{ color: '#f5222d' }}><ExclamationCircleOutlined /> 运行失败</Text>
                                  ),
                                  children: item?.debugMessage ? (
                                    <ReactJson
                                      src={item.debugMessage}
                                      theme={'monokai'}
                                      displayDataTypes={true}
                                      displayObjectSize={true}
                                      name={false}
                                      style={{ padding: '10px' }}
                                    />
                                  ) : item.content
                                }
                              ]}
                              defaultActiveKey={[]}
                            />
                          </Row>
                        ) : null
                      }
                      <Row className={styles.npcChatItem} style={item?.isClear ? { opacity: 0.7 } : {}}>
                        {item?.status === 'wait' ? <LoadingDots/> : null}
                        {item?.status === 'success' ? (
                          <Text className={styles.content}>{item.content}</Text>
                        ) : null}
                        {item?.status === 'fail' ? (
                          <Text className={styles.content}>{item.content}</Text>
                        ) : null}
                      </Row>
                      {
                        item?.totalTime ? (
                          <Row style={{ marginTop: 5, marginLeft: 5 }}>
                            <Text><CheckOutlined style={{ marginRight: 5 }} />{item.totalTime?.toFixed(2)}s</Text>
                          </Row>
                        ) : null
                      }
                    </Col>
                  </Row>
                );
              } else {
                return (
                  <Row
                    key={index}
                    justify={'center'}
                    align={'middle'}
                    wrap={false}
                    style={{ marginBottom: 10, paddingRight: 40 }}
                  >
                    <Divider orientation={'center'}>以上消息已清除</Divider>
                  </Row>
                )
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
                      if (!npcDebugChatLoading) {
                        sendNPCChat().then();
                      }
                    }
                  }}
                />
              </Col>
              <Col className={styles.sendBtn}>
                <Button
                  type={'link'}
                  icon={<SendOutlined/>}
                  style={
                    question === '' ? { color: '#8c8c8c' } : { color: '#F759AB' }
                  }
                  disabled={npcDebugChatLoading}
                  loading={npcDebugChatLoading}
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
                  icon={<ClearOutlined/>}
                  loading={clearNPCHistoryLoading}
                />
              </Row>
              <Row justify={'center'} style={{ fontSize: 12 }}>
                重置对话
              </Row>
            </Col>
          </div>
        </div>
      </div>

      {/*Prompt弹窗*/}
      <PromptModal
        open={openPromptModal}
        shortDescription={editShortDesc}
        npcInfo={npcConfig}
        onChange={(prompt) => {
          setEditTrait(prompt);
          updateConfig({ trait: prompt }).then();
        }}
      />
    </div>
  );
};

export default ChatDebug;
