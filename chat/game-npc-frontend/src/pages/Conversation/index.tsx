import userImg from '@/assets/images/user.png';
import lvPictureLockImg from '@/assets/images/lv_picture_lock.png';
import LoadingDots from '@/components/LoadingDots';
import { INPCAllInfo, INPCLevelPicture } from '@/interfaces/game_npc';
import gameNpcService from '@/services/game_npc';
import { getHashParams } from '@/utils';
import { ClearOutlined, LeftOutlined, SendOutlined, StarOutlined, UnlockOutlined } from '@ant-design/icons';
import { history, useModel } from '@umijs/max';
import { useRequest } from 'ahooks';
import { App, Avatar, Button, Col, Divider, Input, Row, Typography, Image, Progress, Tooltip } from 'antd';
import { useTheme } from 'antd-style';
import React, { useEffect, useRef, useState } from 'react';
import styles from './index.less';
import dayjs from "dayjs";

const { TextArea } = Input;
const { Paragraph, Text } = Typography;

interface IChatItem {
  from: 'npc' | 'user' | 'clear'; // 来源
  status?: 'wait' | 'success' | 'fail'; // 状态
  content?: string | null; // 内容
  contentType?: 'text' | 'image' | null; // 内容类型
  messageTime?: string; // 消息时间
  isClear?: boolean; // 是否清空
  presetProblems?: string[]; // npc预置问题
}

