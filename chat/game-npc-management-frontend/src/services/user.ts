import { request } from '@umijs/max';

export default {
  /**
   * 通过code获取bsToken信息
   * @param data
   */
  async SubmitCode(data: any) {
    return await request('/SubmitCode', { method: 'POST', data: data });
  },
};
