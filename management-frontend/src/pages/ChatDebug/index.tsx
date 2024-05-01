import userImg from '@/assets/images/user.png';
import LoadingDots from '@/components/LoadingDots';
import PromptModal from '@/components/PromptModal';
import { ACCESS_TOKEN_KEY, USER_ID_KEY } from '@/constants';
import {
  IAffinityRules,
  ILevelPictureRule,
  INPCAllInfo,
  INPCInfo,
  IUpdateNPCCharacterRequest,
  ImageTypeEnum,
  NPCCharacterStatusEnum,
} from '@/interfaces/game_npc';
import {
  default as gameNpcService,
  default as npcService,
} from '@/services/game_npc';
import userService from '@/services/user';
import { getHashParams } from '@/utils';
import {
  CheckCircleOutlined,
  CheckOutlined,
  ClearOutlined,
  ClockCircleOutlined,
  CompressOutlined,
  ExclamationCircleOutlined,
  ExpandOutlined,
  FormOutlined,
  LeftOutlined,
  LoadingOutlined,
  OpenAIOutlined,
  PlusOutlined,
  SendOutlined,
} from '@ant-design/icons';
import { history, useModel } from '@umijs/max';
import { useMount, useRequest } from 'ahooks';
import { Timeout } from 'ahooks/es/useRequest/src/types';
import {
  App,
  Avatar,
  Button,
  Col,
  Collapse,
  Divider,
  GetProp,
  Image,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Row,
  Typography,
  Upload,
  UploadFile,
  UploadProps,
} from 'antd';
import ImgCrop from 'antd-img-crop';
import { RcFile } from 'antd/es/upload';
import { useEffect, useState } from 'react';
import ReactJson from 'react-json-view';
import styles from './index.less';

const { TextArea } = Input;
const { Text, Paragraph } = Typography;
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

type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

const getBase64 = (file: FileType): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (error) => reject(error);
  });

