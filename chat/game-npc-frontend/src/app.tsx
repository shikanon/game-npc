// 运行时配置
import { ACCESS_TOKEN_KEY, USER_ID_KEY } from '@/constants';
import { IUserInfo } from '@/interfaces/user';
import userService from '@/services/user';
import { RequestConfig } from '@umijs/max';
import humps from 'humps';
import { message } from "antd";

console.log('环境：', process.env.UMI_ENV);

interface IInitialState {
  user: {
    // 用户模型
    userInfo: IUserInfo | null; // 用户信息
  };
}

// 全局初始化数据配置，用于 Layout 用户信息和权限初始化
// 更多信息见文档：https://umijs.org/docs/max/data-flow
export async function getInitialState(): Promise<IInitialState> {
  const userResult = await userService.Verify();
  console.log('用户信息：', userResult?.data);
  if (userResult?.data?.id) {
    window.localStorage.setItem(USER_ID_KEY, userResult.data.id);

    return {
      user: {
        userInfo: userResult.data || null,
      },
    };
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
      localhost: `/${process.env.UMI_ENV}`,
      'game-npc.clarkchu.com': 'http://game-npc.clarkchu.com/api', // 云开发
    }[window.location.hostname] || '/',
  timeout: 120000, // 超时设置
  withCredentials: true,
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
  },
  requestInterceptors: [
    // @ts-ignore
    (config) => {
      // 添加token
      const token = window.localStorage.getItem(ACCESS_TOKEN_KEY);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      if (config.method === 'post' || config.method === 'delete') {
        config.headers['Content-Type'] = 'application/json;charset=utf-8';
        // 将驼峰转为下划线
        config.data = humps.decamelizeKeys(config.data);
        return config;
      }

      if (config.method === 'get') {
        config.params = humps.decamelizeKeys(config.params);
      }

      console.log(config, '请求配置');

      return config;
    },
  ],
  responseInterceptors: [
    (response: any) => {
      // 拦截响应数据，进行个性化处理
      // console.log('响应结果', response);

      // 将返回的数据转驼峰
      if (response.data) {
        response.data = humps.camelizeKeys(response.data);
      }

      // 全局统一响应错误信息处理
      if (response.data?.code !== 0) {
        message.error(response.data?.msg || '异常错误').then();
      }

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
