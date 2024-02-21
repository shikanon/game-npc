// 自定义菜单配置
import { WechatOutlined } from "@ant-design/icons";

export default {
  route: {
    path: '/',
    routes: [
      {
        name: '聊天',
        path: '/home',
        icon: <WechatOutlined />,
        routes: [],
      },
    ],
  },
  location: {
    pathname: '/',
  },
  appList: [],
};
