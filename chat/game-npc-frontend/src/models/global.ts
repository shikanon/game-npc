// 全局共享数据示例
import { useState } from 'react';

const useGlobal = () => {
  const [name, setName] = useState<string>('');

  return {
    name,
    setName,
  };
};

export default useGlobal;
