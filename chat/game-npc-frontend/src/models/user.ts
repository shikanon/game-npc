// 全局共享数据示例
import { INPCInfo } from '@/interfaces/game_npc';
import { IUserInfo } from '@/interfaces/user';
import { useState } from 'react';

const useUser = () => {
  // 用户信息
  const [userInfo, setUserInfo] = useState<IUserInfo | null>(null);
  // 判断是否需要打开登录弹窗
  const [openLoginModal, setOpenLoginModal] = useState(false);
  // 当前选中的角色
  const [currentCharacter, setCurrentCharacter] = useState<INPCInfo | null>(
    null,
  );
  // 判断是否需要打开性别设置弹窗
  const [openSexModal, setOpenSexModal] = useState(false);

  return {
    openLoginModal,
    setOpenLoginModal,
    openSexModal,
    setOpenSexModal,
    currentCharacter,
    setCurrentCharacter,
    userInfo,
    setUserInfo,
  };
};

export default useUser;
