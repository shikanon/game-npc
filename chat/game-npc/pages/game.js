// pages/game.js
'use client';
import { useState, useEffect } from 'react'
import ChatComponent from '../components/ChatComponent';
import { useTheme } from 'antd-style';
import styles from './ChatLayout.module.css';

const GameChatPage = () => {
  const theme = useTheme();
  const [showComponent, setShowComponent] = useState(false)

  useEffect(() => setShowComponent(true), [])

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
      }}
    >
      <h1>聊天应用-GameWorld</h1>
      <div className={styles.chatLayout}>
      <aside className={styles.listContainer}>
        {/* 在这里放置按钮列表，点击可以切换页面 */}
        <button>按钮1</button>
        <button>按钮2</button>
        {/* 更多按钮... */}
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