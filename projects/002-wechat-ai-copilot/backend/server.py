import uiautomation as auto
import comtypes
import time
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for the frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ChatMessage(BaseModel):
    sender: str
    content: str
    time: str

class AnalyzeRequest(BaseModel):
    content: str

def get_wechat_window():
    # 更鲁棒地查找微信主窗口：尝试多种策略
    def _has_chinese(s: str) -> bool:
        if not s:
            return False
        for ch in s:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    # 1) 精确匹配 Windows 版微信常见类名
    try:
        w = auto.WindowControl(searchDepth=1, ClassName='WeChatMainWndForPC', Name='微信')
        if w and w.Exists(0):
            return w
    except Exception:
        pass

    # 2) 有些微信客户端（Qt 版本）使用 Qt 类名，试试已知的 Qt 类名
    try:
        w = auto.WindowControl(searchDepth=1, ClassName='Qt51514QWindowIcon')
        if w and w.Exists(0):
            return w
    except Exception:
        pass

    # 3) 遍历根窗口，匹配标题或类名的多种可能性
    try:
        root = auto.GetRootControl()
        for c in root.GetChildren():
            try:
                name = getattr(c, 'Name', '') or ''
                cls = getattr(c, 'ClassName', '') or ''
                # 精确或部分匹配中文名称/英文名称
                if '微信' in name or 'WeChat' in name or 'Weixin' in name:
                    return c
                # 如果类名包含 Qt 且标题含中文字符，也很可能是微信
                if 'Qt' in cls and _has_chinese(name):
                    return c
            except Exception:
                continue
    except Exception:
        pass

    # 4) 最后尝试一些通配的 Qt 类名
    try:
        for cls_name in ('Qt51514QWindowIcon', 'Qt5QWindowIcon'):
            try:
                w = auto.WindowControl(searchDepth=1, ClassName=cls_name)
                if w and w.Exists(0):
                    return w
            except Exception:
                continue
    except Exception:
        pass

    return None

@app.get("/api/sync_messages")
def sync_messages():
    # Ensure COM is initialized in this worker thread (FastAPI runs sync endpoints in a threadpool)
    # Without this, comtypes.CoCreateInstance may raise "尚未调用 CoInitialize" (CoInitialize not called).
    comtypes.CoInitialize()
    try:
        window = get_wechat_window()
        if not window or not window.Exists(0):
            return {"status": "error", "message": "WeChat not found"}
        
        # Find all list controls by traversing children and filtering ControlType.
        # Matching by Name='消息' can be unreliable due to encoding, so we search by control type.
        def find_controls_by_type(root_control, ctrl_type, max_depth=6):
            found = []
            def _dfs(node, depth):
                if depth < 0:
                    return
                try:
                    if getattr(node, 'ControlType', None) == ctrl_type:
                        found.append(node)
                except Exception:
                    pass
                try:
                    for ch in node.GetChildren():
                        _dfs(ch, depth - 1)
                except Exception:
                    pass
            _dfs(root_control, max_depth)
            return found

        msg_lists = find_controls_by_type(window, auto.ControlType.ListControl, max_depth=15)

        if len(msg_lists) < 1:
            return {"status": "error", "message": f"Expected at least 1 ListControl, but found {len(msg_lists)}"}

        # Heuristic: if multiple list controls, message list is commonly the second one; otherwise use the first
        msg_list = msg_lists[1] if len(msg_lists) > 1 else msg_lists[0]
        if not msg_list.Exists(0):
            return {"status": "error", "message": "Message list not found"}
        
        # 提取最后 10 条消息
        items = msg_list.GetChildren()[-10:]
        data = []
        for item in items:
            # 简单判断发送者方位 (右侧为己方)
            try:
                rect = item.BoundingRectangle
                list_rect = msg_list.BoundingRectangle
                is_me = (rect.left + rect.width/2) > (list_rect.left + list_rect.width/2)
                sender = "me" if is_me else "them"
                
                content = ""
                if is_me:
                    try:
                        content_element = item.TextControl()
                        content = content_element.Name
                    except auto.LookupError:
                        content = item.Name
                else:
                    content = item.Name

                data.append({"sender": sender, "content": content, "time": time.strftime("%H:%M")})
            except Exception as e:
                import traceback
                print(f"--- Error processing a message item: {item.Name} ---")
                traceback.print_exc()
                continue

        return {"status": "success", "data": data}
    finally:
        try:
            comtypes.CoUninitialize()
        except Exception:
            # Best-effort cleanup; if uninitialize fails, don't crash the endpoint
            pass

@app.post("/api/analyze")
def analyze_message(request: AnalyzeRequest):
    content = request.content
    if "价格" in content or "多少钱" in content:
        suggestions = ["我们的基础版是5万/年", "私有化部署需要详谈", "这是价格表.pdf"]
    elif "报错" in content or "问题" in content:
        suggestions = ["请截图发我看下", "重启试试？", "技术正在排查"]
    else:
        suggestions = ["您好，请问有什么可以帮您？"]
    return {"suggestions": suggestions}


@app.get("/api/list_windows")
def list_windows():
    """调试用：列出根下的顶层窗口的名称与类名，帮助定位 WeChat 窗口属性。"""
    comtypes.CoInitialize()
    try:
        try:
            root = auto.GetRootControl()
        except Exception as e:
            return {"status": "error", "message": f"GetRootControl failed: {e}"}

        children = []
        try:
            for c in root.GetChildren():
                try:
                    children.append({
                        "Name": getattr(c, 'Name', None),
                        "ClassName": getattr(c, 'ClassName', None),
                        "ControlType": getattr(c, 'ControlType', None)
                    })
                except Exception:
                    continue
        except Exception as e:
            return {"status": "error", "message": f"Enumerating children failed: {e}"}

        return {"status": "success", "windows": children}
    finally:
        try:
            comtypes.CoUninitialize()
        except Exception:
            pass


@app.get("/api/debug_window_structure")
def debug_window_structure(depth: int = 4, max_nodes: int = 300):
    """调试：在已定位的微信窗口内递归遍历控件树并返回每个控件的关键信息。

    参数:
      depth: 递归深度（默认4）
      max_nodes: 返回的最大节点数，防止输出过大（默认300）
    """
    comtypes.CoInitialize()
    try:
        w = get_wechat_window()
        if not w or not w.Exists(0):
            return {"status": "error", "message": "WeChat not found"}

        nodes = []
        count = 0

        def _dump(node, cur_depth):
            nonlocal count
            if count >= max_nodes:
                return
            try:
                info = {
                    "depth": cur_depth,
                    "Name": getattr(node, 'Name', None),
                    "ClassName": getattr(node, 'ClassName', None),
                    "ControlType": getattr(node, 'ControlType', None),
                    "AutomationId": getattr(node, 'AutomationId', None),
                }
                nodes.append(info)
                count += 1
            except Exception:
                pass

            if cur_depth <= 0 or count >= max_nodes:
                return
            try:
                for ch in node.GetChildren():
                    _dump(ch, cur_depth - 1)
                    if count >= max_nodes:
                        break
            except Exception:
                pass

        _dump(w, depth)
        return {"status": "success", "nodes": nodes, "count": count}
    finally:
        try:
            comtypes.CoUninitialize()
        except Exception:
            pass

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
