import { useRequest } from 'ahooks';
import {
  App, Col,
  Modal,
  Row,
  Typography,
} from 'antd';
import { ModalProps } from 'antd/es/modal';
import React, { useEffect, useState } from 'react';
import { UserSexEnum } from "@/interfaces/user";
import { useModel } from "@@/exports";
import userService from "@/services/user";
import styles from './index.less';

const { Text, Paragraph } = Typography;

interface Values {
  onChange: (values: any) => void;
}

const CreateFormModal: React.FC<Values & ModalProps> = ({
  onChange,
  ...modalProps
}) => {
  const { message } = App.useApp();

  const { userInfo, setOpenSexModal } = useModel('user');

  const [selectedSex, setSelectedSex] = useState<UserSexEnum>(UserSexEnum.UserSexEnum_Unknown);

  useEffect(() => {}, []);

  // 注册请求
  const {
    // loading: updateUserInfoLoading,
    runAsync: updateUserInfoRequest,
  } =
    useRequest(userService.UpdateUserInfo, { manual: true });

  /**
   * 更新用户信息
   */
  const updateUserInfo = async (sex: UserSexEnum) => {
    setSelectedSex(UserSexEnum.UserSexEnum_Male);

    const result = await updateUserInfoRequest({
      id: userInfo?.id || '',
      sex: sex,
    });

    console.log('更新用户信息成功');
    message.success('设置用户性别成功');

    if (result?.code === 0) {
      setOpenSexModal(false);
    }
  };

  return (
    <Modal
      {...modalProps}
      title={<Text style={{ color: '#fff', fontSize: 16 }}>Welcome to LoveTalk</Text>}
      okText={null}
      cancelText={null}
      width={450}
      styles={{
        header: { textAlign: 'center', backgroundColor: '#262626' },
        body: { padding: '32px 32px 0 32px' },
      }}
      closeIcon={false}
      footer={null}
      maskClosable={false}
      onCancel={() => {
        onChange(true);
      }}
    >
      <Paragraph style={{ color: '#fff' }}>你的性别是？</Paragraph>

      <Row justify={'space-evenly'} align={'middle'}>
        <Col span={10}>
          <div
            className={`${selectedSex === UserSexEnum.UserSexEnum_Male ? styles.active : ''} ${styles.unactive}`}
            onClick={() => {
              updateUserInfo(UserSexEnum.UserSexEnum_Male).then();
            }}
          >
            男性
          </div>
        </Col>
        <Col span={10}>
          <div
            className={`${selectedSex === UserSexEnum.UserSexEnum_Female ? styles.active : ''} ${styles.unactive}`}
            onClick={() => {
              updateUserInfo(UserSexEnum.UserSexEnum_Female).then();
            }}
          >
            女性
          </div>
        </Col>
      </Row>
    </Modal>
  );
};

export default CreateFormModal;
