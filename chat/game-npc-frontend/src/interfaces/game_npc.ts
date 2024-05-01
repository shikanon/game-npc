// NPC角色状态枚举
export enum NPCCharacterStatusEnum {
  NPCCharacterStatusEnum_Unknown = 0, // 未知
  NPCCharacterStatusEnum_Save = 1, // 待发布
  NPCCharacterStatusEnum_Publish = 2, // 已发布
}

// NPC角色性别枚举
export enum NPCCharacterSexEnum {
  NPCCharacterSexEnum_Unknown = 0, // 未知
  NPCCharacterSexEnum_Male = 1, // 男
  NPCCharacterSexEnum_Female = 2, // 女
}

// 好感度规则
export interface IAffinityRules {
  lv: number;
  content?: string;
  score?: number;
}

// NPC聊天等级
export interface INPCLevelPicture {
  lv: number;
  imageUrl?: string;
  description?: string;
  score?: number;
}

// NPC角色信息
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
  sex: NPCCharacterSexEnum;
  status: NPCCharacterStatusEnum;
  createdAt: string;
  updatedAt: string;
  affinityRules?: IAffinityRules[] | null;
  pictures?: INPCLevelPicture[] | null;
  presetProblems?: string[] | null;
  prologue?: string;
}

// 获取NPC角色列表
export interface IGetNPCListRequest {
  name?: string;
  limit?: number;
  page?: number;
}

export interface IGetNPCListResponse {
  code: number;
  data: {
    list: INPCInfo[];
    total: number;
  };
  msg: string;
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
  intimacyLevel: number;
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
  affinityLevel: number;
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
  intimacyLevel: number;
  affinityRules?: IAffinityRules[] | null;
  pictures?: INPCLevelPicture[] | null;
  presetProblems?: string[] | null;
  prologue?: string;
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

// 清空NPC历史对话
export interface IClearNPCHistoryRequest {
  npcId: string;
  userId: string;
}
export interface IClearNPCHistoryResponse {
  code: number;
  data: null;
  msg: string;
}

// 我的NPC场景切换
export interface IMyNPCSceneChangeRequest {
  npcUserId: string;
  scene: string;
}
export interface IMyNPCSceneChangeResponse {
  name: string;
}

// 获取NPC开场白信息
export interface IGetNPCPrologueRequest {
  id: string;
}
export interface IGetNPCPrologueResponse {
  code: number;
  data: string;
  msg: string;
}

// 获取NPC预置问题
export interface IGetNPCPresetProblemsRequest {
  id: string;
}
export interface IGetNPCPresetProblemsResponse {
  code: number;
  data: string[];
  msg: string;
}

// 获取NPC相关图片
export interface IGetNPCPictureRequest {
  id: string;
  lv: number;
}
export interface IGetNPCPictureResponse {
  code: number;
  data: INPCLevelPicture[];
  msg: string;
}

// NPC聊天提示推荐
export interface INPCChatPromptRequest {
  npcId: string;
  userId: string;
}
export interface INPCChatPromptResponse {
  code: number;
  data: {
    suggestionMessages: string[];
  };
  msg: string;
}
