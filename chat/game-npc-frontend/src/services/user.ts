import {
  IUpdateUserInfoRequest,
  IUpdateUserInfoResponse,
  IUserLoginRequest,
  IUserLoginResponse,
  IUserQueryRequest,
  IUserQueryResponse,
  IUserRegisterRequest,
  IUserRegisterResponse,
} from '@/interfaces/user';
import { request } from '@umijs/max';

export default {
  /**
   * 用户注册
   */
  async Register(data?: IUserRegisterRequest) {
    return await request<IUserRegisterResponse>('/user/register', {
      method: 'POST',
      data,
    });
  },

  /**
   * 用户登录
   */
  async Login(data?: IUserLoginRequest) {
    return await request<IUserLoginResponse>('/user/login', {
      method: 'POST',
      data,
    });
  },

  /**
   * 用户查询
   */
  async UserQuery(data?: IUserQueryRequest) {
    return await request<IUserQueryResponse>('/user/query', {
      method: 'POST',
      data,
    });
  },

  /**
   * 更新用户信息
   */
  async UpdateUserInfo(data?: IUpdateUserInfoRequest) {
    return await request<IUpdateUserInfoResponse>('/user/update', {
      method: 'POST',
      data,
    });
  },
};
