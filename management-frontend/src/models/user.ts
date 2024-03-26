// 全局共享数据示例
import { useState } from 'react';

const useUser = () => {
  const [userInfo, setUserInfo] = useState(null);
  return {
    userInfo,
    setUserInfo,
  };
};

export default useUser;
