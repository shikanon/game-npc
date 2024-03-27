import {
  IClearNPCHistoryRequest, IClearNPCHistoryResponse,
  ICreateNPCRequest,
  ICreateNPCResponse,
  IDeleteNPCCharacterRequest,
  IDeleteNPCCharacterResponse,
  IFileUploadRequest,
  IFileUploadResponse,
  IGetNPCAllInfoRequest,
  IGetNPCAllInfoResponse,
  IGetNPCCharacterInfoRequest,
  IGetNPCCharacterInfoResponse,
  IGetNPCChatHistoryRequest,
  IGetNPCChatHistoryResponse,
  IGetNPCListRequest,
  IGetNPCListResponse,
  IMyNPCSceneChangeRequest,
  IMyNPCSceneChangeResponse,
  INPCChatRequest,
  INPCChatResponse,
  IUpdateNPCCharacterRequest,
  IUpdateNPCCharacterResponse,
  IUpdateNPCStatusRequest,
  IUpdateNPCStatusResponse,
} from '@/interfaces/game_npc';
import { request } from '@umijs/max';

export default {
  /**
   * 创建NPC
   */
  async CreateNPC(data?: ICreateNPCRequest) {
    return await request<ICreateNPCResponse>('/npc/create', {
      method: 'POST',
      data,
    });
  },

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
   * 更新NPC角色
   */
  async UpdateNPC(data?: IUpdateNPCCharacterRequest) {
    return await request<IUpdateNPCCharacterResponse>('/npc/update', {
      method: 'POST',
      data,
    });
  },

  /**
   * 更新NPC角色状态
   */
  async UpdateNPCStatus(data?: IUpdateNPCStatusRequest) {
    return await request<IUpdateNPCStatusResponse>('/npc/update_status', {
      method: 'POST',
      data,
    });
  },

  /**
   * 查看单个NPC信息
   */
  async GetNPCInfo(data?: IGetNPCCharacterInfoRequest) {
    return await request<IGetNPCCharacterInfoResponse>('/npc/get', {
      method: 'POST',
      data,
    });
  },

  /**
   * 删除NPC角色
   */
  async DeleteNPC(data: IDeleteNPCCharacterRequest) {
    return await request<IDeleteNPCCharacterResponse>('/npc/remove', {
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
   * 我的NPC场景切换
   */
  async MyNPCSceneSwitch(data?: IMyNPCSceneChangeRequest) {
    return await request<IMyNPCSceneChangeResponse>('/npc/shift_scenes', {
      method: 'POST',
      data,
    });
  },

  /**
   * 文件上传请求
   */
  async FileUpload(data?: IFileUploadRequest) {
    return await request<IFileUploadResponse>('/npc/file_upload', {
      method: 'POST',
      data,
    });
  },
};
