import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Users, Settings, Zap, Send, Search, Smile, Paperclip, Bot, RefreshCw, MoreHorizontal, Cpu, User } from 'lucide-react';
import classnames from 'classnames';
import axios from 'axios';

const conversations = [
  { id: 1, name: '张三', avatar: 'https://i.pravatar.cc/40?u=a042581f4e29026704d', lastMessage: '好的，明天见！', time: '14:23', unread: 2 },
  { id: 2, name: '李四', avatar: 'https://i.pravatar.cc/40?u=a042581f4e29026705d', lastMessage: '这个需求我们评估一下。', time: '14:20', unread: 0 },
  { id: 3, name: '产品-王五', avatar: 'https://i.pravatar.cc/40?u=a042581f4e29026706d', lastMessage: '[文件] 新版UI设计稿.zip', time: '13:55', unread: 1 },
  { id: 4, name: '技术支持-赵六', avatar: 'https://i.pravatar.cc/40?u=a042581f4e29026707d', lastMessage: '你那边现在能复现吗？', time: '13:40', unread: 0 },
  { id: 5, name: '市场部-周七', avatar: 'https://i.pravatar.cc/40?u=a042581f4e29026708d', lastMessage: '活动下周上线，请周知。', time: '11:10', unread: 0 },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [activeConversation, setActiveConversation] = useState(1);
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState({});
  const [aiMode, setAiMode] = useState('copilot');
  const [currentSuggestions, setCurrentSuggestions] = useState(["您好，请问有什么可以帮您的？", "稍等，我正在为您查询。", "很高兴为您服务。"]);
  const [wechatStatus, setWechatStatus] = useState('connecting'); // 'connecting', 'ok', 'error'

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, activeConversation]);

  useEffect(() => {
    const intervalId = setInterval(() => {
      axios.get('http://127.0.0.1:8000/api/sync_messages')
        .then(response => {
          if (response.data.status === 'success') {
            setWechatStatus('ok');
            const fetchedMessages = response.data.data;
            
            setMessages(prevMessages => {
              const currentMessages = prevMessages[activeConversation] || [];
              const lastKnownMessage = currentMessages[currentMessages.length - 1];
              const lastFetchedMessage = fetchedMessages[fetchedMessages.length - 1];

              if (lastFetchedMessage && lastFetchedMessage.sender === 'them' && 
                  (!lastKnownMessage || lastKnownMessage.content !== lastFetchedMessage.content)) {
                handleNewIncomingMessage(lastFetchedMessage);
              }
              
              return { ...prevMessages, [activeConversation]: fetchedMessages };
            });
          } else {
            setWechatStatus('error');
            console.error("WeChat not found or error syncing messages.");
          }
        })
        .catch(error => {
          setWechatStatus('error');
          console.error("Error connecting to backend:", error);
        });
    }, 2000);

    return () => clearInterval(intervalId);
  }, [activeConversation]);


  const handleNewIncomingMessage = (message) => {
    console.log("New incoming message, triggering AI:", message);
    axios.post('http://127.0.0.1:8000/api/analyze', { content: message.content })
      .then(response => {
        if (response.data && response.data.suggestions) {
          setCurrentSuggestions(response.data.suggestions);
        }
      })
      .catch(error => {
        console.error("Error analyzing message:", error);
        setCurrentSuggestions(["您好，请问有什么可以帮您的？", "稍等，我正在为您查询。", "很高兴为您服务。"]);
      });
  };
  
  const handleSendMessage = () => {
    if (!inputText.trim()) return;
    const newMessage = {
      sender: 'me',
      content: inputText,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
    };
    setMessages(prev => ({
        ...prev,
        [activeConversation]: [...(prev[activeConversation] || []), newMessage]
    }));
    setInputText('');
  };

  const activeConvDetails = conversations.find(c => c.id === activeConversation);

  return (
    <div className="flex h-screen w-full bg-[#f0f2f5] text-sm">
      {/* Left Sidebar */}
       <div className="flex flex-col items-center gap-6 bg-[#e6e6e6] p-2">
        <User className="h-10 w-10 text-gray-600 bg-white rounded-full p-1" />
        <div className="flex flex-col gap-4">
          <button className={classnames("p-2 rounded-md", {'bg-[#c9c9c9]': activeTab === 'chat'})} onClick={() => setActiveTab('chat')}>
            <MessageSquare className="h-6 w-6 text-gray-700" />
          </button>
          <button className={classnames("p-2 rounded-md", {'bg-[#c9c9c9]': activeTab === 'users'})} onClick={() => setActiveTab('users')}>
            <Users className="h-6 w-6 text-gray-700" />
          </button>
          <button className={classnames("p-2 rounded-md", {'bg-[#c9c9c9]': activeTab === 'settings'})} onClick={() => setActiveTab('settings')}>
            <Settings className="h-6 w-6 text-gray-700" />
          </button>
        </div>
        <div className="mt-auto">
            <Zap className="h-6 w-6 text-gray-700" />
        </div>
      </div>

      {/* Conversation List */}
      <div className="w-64 flex-shrink-0 border-r border-gray-200 bg-[#f7f7f7] flex flex-col">
        <div className="p-2 border-b border-gray-200">
            <div className="relative">
                <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input type="text" placeholder="搜索" className="w-full rounded-md bg-[#e2e2e2] p-1 pl-8 text-xs focus:outline-none" />
            </div>
        </div>
        <div className="flex-1 overflow-y-auto">
            {conversations.map(conv => (
                <div key={conv.id} 
                     className={classnames("flex items-center p-3 cursor-pointer hover:bg-[#e9e9e9]", {"bg-[#c9c9c9]": activeConversation === conv.id})}
                     onClick={() => setActiveConversation(conv.id)}>
                    <img src={conv.avatar} alt={conv.name} className="h-10 w-10 rounded-md mr-3" />
                    <div className="flex-1 overflow-hidden">
                        <div className="flex justify-between items-center">
                            <p className="font-medium text-gray-800 truncate">{conv.name}</p>
                            <p className="text-xs text-gray-400">{conv.time}</p>
                        </div>
                        <div className="flex justify-between items-start">
                            <p className="text-xs text-gray-500 truncate">{conv.lastMessage}</p>
                            {conv.unread > 0 && <span className="bg-red-500 text-white text-[10px] rounded-full px-1.5 py-0.5">{conv.unread}</span>}
                        </div>
                    </div>
                </div>
            ))}
        </div>
      </div>

      {/* Main Chat Window */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="flex items-center justify-between p-3 border-b border-gray-200 bg-white">
            <div className="font-semibold text-gray-800">{activeConvDetails?.name || 'Chat'}</div>
             <div className="text-xs text-gray-500 flex items-center gap-2">
                {wechatStatus === 'connecting' && <><RefreshCw className="h-3 w-3 animate-spin" /><span>连接中...</span></>}
                {wechatStatus === 'ok' && <span className="h-2 w-2 bg-green-500 rounded-full"></span>}
                {wechatStatus === 'error' && <span className="text-red-500">连接失败</span>}
            </div>
            <button><MoreHorizontal className="h-5 w-5 text-gray-500" /></button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 bg-[#f0f2f5]">
            {(messages[activeConversation] || []).map((msg, index) => (
                <div key={index} className={classnames("flex mb-4", {'justify-end': msg.sender === 'me'})}>
                    {msg.sender === 'them' && <img src={activeConvDetails?.avatar} alt="avatar" className="h-8 w-8 rounded-md mr-3" />}
                    <div className={classnames("max-w-md rounded-lg px-3 py-2 text-sm", {
                        'bg-white text-gray-800': msg.sender === 'them',
                        'bg-[#95ec69] text-gray-800': msg.sender === 'me'
                    })}>
                        {msg.content}
                    </div>
                     {msg.sender === 'me' && <img src="https://i.pravatar.cc/40?u=me" alt="my-avatar" className="h-8 w-8 rounded-md ml-3" />}
                </div>
            ))}
            <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <div className="p-4 border-t border-gray-200 bg-white">
            <div className="flex items-center gap-4 text-gray-500">
                <Smile className="h-6 w-6 cursor-pointer" />
                <Paperclip className="h-6 w-6 cursor-pointer" />
            </div>
            <textarea 
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSendMessage())}
                placeholder="输入消息..."
                className="w-full h-24 p-2 resize-none bg-transparent focus:outline-none"
            />
            <div className="flex justify-end">
                <button 
                    onClick={handleSendMessage}
                    className="px-6 py-1.5 bg-[#07c160] text-white rounded-md text-sm hover:bg-[#06ad56] disabled:bg-gray-300"
                    disabled={!inputText.trim()}
                >
                    发送
                </button>
            </div>
        </div>
      </div>

      {/* AI Copilot Sidebar */}
      <div className="w-80 flex-shrink-0 border-l border-gray-200 bg-white flex flex-col">
         <div className="p-3 border-b border-gray-200">
            <div className="flex items-center gap-2">
                <Cpu className="h-5 w-5 text-blue-500" />
                <h2 className="font-semibold text-gray-800">AI Copilot</h2>
            </div>
        </div>
        
        <div className="p-4 flex-1 flex flex-col gap-4">
            <div className="flex rounded-md bg-gray-100 p-1">
                <button 
                    className={classnames("flex-1 text-center text-xs p-1 rounded-md", {'bg-white shadow-sm': aiMode === 'copilot'})}
                    onClick={() => setAiMode('copilot')}
                >
                    <Bot className="h-4 w-4 inline-block mr-1" />
                    辅助模式
                </button>
                 <button 
                    className={classnames("flex-1 text-center text-xs p-1 rounded-md", {'bg-white shadow-sm': aiMode === 'auto'})}
                    onClick={() => setAiMode('auto')}
                >
                    <Zap className="h-4 w-4 inline-block mr-1" />
                    自动回复
                </button>
            </div>

            <div className="flex items-center justify-between">
                <p className="text-xs font-semibold text-gray-600">回复建议</p>
                <button onClick={() => handleNewIncomingMessage((messages[activeConversation] || []).slice(-1)[0])}><RefreshCw className="h-4 w-4 text-gray-400 hover:text-gray-600" /></button>
            </div>
            
            <div className="flex flex-col gap-2">
                {currentSuggestions.map((suggestion, i) => (
                    <div key={i} className="bg-gray-50 p-2 rounded-md cursor-pointer hover:bg-gray-100" onClick={() => setInputText(suggestion)}>
                        <p className="text-xs text-gray-700">{suggestion}</p>
                    </div>
                ))}
            </div>
        </div>
        
        <div className="p-4 border-t border-gray-200 text-center">
            <p className="text-xs text-gray-400">由 Gemini 驱动</p>
        </div>
      </div>
    </div>
  );
}