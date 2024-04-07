// 运行时配置
import { RequestConfig } from '@umijs/max';
import { message } from 'antd';
import humps from 'humps';
import { USER_ID_KEY } from "@/constants";
import { IUserInfo } from '@/interfaces/user';
import userService from '@/services/user';

interface IInitialState {
  user: {
    // 用户模型
    userInfo: IUserInfo | null; // 用户信息
  };
}

// 全局初始化数据配置，用于 Layout 用户信息和权限初始化
// 更多信息见文档：https://umijs.org/docs/max/data-flow
export async function getInitialState(): Promise<IInitialState> {
  const storageUserId = localStorage.getItem(USER_ID_KEY);
  if (storageUserId) {
    const userResult = await userService.UserQuery({
      id: storageUserId || '',
    });
    console.log('用户信息：', userResult?.data);
    if (userResult?.data?.id) {
      window.localStorage.setItem(USER_ID_KEY, userResult.data.id);

      return {
        user: {
          userInfo: userResult.data || null,
        },
      };
    }
  }
  return {
    user: {
      userInfo: null,
    },
  };
}

// 全局初始化请求配置配置
// 更多信息见文档：https://umijs.org/docs/max/request
export const request: RequestConfig = {
  // 根据访问域名区分接口网关
  baseURL:
    {
      localhost: '/dev',
      'management-game-npc.clarkchu.com':
        'http://game-npc.clarkchu.com/api/', // 云开发
    }[window.location.hostname] || '/',
  timeout: 120000, // 超时设置
  withCredentials: true,
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
  },
  requestInterceptors: [
    // @ts-ignore
    (config) => {
      // 拦截请求数据，进行个性化处理

      if (config.method === 'post' && /file_upload/.test(config.url)) {
        config.headers['Content-Type'] =
          'multipart/form-data;boundary=<calculated when request is sent>';
        return config;
      }

      if (config.method === 'post') {
        config.headers['Content-Type'] = 'application/json;charset=utf-8';
        // 将驼峰转为下划线
        config.data = humps.decamelizeKeys(config.data);
        return config;
      }

      console.log(config, '请求配置');

      return config;
    },
  ],
  responseInterceptors: [
    (response: any) => {
      // 拦截响应数据，进行个性化处理

      // 将返回的数据转驼峰
      if (response.data) {
        response.data = humps.camelizeKeys(response.data);
      }

      // 全局统一响应错误信息处理
      if (response.data?.code !== 0) {
        message.error(response.data?.baseRsp?.subMsg).then();
      }

      // console.log('响应结果', response);

      return response;
    },
  ],
  // other axios options you want
  errorConfig: {
    errorHandler(error: any, opts: any) {
      console.log(error, opts);
      return Promise.reject(error);
    },
    // 错误抛出
    errorThrower: (error: any) => {
      console.log(error, 'error');
      return Promise.reject(error);
    },
  },
};