const Conversation = () => {
  const theme = useTheme();
  const { message } = App.useApp();
  const { userInfo } = useModel('user');

  const [npcAllInfo, setNpcAllInfo] = useState<INPCAllInfo | null>(null);
  const [question, setQuestion] = useState('');
  const [promptQuestionList, setPromptQuestionList] = useState<string[]>([]);
  const [chatList, setChatList] = useState<IChatItem[]>([]);
  const [chatBg, setChatBg] = useState('');
  const [achieveNextLvPicture, setAchieveNextLvPicture] =
    useState<INPCLevelPicture|null>(null);
  const [showLvPicture, setShowLvPicture] = useState<INPCLevelPicture|null>(null);
  const [openNextLvPicture, setOpenNextLvPicture] = useState(false);
  const [isUnlockNpcPicture, setIsUnlockNpcPicture] = useState(false);
  const lvPictureContainerRef = useRef(null);
  const showPictureContainerRef = useRef(null);

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

  // NPC聊天Prompt
  const {
    loading: getNPCChatPromptLoading,
    runAsync: getNPCChatPromptRequest,
  } = useRequest(
    gameNpcService.NPCChatPrompt,
    { manual: true },
  );

  // 清除NPC聊天历史
  const { loading: clearNPCHistoryLoading, runAsync: clearNPCHistoryRequest } =
    useRequest(gameNpcService.ClearNPCHistory, { manual: true });

  // // 获取开场白
  // const {
  //   runAsync: getNPCPrologueRequest,
  //   // loading: getNPCPrologueLoading,
  // } = useRequest(gameNpcService.GetNPCPrologue, { manual: true });
  //
  // // 获取预置问题
  // const {
  //   runAsync: getNPCPresetProblemsRequest,
  //   // loading: getNPCPresetProblemsLoading,
  // } = useRequest(gameNpcService.GetNPCPresetProblems, { manual: true });

  // /**
  //  * 获取开场白信息
  //  */
  // const getNPCPrologue = async () => {
  //   const prologueResult = await getNPCPrologueRequest({
  //     id: getHashParams()?.characterId || '',
  //   });
  //   console.log(prologueResult, '开场白信息');
  //   const problemsResult = await getNPCPresetProblemsRequest({
  //     id: getHashParams()?.characterId || '',
  //   });
  //
  //   if (prologueResult.data) {
  //
  //   }
  // };

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
   * @param action
   */
  const getNPCAllInfo = async (action: 'init' | 'update') => {
    const result = await getNPCAllInfoRequest({
      npcId: getHashParams()?.characterId || '',
      userId: userInfo?.id || '',
    });
    console.log(result, '当前NPC全部信息');

    if (result?.data) {
      setNpcAllInfo(result.data);

      // 判断是init还是update
      if (action === 'init') {
        // 初始化设置聊天背景

        // // 当前聊天亲密度分数
        // const currentScore = result?.data?.score || 0;
        // // 下一个等级的聊天背景
        // const nextLvPicture =
        //   result?.data?.pictures?.find((item) => currentScore >= (item?.score || 0)) || null;
        // console.log(nextLvPicture, '下一个等级的聊天背景');
        // if (nextLvPicture) {
        //   setChatBg(nextLvPicture?.imageUrl || '');
        // } else {
        setChatBg(result.data.chatBackground || '')
        // }

        // setOpenLvPicture(true);
        // setIsUnlockNpcPicture(false);
        // setAchieveNextLvPicture({ imageUrl: result?.data?.chatBackground || '' , description: '聊天背景' });

        if (result?.data?.dialogueContext?.length) {
          // 插入历史对话内容
          const newChatList: IChatItem[] =
            result?.data?.dialogueContext?.map((item) => {
              return {
                from: item?.roleFrom === result?.data?.name
                  ? 'npc'
                  : 'user',
                status: 'success',
                content: item?.content || null,
                contentType: item?.contentType || null,
                messageTime: item?.createdAt,
              };
            }) || [];
          // 插入npc回复的预设问题
          newChatList.unshift({
            from: 'npc',
            status: 'success',
            content: result?.data.prologue || '',
            contentType: 'text',
            messageTime: dayjs().format('YYYY-MM-DD HH:mm:ss'),
          })
          console.log(newChatList, '对话列表');
          setChatList(newChatList);

          // 滚动到底部
          scrollToBottom();
        } else {
          setChatList([
            {
              from: 'npc',
              status: 'success',
              content: result?.data.prologue || '',
              contentType: 'text',
              presetProblems: result?.data?.presetProblems || [],
              messageTime: dayjs().format('YYYY-MM-DD HH:mm:ss'),
            }
          ]);
        }
      } else {
        // 当前聊天亲密度分数
        const currentScore = result?.data?.score || 0;
        const nextLvPicture =
          result?.data?.pictures?.find((item) => item.score === currentScore) || null;

        if (nextLvPicture) {

          // 设置等级lv图片
          setAchieveNextLvPicture(nextLvPicture || null);

          // 发送聊天问题
          // eslint-disable-next-line @typescript-eslint/no-use-before-define
          sendNPCChat(nextLvPicture?.description || '', nextLvPicture?.imageUrl).then();
        }
      }
    }
  };

  /**
   * 获取NPC聊天提示
   */
  const getNPCChatPrompt = async () => {
    const result = await getNPCChatPromptRequest({
      npcId: getHashParams()?.characterId || '',
      userId: userInfo?.id || '',
    });

    if (result?.data?.suggestionMessages) {
      setPromptQuestionList(result.data.suggestionMessages);

      // 滚动到底部
      scrollToBottom();
    } else {
      setPromptQuestionList([]);
    }
  }

  /**
   * 发起NPC聊天
   */
  const sendNPCChat = async (inputQuestion: string, imageUrl?: string) => {
    // 组装我发送的信息
    const waitChatList: IChatItem[] = JSON.parse(JSON.stringify(chatList));

    // 如果是图片类型消息，则发送一张图片
    if (imageUrl) {
      waitChatList.push({ from: 'npc', status: 'success', content: imageUrl, contentType: 'image', messageTime: dayjs().format('YYYY-MM-DD HH:mm:ss')});
      waitChatList.push({ from: 'npc', status: 'success', content: inputQuestion, messageTime: dayjs().format('YYYY-MM-DD HH:mm:ss') });

      setChatList(waitChatList);

      scrollToBottom();
    } else {
      waitChatList.push({ from: 'user', content: inputQuestion, messageTime: dayjs().format('YYYY-MM-DD HH:mm:ss') });
      waitChatList.push({ from: 'npc', status: 'wait', content: '' });

      setChatList(waitChatList);
      setQuestion('');

      scrollToBottom();

      const result = await npcChatRequest({
        question: inputQuestion,
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
        waitChatList[waitChatList.length - 1].messageTime = dayjs().format('YYYY-MM-DD HH:mm:ss');
        setChatList(waitChatList);
      } else {
        waitChatList[waitChatList.length - 1].status = 'fail';
        waitChatList[waitChatList.length - 1].content = '回答失败，请重试';
        waitChatList[waitChatList.length - 1].messageTime = dayjs().format('YYYY-MM-DD HH:mm:ss');
        setChatList(waitChatList);
      }

      scrollToBottom();

      // 更新npc对象信息
      getNPCAllInfo('update').then();

      // 获取NPC聊天提示
      getNPCChatPrompt().then();
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
   * 获取等级lv进度条
   */
  const getLvContainer = () => {
    const currentLv = npcAllInfo?.affinityLevel || 0;
    const nextLv = currentLv + 1;
    const currentScore = npcAllInfo?.score || 0;
    const nextLvScore = npcAllInfo?.affinityRules?.[nextLv]?.score || 0;

    return (
      <Col>
        <Tooltip
          overlayInnerStyle={{ background: 'linear-gradient(to right, #ED6BC9, #F8DA77)' }}
          title={(
            <Col>
              <Row>当前已有：{currentScore}亲密值</Row>
              <Row>升级到LV{nextLv}所需：{nextLvScore}亲密值</Row>
            </Col>
          )}
        >
          <Progress
            showInfo={false}
            strokeColor={{'0%': '#f759ab', '100%' : '#ffd6e7'}}
            trailColor={'#ffd6e7'}
            percent={(currentScore / nextLvScore) * 100}
          />
        </Tooltip>
        <Row justify={'space-between'}>
          <Col>LV{currentLv}</Col>
          <Col>
            <Row justify={'end'}>
              LV{nextLv}
            </Row>
            <Row justify={'end'}>
              <Button
                className={styles.upgradeBtn}
                type={'primary'}
                size={'small'}
              >
                升级有惊喜
              </Button>
            </Row>
          </Col>
        </Row>
      </Col>
    )
  }

  const handleClickOutside = (event: any) => {
    // @ts-ignore
    if (lvPictureContainerRef.current && !lvPictureContainerRef.current?.contains(event.target)) {
      setOpenNextLvPicture(false);
    }

    // @ts-ignore
    if (showPictureContainerRef.current && !showPictureContainerRef.current?.contains(event.target)) {
      setShowLvPicture(null);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (userInfo) {
      // 初始化获取NPC全部信息
      getNPCAllInfo('init').then();

      // 初始化获取开场白
      // getNPCPrologue().then();
      // 初始化获取回复推荐问题
      getNPCChatPrompt().then();
    }
  }, [userInfo]);

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
        backgroundImage: `url(${chatBg || ''})`,
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

        {
          npcAllInfo?.pictures?.length ? (
            <Row className={styles.pictureList} justify={'start'}>
              {
                npcAllInfo?.pictures?.map((item, index) => {
                  // 解锁当前图片等级
                  if (item?.imageUrl && item.lv > 0 && item.lv <= npcAllInfo?.affinityLevel) {
                    return (
                      <Col
                        key={index}
                        className={styles.photoItem}
                        onClick={() => {
                          setShowLvPicture(item);
                        }}
                      >
                        <Image
                          preview={false}
                          className={styles.photoItem}
                          src={item.imageUrl || ''}
                          alt={'相册图片'}
                        />
                      </Col>
                    )
                  } else if (item.lv > 0 && item.lv > npcAllInfo?.affinityLevel) {
                    return (
                      <Col
                        key={index}
                        className={styles.noPhotoItem}
                      >
                        <Image
                          preview={false}
                          src={lvPictureLockImg || ''}
                          alt={'相册图片'}
                        />
                        <Text>等级{item.lv}开放</Text>
                      </Col>
                    );
                  } else {
                    return null;
                  }
                })
              }
            </Row>
          ) : null
        }
      </div>
      <div
        className={styles.chatContainer}
        style={{
          backgroundColor: theme.colorBgLayout,
          backgroundImage: `url(${chatBg || ''})`,
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
                  <Col>
                    {/*<Row*/}
                    {/*  justify={'end'}*/}
                    {/*  style={{*/}
                    {/*    marginBottom: 5,*/}
                    {/*    marginRight: 5,*/}
                    {/*    color: '#ffffff',*/}
                    {/*  }}*/}
                    {/*>*/}
                    {/*  {userInfo?.name || '-'}*/}
                    {/*</Row>*/}
                    <Row className={styles.userChatItem} style={item?.isClear ? { opacity: 0.7 } : {}}>
                      <Text className={styles.content}>{item.content}</Text>
                    </Row>
                    <Row
                      justify={'end'}
                      style={{
                        marginRight: 5,
                        color: '#ffffff',
                      }}
                    >
                      {item?.messageTime || '-'}
                    </Row>
                  </Col>
                  <Col>
                    <Avatar src={userImg} size={32} />
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
                    <Avatar src={npcAllInfo?.profile || ''} size={32} />
                  </Col>
                  <Col>
                    {
                      item?.contentType === 'image' ? (
                        <Image
                          className={styles.npcImageItem}
                          style={isUnlockNpcPicture ? {} : { filter: 'blur(5px)' }}
                          preview={false}
                          height={300}
                          width={300 * 0.75}
                          src={item?.content || ''}
                          onClick={() => {
                            setOpenNextLvPicture(true);
                          }}
                        />
                      ) : (
                        <Col>
                          {/*<Row*/}
                          {/*  justify={'start'}*/}
                          {/*  style={{*/}
                          {/*    marginBottom: 5,*/}
                          {/*    marginLeft: 5,*/}
                          {/*    color: '#ffffff',*/}
                          {/*  }}*/}
                          {/*>*/}
                          {/*  {npcAllInfo?.name || '-'}*/}
                          {/*</Row>*/}
                          <Row className={styles.npcChatItem} style={item?.isClear ? { opacity: 0.7 } : {}}>
                            {item?.status === 'wait' ? <LoadingDots /> : null}
                            {item?.status === 'success' ? (
                              <Text className={styles.content}>{item.content}</Text>
                            ) : null}
                            {item?.status === 'fail' ? (
                              <Text className={styles.content}>{item.content}</Text>
                            ) : null}
                          </Row>
                          {
                            item?.messageTime ? (
                              <Row
                                justify={'start'}
                                style={{
                                  marginLeft: 5,
                                  color: '#ffffff',
                                }}
                              >
                                {item?.messageTime || '-'}
                              </Row>
                            ) : null
                          }
                        </Col>
                      )
                    }
                    {
                      item?.presetProblems?.length && chatList.length === 1 ? (
                        <>
                          {item?.presetProblems?.map((problem, index) => {
                            return (
                              <div key={index} style={{ textAlign: 'left', marginLeft: 5 }}>
                                <Row
                                  className={styles.presetProblemItem}
                                  justify={'end'}
                                  key={index}
                                  style={{ display: 'inline-flex' }}
                                  onClick={() => {
                                    setQuestion(problem);

                                    // 发送聊天
                                    if (!npcChatLoading) {
                                      sendNPCChat(problem).then();
                                    }
                                  }}
                                >
                                  {problem}
                                </Row>
                                <br/>
                              </div>
                            );
                          })}
                        </>
                      ) : null
                    }
                    {
                      !getNPCChatPromptLoading &&
                      !npcChatLoading &&
                      promptQuestionList.length &&
                      chatList.length > 1 &&
                      index === (chatList.length - 1) ? (
                        <>
                          {promptQuestionList?.map((problem, index) => {
                            return (
                              <div key={index} style={{ textAlign: 'left', marginLeft: 5 }}>
                                <Row
                                  className={styles.presetProblemItem}
                                  justify={'end'}
                                  key={index}
                                  style={{ display: 'inline-flex' }}
                                  onClick={() => {
                                    setQuestion(problem);

                                    // 发送聊天
                                    if (!npcChatLoading) {
                                      sendNPCChat(problem).then();
                                      setPromptQuestionList([]);
                                    }
                                  }}
                                >
                                  {problem}
                                </Row>
                                <br/>
                              </div>
                            );
                          })}
                        </>
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
                  <Divider orientation={'center'}>以上对话内容已清除</Divider>
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
                    if (!npcChatLoading) {
                      sendNPCChat(target.value).then();
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
                  sendNPCChat(question).then();
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
        {getLvContainer()}
        <Row style={{ marginTop: 10 }} justify={'start'} align={'bottom'}>
          <Col>
            <Avatar src={npcAllInfo?.profile || ''} size={48} />
          </Col>
          <Col style={{ marginLeft: 5 }}>{npcAllInfo?.name || '-'}</Col>
        </Row>

        <Row>
          <Paragraph style={{ margin: '10px 0 0 0' }}>
            {npcAllInfo?.shortDescription || '-'}
          </Paragraph>
        </Row>
      </div>

      {
        openNextLvPicture ? (
          <div
            ref={lvPictureContainerRef}
            className={styles.lvPictureContainer}
          >
            <div
              className={styles.lvPicture}
              style={
                isUnlockNpcPicture ? {
                  backgroundImage: `url(${achieveNextLvPicture?.imageUrl || ''})`,
                } : {
                  filter: 'blur(5px)',
                  backgroundImage: `url(${achieveNextLvPicture?.imageUrl || ''})`,
                }
              }
            />
            {
              isUnlockNpcPicture ? null : (
                <Button
                  type={'primary'}
                  icon={<UnlockOutlined/>}
                  className={styles.unlock}
                  onClick={() => {
                    // 解锁等级lv图片
                    setIsUnlockNpcPicture(true);
                    // 免费解锁，应用等级lv聊天背景
                    // setChatBg(achieveNextLvPicture?.imageUrl || '');
                  }}
                >
                  免费解锁
                </Button>
              )
            }
          </div>
        ) : null
      }

      {
        showLvPicture ? (
          <div
            ref={showPictureContainerRef}
            className={styles.lvPictureContainer}
          >
            <div
              className={styles.lvPicture}
              style={{
                backgroundImage: `url(${showLvPicture?.imageUrl || ''})`,
              }}
            />
            <Button
              type={'primary'}
              icon={<StarOutlined />}
              className={styles.unlock}
              onClick={() => {
                setChatBg(showLvPicture?.imageUrl || '');
                setShowLvPicture(null);
              }}
            >
              设为聊天背景
            </Button>
          </div>
        ) : null
      }
    </div>
  );
};

export default Conversation;
