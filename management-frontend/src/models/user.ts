// 全局共享数据示例
import { useState } from 'react';
import { IUserInfo } from "@/interfaces/user";

const useUser = () => {
  const [userInfo, setUserInfo] = useState<IUserInfo|null>(null);
  // 判断是否需要打开登录弹窗
  const [openLoginModal, setOpenLoginModal] = useState(false);

  return {
    userInfo,
    setUserInfo,
    openLoginModal,
    setOpenLoginModal,
  };
};

export default useUser;