const ChatDebug = () => {
  const { message } = App.useApp();
  const { userInfo, setUserInfo, openPromptModal, setOpenPromptModal } =
    useModel('user');

  const [activeKey, setActiveKey] = useState<string | string[]>([]);
  const [editName, setEditName] = useState<string>('');
  const [editShortDesc, setEditShortDesc] = useState<string>('');
  const [editTrait, setEditTrait] = useState<string>('');
  const [prologue, setPrologue] = useState<string>('');
  const [presetProblems, setPresetProblems] = useState<string[]>(['', '', '']);
  const [affinityRules, setAffinityRules] = useState<IAffinityRules[]>([
    { lv: 1, score: 5, content: '陌生' },
    { lv: 2, score: 15, content: '普通' },
    { lv: 3, score: 30, content: '友好' },
    { lv: 4, score: 60, content: '亲密' },
    { lv: 5, score: 100, content: '恋人' },
  ]);
  const [picturesRule, setPicturesRule] = useState<ILevelPictureRule[]>([
    { lv: 1, score: 5, imageUrl: '', description: '' },
    { lv: 2, score: 15, imageUrl: '', description: '' },
    { lv: 3, score: 30, imageUrl: '', description: '' },
    { lv: 4, score: 60, imageUrl: '', description: '' },
    { lv: 5, score: 100, imageUrl: '', description: '' },
  ]);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState('');
  const [previewTitle, setPreviewTitle] = useState('');
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
  } = useRequest(npcService.GetNPCInfo, { manual: true });

  // 获取NPC全部信息
  const {
    // loading: getNPCAllInfoLoading,
    runAsync: getNPCAllInfoRequest,
  } = useRequest(gameNpcService.GetNPCAllInfo, { manual: true });

  const { runAsync: updateNPCStatusRequest, loading: updateNPCStatusLoading } =
    useRequest(npcService.UpdateNPCStatus, { manual: true });

  // NPC聊天
  const { loading: npcDebugChatLoading, runAsync: npcDebugChatRequest } =
    useRequest(gameNpcService.NPCDebugChat, { manual: true });

  // 清除NPC聊天历史
  const { loading: clearNPCHistoryLoading, runAsync: clearNPCHistoryRequest } =
    useRequest(gameNpcService.ClearNPCHistory, { manual: true });

  const {
    runAsync: fileUploadRequest,
    // loading: fileUploadLoading,
  } = useRequest(npcService.FileUpload, { manual: true });

  // // 获取开场白
  // const { runAsync: getNPCPrologueRequest, loading: getNPCPrologueLoading } =
  //   useRequest(npcService.GetNPCPrologue, { manual: true });
  //
  // // 获取预置问题
  // const {
  //   runAsync: getNPCPresetProblemsRequest,
  //   loading: getNPCPresetProblemsLoading,
  // } = useRequest(npcService.GetNPCPresetProblems, { manual: true });

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
    const result = await getNPCInfoRequest({
      id: getHashParams()?.characterId,
    });
    console.log(result, '查询结果');
    if (result?.data) {
      setNpcConfig(result.data);

      setEditName(result.data.name);
      setEditShortDesc(result.data.shortDescription);
      setEditTrait(result.data.trait);
      setPrologue(result.data.prologue || '');
      if (result?.data?.presetProblems) {
        setPresetProblems(result.data.presetProblems);
      }
      if (result?.data?.affinityRules) {
        setAffinityRules(result.data.affinityRules);
      }
      if (result.data.pictures) {
        setPicturesRule(
          result.data.pictures?.map((item) => {
            return {
              ...item,
              imageFileList: [],
            };
          }) || [],
        );
      }
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

  // /**
  //  * 获取NPC聊天开场白
  //  */
  // const getNPCPrologue = async () => {
  //   const result = await getNPCPrologueRequest({
  //     id: getHashParams()?.characterId || '',
  //   });
  //   console.log(result, '开场白');
  // };

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
      waitChatList[waitChatList.length - 1].debugMessage =
        result?.data?.debugMessage || null;
      waitChatList[waitChatList.length - 1].totalTime =
        result?.data?.totalTime || null;

      setChatList(waitChatList);
      scrollToBottom();
    } else {
      waitChatList[waitChatList.length - 1].status = 'fail';
      waitChatList[waitChatList.length - 1].content = '回答失败，请重试';
      waitChatList[waitChatList.length - 1].debugMessage =
        result?.data?.debugMessage || null;
      waitChatList[waitChatList.length - 1].totalTime =
        result?.data?.totalTime || null;

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
      affinityRules: config?.affinityRules || npcConfig?.affinityRules,
      prologue: config?.prologue || npcConfig?.prologue,
      pictures: config?.pictures || npcConfig?.pictures,
      presetProblems: config?.presetProblems || npcConfig?.presetProblems,
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
          prologue: prologue,
          affinityRules: affinityRules,
          pictures: config?.pictures || npcConfig?.pictures,
          presetProblems: presetProblems,
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

  /**
   * 亲密值变更
   * @param item
   * @param value
   */
  const onIntimacyValueChange = (
    item: IAffinityRules,
    value: number | null,
  ) => {
    const newAffinityRules = affinityRules.map((rule) => {
      if (rule.lv === item.lv) {
        return {
          ...rule,
          score: value || 0,
        };
      }
      return rule;
    });
    const newPictureRules = picturesRule.map((rule) => {
      if (rule.lv === item.lv) {
        return {
          ...rule,
          score: value || 0,
        };
      }
      return rule;
    });
    setAffinityRules(newAffinityRules);
    setPicturesRule(newPictureRules);

    // 简单防抖处理
    if (debounceTimeout) {
      clearTimeout(debounceTimeout);
    }

    debounceTimeout = setTimeout(() => {
      updateConfig({
        affinityRules: newAffinityRules,
        pictures: newPictureRules,
      }).then();
    }, 2000);
  };

  /**
   * 好感度描述变更
   * @param item
   * @param value
   */
  const onLikeabilityDescChange = (item: IAffinityRules, value: string) => {
    const newAffinityRules = affinityRules.map((rule) => {
      if (rule.lv === item.lv) {
        return {
          ...rule,
          content: value,
        };
      }
      return rule;
    });

    setAffinityRules(newAffinityRules);

    // 简单防抖处理
    if (debounceTimeout) {
      clearTimeout(debounceTimeout);
    }

    debounceTimeout = setTimeout(() => {
      updateConfig({
        affinityRules: newAffinityRules,
      }).then();
    }, 2000);
  };

  /**
   * 图片触发场景变更
   * @param item
   * @param value
   */
  const onImageConditionChange = (item: ILevelPictureRule, value: string) => {
    const newPicturesRule = picturesRule.map((rule) => {
      if (rule.lv === item.lv) {
        return {
          ...rule,
          description: value,
        };
      }
      return rule;
    });
    setPicturesRule(newPicturesRule);

    // 简单防抖处理
    if (debounceTimeout) {
      clearTimeout(debounceTimeout);
    }

    debounceTimeout = setTimeout(() => {
      updateConfig({
        pictures:
          newPicturesRule?.map((rule) => {
            return {
              lv: rule.lv,
              imageUrl: rule.imageUrl || '',
              description: rule.description || '',
              score: rule?.score,
            };
          }) || [],
      }).then();
    }, 2000);
  };

  // /**
  //  * 图片上传前
  //  * @param item
  //  * @param file
  //  */
  // const beforeImageUpload = async (item: ILevelPictureRule, file: FileType) => {
  //   const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
  //   if (!isJpgOrPng) {
  //     message.error('You can only upload JPG/PNG file!');
  //   }
  //   const isLt2M = file.size / 1024 / 1024 < 2;
  //   if (!isLt2M) {
  //     message.error('Image must smaller than 2MB!');
  //   }
  //   return isJpgOrPng && isLt2M;
  // };

  /**
   * 图片上传
   * @param item
   * @param file
   * @param fileList
   */
  const handleChatBgChange = async (
    item: ILevelPictureRule,
    file: UploadFile,
    fileList: UploadFile[],
  ) => {
    const formData = new FormData();

    console.log(file, 'file');
    formData.append('file', file as RcFile);
    formData.append(
      'image_type',
      ImageTypeEnum.ImageTypeEnum_ChatBackground as unknown as string,
    );
    // @ts-ignore
    const result = await fileUploadRequest(formData);
    console.log(result, '上传结果');

    if (result?.data && result?.code === 0) {
      const newPicturesRule = picturesRule.map((rule) => {
        if (rule.lv === item.lv) {
          return {
            ...rule,
            imageUrl: result?.data,
            imageFileList: fileList,
          };
        }
        return rule;
      });
      setPicturesRule(newPicturesRule);

      updateConfig({
        pictures: newPicturesRule.map((rule) => {
          return {
            lv: rule.lv,
            imageUrl: rule.imageUrl || '',
            description: rule.description || '',
            score: rule.score,
          };
        }),
      }).then();
    }
  };

  /**
   * 图片移除
   * @param item
   */
  const onImageRemove = (item: ILevelPictureRule) => {
    const newPicturesRule = picturesRule.map((rule) => {
      if (rule.lv === item.lv) {
        return {
          ...rule,
          imageUrl: '',
          imageFileList: [],
        };
      }
      return rule;
    });
    setPicturesRule(newPicturesRule);
  };

  const handlePreview = async (file: UploadFile) => {
    if (!file.url && !file.preview) {
      file.preview = await getBase64(file.originFileObj as FileType);
    }

    setPreviewImage(file.url || (file.preview as string));
    setPreviewOpen(true);
    setPreviewTitle(
      file.name || file.url!.substring(file.url!.lastIndexOf('/') + 1),
    );
  };

  useMount(async () => {
    const storageAccessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (storageAccessToken) {
      const userResult = await userService.Verify();
      console.log('用户信息：', userResult?.data);
      if (userResult?.data?.id) {
        window.localStorage.setItem(USER_ID_KEY, userResult.data.id);
        setUserInfo(userResult.data || null);
      }
      getNPCInfo().then();
    } else {
      history.push('/');
    }
  });

  useEffect(() => {
    if (userInfo?.id) {
      getNPCAllInfo().then();
    }
  }, [userInfo]);

  useEffect(() => {
    console.log(affinityRules, 'affinityRules');
  }, [affinityRules]);

  useEffect(() => {
    console.log(picturesRule, 'picturesRule');
  }, [picturesRule]);

  return (
    <div
      style={
        {
          // backgroundImage: `url(${npcAllInfo?.chatBackground || ''})`,
        }
      }
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
                <Col style={{ marginRight: 5 }}>{npcConfig?.name}</Col>
                <Col>
                  <Popconfirm
                    title={null}
                    icon={null}
                    description={
                      <Input
                        value={editName}
                        onChange={(e) => {
                          setEditName(e.target.value);
                        }}
                      />
                    }
                    onConfirm={() => {
                      updateConfig({ name: editName }).then();
                    }}
                    okText="确定"
                    cancelText="取消"
                    okButtonProps={{ loading: updateNPCLoading }}
                  >
                    <Button
                      loading={updateNPCLoading}
                      size={'small'}
                      type={'link'}
                      icon={<FormOutlined />}
                    />
                  </Popconfirm>
                </Col>
              </Row>
              <Row>
                {npcConfig?.status ===
                NPCCharacterStatusEnum.NPCCharacterStatusEnum_Save ? (
                  <Text style={{ color: '#8c8c8c' }}>
                    <ClockCircleOutlined
                      style={{ color: '#389e0d', marginRight: 3 }}
                    />
                    未发布
                  </Text>
                ) : null}
                {npcConfig?.status ===
                NPCCharacterStatusEnum.NPCCharacterStatusEnum_Publish ? (
                  <Text style={{ color: '#8c8c8c' }}>
                    <CheckCircleOutlined
                      style={{ color: '#389e0d', marginRight: 3 }}
                    />
                    已发布
                  </Text>
                ) : null}
                <Text style={{ marginLeft: 20, color: '#8c8c8c' }}>
                  自动保存 {npcConfig?.updatedAt}
                </Text>
              </Row>
            </Col>
          </Row>
        </Col>
        <Col>
          <Popconfirm
            placement="leftTop"
            title={'角色发布'}
            description={
              <Text>
                发布角色到线上，用户将实时看到最新角色信息，如果此前角色已发布，
                <br />
                则最新角色信息会覆盖旧信息（可能会影响用户体验，请谨慎发布）。
              </Text>
            }
            okText="发布"
            cancelText="取消"
            onConfirm={() => {
              updateNPCStatus(
                getHashParams()?.characterId,
                NPCCharacterStatusEnum.NPCCharacterStatusEnum_Publish,
              ).then();
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
        <div className={styles.promptConfig}>
          <div>
            <Collapse
              accordion
              bordered={false}
              expandIconPosition={'end'}
              collapsible={'icon'}
              defaultActiveKey={['1']}
              expandIcon={(panelProps) => {
                if (panelProps.isActive) {
                  return <CompressOutlined />;
                } else {
                  return <ExpandOutlined />;
                }
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
                          }).then();
                        }, 2000);
                      }}
                    />
                  ),
                },
              ]}
            />
          </div>

          <div>
            <Collapse
              accordion
              bordered={false}
              expandIconPosition={'end'}
              collapsible={'icon'}
              expandIcon={(panelProps) => {
                if (panelProps.isActive) {
                  return <CompressOutlined />;
                } else {
                  return <ExpandOutlined />;
                }
              }}
              activeKey={activeKey}
              onChange={(key) => {
                setActiveKey(key);
              }}
              items={[
                {
                  key: '1',
                  label: '简短描述',
                  children: (
                    <TextArea
                      style={{ width: '100%' }}
                      placeholder="请输入"
                      showCount
                      autoSize={{
                        minRows: 5,
                        maxRows: 10,
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
                          }).then();
                        }, 2000);
                      }}
                    />
                  ),
                },
                // {
                //   key: '2',
                //   label: '完整Prompt',
                //   children: (
                //     <TextArea
                //       placeholder="请输入"
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
        </div>

        <div className={styles.chatConfig}>
          <Collapse
            bordered={false}
            defaultActiveKey={[]}
            items={[
              {
                key: '1',
                label: '好感度规则',
                children: (
                  <>
                    {affinityRules?.map((item) => {
                      return (
                        <Col key={item.lv} style={{ marginBottom: 10 }}>
                          <Row>亲密等级LV{item.lv}</Row>
                          <Row align={'top'} style={{ marginTop: 5 }}>
                            <Col style={{ marginRight: 10 }}>
                              <InputNumber
                                style={{ width: 80 }}
                                value={item.score || ''}
                                placeholder={'所需亲密值'}
                                onChange={(value) => {
                                  console.log(value, '亲密值');
                                  onIntimacyValueChange(item, value || null);
                                }}
                              />
                            </Col>
                            <Col style={{ flex: 1 }}>
                              <TextArea
                                autoSize={{ minRows: 2, maxRows: 5 }}
                                value={item.content || ''}
                                maxLength={500}
                                placeholder={'请输入该等级下的好感度描述'}
                                onChange={(e) => {
                                  console.log(e.target.value, '描述');
                                  onLikeabilityDescChange(item, e.target.value);
                                }}
                              />
                            </Col>
                          </Row>
                        </Col>
                      );
                    })}
                  </>
                ),
              },
              {
                key: '2',
                label: '图片回复',
                children: (
                  <>
                    {picturesRule?.map((item) => {
                      return (
                        <Col key={item.lv} style={{ marginBottom: 10 }}>
                          <Row>图片LV{item.lv}</Row>
                          <Row align={'top'} style={{ marginTop: 5 }}>
                            <Col style={{ marginRight: 10 }}>
                              <ImgCrop
                                rotationSlider
                                // aspectSlider
                                aspect={3 / 4}
                                showReset
                                cropShape={'rect'}
                              >
                                <Upload
                                  listType="picture-card"
                                  fileList={item?.imageFileList || []}
                                  beforeUpload={() => {
                                    return false;
                                    // beforeImageUpload(item, file).then();
                                  }}
                                  onPreview={handlePreview}
                                  onChange={(info) => {
                                    handleChatBgChange(
                                      item,
                                      info.file,
                                      info.fileList,
                                    );
                                  }}
                                  onRemove={() => {
                                    onImageRemove(item);
                                  }}
                                >
                                  {(item?.imageFileList?.length || 0) >=
                                  1 ? null : (
                                    <>
                                      {item?.imageUrl ? (
                                        <Image
                                          src={item?.imageUrl}
                                          style={{ width: 50 }}
                                          preview={false}
                                        />
                                      ) : (
                                        <button
                                          style={{
                                            border: 0,
                                            background: 'none',
                                          }}
                                          type="button"
                                        >
                                          <PlusOutlined />
                                          <div style={{ marginTop: 8 }}>
                                            Upload
                                          </div>
                                        </button>
                                      )}
                                    </>
                                  )}
                                </Upload>
                              </ImgCrop>
                            </Col>
                            <Col style={{ flex: 1 }}>
                              <TextArea
                                autoSize={{ minRows: 3, maxRows: 5 }}
                                value={item.description || ''}
                                maxLength={500}
                                placeholder={'请输入触发该图片的场景或对话信息'}
                                onChange={(e) => {
                                  console.log(e.target.value, '场景');

                                  onImageConditionChange(item, e.target.value);
                                }}
                              />
                            </Col>
                          </Row>
                        </Col>
                      );
                    })}
                  </>
                ),
              },
              // {
              //   key: '3',
              //   label: '主动问候',
              //   children: (
              //     <Col>
              //       <Row style={{ marginBottom: 15 }}>
              //         <Col>主动问候时间范围</Col>
              //         <Col style={{ marginTop: 5 }}>
              //           <Radio.Group defaultValue="a" buttonStyle="solid">
              //             <Radio.Button style={{ marginRight: 10 }} value="a">
              //               00:00-6:00
              //             </Radio.Button>
              //             <Radio.Button style={{ marginRight: 10 }} value="b">
              //               6:00-12:00
              //             </Radio.Button>
              //             <Radio.Button style={{ marginRight: 10 }} value="c">
              //               12:00-18:00
              //             </Radio.Button>
              //             <Radio.Button value="d">18:00-24:00</Radio.Button>
              //           </Radio.Group>
              //         </Col>
              //       </Row>
              //
              //       <Row style={{ marginBottom: 5 }}>主动问候Prompt</Row>
              //       <Row>
              //         <TextArea
              //           autoSize={{ minRows: 3, maxRows: 5 }}
              //           value={''}
              //           placeholder={'请输入主动问候Prompt'}
              //           onChange={(e) => {
              //             console.log(e.target.value, '问候');
              //           }}
              //         />
              //       </Row>
              //     </Col>
              //   ),
              // },
              {
                key: '4',
                label: '开场白',
                children: (
                  <Col>
                    <Col style={{ marginBottom: 5 }}>开场白内容</Col>
                    <Col>
                      <TextArea
                        autoSize={{ minRows: 3, maxRows: 5 }}
                        placeholder={'请输入开场白'}
                        value={prologue}
                        onChange={(e) => {
                          console.log(e.target.value, '开场白');

                          setPrologue(e.target.value);

                          // 简单防抖处理
                          if (debounceTimeout) {
                            clearTimeout(debounceTimeout);
                          }

                          debounceTimeout = setTimeout(() => {
                            updateConfig({
                              prologue: e.target.value,
                            }).then();
                          }, 2000);
                        }}
                      />
                    </Col>

                    <Col style={{ marginTop: 15, marginBottom: 5 }}>
                      开场白预置回复问题
                    </Col>

                    {presetProblems?.map((item, index) => {
                      return (
                        <Row key={index} style={{ marginBottom: 10 }}>
                          <TextArea
                            autoSize={{ minRows: 1, maxRows: 3 }}
                            value={presetProblems[index] || ''}
                            placeholder={'请输入'}
                            onChange={(e) => {
                              console.log(e.target.value, '预置问题');

                              const newPresetProblems = presetProblems?.map(
                                (_item, _index) => {
                                  if (index === _index) {
                                    return e.target.value;
                                  } else {
                                    return _item;
                                  }
                                },
                              );

                              setPresetProblems(newPresetProblems);

                              // 简单防抖处理
                              if (debounceTimeout) {
                                clearTimeout(debounceTimeout);
                              }

                              debounceTimeout = setTimeout(() => {
                                updateConfig({
                                  presetProblems: newPresetProblems,
                                }).then();
                              }, 2000);
                            }}
                          />
                        </Row>
                      );
                    })}
                  </Col>
                ),
              },
              {
                key: '5',
                label: '回复推荐',
                children: (
                  <Col>
                    <Row>
                      <Paragraph style={{ color: '#8c8c8c' }}>
                        每个角色回复后面跟上3条聊天提示，提示用户可以说的话（根据上下文和prompt进行提示）
                      </Paragraph>
                    </Row>

                    <Row style={{ marginBottom: 5 }}>自定义灵感回复prompt</Row>
                    <Row>
                      <TextArea
                        autoSize={{ minRows: 3, maxRows: 5 }}
                        value={''}
                        placeholder={'请输入'}
                        onChange={(e) => {
                          console.log(e.target.value, '请输入');
                        }}
                      />
                    </Row>
                  </Col>
                ),
              },
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
                      <Row
                        justify={'end'}
                        style={{
                          marginBottom: 5,
                          marginRight: 10,
                          color: '#595959',
                        }}
                      >
                        {userInfo?.name || '-'}
                      </Row>
                      <Row
                        className={styles.userChatItem}
                        style={item?.isClear ? { opacity: 0.7 } : {}}
                      >
                        <Text className={styles.content}>{item.content}</Text>
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
                      <Row
                        style={{
                          marginBottom: 5,
                          marginLeft: 5,
                          color: '#595959',
                        }}
                      >
                        {npcConfig?.name || '-'}
                      </Row>
                      {item?.status === 'success' && item?.debugMessage ? (
                        <Row style={{ marginBottom: 10, marginLeft: 5 }}>
                          <Collapse
                            size={'small'}
                            expandIconPosition={'end'}
                            items={[
                              {
                                key: '1',
                                label: (
                                  <Text style={{ color: '#389e0d' }}>
                                    <CheckCircleOutlined /> 运行完毕
                                  </Text>
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
                                ),
                              },
                            ]}
                            defaultActiveKey={[]}
                          />
                        </Row>
                      ) : null}
                      {item?.status === 'wait' ? (
                        <Row style={{ marginBottom: 10, marginLeft: 5 }}>
                          <Collapse
                            size={'small'}
                            expandIconPosition={'end'}
                            items={[
                              {
                                key: '1',
                                label: (
                                  <Text style={{ color: '#ff9c6e' }}>
                                    <LoadingOutlined /> 运行中
                                  </Text>
                                ),
                                children: null,
                              },
                            ]}
                            defaultActiveKey={[]}
                          />
                        </Row>
                      ) : null}
                      {item?.status === 'fail' ? (
                        <Row style={{ marginBottom: 10, marginLeft: 5 }}>
                          <Collapse
                            size={'small'}
                            expandIconPosition={'end'}
                            items={[
                              {
                                key: '1',
                                label: (
                                  <Text style={{ color: '#f5222d' }}>
                                    <ExclamationCircleOutlined /> 运行失败
                                  </Text>
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
                                ) : (
                                  item.content
                                ),
                              },
                            ]}
                            defaultActiveKey={[]}
                          />
                        </Row>
                      ) : null}
                      <Row
                        className={styles.npcChatItem}
                        style={item?.isClear ? { opacity: 0.7 } : {}}
                      >
                        {item?.status === 'wait' ? <LoadingDots /> : null}
                        {item?.status === 'success' ? (
                          <Text className={styles.content}>{item.content}</Text>
                        ) : null}
                        {item?.status === 'fail' ? (
                          <Text className={styles.content}>{item.content}</Text>
                        ) : null}
                      </Row>
                      {item?.totalTime ? (
                        <Row style={{ marginTop: 5, marginLeft: 5 }}>
                          <Text>
                            <CheckOutlined style={{ marginRight: 5 }} />
                            {item.totalTime?.toFixed(2)}s
                          </Text>
                        </Row>
                      ) : null}
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
                );
              }
            })}
          </div>
          <div className={styles.footer}>
            <Row
              justify={'start'}
              align={'middle'}
              className={styles.chatInput}
            >
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
                  icon={<SendOutlined />}
                  style={
                    question === ''
                      ? { color: '#8c8c8c' }
                      : { color: '#F759AB' }
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
      </div>

      <Modal
        open={previewOpen}
        title={previewTitle}
        footer={null}
        onCancel={() => {
          setPreviewOpen(false);
        }}
      >
        <img alt="example" style={{ width: '100%' }} src={previewImage} />
      </Modal>

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
