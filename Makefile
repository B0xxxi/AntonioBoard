# Makefile для установки плагина языковой панели

PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
DESKTOP_DIR = ~/.config/autostart
SYSTEM_DESKTOP_DIR = /etc/xdg/autostart

PYTHON_SCRIPT = src/keyboard_panel.py
DESKTOP_FILE = keyboard-panel.desktop
TARGET_SCRIPT = $(BINDIR)/keyboard_panel.py

.PHONY: all install uninstall install-user uninstall-user clean help

all:
	@echo "Используйте 'make install' для установки плагина"

# Установка для всех пользователей (требует sudo)
install:
	@echo "Установка плагина языковой панели..."
	sudo mkdir -p $(BINDIR)
	sudo cp $(PYTHON_SCRIPT) $(TARGET_SCRIPT)
	sudo chmod 755 $(TARGET_SCRIPT)
	sudo mkdir -p $(SYSTEM_DESKTOP_DIR)
	sudo cp $(DESKTOP_FILE) $(SYSTEM_DESKTOP_DIR)/
	sudo chmod 644 $(SYSTEM_DESKTOP_DIR)/$(DESKTOP_FILE)
	@echo "Установка завершена! Перезапустите сессию для автозапуска."

# Установка только для текущего пользователя
install-user:
	@echo "Установка плагина языковой панели для пользователя..."
	mkdir -p ~/bin
	cp $(PYTHON_SCRIPT) ~/bin/keyboard_panel.py
	chmod 755 ~/bin/keyboard_panel.py
	mkdir -p $(DESKTOP_DIR)
	sed 's|/usr/local/bin/keyboard_panel.py|$(HOME)/bin/keyboard_panel.py|' $(DESKTOP_FILE) > $(DESKTOP_DIR)/$(DESKTOP_FILE)
	chmod 644 $(DESKTOP_DIR)/$(DESKTOP_FILE)
	@echo "Установка завершена! Добавьте ~/bin в PATH или перезапустите сессию."

# Удаление системной установки
uninstall:
	@echo "Удаление плагина языковой панели..."
	sudo rm -f $(TARGET_SCRIPT)
	sudo rm -f $(SYSTEM_DESKTOP_DIR)/$(DESKTOP_FILE)
	@echo "Удаление завершено."

# Удаление пользовательской установки
uninstall-user:
	@echo "Удаление плагина языковой панели для пользователя..."
	rm -f ~/bin/keyboard_panel.py
	rm -f $(DESKTOP_DIR)/$(DESKTOP_FILE)
	@echo "Удаление завершено."

# Проверка зависимостей
check-deps:
	@echo "Проверка зависимостей..."
	@python3 -c "import gi; gi.require_version('Gtk', '3.0'); gi.require_version('AppIndicator3', '0.1'); print('Все зависимости установлены')" || \
	(echo "Отсутствуют необходимые зависимости!"; \
	 echo "Установите их командой:"; \
	 echo "sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1"; \
	 exit 1)

# Тестирование (запуск без установки)
test:
	@echo "Тестирование плагина..."
	python3 $(PYTHON_SCRIPT)

# Очистка временных файлов
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Справка
help:
	@echo "Доступные команды:"
	@echo "  make install        - Установка для всех пользователей (требует sudo)"
	@echo "  make install-user   - Установка для текущего пользователя"
	@echo "  make uninstall      - Удаление системной установки"
	@echo "  make uninstall-user - Удаление пользовательской установки"
	@echo "  make check-deps     - Проверка зависимостей"
	@echo "  make test          - Тестирование без установки"
	@echo "  make clean         - Очистка временных файлов"
	@echo "  make help          - Показать эту справку"