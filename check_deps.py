#!/usr/bin/env python3
"""
Скрипт проверки зависимостей для плагина языковой панели
"""

import sys

def check_dependencies():
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        
        # Пробуем AyatanaAppIndicator3 (новые версии)
        try:
            gi.require_version('AyatanaAppIndicator3', '0.1')
            from gi.repository import AyatanaAppIndicator3
            print("[OK] Найден AyatanaAppIndicator3")
            return True
        except (ImportError, ValueError):
            pass
        
        # Fallback на старый AppIndicator3
        try:
            gi.require_version('AppIndicator3', '0.1')
            from gi.repository import AppIndicator3
            print("[OK] Найден AppIndicator3")
            return True
        except (ImportError, ValueError):
            pass
            
        print("[ERROR] Не найден ни AyatanaAppIndicator3, ни AppIndicator3")
        return False
        
    except ImportError as e:
        print("[ERROR] Ошибка импорта: {}".format(e))
        return False

if __name__ == "__main__":
    if check_dependencies():
        print("[OK] Все зависимости установлены")
        sys.exit(0)
    else:
        print("[ERROR] Отсутствуют необходимые зависимости!")
        print("Установите их командой:")
        print("sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1")
        print("Или для старых версий:")
        print("sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1")
        sys.exit(1)