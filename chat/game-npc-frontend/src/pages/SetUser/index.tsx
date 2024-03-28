import selectSexTipsImg from '@/assets/images/select_sex_tips.png';
import userService from '@/services/user';
import { history, useModel } from '@umijs/max';
import { useRequest } from 'ahooks';
import { Button, Image, Row } from 'antd';
import { useTheme } from 'antd-style';
import { useEffect, useState } from 'react';
import styles from './index.less';
import { UserSexEnum } from "@/interfaces/user";

const Login = () => {
  const theme = useTheme();
  const { userInfo } = useModel('user');
  const [selectedSex, setSelectedSex] = useState<UserSexEnum>(UserSexEnum.UserSexEnum_Unknown);

  // 注册请求
  const { loading: updateUserInfoLoading, runAsync: updateUserInfoRequest } =
    useRequest(userService.UpdateUserInfo, { manual: true });

  /**
   * 更新用户信息
   */
  const updateUserInfo = async () => {
    const result = await updateUserInfoRequest({
      id: userInfo?.id || '',
      sex: selectedSex,
    });

    console.log('更新用户信息成功');
    if (result?.code === 0) {
      history.push('/character');
    }
  };

  useEffect(() => {}, []);

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
      }}
      className={styles.container}
    >
      <Row className={styles.title}>
        <Image preview={false} src={selectSexTipsImg} height={50} />
      </Row>

      <div className={styles.selectedSex}>
        <div
          style={
            selectedSex === UserSexEnum.UserSexEnum_Male
              ? {
                  width: 240,
                  height: 240,
                  color: '#DD661B',
                  border: '3px solid #DD661B',
                }
              : {}
          }
          onClick={() => setSelectedSex(UserSexEnum.UserSexEnum_Male)}
        >
          男
        </div>
        <div
          style={
            selectedSex === UserSexEnum.UserSexEnum_Female
              ? {
                  width: 240,
                  height: 240,
                  color: '#DD661B',
                  border: '3px solid #DD661B',
                }
              : {}
          }
          onClick={() => setSelectedSex(UserSexEnum.UserSexEnum_Female)}
        >
          女
        </div>
      </div>

      <Row justify={'center'} style={{ marginTop: 100 }}>
        <Button
          type={'primary'}
          style={{
            background: 'linear-gradient(to right, #F8DA77, #ED6BC9)',
            border: 'none',
          }}
          loading={updateUserInfoLoading}
          onClick={() => {
            updateUserInfo().then();
          }}
        >
          开始聊天!
        </Button>
      </Row>
    </div>
  );
};

export default Login;
