#!/bin/bash
# Скрипт быстрой установки плагина языковой панели

set -e

echo "🚀 Установка плагина языковой панели для Raspberry Pi OS"
echo ""

# Проверка прав суперпользователя для системной установки
if [ "$1" = "--system" ]; then
    if [ "$EUID" -ne 0 ]; then
        echo "❌ Для системной установки запустите с sudo"
        exit 1
    fi
    INSTALL_TYPE="system"
else
    INSTALL_TYPE="user"
fi

# Проверка операционной системы
if ! command -v apt-get >/dev/null 2>&1; then
    echo "⚠️  Этот скрипт предназначен для Debian/Ubuntu систем"
    echo "Установите зависимости вручную и используйте Makefile"
    exit 1
fi

echo "📦 Установка зависимостей..."
if [ "$INSTALL_TYPE" = "system" ]; then
    apt-get update
    # Пробуем новый пакет
    if ! apt-get install -y python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1; then
        echo "⚠️  Пробуем старый пакет AppIndicator3..."
        apt-get install -y python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
    fi
else
    echo "Для установки зависимостей выполните:"
    echo "sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1"
    echo "Или для старых версий:"
    echo "sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1"
    
    # Проверяем зависимости
    if ! python3 -c "
import gi
gi.require_version('Gtk', '3.0')
try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3
except:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3
" 2>/dev/null; then
        echo "❌ Не все зависимости установлены!"
        echo "Установите их командами выше и запустите скрипт снова"
        exit 1
    fi
fi

echo "✅ Зависимости установлены"
echo ""

# Установка плагина
echo "🔧 Установка плагина..."
if [ "$INSTALL_TYPE" = "system" ]; then
    make install
else
    make install-user
fi

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "📋 Что дальше:"
echo "1. Перезапустите сессию для автозапуска"
echo "2. Или запустите вручную: keyboard_panel.py"
echo "3. Найдите иконку клавиатуры в системном трее"
echo ""
echo "💡 Полезные команды:"
echo "  make test          - Тестирование"
echo "  make uninstall     - Удаление (системная установка)"
echo "  make uninstall-user - Удаление (пользовательская)"
echo ""
echo "🔗 Документация: README.md"