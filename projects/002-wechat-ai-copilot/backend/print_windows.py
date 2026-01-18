import uiautomation as auto
import sys

def print_windows():
    """
    Prints the Name and ClassName of all top-level windows.
    """
    # Set console encoding to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("Listing all top-level windows...\n")
    root = auto.GetRootControl()
    for window in root.GetChildren():
        if window.ControlTypeName == 'WindowControl':
            print(f"Name: '{window.Name}', ClassName: '{window.ClassName}'")

if __name__ == "__main__":
    print_windows()
