import { useRequest } from 'ahooks';
import {
  App, Button,
  Col,
  Form,
  Input,
  Modal,
  Row,
  Typography,
} from 'antd';
import { ModalProps } from 'antd/es/modal';
import React, { useEffect, useState } from 'react';
import { CloseOutlined } from "@ant-design/icons";
import { IUserLoginRequest, IUserRegisterRequest } from "@/interfaces/user";
import { ACCESS_TOKEN_KEY, USER_ID_KEY } from "@/constants";
import { useModel } from "@@/exports";
import userService from "@/services/user";

const { Text, Paragraph } = Typography;

interface Values {
  onChange: (values: any) => void;
}

const CreateFormModal: React.FC<Values & ModalProps> = ({
  onChange,
  ...modalProps
}) => {
  const { message } = App.useApp();

  const [form] = Form.useForm();

  const { setUserInfo } = useModel('user');
  // 登录模式
  const [loginType, setLoginType] = useState<'login' | 'register'>('login');

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
          if (result?.data?.accessToken) {
            window.localStorage.setItem(ACCESS_TOKEN_KEY, result.data.accessToken);
          }

          message.success('注册成功');

          // 进入角色页面
          onChange(true);
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
          if (result?.data?.accessToken) {
            window.localStorage.setItem(ACCESS_TOKEN_KEY, result.data.accessToken);
          }

          message.success('登录成功');

          // 进入角色页面
          onChange(true);
        }
      })
      .catch(() => {});
  };

  return (
    <Modal
      {...modalProps}
      title={'Welcome to LoveTalk 后台'}
      okText={null}
      cancelText={null}
      width={450}
      styles={{
        header: { textAlign: 'center' },
        body: { padding: '32px 32px 0 32px' },
      }}
      closeIcon={<CloseOutlined style={{ color: '#fff' }} />}
      footer={null}
      onCancel={() => {
        onChange(true);
      }}
    >
      <Form
        form={form}
        labelCol={{ span: 6 }}
        wrapperCol={{ span: 16 }}
        initialValues={{ remember: true }}
      >
        <Form.Item
          label={<Text>用户名</Text>}
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
          label={<Text>密码</Text>}
          name="password"
          rules={[
            { required: true, message: '请输入密码' },
            { pattern: /^[^\u4e00-\u9fa5]+$/, message: '密码不能是中文' },
          ]}
          hasFeedback
        >
          <Input.Password />
        </Form.Item>

        {
          loginType === 'register' ? (
            <Form.Item
              label={<Text>确认密码</Text>}
              name="confirm_password"
              dependencies={['password']}
              hasFeedback
              rules={[
                { required: true, message: '请输入密码' },
                { pattern: /^[^\u4e00-\u9fa5]+$/, message: '密码不能是中文' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('新密码与确认密码不一致'));
                  },
                }),
              ]}
            >
              <Input.Password />
            </Form.Item>
          ) : null
        }
      </Form>

      <Row justify={'center'} style={{ marginTop: 30 }}>
        <Col style={{ width: '90%' }}>
          <Button
            style={{ width: '100%', backgroundColor: '#FF85C0', border: 'none'}}
            loading={loginLoading || registerLoading}
            onClick={() => {
              if (loginType === 'login') {
                login().then();
              } else {
                register().then();
              }
            }}
          >
            {loginType === 'login' ? '登录' : '注册'}
          </Button>
        </Col>
      </Row>
      {
        loginType === 'login' ? (
          <Row style={{ marginTop: 3, paddingLeft: '5%' }}>
            <Paragraph style={{ color: '#bfbfbf' }}>
              没有账户？
              <Text
                style={{ color: '#4096ff', cursor: 'pointer' }}
                onClick={() => {
                  setLoginType('register');
                }}
              >开始注册</Text>
            </Paragraph>
          </Row>
        ) : (
          <Row style={{ marginTop: 3, paddingLeft: '5%' }}>
            <Paragraph style={{ color: '#bfbfbf' }}>
              有账户？
              <Text
                style={{ color: '#4096ff', cursor: 'pointer' }}
                onClick={() => {
                  setLoginType('login');
                }}
              >直接登录</Text>
            </Paragraph>
          </Row>
        )
      }
    </Modal>
  );
};

export default CreateFormModal;
