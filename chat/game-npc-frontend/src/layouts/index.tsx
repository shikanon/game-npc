import layoutConfig from '@/layouts/layoutConfig';
import logoImg from '@/assets/images/logo.png';
import brandImg from '@/assets/images/brand.png';
import feedbackImg from '@/assets/images/feedback.png';
import shareImg from '@/assets/images/share.png';
import userImg from '@/assets/images/user.png';
import { ACCESS_TOKEN_KEY, USER_ID_KEY } from '@/constants';
import { ProLayout } from '@ant-design/pro-components';
import { Outlet, useLocation, useModel } from '@umijs/max';
import { useMount } from 'ahooks';
import { App, Button, Col, ConfigProvider, Image, Input, Modal, Popover, Row } from 'antd';
import copy from 'copy-to-clipboard';
import { useEffect, useState } from 'react';
import styles from './index.less';
import LoginModal from "@/components/LoginModal";
import SexModal from "@/components/SexModal";

const { TextArea } = Input;

interface IFeedbackItemType {
  label: string;
  value: string;
  selected: boolean;
}

export default () => {
  // 初始化的状态数据
  const { initialState } = useModel('@@initialState');
  const { userInfo, setUserInfo, openLoginModal, setOpenLoginModal, openSexModal, setOpenSexModal } = useModel('user');
  const { message } = App.useApp();

  const { pathname } = useLocation();
  // 动态path切换
  const [currentPath, setCurrentPath] = useState('/');
  // 反馈弹窗
  const [modalOpen, setModalOpen] = useState(false);
  // 反馈列表
  const [feedbackList, setFeedbackList] = useState<IFeedbackItemType[]>([
    { label: '功能不完善', value: '1', selected: false },
    { label: '情感表达不准确', value: '2', selected: false },
    { label: '缺乏个性化', value: '3', selected: false },
    { label: '用户体验不佳', value: '4', selected: false },
    { label: '情感表达过于机械', value: '5', selected: false },
  ]);

  useMount(() => {
    // console.log(initialState, 'initialState');
    // console.log(access, 'access');

    if (initialState?.user?.userInfo) {
      setUserInfo(initialState.user.userInfo);
    } else {
      // setOpenLoginModal(true);
    }
  });

  useEffect(() => {
    // console.log(pathname, 'pathname');
    setCurrentPath(pathname);
  }, [pathname]);

  useEffect(() => {}, []);

  return (
    // 更多配置访问：https://procomponents.ant.design/components/layout#prolayout
    <ProLayout
      {...layoutConfig}
      location={{
        pathname: currentPath,
      }}
      token={{
        // 可使用token配置当前layout主题
        // 更多token主题设置访问：https://procomponents.ant.design/components/layout#token
        header: {
          colorBgHeader: '#ffffff',
          colorHeaderTitle: '#141414',
          colorTextMenu: '#dfdfdf',
          colorTextMenuSecondary: '#dfdfdf',
          colorTextMenuSelected: '#fff',
          colorBgMenuItemSelected: '#1677ff', // 设置选中的菜单的背景色
          colorTextMenuActive: 'rgba(255,255,255,0.85)',
          colorTextRightActionsItem: '#dfdfdf',
        },
        sider: {
          colorMenuBackground: '#fff',
          colorMenuItemDivider: '#dfdfdf',
          colorTextMenu: '#595959',
          colorTextMenuSelected: 'rgba(42,122,251,1)',
          colorBgMenuItemSelected: 'rgba(230,243,254,1)',
        },
      }}
      // title="AI聊天"
      // logo={<Image src={logoImg} preview={false} width={48}/>}
      pure={true} // 是否删除掉所有的自带界面
      menu={{
        locale: false, // 是否使用国际化
        defaultOpenAll: true, // 默认展开所有菜单
        ignoreFlatMenu: true, // 忽略手动折叠过的菜单状态
        // type: 'group', // 菜单的类型 // 开启分组
      }}
      siderWidth={200}
      fixSiderbar={true}
      layout="top" // 混合布局模式，另外还有 'top | side | mix'
      // splitMenus={true} // 自动切割菜单是 mix 模式专属的能力，他可以把第一级的菜单放置到顶栏中。我们可以设置 splitMenus=true 来打开它
      headerContentRender={() => null}
      menuFooterRender={() => null}
    >
      <ConfigProvider
        theme={{
          components: {
            Modal: {
              contentBg: '#262626',
            },
          },
        }}
      >
        <App style={{ position: 'relative' }}>
          <Row className={styles.nav} justify={'space-between'} align={'middle'}>
            <Col className={styles.productName}>
              <Row justify={'start'} align={'middle'}>
                <Col>
                  <Image src={brandImg} preview={false} height={24} />
                </Col>
              </Row>
            </Col>
            <Col>
              <Row justify={'end'} align={'middle'}>
                <Col
                  style={{ cursor: 'pointer' }}
                  onClick={() => setModalOpen(true)}
                >
                  <Popover
                    content={'点进来，把你想要的都告诉我们'}
                    title=""
                    trigger="hover"
                    placement={'bottomRight'}
                  >
                    <Image src={feedbackImg} preview={false} width={32} />
                  </Popover>
                </Col>
                <Col style={{ margin: '0 50px' }}>
                  <Popover
                    content={
                      <Button
                        type={'text'}
                        onClick={() => {
                          copy(window.location.href);

                          message.info('复制网址成功，快去分享给朋友吧！').then();
                        }}
                      >
                        一键分享
                      </Button>
                    }
                    title=""
                    trigger="hover"
                  >
                    <Image src={shareImg} preview={false} width={32} />
                  </Popover>
                </Col>
                <Col>
                  <Popover
                    content={
                      <Button
                        type={'text'}
                        onClick={() => {
                          if (userInfo?.id) {
                            setUserInfo(null);
                            window.localStorage.removeItem(USER_ID_KEY);
                            window.localStorage.removeItem(ACCESS_TOKEN_KEY);

                            message.success('退出登录成功').then();

                            setTimeout(() => {
                              setOpenLoginModal(true);
                            }, 500)
                          } else {
                            setOpenLoginModal(true);
                          }
                        }}
                      >
                        {userInfo?.id ? '退出登录' : '登录'}
                      </Button>
                    }
                    title=""
                    trigger="hover"
                  >
                    <Image
                      src={userImg}
                      preview={false}
                      width={32}
                      style={{ cursor: 'pointer' }}
                    />
                  </Popover>
                </Col>
              </Row>
            </Col>
          </Row>

          <Outlet />

          <Modal
            title="你有什么想法，请务必告诉我们"
            centered
            destroyOnClose
            open={modalOpen}
            okText={'提交'}
            width={600}
            onOk={() => setModalOpen(false)}
            okButtonProps={{
              style: {
                background:
                  'linear-gradient(to right, #526EF8, #8AB6E8, #C2FFD8)',
                border: 'none',
              },
            }}
            onCancel={() => setModalOpen(false)}
          >
            <Row
              style={{ marginTop: 30, marginBottom: 10 }}
              justify={'start'}
              align={'middle'}
            >
              {feedbackList.map((item, index) => {
                return (
                  <Col
                    key={index}
                    className={styles.feedbackItem}
                    style={
                      item.selected
                        ? { backgroundColor: '#1677ff', color: '#fff' }
                        : {}
                    }
                    onClick={() => {
                      const list = [...feedbackList];
                      list[index].selected = !list[index].selected;
                      setFeedbackList(list);
                    }}
                  >
                    {item.label}
                  </Col>
                );
              })}
            </Row>

            <Row>
              <TextArea
                style={{ width: '100%', height: 100, padding: 10 }}
                placeholder={
                  '你想要什么新体验？角色更丰富？聊天内容更劲爆？把你的想法告诉我们吧！'
                }
              />
            </Row>
          </Modal>

          <LoginModal
            open={openLoginModal}
            onChange={() => {
              setOpenLoginModal(false);
            }}
          />

          <SexModal
            open={openSexModal}
            onChange={() => {
              setOpenSexModal(false);
            }}
          />
        </App>
      </ConfigProvider>
    </ProLayout>
  );
};
