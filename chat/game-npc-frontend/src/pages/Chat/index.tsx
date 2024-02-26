import { useState, useEffect } from 'react'
import ChatComponent from './components/ChatComponent';
import styles from './index.less';
import { useTheme } from 'antd-style';
import { Button, Popover, Row, Space } from "antd";
import gameNPCServices from '@/services/game_npc';
import { useRequest } from "ahooks";
import { IGetNPCInfoResponse } from "@/interfaces/game_npc";

const GameChatPage = () => {
  const theme = useTheme();
  const [showComponent, setShowComponent] = useState(false)
  const [npcInfo, setNPCInfo] = useState<IGetNPCInfoResponse|null>(null);
  const [showNPCInfo, setShowNPCInfo] = useState(false);

  useEffect(() => setShowComponent(true), [])

  const {
    loading: getNPCInfoLoading,
    runAsync: getNPCInfoRequest,
  } = useRequest(gameNPCServices.GetNPCInfo, {
    manual: true,
  });

  /**
   * 获取NPC信息
   */
  const getNPCInfo = async () => {
    const result = await getNPCInfoRequest({ npcName: '西门牛牛' });

    if (result) {
      setNPCInfo(result);
      setShowNPCInfo(true);
    } else {
      setNPCInfo(null);
      setShowNPCInfo(false);
    }
  };

  return (
    <div
      style={{
        backgroundColor: theme.colorBgLayout,
      }}
      className={styles.container}
    >
      <div style={{ marginLeft: 10 }}><h2>聊天应用-GameWorld</h2></div>

      <div className={styles.chatLayout}>
        <aside className={styles.listContainer}>
          {/* 在这里放置按钮列表，点击可以切换页面 */}
          <Space direction={'vertical'}>
            <Button style={{ width: '100%' }}>买礼物送给她</Button>
            <Popover
              placement={'rightBottom'}
              content={
                <div style={{ width: 400 }}>
                  {showNPCInfo && (
                    <div className={styles.npcInfoModal}>
                      <h2>角色状态信息</h2>
                      <Space direction={'vertical'} size={'large'}>
                        <Row>角色名称：{npcInfo?.npcName}</Row>
                        <Row>好感：{npcInfo?.affinity || '-'}</Row>
                        <Row>性格：{npcInfo?.npcTrait}</Row>
                        <Row>场景：{npcInfo?.scene}</Row>
                        <Row>想法：{npcInfo?.event || '-'}</Row>
                      </Space>
                    </div>
                  )}
                </div>
              }
              title={null}
              trigger="click"
            >
              <Button
                style={{ width: '100%' }}
                loading={getNPCInfoLoading}
                onClick={getNPCInfo}
              >
                查看角色状态信息
              </Button>
            </Popover>

            {/* 更多按钮... */}
            <Button style={{ width: '100%' }}>场景切换</Button>
            <Button style={{ width: '100%' }}>导入语料丰富角色设定</Button>
            <Button style={{ width: '100%' }}>清空对话和记忆</Button>
          </Space>
        </aside>

        <div className={styles.chatContainer}>
          {
            showComponent && <ChatComponent/>
          }
        </div>
      </div>
    </div>
  );
};

export default GameChatPage;

