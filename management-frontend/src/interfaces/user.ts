// NPC角色性别枚举
export enum UserSexEnum {
  UserSexEnum_Unknown = 0, // 未知
  UserSexEnum_Male = 1, // 男
  UserSexEnum_Female = 2, // 女
}

// 用户注册
export interface IUserRegisterRequest {
  name: string;
  password: string;
  phone?: string;
  sex?: UserSexEnum;
}
// 用户信息
export interface IUserInfo {
  id: string;
  createdAt: string;
  money: number;
  name: string;
  password: string;
  phone: string;
  sex: UserSexEnum;
}
export interface IUserRegisterResponse {
  code: number;
  data: IUserInfo;
  msg: string;
}

// 用户登录
export interface IUserLoginRequest {
  name: string;
  password: string;
}
export interface IUserLoginResponse {
  code: number;
  data: IUserInfo;
  msg: string;
}

// 用户查询
export interface IUserQueryRequest {
  id: string;
  name?: string;
  orderBy?: any;
  page?: number;
  limit?: number;
}
export interface IUserQueryResponse {
  code: number;
  data: IUserInfo;
  msg: string;
}

// 更新用户信息
export interface IUpdateUserInfoRequest {
  id: string;
  name?: string;
  password?: string;
  sex?: UserSexEnum;
  phone?: string;
  money?: number;
}
export interface IUpdateUserInfoResponse {
  code: number;
  data: IUserInfo;
  msg: string;
}
