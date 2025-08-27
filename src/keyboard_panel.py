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
        print("Ошибка: не найден AppIndicator3 или AyatanaAppIndicator3")
        print("Установите: sudo apt-get install gir1.2-ayatanaappindicator3-0.1")
        exit(1)

from gi.repository import Gtk, GObject, GLib
import subprocess
import os
import sys
import signal

class KeyboardPanel:
    def __init__(self):
        self.current_layout = "en"
        self.layouts = self.get_available_layouts()
        
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
        
        # Устанавливаем таймер для периодического обновления
        GLib.timeout_add_seconds(1, self.update_current_layout)

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
        current_item = Gtk.MenuItem(label="Текущая: {}".format(self.current_layout.upper()))
        current_item.set_sensitive(False)
        menu.append(current_item)
        
        # Разделитель
        separator = Gtk.SeparatorMenuItem()
        menu.append(separator)
        
        # Пункты для каждой доступной раскладки
        for layout in self.layouts:
            layout_name = self.get_layout_name(layout)
            item = Gtk.MenuItem(label="Переключить на {}".format(layout_name))
            item.connect('activate', self.on_layout_selected, layout)
            menu.append(item)
        
        # Разделитель
        separator2 = Gtk.SeparatorMenuItem()
        menu.append(separator2)
        
        # Выход
        quit_item = Gtk.MenuItem(label="Выход")
        quit_item.connect('activate', self.quit)
        menu.append(quit_item)
        
        menu.show_all()
        return menu

    def get_layout_name(self, layout):
        """Возвращает читаемое имя раскладки"""
        layout_names = {
            'us': 'Английский (US)',
            'ru': 'Русский',
            'en': 'Английский',
            'de': 'Немецкий',
            'fr': 'Французский',
            'es': 'Испанский',
            'it': 'Итальянский'
        }
        return layout_names.get(layout, layout.upper())

    def on_layout_selected(self, widget, layout):
        """Обработчик выбора раскладки"""
        if self.set_layout(layout):
            self.current_layout = layout
            self.update_indicator_label()
            # Обновляем меню
            self.indicator.set_menu(self.create_menu())

    def update_current_layout(self):
        """Обновляет информацию о текущей раскладке"""
        new_layout = self.get_current_layout()
        if new_layout != self.current_layout:
            self.current_layout = new_layout
            self.update_indicator_label()
            # Обновляем меню при изменении раскладки
            self.indicator.set_menu(self.create_menu())
        return True  # Продолжаем таймер

    def update_indicator_label(self):
        """Обновляет отображаемый текст индикатора"""
        self.indicator.set_label(self.current_layout.upper(), "")

    def quit(self, widget=None):
        """Завершает работу приложения"""
        Gtk.main_quit()

    def run(self):
        """Запускает главный цикл приложения"""
        # Обработка сигнала завершения
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, lambda signum, frame: self.quit())
        
        try:
            Gtk.main()
        except KeyboardInterrupt:
            self.quit()

def main():
    """Точка входа в приложение"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Плагин языковой панели для панели задач Raspberry Pi OS")
        print("Использование: keyboard_panel.py")
        print("")
        print("Показывает текущую раскладку клавиатуры в системном трее")
        print("и позволяет переключать языки через контекстное меню.")
        return

    # Проверяем, что запущена графическая среда
    if not os.environ.get('DISPLAY'):
        print("Ошибка: Не найдена графическая среда (DISPLAY не установлен)")
        sys.exit(1)

    try:
        panel = KeyboardPanel()
        panel.run()
    except Exception as e:
        print("Ошибка при запуске: {}".format(e))
        sys.exit(1)

if __name__ == '__main__':
    main()