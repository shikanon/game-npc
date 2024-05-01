import {
  IClearNPCHistoryRequest,
  IClearNPCHistoryResponse,
  IGetNPCAllInfoRequest,
  IGetNPCAllInfoResponse,
  IGetNPCChatHistoryRequest,
  IGetNPCChatHistoryResponse,
  IGetNPCListRequest,
  IGetNPCListResponse,
  IGetNPCPictureRequest,
  IGetNPCPictureResponse,
  IGetNPCPresetProblemsRequest,
  IGetNPCPresetProblemsResponse,
  IGetNPCPrologueRequest,
  IGetNPCPrologueResponse,
  IMyNPCSceneChangeRequest,
  IMyNPCSceneChangeResponse,
  INPCChatPromptRequest,
  INPCChatPromptResponse,
  INPCChatRequest,
  INPCChatResponse,
} from '@/interfaces/game_npc';
import { request } from '@umijs/max';

export default {
  /**
   * 查询NPC角色列表
   */
  async GetNPCList(data?: IGetNPCListRequest) {
    return await request<IGetNPCListResponse>('/npc/query', {
      method: 'POST',
      data,
    });
  },

  /**
   * NPC文字聊天
   */
  async NPCChat(data?: INPCChatRequest) {
    return await request<INPCChatResponse>('/npc/chat', {
      method: 'POST',
      data,
    });
  },

  /**
   * 查看NPC全部信息
   */
  async GetNPCAllInfo(data?: IGetNPCAllInfoRequest) {
    return await request<IGetNPCAllInfoResponse>('/npc/get_npc_all_info', {
      method: 'POST',
      data,
    });
  },

  /**
   * 获取NPC聊天记录
   */
  async GetNPCChatHistory(data?: IGetNPCChatHistoryRequest) {
    return await request<IGetNPCChatHistoryResponse>(
      '/npc/get_history_dialogue',
      {
        method: 'POST',
        data,
      },
    );
  },

  /**
   * 清空NPC聊天记录
   */
  async ClearNPCHistory(data?: IClearNPCHistoryRequest) {
    return await request<IClearNPCHistoryResponse>(
      '/npc/clear_history_dialogue',
      {
        method: 'POST',
        data,
      },
    );
  },

  /**
   * 我的NPC场景切换
   */
  async MyNPCSceneSwitch(data?: IMyNPCSceneChangeRequest) {
    return await request<IMyNPCSceneChangeResponse>('/npc/shift_scenes', {
      method: 'POST',
      data,
    });
  },

  /**
   * 获取NPC开场白信息
   */
  async GetNPCPrologue(data?: IGetNPCPrologueRequest) {
    return await request<IGetNPCPrologueResponse>('/npc/get_prologue', {
      method: 'POST',
      data,
    });
  },

  /**
   * 获取NPC预置问题
   */
  async GetNPCPresetProblems(data?: IGetNPCPresetProblemsRequest) {
    return await request<IGetNPCPresetProblemsResponse>(
      '/npc/get_preset_problems',
      {
        method: 'POST',
        data,
      },
    );
  },

  /**
   * 获取NPC相关图片
   */
  async GetNPCPicture(data?: IGetNPCPictureRequest) {
    return await request<IGetNPCPictureResponse>('/npc/get_picture', {
      method: 'POST',
      data,
    });
  },

  /**
   * NPC聊天提示
   */
  async NPCChatPrompt(data?: INPCChatPromptRequest) {
    return await request<INPCChatPromptResponse>('/npc/chat-suggestion', {
      method: 'POST',
      data,
    });
  },
};
