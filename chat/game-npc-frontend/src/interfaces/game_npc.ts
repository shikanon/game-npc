// 游戏NPC相关接口
export interface IGameChatRequest {
  question: string;
  userName?: string;
  npcName?: string;
}
export interface IGameChatResponse {
  affinityScore?: number;
  answer?: string;
  thought?: string;
}

// 获取NPC信息
export interface IGetNPCInfoRequest {
  npcName: string;
}
export interface IGetNPCInfoResponse {
  npcName: string;
  npcTrait: string;
  scene: string;
  event: string;
}
