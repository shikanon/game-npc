import React from 'react';
import { ProChat } from '@ant-design/pro-chat';
import fetch from 'isomorphic-unfetch';

var question = "";
var user_name = "";
var npc_name = "";

const ChatComponent = () => {
  const handleRequest = async (messages) => {
    console.log("message:\n",messages);
    const lastMessage = messages[messages.length - 1];
    question = lastMessage.content;
    console.log("question:\n",question);
    // 模拟发送消息到服务端并接收回复的逻辑
    // 这里只是一个例子，您应根据实际情况进行适当的实现
    const url = "http://127.0.0.1:8000/chat";
    // const url = "http://175.178.22.107:8000/chat";
    user_name = "小名"
    npc_name = "西门牛牛"
    const postData = {
      question: question,
      user_name: user_name,
      npc_name: npc_name,
    };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      });
      const responseData = await response.json();
      console.log(responseData);
      return new Response(responseData.answer);
    } catch (error) {
      // 错误处理
      console.error("Failed to fetch response:", error);
    }
  };

  return (
    <ProChat
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
