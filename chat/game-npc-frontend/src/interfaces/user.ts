// 用户注册
export interface IUserRegisterRequest {
  name: string;
  password: string;
  phone?: string;
  sex?: string;
}
// 用户信息
export interface IUserInfo {
  id: string;
  createdAt: string;
  money: number;
  name: string;
  password: string;
  phone: string;
  sex: string;
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
  sex?: string;
  phone?: string;
  money?: number;
}
export interface IUpdateUserInfoResponse {
  code: number;
  data: IUserInfo;
  msg: string;
}
