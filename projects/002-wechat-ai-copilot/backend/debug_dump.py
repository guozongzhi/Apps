import json
import comtypes
import uiautomation as auto


def has_chinese(s: str) -> bool:
    if not s:
        return False
    for ch in s:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def find_wechat_window():
    try:
        w = auto.WindowControl(searchDepth=1, ClassName='WeChatMainWndForPC', Name='微信')
        if w and w.Exists(0):
            return w
    except Exception:
        pass
    try:
        w = auto.WindowControl(searchDepth=1, ClassName='Qt51514QWindowIcon')
        if w and w.Exists(0):
            return w
    except Exception:
        pass
    try:
        root = auto.GetRootControl()
        for c in root.GetChildren():
            try:
                name = getattr(c, 'Name', '') or ''
                cls = getattr(c, 'ClassName', '') or ''
                if '微信' in name or 'WeChat' in name or 'Weixin' in name:
                    return c
                if 'Qt' in cls and has_chinese(name):
                    return c
            except Exception:
                continue
    except Exception:
        pass
    return None


def dump_tree(win, depth=5, max_nodes=400):
    nodes = []
    count = 0

    def _dump(node, cur_depth):
        nonlocal count
        if count >= max_nodes:
            return
        try:
            info = {
                'depth': cur_depth,
                'Name': getattr(node, 'Name', None),
                'ClassName': getattr(node, 'ClassName', None),
                'ControlType': getattr(node, 'ControlType', None),
                'AutomationId': getattr(node, 'AutomationId', None)
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

    _dump(win, depth)
    return nodes


if __name__ == '__main__':
    comtypes.CoInitialize()
    try:
        w = find_wechat_window()
        if not w or not w.Exists(0):
            print(json.dumps({'status': 'error', 'message': 'WeChat not found'} , ensure_ascii=False))
        else:
            nodes = dump_tree(w, depth=5, max_nodes=400)
            print(json.dumps({'status': 'success', 'count': len(nodes), 'nodes': nodes}, ensure_ascii=False))
    finally:
        try:
            comtypes.CoUninitialize()
        except Exception:
            pass
