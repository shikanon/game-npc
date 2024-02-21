import {} from '@/constants';
import layoutConfig from '@/layouts/layoutConfig';
import logoImg from '@/assets/images/logo.png';
import { ProLayout } from '@ant-design/pro-components';
import { Outlet, useAccess, useLocation, useModel } from '@umijs/max';
import { useMount } from 'ahooks';
import { App, Image } from 'antd';
import { useEffect, useState } from 'react';

export default () => {
  // 初始化的状态数据
  const { initialState } = useModel('@@initialState');
  const {} = useModel('global');

  // 初始化的用户权限
  const access = useAccess();
  const { pathname } = useLocation();
  // 动态path切换
  const [currentPath, setCurrentPath] = useState('/');

  useMount(() => {
    console.log(initialState, 'initialState');
    console.log(access, 'access');
  });

  useEffect(() => {
    // console.log(pathname, 'pathname');
    setCurrentPath(pathname);
  }, [pathname]);

  useEffect(() => {

  }, []);

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
      title="AI聊天"
      logo={<Image src={logoImg} preview={false} width={48}/>}
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
      <App>
        <Outlet />
      </App>
    </ProLayout>
  );
};
