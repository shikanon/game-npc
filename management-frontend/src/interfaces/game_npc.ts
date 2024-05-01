import { UploadFile } from 'antd';

export enum ImageTypeEnum {
  ImageTypeEnum_Unknown = 0,
  ImageTypeEnum_Avatar = 1,
  ImageTypeEnum_ChatBackground = 2,
}

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

// 图片规则
export interface ILevelPictureRule {
  lv: number; // 等级
  imageUrl?: string; // 图片
  description?: string; // 场景或描述
  score?: number;
  imageFileList?: UploadFile[]; // 图片文件列表
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

// 创建NPC
export interface ICreateNPCRequest {
  name: string;
  shortDescription?: string;
  trait?: string;
  profile?: string;
  sex?: NPCCharacterSexEnum;
  chatBackground?: string;
  promptDescription?: string;
  affinityLevelDescription?: string;
  affinityRules?: IAffinityRules[] | null;
  pictures?: INPCLevelPicture[] | null;
  presetProblems?: string[] | null;
  prologue?: string;
}
export interface ICreateNPCResponse {
  code: number;
  data: string | null;
  msg: string;
}

/**
 * 更新NPC角色
 * 备注：单独的更新接口，用于更新NPC角色信息
 */
export interface IUpdateNPCCharacterRequest {
  id?: string; // NPC角色ID
  name?: string; // NPC角色名称
  sex?: NPCCharacterSexEnum; // NPC角色性别
  profile?: string; // NPC角色头像
  chatBackground?: string; // NPC角色聊天背景
  shortDescription?: string; // NPC角色短描述
  trait?: string; // NPC角色描述
  promptDescription?: string; // NPC角色详细描述
  affinityRules?: IAffinityRules[] | null;
  pictures?: INPCLevelPicture[] | null;
  presetProblems?: string[] | null;
  prologue?: string;
  status?: NPCCharacterStatusEnum;
}

export interface IUpdateNPCCharacterResponse {
  code: number;
  data: {
    id: string; // NPC角色ID
    name?: string; // NPC角色名称
    sex?: NPCCharacterSexEnum; // NPC角色性别
    profile?: string; // NPC角色头像
    chatBackground?: string; // NPC角色聊天背景
    shortDescription?: string; // NPC角色短描述
    promptDescription?: string; // NPC角色详细描述
    status: NPCCharacterStatusEnum;
    createdAt: string;
    updatedAt: string;
    affinityRules?: IAffinityRules[] | null;
    pictures?: INPCLevelPicture[] | null;
    presetProblems?: string[] | null;
    prologue?: string;
  };
  msg: string;
}

// 更新NPC角色状态
export interface IUpdateNPCStatusRequest {
  id: string | null;
  status: NPCCharacterStatusEnum;
}
export interface IUpdateNPCStatusResponse {
  code: number;
  data: {
    id: string; // NPC角色ID
    name?: string; // NPC角色名称
    sex?: NPCCharacterSexEnum; // NPC角色性别
    profile?: string; // NPC角色头像
    chatBackground?: string; // NPC角色聊天背景
    shortDescription?: string; // NPC角色短描述
    promptDescription?: string; // NPC角色详细描述
    status: NPCCharacterStatusEnum;
    createdAt: string;
    updatedAt: string;
    affinityRules?: IAffinityRules[];
    pictures?: INPCLevelPicture[];
    presetProblems?: string[];
    prologue?: string;
  };
  msg: string;
}

/**
 * 删除NPC角色
 * 备注：单独的删除接口，用于删除NPC角色
 */
export interface IDeleteNPCCharacterRequest {
  id?: string | null; // NPC角色ID
}

export interface IDeleteNPCCharacterResponse {
  code: number;
  data: null;
  msg: string;
}

/**
 * 获取NPC角色信息
 * 备注：单独的获取NPC角色详情接口，点击调试进入调试页获取NPC角色详情
 */
export interface IGetNPCCharacterInfoRequest {
  id: string | null; // NPC角色ID
}

export interface IGetNPCCharacterInfoResponse {
  code: number;
  data: INPCInfo;
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

// NPC文字聊天
export interface INPCDebugChatRequest {
  userId: string;
  npcId: string;
  scene: string;
  question: string;
  contentType: string;
}
export interface INPCDebugMessage {
  message: string;
  messageType: string;
  affinityScore: number;
  intimacyLevel: number;
  debugMessage: string;
  totalTime: number;
}
export interface INPCDebugChatResponse {
  code: number;
  data: INPCDebugMessage;
  msg: string;
}

export interface IGeneratorNpcTraitRequest {
  npcName: string;
  npcSex: string;
  npcShortDescription: string;
}
export interface IGeneratorNpcTraitResponse {
  code: number;
  data: string | null;
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
  intimacyLevel: number;
  pictures?: INPCLevelPicture[];
  presetProblems?: string[];
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

// 文件上传
export interface IFileUploadRequest {
  file: string;
  imageType: ImageTypeEnum;
}
export interface IFileUploadResponse {
  code: number;
  data: string;
  message: string;
}
