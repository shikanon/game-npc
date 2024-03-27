import {
  ImageTypeEnum,
  INPCInfo,
  NPCCharacterSexEnum,
  NPCCharacterStatusEnum,
} from '@/interfaces/game_npc';
import npcService from '@/services/game_npc';
import { getHashParams } from '@/utils';
import { PlusOutlined } from '@ant-design/icons';
import { history } from '@umijs/max';
import { useMount, useRequest } from 'ahooks';
import {
  App,
  Avatar,
  Button,
  Col,
  Form,
  GetProp,
  Image,
  Input,
  Modal,
  Radio,
  Row,
  Space,
  Typography,
  Upload,
  UploadFile,
  UploadProps,
} from 'antd';
import { RcFile } from 'antd/es/upload';
import React, { useEffect, useRef, useState } from 'react';
import styles from './index.less';

const { TextArea } = Input;
const { Paragraph, Text } = Typography;

type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

const getBase64 = (file: FileType): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (error) => reject(error);
  });

const Character: React.FC = () => {
  const { message } = App.useApp();
  const [form] = Form.useForm();

  const [npcInfo, setNpcInfo] = useState<INPCInfo | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState('');
  const [previewTitle, setPreviewTitle] = useState('');
  const [avatarFileList, setAvatarFileList] = useState<UploadFile[]>([]);
  const [chatBgFileList, setChatBgFileList] = useState<UploadFile[]>([]);
  const avatarSrc = useRef('');
  const chatBgSrc = useRef('');

  const { runAsync: fileUploadRequest, loading: fileUploadLoading } =
    useRequest(npcService.FileUpload, { manual: true });

  const { runAsync: createNPCRequest, loading: createNPCLoading } = useRequest(
    npcService.CreateNPC,
    { manual: true },
  );

  const { runAsync: updateNPCRequest, loading: updateNPCLoading } = useRequest(
    npcService.UpdateNPC,
    { manual: true },
  );

  const { runAsync: getNPCInfoRequest, loading: getNPCInfoLoading } =
    useRequest(npcService.GetNPCInfo, { manual: true });

  const { runAsync: updateNPCStatusRequest, loading: updateNPCStatusLoading } =
    useRequest(npcService.UpdateNPCStatus, { manual: true });

  // 获取可传递的马甲包租户
  useEffect(() => {}, []);

  /**
   * 获取NPC信息
   * @param id
   */
  const getNPCInfo = async (id: string | null) => {
    const result = await getNPCInfoRequest({ id });
    console.log(result, '查询结果');
    if (result?.data) {
      setNpcInfo(result.data);
      avatarSrc.current = result.data.profile;
      chatBgSrc.current = result.data.chatBackground;
      form.setFieldsValue({
        name: result.data.name,
        sex: result.data.sex,
        shortDescription: result.data.shortDescription,
        promptDescription: result.data.promptDescription,
      });
    }
  };

  const beforeAvatarUpload = async (file: FileType) => {
    const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
    if (!isJpgOrPng) {
      message.error('You can only upload JPG/PNG file!');
    }
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error('Image must smaller than 2MB!');
    }

    const formData = new FormData();
    formData.append('file', file as RcFile);
    formData.append(
      'image_type',
      ImageTypeEnum.ImageTypeEnum_Avatar as unknown as string,
    );
    // @ts-ignore
    const result = await fileUploadRequest(formData);
    console.log(result, '上传结果');

    if (result?.data && result?.code === 0) {
      avatarSrc.current = result?.data;
    }

    return isJpgOrPng && isLt2M;
  };

  const handleAvatarChange: UploadProps['onChange'] = ({
    fileList: newFileList,
  }) => {
    setAvatarFileList(newFileList);
  };

  const beforeChatBgUpload = async (file: FileType) => {
    const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
    if (!isJpgOrPng) {
      message.error('You can only upload JPG/PNG file!');
    }
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error('Image must smaller than 2MB!');
    }

    const formData = new FormData();
    formData.append('file', file as RcFile);
    formData.append(
      'image_type',
      ImageTypeEnum.ImageTypeEnum_ChatBackground as unknown as string,
    );
    // @ts-ignore
    const result = await fileUploadRequest(formData);
    console.log(result, '上传结果');

    if (result?.data && result?.code === 0) {
      chatBgSrc.current = result?.data;
    }

    return isJpgOrPng && isLt2M;
  };

  const handleChatBgChange: UploadProps['onChange'] = ({
    fileList: newFileList,
  }) => {
    setChatBgFileList(newFileList);
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

  const handleCancel = () => setPreviewOpen(false);

  /**
   * 保存并调试
   */
  const saveAndDebug = async () => {
    form.validateFields().then(async (values) => {
      console.log(values);

      if (getHashParams()?.id) {
        const result = await updateNPCRequest({
          ...values,
          id: getHashParams()?.id,
          profile: avatarSrc.current,
          chatBackground: chatBgSrc.current,
        });
        console.log(result, '更新结果');
        if (result?.code === 0) {
          history.push(`/chatDebug?characterId=${result.data}`);
        }
      } else {
        const result = await createNPCRequest({
          ...values,
          profile: avatarSrc.current,
          chatBackground: chatBgSrc.current,
        });
        console.log(result, '创建结果');
        if (result?.code === 0) {
          history.push(`/chatDebug?characterId=${result.data}`);
        }
      }
    });
  };

  /**
   * 保存角色
   */
  const save = async () => {
    form.validateFields().then(async (values) => {
      console.log(values);

      if (getHashParams()?.id) {
        const result = await updateNPCRequest({
          ...values,
          id: getHashParams()?.id,
          profile: avatarSrc.current,
          chatBackground: chatBgSrc.current,
        });
        console.log(result, '更新结果');

        if (result?.code === 0) {
          history?.push('/');
        }
      } else {
        const result = await createNPCRequest({
          ...values,
          profile: avatarSrc.current,
          chatBackground: chatBgSrc.current,
        });
        console.log(result, '创建结果');

        if (result?.code === 0) {
          history?.push('/');
        }
      }
    });
  };

  /**
   * 创建并发布
   */
  const saveAndPublish = async () => {
    form.validateFields().then(async (values) => {
      console.log(values);
      if (getHashParams()?.id) {
        const result = await updateNPCRequest({
          ...values,
          id: getHashParams()?.id,
          profile: avatarSrc.current,
          chatBackground: chatBgSrc.current,
        });
        console.log(result, '更新结果');
        if (result?.data && result?.code === 0) {
          const updateResult = await updateNPCStatusRequest({
            id: getHashParams()?.id,
            status: NPCCharacterStatusEnum.NPCCharacterStatusEnum_Publish,
          });
          console.log(updateResult, '更新状态结果');

          if (result?.code === 0) {
            history?.push('/');
          }
        }
      } else {
        const result = await createNPCRequest({
          ...values,
          profile: avatarSrc.current,
          chatBackground: chatBgSrc.current,
        });
        console.log(result, '创建结果');
        if (result?.data && result?.code === 0) {
          const updateResult = await updateNPCStatusRequest({
            id: result?.data,
            status: NPCCharacterStatusEnum.NPCCharacterStatusEnum_Publish,
          });
          console.log(updateResult, '更新状态结果');

          if (result?.code === 0) {
            history?.push('/');
          }
        }
      }
    });
  };

  useMount(() => {
    if (getHashParams()?.id) {
      getNPCInfo(getHashParams()?.id).then();
    }
  });

  return (
    <div className={styles.container}>
      <Form form={form} initialValues={{}}>
        <Row justify={'space-between'} align={'top'}>
          <Col span={8}>
            <Form.Item
              label="角色头像"
              name="avatar"
              rules={[{ required: false }]}
              extra="支持JPG、PNG格式图片，5M以内"
            >
              <Upload
                listType="picture-circle"
                fileList={avatarFileList}
                beforeUpload={beforeAvatarUpload}
                onPreview={handlePreview}
                onChange={handleAvatarChange}
                onRemove={() => {
                  avatarSrc.current = '';
                }}
              >
                {avatarFileList.length >= 1 ? null : (
                  <>
                    {npcInfo?.profile ? (
                      <Avatar
                        src={npcInfo.profile}
                        style={{ width: '100%', height: '100%' }}
                      />
                    ) : (
                      <button
                        style={{ border: 0, background: 'none' }}
                        type="button"
                      >
                        <PlusOutlined />
                        <div style={{ marginTop: 8 }}>Upload</div>
                      </button>
                    )}
                  </>
                )}
              </Upload>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              label="角色背景"
              name="chatBackground"
              rules={[{ required: false }]}
              extra={
                <>
                  支持JPG、PNG格式图片，5M以内
                  <br />
                  背景图片将用于：角色卡片列表、聊天背景
                </>
              }
            >
              <Upload
                listType="picture-card"
                fileList={chatBgFileList}
                beforeUpload={beforeChatBgUpload}
                onPreview={handlePreview}
                onChange={handleChatBgChange}
                onRemove={() => {
                  chatBgSrc.current = '';
                }}
              >
                {chatBgFileList.length >= 1 ? null : (
                  <>
                    {npcInfo?.chatBackground ? (
                      <Image
                        src={npcInfo.chatBackground}
                        style={{ width: 50 }}
                        preview={false}
                      />
                    ) : (
                      <button
                        style={{ border: 0, background: 'none' }}
                        type="button"
                      >
                        <PlusOutlined />
                        <div style={{ marginTop: 8 }}>Upload</div>
                      </button>
                    )}
                  </>
                )}
              </Upload>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Space>
              <Button
                loading={createNPCLoading || updateNPCLoading}
                onClick={() => {
                  saveAndDebug().then();
                }}
              >
                保存并调试
              </Button>
              <Button
                type={'primary'}
                loading={
                  createNPCLoading || updateNPCLoading || updateNPCStatusLoading
                }
                onClick={() => {
                  saveAndPublish().then();
                }}
              >
                {npcInfo ? '更新' : '创建'}并发布
              </Button>
              <Button
                type={'primary'}
                style={{ backgroundColor: '#F759AB' }}
                loading={createNPCLoading || updateNPCLoading}
                onClick={() => {
                  save().then();
                }}
              >
                保存角色
              </Button>
            </Space>
          </Col>
        </Row>
        <Form.Item label="角色名称" name="name" rules={[{ required: true }]}>
          <Input style={{ width: 300 }} placeholder="请输入" maxLength={12} />
        </Form.Item>
        <Form.Item label="角色性别" name={['sex']} rules={[{ required: true }]}>
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
          style={{ paddingLeft: 10 }}
          extra={
            <>
              （仅用于C端显示）
              <Button type={'link'}>根据简短描述生成角色描述</Button>
            </>
          }
        >
          <TextArea
            placeholder="请输入"
            maxLength={50}
            style={{ width: 500 }}
            autoSize={{
              minRows: 2,
              maxRows: 4,
            }}
          />
        </Form.Item>
        <Form.Item
          label="角色描述"
          name="promptDescription"
          style={{ paddingLeft: 10 }}
          extra={<>（参与角色大模型调优）</>}
        >
          <TextArea
            placeholder="请输入"
            maxLength={50}
            style={{ width: 500 }}
            autoSize={{
              minRows: 4,
              maxRows: 4,
            }}
          />
        </Form.Item>
      </Form>

      <Col style={{ paddingLeft: 60 }}>
        <Row>
          <Button type={'link'}>查看完整Prompt描述</Button>
        </Row>
        <div className={styles.promptDesc}>暂无内容</div>
      </Col>

      <Modal
        open={previewOpen}
        title={previewTitle}
        footer={null}
        onCancel={handleCancel}
      >
        <img alt="example" style={{ width: '100%' }} src={previewImage} />
      </Modal>
    </div>
  );
};

export default Character;
