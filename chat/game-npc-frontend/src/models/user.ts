// 全局共享数据示例
import { useState } from 'react';
import { IUserInfo } from "@/interfaces/user";

const useUser = () => {
  // 用户信息
  const [userInfo, setUserInfo] = useState<IUserInfo|null>(null);

  return {
    userInfo,
    setUserInfo,
  };
};

export default useUser;
