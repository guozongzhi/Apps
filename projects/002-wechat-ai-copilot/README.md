# 🤖 Project 002: WeChat AI Copilot (微信智能客服工作台)

本项目是一个 **非侵入式** 的微信智能辅助系统。它不破解微信协议，而是像“外挂”一样通过 Windows UI Automation 技术“看”屏幕，读取聊天内容，并利用 LLM (大模型) 实时生成回复建议。

## 📐 架构设计 (Architecture)

系统分为两个独立进程，通过 HTTP API 通信：

1. **👁️ 眼睛 (Backend Service)**:
   - **技术栈**: Python + `uiautomation` + FastAPI
   - **职责**: 监听微信 PC 版窗口，抓取实时消息，提供本地 API。
2. **🧠 大脑 & UI (Frontend Client)**:
   - **技术栈**: Electron + React + Tailwind CSS
   - **职责**: 显示客服工作台，轮询后端消息，调用 AI 生成回复建议。

## 🏗️ AI 构建指令集 (Build Prompts)

请按顺序复制以下 Prompt 发送给你的 AI 编程助手（如 Cursor, GitHub Copilot, ChatGPT），即可自动生成项目代码。

### Phase 1: 前端 UI 初始化

**复制以下内容给 AI:**

> Prompt 1:
>
> 我需要初始化一个名为 wechat-copilot-ui 的前端项目。
>
> 1. **环境配置**:
>
>    - 使用 Vite + React + Tailwind CSS。
>    - 安装依赖: `lucide-react` (图标), `classnames`, `axios`。
>
> 2. 代码实现:
>
>    请使用以下代码完全替换 src/App.jsx 的内容。这是已经设计好的高保真 UI 原型：

> ```
> import React, { useState, useEffect, useRef } from 'react';
> import { MessageSquare, Users, Settings, Zap, Send, Search, Smile, Paperclip, Bot, RefreshCw, MoreHorizontal, Cpu } from 'lucide-react';
> ```

> // ... (此处省略部分 Mock 数据，由 AI 自动补充或使用下文逻辑) ...

> export default function App() {
>
> const [activeTab, setActiveTab] = useState('chat');
>
> const [inputText, setInputText] = useState('');
>
> // 这里的 messages 状态后续需要改为从后端 API 获取
>
> const [messages, setMessages] = useState({});
>
> const [aiMode, setAiMode] = useState('copilot');

> return (
>
> ```
>    {/* 此处应包含完整的 UI 布局，请参考之前设计的 WechatAICustomerService.jsx */}
>    <div className="flex-1 flex items-center justify-center text-gray-500">
>       UI 初始化中... (请完善侧边栏、联系人列表、聊天框、AI面板布局)
>    </div>
> </div>
> ```
>
> );
>
> }
>
> ```
> **任务**: 请给出终端初始化命令，并补全 `App.jsx` 的完整 UI 代码。
> ```

### Phase 2: 后端监听服务

**复制以下内容给 AI:**

> Prompt 2:
>
> 请创建一个 Python 后端服务，文件名为 backend/server.py。
>
> 1. **依赖**: `pip install uiautomation fastapi uvicorn pydantic`
> 2. **核心代码**: 请直接使用以下逻辑实现微信窗口监听：

> ```
> import uiautomation as auto
> import time
> from fastapi import FastAPI
> from pydantic import BaseModel
> import uvicorn
> from typing import List
> ```

> app = FastAPI()

> class ChatMessage(BaseModel):
>
> sender: str
>
> content: str
>
> time: str

> def get_wechat_window():
>
> \# 查找名为'微信'的主窗口
>
> return auto.WindowControl(searchDepth=1, ClassName='WeChatMainWndForPC', Name='微信')

> @app.get("/api/sync_messages")
>
> def sync_messages():
>
> window = get_wechat_window()
>
> if not window or not window.Exists(0):
>
> return {"status": "error", "message": "WeChat not found"}
>
> ```
> # 查找消息列表
> msg_list = window.ListControl(Name='消息')
> if not msg_list.Exists(0):
>     return {"data": []}
>     
> # 提取最后 10 条消息
> items = msg_list.GetChildren()[-10:]
> data = []
> for item in items:
>     # 简单判断发送者方位 (右侧为己方)
>     rect = item.BoundingRectangle
>     list_rect = msg_list.BoundingRectangle
>     sender = "me" if (rect.left + rect.width/2) > (list_rect.left + list_rect.width/2) else "them"
>     data.append({"sender": sender, "content": item.Name, "time": time.strftime("%H:%M")})
>     
> return {"status": "success", "data": data}
> ```

> if name == "main":
>
> uvicorn.run(app, host="127.0.0.1", port=8000)
>
> ```
> **任务**: 保存该文件，并告诉我如何运行它。
> ```

### Phase 3: 前后端联调 (React Hook)

**复制以下内容给 AI:**

> Prompt 3:
>
> 现在我要将前端连接到 Python 后端。
>
> 请修改 `src/App.jsx`:
>
> 1. 使用 `useEffect` 创建一个轮询器（Polling），每 2000ms 请求一次 `http://127.0.0.1:8000/api/sync_messages`。
> 2. 将获取到的真实消息更新到 React 的 `messages` 状态中。
> 3. **重要**: 当检测到最新的一条消息是 `sender === 'them'` (对方发来的) 且与上一条不同时，自动触发一个 `handleNewIncomingMessage` 函数（我们稍后在这个函数里接 AI）。

### Phase 4: 伪造 AI 智能 (Mock Intelligence)

**复制以下内容给 AI:**

> Prompt 4:
>
> 为了演示智能客服功能，请升级 Python 后端 server.py：
>
> 1. 新增接口 `POST /api/analyze`。
> 2. **逻辑**: 不用真调 OpenAI，写死几个规则：
>    - 如果内容包含 "价格" -> 返回建议 ["我们的基础版是5万/年", "私有化部署需要详谈", "这是价格表.pdf"]
>    - 如果内容包含 "报错" -> 返回建议 ["请截图发我看下", "重启试试？", "技术正在排查"]
>    - 默认 -> 返回 ["您好，请问有什么可以帮您？"]
> 3. 修改前端，在 `handleNewIncomingMessage` 里调用这个接口，并将返回的建议显示在右侧侧边栏。

## 🚀 运行指南 (Run Guide)

### 1. 启动后端 (必须管理员权限)

Windows 的 UIAutomation 通常需要管理员权限才能读取其他软件的句柄。

```
# 打开管理员模式的 PowerShell
cd backend
python server.py
```

### 2. 启动前端

```
cd wechat-copilot-ui
npm run dev
```