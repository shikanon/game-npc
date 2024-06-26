import { PageParams } from '@/interfaces/common';
import { INPCInfo, NPCCharacterStatusEnum } from '@/interfaces/game_npc';
import npcService from '@/services/game_npc';
import { history, useModel } from '@umijs/max';
import { useMount, useRequest } from 'ahooks';
import {
  Avatar,
  Button,
  Col,
  Form,
  Image,
  Input,
  Popconfirm,
  Row,
  Space,
  Table,
  Tag, Tooltip,
  Typography,
} from 'antd';
import { ColumnsType } from 'antd/es/table';
import { useState } from 'react';
import styles from './index.less';
import { UserOutlined } from "@ant-design/icons";

const { Text } = Typography;

const Character: React.FC = () => {
  const [form] = Form.useForm();
  const { userInfo, setOpenLoginModal } = useModel('user');

  const [npcList, setNpcList] = useState<INPCInfo[]>([]);
  const [searchParams, setSearchParams] = useState<any | null>(null); // 搜索框筛选参数
  const [queryPage, setQueryPage] = useState<PageParams | null>(null); // 查询页码数据
  const [listTotal, setListTotal] = useState<number | null>(null); // 列表总数

  const { runAsync: getNPCListRequest, loading: getNPCListLoading } =
    useRequest(npcService.GetNPCList, { manual: true });

  const { runAsync: updateNPCStatusRequest, loading: updateNPCStatusLoading } =
    useRequest(npcService.UpdateNPCStatus, { manual: true });

  const { runAsync: deleteNPCRequest, loading: deleteNPCLoading } = useRequest(
    npcService.DeleteNPC,
    { manual: true },
  );

  /**
   * 获取列表
   * @param params
   */
  const getList = async (params?: any) => {
    console.log(params, 'params');
    const result = await getNPCListRequest({
      ...params,
      page: params?.page || 1,
      limit: params?.limit || 10,
    });
    console.log(result, '查询结果');
    if (result?.data?.list) {
      setNpcList(result.data.list);
      setListTotal(result.data.total);
    } else {
      setNpcList([]);
      setListTotal(0);
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
      setOpenLoginModal(true);
      return false;
    }

    const result = await updateNPCStatusRequest({
      id: id,
      status: status,
    });
    console.log(result, '更新状态结果');

    getList({
      ...searchParams,
      page: queryPage?.page,
      limit: queryPage?.limit,
    }).then();
  };

  /**
   * 删除NPC
   * @param id
   */
  const deleteNPC = async (id: string) => {
    if (!userInfo?.id) {
      setOpenLoginModal(true);
      return false;
    }

    const result = await deleteNPCRequest({ id });
    console.log(result, '删除结果');
    if (result.code === 0) {
      getList({
        ...searchParams,
        page: queryPage?.page,
        limit: queryPage?.limit,
      }).then();
    }
  };

  const submitForm = () => {
    form.validateFields().then((values) => {
      setSearchParams(values);
      setQueryPage({
        page: 1,
        limit: 10,
      });

      getList({
        ...values,
        page: 1,
        limit: 10,
      }).then();
    });
  };

  const columns: ColumnsType<any> = [
    {
      title: '角色头像',
      fixed: 'left',
      dataIndex: 'profile',
      width: 80,
      render: (text) => {
        if (text === '') {
          return <Avatar icon={<UserOutlined />} size={'large'} />;
        } else {
          return <Avatar src={text || ''} size={'large'} />;
        }
      },
    },
    {
      title: '角色姓名',
      fixed: 'left',
      dataIndex: 'name',
      width: 80,
      render: (text) => text || '-',
    },
    {
      title: '角色背景',
      dataIndex: 'chatBackground',
      width: 80,
      render: (text) => {
        if (text !== '') {
          return <Image src={text || ''} height={100} width={75} />;
        } else {
          return '-';
        }
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 80,
      render: (text: NPCCharacterStatusEnum) => {
        if (text === NPCCharacterStatusEnum.NPCCharacterStatusEnum_Unknown) {
          return '-';
        } else if (
          text === NPCCharacterStatusEnum.NPCCharacterStatusEnum_Save
        ) {
          return <Tag color="geekblue">未发布</Tag>;
        } else if (
          text === NPCCharacterStatusEnum.NPCCharacterStatusEnum_Publish
        ) {
          return <Tag color="green">已发布</Tag>;
        }
      },
    },
    {
      title: '简单描述',
      dataIndex: 'shortDescription',
      width: 180,
      render: (text) => (
        <Text style={{ width: 200 }} ellipsis={{ tooltip: text }}>
          {text || '-'}
        </Text>
      ),
    },
    {
      title: '角色描述',
      dataIndex: 'trait',
      width: 180,
      render: (text) => (
        <Tooltip
          title={text}
          overlayInnerStyle={{ maxHeight: 500, width: 400, overflowY: 'auto' }}
        >
          <Text style={{ width: 200 }} ellipsis={{  }}>
            {text || '-'}
          </Text>
        </Tooltip>
      ),
    },
    {
      title: '操作',
      fixed: 'right',
      dataIndex: 'operation',
      width: 210,
      render: (text, record: INPCInfo) => (
        <Space size={'small'}>
          {record?.status ===
          NPCCharacterStatusEnum.NPCCharacterStatusEnum_Save || record?.status === NPCCharacterStatusEnum.NPCCharacterStatusEnum_Unknown ? (
            <Button
              type={'link'}
              size={'small'}
              loading={updateNPCStatusLoading}
              onClick={() => {
                updateNPCStatus(
                  record.id,
                  NPCCharacterStatusEnum.NPCCharacterStatusEnum_Publish,
                ).then();
              }}
            >
              发布
            </Button>
          ) : null}

          {record?.status ===
          NPCCharacterStatusEnum.NPCCharacterStatusEnum_Publish ? (
            <Button
              type={'link'}
              size={'small'}
              loading={updateNPCStatusLoading}
              onClick={() => {
                updateNPCStatus(
                  record.id,
                  NPCCharacterStatusEnum.NPCCharacterStatusEnum_Save,
                ).then();
              }}
            >
              下架
            </Button>
          ) : null}

          <Button
            type={'link'}
            size={'small'}
            onClick={() => {
              if (userInfo?.id) {
                history.push(`/chatDebug?characterId=${record.id}`);
              } else {
                setOpenLoginModal(true);
              }
            }}
          >
            调试
          </Button>

          <Button
            type={'link'}
            size={'small'}
            onClick={() => {
              if (userInfo?.id) {
                history.push(`/characterConfig?id=${record.id}`);
              } else {
                setOpenLoginModal(true);
              }
            }}
          >
            修改
          </Button>

          <Popconfirm
            title="温馨提示"
            description="你确认要删除该NPC角色吗？"
            onConfirm={() => {
              deleteNPC(record.id).then();
            }}
            okText="确定"
            cancelText="取消"
            cancelButtonProps={{ loading: deleteNPCLoading }}
          >
            <Button type={'link'} size={'small'} danger loading={deleteNPCLoading}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  useMount(() => {
    getList().then();
  });

  return (
    <div className={styles.container}>
      <Row
        justify={'space-between'}
        align={'middle'}
        style={{ marginBottom: 30 }}
      >
        <Col>
          <Space size={'large'}>
            <Form form={form} layout="inline">
              <Form.Item label={'角色名称'} name="name">
                <Input placeholder="请输入" />
              </Form.Item>
            </Form>
            <Button
              type={'primary'}
              onClick={() => {
                submitForm();
              }}
            >
              查询
            </Button>
            <Button
              onClick={() => {
                form.resetFields();
              }}
            >
              重置
            </Button>
          </Space>
        </Col>
        <Col style={{ marginLeft: 50 }}>
          <Button
            type={'primary'}
            style={{ backgroundColor: '#F759AB' }}
            onClick={() => {
              if (userInfo?.id) {
                history.push('/characterConfig');
              } else {
                setOpenLoginModal(true);
              }
            }}
          >
            创建角色
          </Button>
        </Col>
      </Row>

      <Table
        rowKey="id"
        style={{}}
        loading={getNPCListLoading}
        columns={columns}
        scroll={{ x: '100%' }}
        dataSource={npcList}
        pagination={{
          total: listTotal ?? 0,
          showSizeChanger: true,
          showQuickJumper: true,
          current: queryPage?.page,
          pageSize: queryPage?.limit || 10,
          onChange: (pageNum: number, pageSize: number) => {
            // 更新当前页码
            setQueryPage({
              page: (pageNum - 1) * pageSize,
              limit: pageSize,
            });

            // 更新列表
            getList({
              ...searchParams,
              page: (pageNum - 1) * pageSize,
              limit: pageSize,
            }).then();
          },
        }}
      />
    </div>
  );
};

export default Character;
