import uiautomation as auto
import sys

def print_control_tree(control, depth=0):
    """
    Recursively prints the control's properties and its children.
    """
    indent = "  " * depth
    try:
        control_type = control.ControlTypeName
    except:
        control_type = "UnknownType"
        
    try:
        control_name = control.Name
    except:
        control_name = "UnknownName"

    try:
        control_classname = control.ClassName
    except:
        control_classname = "UnknownClassName"
        
    print(f"{indent}Name: '{control_name}', ClassName: '{control_classname}', ControlType: '{control_type}'")
    
    try:
        for child in control.GetChildren():
            print_control_tree(child, depth + 1)
    except:
        # Some controls may not support GetChildren or have other issues
        pass

def inspect_wechat_window_deep():
    """
    Finds the WeChat window and lists all its descendant controls.
    """
    # Set console encoding to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')

    print("Searching for WeChat window...")
    window = auto.WindowControl(searchDepth=1, ClassName='WeChatMainWndForPC')

    if not window.Exists(5): # Wait up to 5 seconds
        print("WeChat window not found. Please make sure WeChat is running.")
        return

    print("\n--- WeChat Window Found ---")
    print_control_tree(window)
    print("\n--- Inspection Complete ---")

if __name__ == "__main__":
    inspect_wechat_window_deep()
