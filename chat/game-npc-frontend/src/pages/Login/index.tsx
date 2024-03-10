import { useEffect } from 'react'
import styles from './index.less';
import { useTheme } from 'antd-style';
import { Button, Col, Form, Input, Row, Space } from "antd";

const Login = () => {
  const theme = useTheme();

  useEffect(() => {

  }, [])

  const onFinish = (values: any) => {
    console.log('Success:', values);
  };

  const onFinishFailed = (errorInfo: any) => {
    console.log('Failed:', errorInfo);
  };

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
      }}
      className={styles.container}
    >
      <Row
         className={styles.title}
      >
        快来登录吧
      </Row>

      <div className={styles.loginContainer}>
        <Form
          name="basic"
          labelCol={{ span: 8 }}
          wrapperCol={{ span: 16 }}
          initialValues={{ remember: true }}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
          autoComplete="off"
        >
          <Form.Item
            label="用户名"
            name="userName"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password />
          </Form.Item>

          <Form.Item
            wrapperCol={{ offset: 10, span: 16 }}
            style={{ marginTop: 50 }}
          >
            <Button
              type={'primary'}
              htmlType="submit"
            >
              注册/登录
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default Login;
