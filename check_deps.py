#!/usr/bin/env python3
"""
Dependencies checker for keyboard panel plugin
"""

import sys

def check_dependencies():
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        
        # Try AyatanaAppIndicator3 (newer versions)
        try:
            gi.require_version('AyatanaAppIndicator3', '0.1')
            from gi.repository import AyatanaAppIndicator3
            print("[OK] Found AyatanaAppIndicator3")
            return True
        except (ImportError, ValueError):
            pass
        
        # Fallback to old AppIndicator3
        try:
            gi.require_version('AppIndicator3', '0.1')
            from gi.repository import AppIndicator3
            print("[OK] Found AppIndicator3")
            return True
        except (ImportError, ValueError):
            pass
            
        print("[ERROR] Neither AyatanaAppIndicator3 nor AppIndicator3 found")
        return False
        
    except ImportError as e:
        print("[ERROR] Import error: {}".format(e))
        return False

if __name__ == "__main__":
    if check_dependencies():
        print("[OK] All dependencies are installed")
        sys.exit(0)
    else:
        print("[ERROR] Missing required dependencies!")
        print("Install them with:")
        print("sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1")
        print("Or for older versions:")
        print("sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1")
        sys.exit(1)