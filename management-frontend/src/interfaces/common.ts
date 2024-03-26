/**
 * 翻页查询参数
 */
export interface PageParams {
  page: number;
  limit: number;
}

/**
 * 基础响应类型
 */
export interface IBaseRsp<T = any> {
  code: number;
  config: {
    url: string;
  };
  data?: T;
  msg: string;
  baseRsp: {
    subMsg: string;
    subCode: number;
  };
}
