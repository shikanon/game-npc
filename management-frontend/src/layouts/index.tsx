import logo from '@/assets/images/logo.png';
import {} from '@/constants';
import layoutConfig from '@/layouts/layoutConfig';
import { LogoutOutlined } from '@ant-design/icons';
import { ProLayout } from '@ant-design/pro-components';
import { Outlet, history, useAccess, useLocation, useModel } from '@umijs/max';
import { useMount } from 'ahooks';
import {
  App,
  Avatar,
  Col,
  Divider,
  Dropdown,
  Image,
  Row,
  Typography,
} from 'antd';
import { useEffect, useRef, useState } from 'react';
import styles from './index.less';

const { Text } = Typography;

export default () => {
  // 初始化的状态数据
  const { initialState } = useModel('@@initialState');

  // 初始化的用户权限
  const access = useAccess();
  const { pathname } = useLocation();
  // 动态path切换
  const [currentPath, setCurrentPath] = useState('/');

  // 功能点漫游指引元素
  const tour1EleRef = useRef(null);
  const tour2EleRef = useRef(null);

  useMount(() => {
    console.log(initialState, 'initialState');
    console.log(access, 'access');
  });

  useEffect(() => {
    // console.log(pathname, 'pathname');
    setCurrentPath(pathname);
  }, [pathname]);

  /**
   * 退出登录
   */
  const onMenuClick = async () => {
    // 退出登录 注释掉，因为这个接口没有实现
  };

  // 用户抽屉菜单
  const menu = {
    items: [
      {
        key: 'logout',
        label: '退出登录',
        icon: <LogoutOutlined />,
        onClick: onMenuClick,
        className: styles.menu,
      },
    ],
  };

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
      title="NPC管理系统"
      logo={<Image src={logo} width={32} preview={false} />}
      menu={{
        locale: false, // 是否使用国际化
        defaultOpenAll: true, // 默认展开所有菜单
        ignoreFlatMenu: true, // 忽略手动折叠过的菜单状态
        // type: 'group', // 菜单的类型 // 开启分组
      }}
      siderWidth={200}
      fixSiderbar={true}
      layout="mix" // 混合布局模式，另外还有 'top | side | mix'
      // splitMenus={true} // 自动切割菜单是 mix 模式专属的能力，他可以把第一级的菜单放置到顶栏中。我们可以设置 splitMenus=true 来打开它
      menuItemRender={(item, dom) => {
        if (item.path === '/metric-list') {
          return (
            <a
              ref={tour1EleRef}
              onClick={() => {
                history.push(item?.path || '/');
                setCurrentPath(item?.path || '/');
              }}
            >
              {dom}
            </a>
          );
        } else if (item.path === '/mutex-group') {
          return (
            <a
              ref={tour2EleRef}
              onClick={() => {
                history.push(item?.path || '/');
                setCurrentPath(item?.path || '/');
              }}
            >
              {dom}
            </a>
          );
        } else {
          return (
            <a
              onClick={() => {
                history.push(item?.path || '/');
                setCurrentPath(item?.path || '/');
              }}
            >
              {dom}
            </a>
          );
        }
      }}
      headerContentRender={() => null}
      menuFooterRender={() => (
        <Col>
          <Row>
            <Divider />
          </Row>

          {/*头像昵称*/}
          <Row>
            <Dropdown autoAdjustOverflow menu={menu}>
              <Row justify="start" align="middle">
                <Col style={{ marginLeft: 8 }}>
                  <Avatar className={styles.avatar} src={null} alt="avatar">
                    --
                  </Avatar>
                </Col>
                <Col style={{ marginLeft: 10 }}>
                  <Text>{'--'}</Text>
                </Col>
              </Row>
            </Dropdown>
          </Row>
        </Col>
      )}
    >
      <App>
        <Outlet />
      </App>
    </ProLayout>
  );
};
