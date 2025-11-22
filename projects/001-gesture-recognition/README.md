# 🖐️ Project 001: Real-time Gesture Recognition (实时手势识别)

![Status](https://img.shields.io/badge/Status-Complete-success)
![AI-Model](https://img.shields.io/badge/AI-MediaPipe-blue)
![Language](https://img.shields.io/badge/Python-3.8+-yellow)

本项目使用 **Google MediaPipe** 和 **OpenCV** 实现了一个基于摄像头的实时手势识别系统。它可以捕捉手部骨骼关键点，并根据几何规则判断简单的手势含义。

## ✨ 功能特性

* 📷 **实时捕捉**：调用电脑摄像头获取视频流。
* 🦴 **骨骼可视化**：在画面上绘制 21 个手部关键点及连接线。
* 🤖 **手势分类**：目前支持识别以下手势：
    * ✋ **Open Palm** (手掌张开)
    * ✊ **Closed Fist** (握拳)
    * 👍 **Thumbs Up** (点赞/竖大拇指)
    * 🚫 **None** (未检测到或无法识别)

## 🚀 快速开始 (Quick Start)

### 1. 安装依赖

确保你位于 `projects/001-gesture-recognition` 目录下：

```bash
pip install -r requirements.txt
```

### 2. 安装依赖

让 pip 安装 AI 建议的依赖包：

```
pip install -r requirements.txt
```

### 3. 运行程序

启动主程序：

```
python main.py
```

*按键盘上的 **`q`** 键可退出程序。*



## 🧠 AI 协作日志 (Prompt Log)



本项目的核心价值在于“Prompt 即源码”。以下是构建本项目时使用的关键提示词（Prompts），你可以参考这些思路来复现或改进项目。



### 1. 基础设施搭建 (Infrastructure)

**目的**：确定技术栈并生成依赖文件。

> **User Prompt:**
>
> Plaintext
>
> ```
> 我正在初始化一个新的 Python 项目。目标是使用电脑摄像头实时检测手势。
> 我决定使用的技术栈是 OpenCV 用于视频流处理，MediaPipe Solutions 用于手部关键点检测。
> ```

> 请为我生成一个合适的 `requirements.txt` 文件内容，只包含最核心的依赖。



### 2. MVP 核心逻辑生成 (Core Logic)

**目的**：生成包含摄像头调用、模型加载和基础绘制功能的完整代码。

> **User Prompt:**
>
> Plaintext
>
> ```
> 你是一个资深的 Python 计算机视觉工程师。我需要你帮我编写一个实时手势识别的脚本 `main.py`。
> ```

> 需求如下：
>
> 1. 使用 `cv2` (OpenCV) 打开默认摄像头捕获视频流。
> 2. 集成 `mediapipe` 的 Hands 模块来检测画面中的手部（设置为检测单手即可）。
> 3. 如果检测到手，请使用 `mp.solutions.drawing_utils` 在视频帧上绘制出手部的关键点和连接线。
> 4. **核心逻辑**：请编写一个函数，根据 MediaPipe 返回的 21 个手部关键点坐标，设计简单的几何算法来识别以下三种手势：
>    - "Open Palm" (五指张开)
>    - "Closed Fist" (握拳)
>    - "Thumbs Up" (竖大拇指)
> 5. 实时在视频画面的左上角用明显的文字显示当前识别出的手势名称。
> 6. 代码结构要清晰，包含注释，并支持按 'q' 键退出。



### 3. 逻辑优化与迭代 (Refinement)



**目的**：解决初始版本中“握拳”识别不准的问题。

> **User Prompt:**
>
> Plaintext
>
> ```
> 目前的代码可以运行，但是手势判断的逻辑不太准确，经常把握拳误识别成张开手掌。
> ```

> 请优化一下手势识别的判断逻辑函数。 不要只简单判断指尖y坐标是否高于指根。

> 建议思路：
>
> 1. 计算食指、中指、无名指、小指的指尖(TIP)与掌心(WRIST, Index 0)的欧几里得距离。如果距离都显著小于手指伸直时的长度，判定为卷曲。
> 2. 对于大拇指，结合其相对于食指的位置来判断。

> 请基于这个思路重写判断函数，提高准确率。

------



## 📂 文件结构



Plaintext

```
.
├── main.py           # 主程序入口 (AI 生成)
├── requirements.txt  # 依赖列表 (AI 生成)
└── README.md         # 项目文档
```



## ⚠️ 已知限制



- **光线影响**：在背光或过暗环境下，MediaPipe 可能无法检测到手部。
- **简单的几何规则**：目前使用几何规则判断手势，而非训练好的分类模型，因此对于复杂角度的手势可能存在误判。
- **单手限制**：代码主要针对单手场景优化，双手同时出现可能会造成标注闪烁。

------

*Created by Human Architect & AI Builder*