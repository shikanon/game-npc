// 获取NPC角色列表
export interface IGetNPCListRequest {
  limit?: number;
  page?: number;
}
export interface INPCInfo {
  id: string;
  name: string;
  shortDescription: string;
  trait: string;
  promptDescription: string;
  profile: string;
  chatBackground: string;
  affinityLevelDescription: string;
  knowledgeId: string;
  createdAt: string;
  updatedAt: string;
}
export interface IGetNPCListResponse {
  code: number;
  data: INPCInfo[];
  msg: string;
}

// 创建NPC
export interface ICreateNPCRequest {
  name: string;
  shortDescription: string;
  trait: string;
  profile: string;
  chatBackground: string;
  affinityLevelDescription: string;
}
export interface ICreateNPCResponse {
  name: string;
}

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

// NPC文字聊天
export interface INPCChatRequest {
  userId: string;
  npcId: string;
  scene: string;
  question: string;
  contentType: string;
}
export interface INPCMessage {
  affinityScore: number;
  message: string;
  messageType: string;
}
export interface INPCChatResponse {
  code: number;
  data: INPCMessage;
  msg: string;
}

// 查看NPC信息
export interface IGetNPCAllInfoRequest {
  userId: string;
  npcId: string;
}
export interface dialogueItem {
  content?: string | null;
  contentType?: 'text' | 'image';
  createdAt: string;
  id: string;
  roleFrom: string;
  roleTo: string;
}
// NPC全部信息
export interface INPCAllInfo {
  affinityLevel: string;
  affinityLevelDescription: string;
  chatBackground: string;
  createdAt: string;
  dialogueContext?: dialogueItem[];
  dialogueRound: number;
  id: string;
  name: string;
  npcId: string;
  profile: string;
  promptDescription: string;
  scene: string;
  score: number;
  shortDescription: string;
  trait: string;
  userId: string;
}
export interface IGetNPCAllInfoResponse {
  code: number;
  data: INPCAllInfo;
  msg: string;
}

// 获取NPC聊天记录
export interface IGetNPCChatHistoryRequest {
  npcId: string;
  userId: string;
}
export interface IGetNPCChatHistoryResponse {
  code: number;
  data: null;
  msg: string;
}

// 清空我的NPC记忆
export interface IClearMyNPCMemoryRequest {
  npcUserId: string;
  npcId: string;
}
export interface IClearMyNPCMemoryResponse {
  name: string;
}

// 我的NPC场景切换
export interface IMyNPCSceneChangeRequest {
  npcUserId: string;
  scene: string;
}
export interface IMyNPCSceneChangeResponse {
  name: string;
}
