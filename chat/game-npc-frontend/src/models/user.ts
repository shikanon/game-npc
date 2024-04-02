// 全局共享数据示例
import { useState } from 'react';
import { IUserInfo } from "@/interfaces/user";

const useUser = () => {
  // 用户信息
  const [userInfo, setUserInfo] = useState<IUserInfo|null>(null);
  // 判断是否需要打开登录弹窗
  const [openLoginModal, setOpenLoginModal] = useState(false);
  // 判断是否需要打开性别设置弹窗
  const [openSexModal, setOpenSexModal] = useState(false);

  return {
    openLoginModal,
    setOpenLoginModal,
    openSexModal,
    setOpenSexModal,
    userInfo,
    setUserInfo,
  };
};

export default useUser;
