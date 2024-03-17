import loginTipsImg from '@/assets/images/login_tips.png';
import { USER_ID_KEY } from '@/constants';
import { IUserLoginRequest, IUserRegisterRequest } from '@/interfaces/user';
import userService from '@/services/user';
import { history, useModel } from '@umijs/max';
import { useRequest } from 'ahooks';
import { App, Button, Col, Form, Image, Input, Row } from 'antd';
import { useTheme } from 'antd-style';
import { useEffect } from 'react';
import styles from './index.less';

const Login = () => {
  const theme = useTheme();
  const { message } = App.useApp();
  const [form] = Form.useForm();
  const { setUserInfo } = useModel('user');

  // 注册请求
  const { loading: registerLoading, runAsync: registerRequest } = useRequest(
    userService.Register,
    { manual: true },
  );
  // 登录请求
  const { loading: loginLoading, runAsync: loginRequest } = useRequest(
    userService.Login,
    { manual: true },
  );

  useEffect(() => {}, []);

  /**
   * 注册
   */
  const register = async () => {
    form
      .validateFields()
      .then(async (values: IUserRegisterRequest) => {
        console.log('Success:', values);

        const result = await registerRequest({ ...values });

        console.log(result);

        if (result?.data?.id) {
          setUserInfo(result.data);
          window.localStorage.setItem(USER_ID_KEY, result?.data?.id);

          // 进入角色页面
          history.push('/set_user');
        } else {
          message.warning(result?.msg);
        }
      })
      .catch(() => {});
  };

  /**
   * 登录
   */
  const login = async () => {
    form
      .validateFields()
      .then(async (values: IUserLoginRequest) => {
        console.log('Success:', values);

        const result = await loginRequest({ ...values });

        console.log(result);

        if (result?.data?.id) {
          setUserInfo(result.data);
          window.localStorage.setItem(USER_ID_KEY, result?.data?.id);

          // 进入角色页面
          history.push('/character');
        } else {
          message.warning(result?.msg);
        }
      })
      .catch(() => {});
  };

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
      }}
      className={styles.container}
    >
      <Row className={styles.title}>
        <Image preview={false} src={loginTipsImg} height={50} />
      </Row>

      <div className={styles.loginContainer}>
        <Form
          name="user"
          form={form}
          labelCol={{ span: 8 }}
          wrapperCol={{ span: 16 }}
          initialValues={{ remember: true }}
        >
          <Form.Item
            label="用户名"
            name="name"
            rules={[
              { required: true, message: '请输入用户名' },
              {
                pattern: /^[a-zA-Z][a-zA-Z0-9]{0,19}$/,
                message:
                  '用户名只能输入英文和数字，且必须以英文开头，20个字符以内',
              },
            ]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { pattern: /^[^\u4e00-\u9fa5]+$/, message: '密码不能是中文' },
            ]}
          >
            <Input.Password />
          </Form.Item>
        </Form>

        <Row justify={'center'} align={'middle'} style={{ marginTop: 10 }}>
          <Col style={{ marginRight: 30 }}>
            <Button
              style={{ backgroundColor: '#FFC069' }}
              type={'primary'}
              loading={registerLoading}
              onClick={() => {
                register().then();
              }}
            >
              注册
            </Button>
          </Col>

          <Col>
            <Button
              type={'primary'}
              loading={loginLoading}
              onClick={() => {
                login().then();
              }}
            >
              登录
            </Button>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Login;
