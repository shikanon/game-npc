import React from 'react';
import { ProChat } from '@ant-design/pro-chat';
import { useRequest } from 'ahooks';
import gameNPCServices from '@/services/game_npc';

const ChatComponent = () => {
  const {
    // loading: gameChatLoading,
    runAsync: gameChatRequest,
  } = useRequest(gameNPCServices.GameChat, {
    manual: true,
  });

  /**
   * 发起聊天
   * @param messages
   */
  const handleRequest = async (messages: any): Promise<any> => {
    console.log("message:\n",messages);
    const lastMessage = messages[messages.length - 1];
    const question = lastMessage.content;
    console.log("question:\n",question);
    const userName = "小名"
    const npcName = "西门牛牛"

    // 模拟发送消息到服务端并接收回复的逻辑
    // 这里只是一个例子，您应根据实际情况进行适当的实现

    const result = await gameChatRequest({
      question: question,
      userName: userName,
      npcName: npcName,
    });

    console.log("result:",result);

    if (result) {
      return new Response(result.answer);
    } else {
      return new Response(null);
    }
  };

  return (
    <ProChat
      // loading={gameChatLoading}
      style={{
        height: '80vh',
        width: '80vw',
        marginLeft: 'auto',
        marginRight: 0,
      }}
      request={handleRequest}
    />
  );
};

export default ChatComponent;
