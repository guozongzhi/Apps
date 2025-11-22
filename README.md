# 🚀 AI-Native Experiments

![Status](https://img.shields.io/badge/Status-Active-success)
![AI-Generated](https://img.shields.io/badge/Code-AI__Generated-blueviolet)
![Maintainer](https://img.shields.io/badge/Role-Architect_&_Auditor-blue)

欢迎来到 **AI-Native Experiments**。这是一个完全由 AI 辅助构建的实验性仓库。

## 💡 核心理念 (Manifesto)

本仓库的所有代码、文档、甚至测试用例，均遵循 **"AI First"** 原则：

1.  **AI 生成为主**：核心逻辑和代码实现优先使用 LLM (ChatGPT, Claude, DeepSeek, Copilot 等) 生成。
2.  **人类作为架构师**：我的角色是提出需求、设计架构、Code Review 以及调试最终的集成。
3.  **Prompt 即源码**：不仅关注代码本身，更关注生成代码背后的 *Prompt Engineering* 和迭代过程。

## 🛠️ 技术栈与工具 (AI Stack)

在这个旅程中，我主要使用的 AI 协作者包括但不限于：

* **架构与逻辑设计**: [如: ChatGPT o1 / Claude 3.5 Sonnet]
* **代码生成与补全**: [如: Github Copilot / DeepSeek Coder]
* **调试与优化**: [如: Gemini / ChatGPT-4o]

## 📂 目录结构

为了更好地管理不同的 AI 应用尝试，仓库采用以下结构：

```text
.
├── 📂 projects/               # 具体的 AI 应用项目源码
│   ├── 001-project-name/      # 项目 1
│   ├── 002-project-name/      # 项目 2
│   └── ...
├── 📂 prompts/                # 沉淀优秀的 Prompt 模板和对话记录
├── 📂 docs/                   # AI 生成的设计文档或架构图
├── .gitignore
└── README.md
```
## 🚧 实验项目列表 (Roadmap)

| **ID** | **项目名称**               | **简介**             | **核心 AI 技术** | **状态** |
| ------ | -------------------------- | -------------------- | ---------------- | -------- |
| 001    | **Project Initialization** | 仓库搭建与自动化脚本 | Scripting        | ✅ 完成   |
| 002    | **手势识别控制台** | 利用摄像头实时检测手部关键点并判断基础手势含义 | Computer Vision (MediaPipe) | 🔄 进行中 |
| ...    | ...                        | ...                  | ...              | ...      |

## 📝 工作流 (Workflow)

对于每一个新项目，我将遵循以下 "DAR" 流程：

Draft (构思): 向 AI 描述模糊的想法，生成需求文档 (PRD)。

Architect (设计): 让 AI 规划技术栈和文件结构。

Refine (实现): 模块化生成代码，人工进行 Review 和组装。

## ⚠️ 免责声明

虽然我致力于构建高质量应用，但由于代码主要由 AI 生成，可能包含未被发现的逻辑漏洞或幻觉。在生产环境中使用前请务必进行严格审计。

Last Updated: 2025-11-22