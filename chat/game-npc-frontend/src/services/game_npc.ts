import { request } from '@umijs/max';
import { IGameChatRequest, IGameChatResponse, IGetNPCInfoRequest, IGetNPCInfoResponse } from "@/interfaces/game_npc";

export default {
  /**
   * 游戏NPC聊天
   * @constructor
   */
  async GameChat(data?: IGameChatRequest) {
    return await request<IGameChatResponse>('/chat', {
      method: 'POST',
      data,
    });
  },

  /**
   * 获取NPC信息
   * @constructor
   */
  async GetNPCInfo(params?: IGetNPCInfoRequest) {
    return await request<IGetNPCInfoResponse>('/npc-info', {
      method: 'GET',
      params,
    });
  },
};
