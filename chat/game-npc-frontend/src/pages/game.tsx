// pages/game.js
'use client';
import { useState, useEffect } from 'react'
import ChatComponent from '../components/ChatComponent';
import { useTheme } from 'antd-style';
import styles from './ChatLayout.module.css';

const GameChatPage = () => {
  const theme = useTheme();
  const [showComponent, setShowComponent] = useState(false)
  const [npcInfo, setNPCInfo] = useState(null);
  const [showNPCInfo, setShowNPCInfo] = useState(false);

  useEffect(() => setShowComponent(true), [])

  const fetchNPCInfo = async () => {
    try {
      const queryParams = new URLSearchParams({ npc_name: "西门牛牛" });
      const infoUrl = `http://127.0.0.1:8000/npc-info?${queryParams.toString()}`;
      const response = await fetch(infoUrl);
      if (response.ok) {
        const data = await response.json();
        setNPCInfo(data);
        setShowNPCInfo(true);
      } else {
        throw new Error('Network response was not ok.');
      }
    } catch (error) {
      console.error("Fetching NPC info failed", error);
      // 处理错误，可能是显示一个错误信息
    }
  };

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
      }}
    >
      <h1>聊天应用-GameWorld-泛互行解团队演示demo</h1>
      <div className={styles.chatLayout}>
      <aside className={styles.listContainer}>
        {/* 在这里放置按钮列表，点击可以切换页面 */}
        <button>买礼物送给她</button>
        <button onClick={fetchNPCInfo}>查看角色状态信息</button>
        {showNPCInfo && (
        <div className={styles.npcInfoModal}>
          <h2>角色状态信息</h2>
          <p>角色名称:</p>
          <p>{npcInfo.npc_name}</p>
          <p>性格:</p>
          <p>{npcInfo.npc_trait}</p>
          <p>场景:</p>
          <p>{npcInfo.scene}</p>
          <p>想法:</p>
          <p>{npcInfo.event}</p>
          <button onClick={() => setShowNPCInfo(false)}>关闭状态框</button>
        </div>
        )}
        {/* 更多按钮... */}
        <button>战斗</button>
        <button>导入语料丰富角色设定</button>
        <button>清空对话和记忆</button>
      </aside>
      <div className={styles.chatContainer}>
        {
          showComponent && <ChatComponent />
        }   
      </div>
    </div> 
    </div>
  );
};

export default GameChatPage;