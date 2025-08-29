#!/usr/bin/env python3
"""
Плагин языковой панели для панели задач Raspberry Pi OS
Показывает текущую раскладку клавиатуры и позволяет переключать языки
"""

import gi
gi.require_version('Gtk', '3.0')

# Пробуем использовать AyatanaAppIndicator3 (новые версии)
try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3 as AppIndicator3
except (ImportError, ValueError):
    # Fallback на старый AppIndicator3
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3
    except (ImportError, ValueError):
        print("Error: AppIndicator3 or AyatanaAppIndicator3 not found")
        print("Install: sudo apt-get install gir1.2-ayatanaappindicator3-0.1")
        exit(1)

from gi.repository import Gtk, GObject, GLib
import subprocess
import os
import sys
import signal
from config import Config
from flags import get_flag_emoji, get_flag_text, get_country_name

class KeyboardPanel:
    def __init__(self):
        self.current_layout = "en"
        self.layouts = self.get_available_layouts()
        self.config = Config()
        
        # Создаем системный индикатор
        self.indicator = AppIndicator3.Indicator.new(
            "keyboard-panel",
            "input-keyboard",
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.create_menu())
        
        # Обновляем текущую раскладку
        self.update_current_layout()
        self.update_indicator_display()
        
        # Устанавливаем таймер для периодического обновления
        update_interval = self.config.get_update_interval()
        GLib.timeout_add_seconds(update_interval, self.update_current_layout)

    def get_available_layouts(self):
        """Получает список доступных раскладок клавиатуры"""
        try:
            result = subprocess.run(['setxkbmap', '-query'], 
                                  capture_output=True, text=True)
            
            layouts = []
            for line in result.stdout.split('\n'):
                if line.startswith('layout:'):
                    layout_list = line.split(':')[1].strip().split(',')
                    layouts = [l.strip() for l in layout_list]
                    break
            
            # Если не удалось получить раскладки, используем базовые
            if not layouts:
                layouts = ['us', 'ru']
                
            return layouts
        except:
            return ['us', 'ru']

    def get_current_layout(self):
        """Получает текущую активную раскладку"""
        try:
            result = subprocess.run(['setxkbmap', '-query'], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line.startswith('layout:'):
                    # Берем первую раскладку как активную
                    current = line.split(':')[1].strip().split(',')[0].strip()
                    return current
                    
        except:
            pass
        
        return "en"

    def set_layout(self, layout):
        """Устанавливает раскладку клавиатуры"""
        try:
            subprocess.run(['setxkbmap', layout], check=True)
            return True
        except:
            return False

    def create_menu(self):
        """Создает контекстное меню"""
        menu = Gtk.Menu()
        
        # Заголовок с текущей раскладкой
        current_item = Gtk.MenuItem(label="Current: {}".format(self.current_layout.upper()))
        current_item.set_sensitive(False)
        menu.append(current_item)
        
        # Разделитель
        separator = Gtk.SeparatorMenuItem()
        menu.append(separator)
        
        # Пункты для каждой доступной раскладки
        for layout in self.layouts:
            layout_name = self.get_layout_name(layout)
            item = Gtk.MenuItem(label="Switch to {}".format(layout_name))
            item.connect('activate', self.on_layout_selected, layout)
            menu.append(item)
        
        # Разделитель
        separator2 = Gtk.SeparatorMenuItem()
        menu.append(separator2)
        
        # Настройки
        settings_item = Gtk.MenuItem(label="Settings")
        settings_submenu = self.create_settings_menu()
        settings_item.set_submenu(settings_submenu)
        menu.append(settings_item)
        
        # Разделитель
        separator3 = Gtk.SeparatorMenuItem()
        menu.append(separator3)
        
        # Выход
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect('activate', self.quit)
        menu.append(quit_item)
        
        menu.show_all()
        return menu

    def get_layout_name(self, layout):
        """Returns readable layout name"""
        layout_names = {
            'us': 'English (US)',
            'ru': 'Russian',
            'en': 'English',
            'de': 'German',
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian'
        }
        return layout_names.get(layout, layout.upper())

    def on_layout_selected(self, widget, layout):
        """Layout selection handler"""
        if self.set_layout(layout):
            self.current_layout = layout
            self.update_indicator_display()
            # Update menu
            self.indicator.set_menu(self.create_menu())

    def update_current_layout(self):
        """Updates current layout information"""
        new_layout = self.get_current_layout()
        if new_layout != self.current_layout:
            self.current_layout = new_layout
            self.update_indicator_display()
            # Update menu when layout changes
            self.indicator.set_menu(self.create_menu())
        return True  # Continue timer

    def create_settings_menu(self):
        """Creates settings menu"""
        menu = Gtk.Menu()
        
        # Icon settings
        icon_item = Gtk.MenuItem(label="Icon type")
        icon_submenu = Gtk.Menu()
        
        icon_types = [
            ('none', 'No icon'),
            ('keyboard', 'Keyboard'),
            ('flag', 'Country flag')
        ]
        
        current_icon_type = self.config.get_icon_type()
        
        for icon_type, label in icon_types:
            item = Gtk.CheckMenuItem(label=label)
            item.set_active(icon_type == current_icon_type)
            item.connect('activate', self.on_icon_type_changed, icon_type)
            icon_submenu.append(item)
        
        icon_item.set_submenu(icon_submenu)
        menu.append(icon_item)
        
        # Text display setting
        text_item = Gtk.CheckMenuItem(label="Show text")
        text_item.set_active(self.config.get_show_text())
        text_item.connect('activate', self.on_show_text_changed)
        menu.append(text_item)
        
        menu.show_all()
        return menu
    
    def on_icon_type_changed(self, widget, icon_type):
        """Icon type change handler"""
        if widget.get_active():
            self.config.set_icon_type(icon_type)
            self.update_indicator_display()
            # Update menu to show only one active option
            self.indicator.set_menu(self.create_menu())
    
    def on_show_text_changed(self, widget):
        """Text display change handler"""
        self.config.set_show_text(widget.get_active())
        self.update_indicator_display()
    
    def update_indicator_display(self):
        """Updates indicator display (icon and text)"""
        icon_type = self.config.get_icon_type()
        show_text = self.config.get_show_text()
        
        # Determine icon
        if icon_type == 'flag':
            # Try to use emoji flag
            try:
                icon_name = None  # Use text instead of icon for flags
                self.indicator.set_icon_full("", "")
            except:
                # Fallback to standard keyboard icon
                self.indicator.set_icon_full("input-keyboard", "")
        elif icon_type == 'keyboard':
            self.indicator.set_icon_full("input-keyboard", "")
        else:  # none
            self.indicator.set_icon_full("", "")
        
        # Determine text
        label_text = ""
        if show_text:
            if icon_type == 'flag':
                # Show ASCII flag and abbreviation (avoid emoji)
                flag = get_flag_text(self.current_layout)
                label_text = "{} {}".format(flag, self.current_layout.upper())
            else:
                # Only layout abbreviation
                label_text = self.current_layout.upper()
        elif icon_type == 'flag':
            # Only ASCII flag without text (avoid emoji)
            label_text = get_flag_text(self.current_layout)
        
        # Safe text setting (ASCII only)
        try:
            self.indicator.set_label(label_text, "")
        except UnicodeEncodeError:
            # Fallback to simple display
            self.indicator.set_label(self.current_layout.upper(), "")

    def quit(self, widget=None):
        """Terminates application"""
        Gtk.main_quit()

    def run(self):
        """Starts main application loop"""
        # Signal handling
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, lambda signum, frame: self.quit())
        
        try:
            Gtk.main()
        except KeyboardInterrupt:
            self.quit()

def main():
    """Application entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Keyboard panel plugin for Raspberry Pi OS taskbar")
        print("Usage: keyboard_panel.py")
        print("")
        print("Shows current keyboard layout in system tray")
        print("and allows switching languages via context menu.")
        return

    # Check if graphics environment is running
    if not os.environ.get('DISPLAY'):
        print("Error: No graphics environment found (DISPLAY not set)")
        sys.exit(1)

    try:
        panel = KeyboardPanel()
        panel.run()
    except Exception as e:
        print("Startup error: {}".format(e))
        sys.exit(1)

if __name__ == '__main__':
    main()