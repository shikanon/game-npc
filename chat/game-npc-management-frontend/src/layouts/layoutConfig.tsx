// 自定义菜单配置

export default {
  route: {
    path: '/',
    routes: [
      {
        name: '角色管理',
        path: '/characterList',
        component: '@/pages/CharacterList',
      },
    ],
  },
  location: {
    pathname: '/',
  },
  appList: [],
};
