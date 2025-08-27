#!/usr/bin/env python3
"""
Configuration management for keyboard panel plugin
"""

import os
import json
import configparser
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'keyboard-panel'
        self.config_file = self.config_dir / 'config.ini'
        
        # Default settings
        self.defaults = {
            'display': {
                'icon_type': 'keyboard',  # 'none', 'flag', 'keyboard'
                'show_text': 'true',      # Show layout abbreviation
                'text_position': 'right'  # 'left', 'right'
            },
            'behavior': {
                'update_interval': '1',   # seconds
                'autostart': 'true'
            }
        }
        
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create with defaults"""
        if self.config_file.exists():
            try:
                self.config.read(self.config_file)
                # Ensure all sections exist
                for section, options in self.defaults.items():
                    if not self.config.has_section(section):
                        self.config.add_section(section)
                    for key, value in options.items():
                        if not self.config.has_option(section, key):
                            self.config.set(section, key, value)
                self.save_config()
            except Exception as e:
                print("Error loading config: {}".format(e))
                self.create_default_config()
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        for section, options in self.defaults.items():
            self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        except Exception as e:
            print("Error saving config: {}".format(e))
    
    def get(self, section, option, fallback=None):
        """Get configuration value"""
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if fallback is not None:
                return fallback
            return self.defaults.get(section, {}).get(option, '')
    
    def set(self, section, option, value):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
        self.save_config()
    
    def get_bool(self, section, option, fallback=False):
        """Get boolean configuration value"""
        value = self.get(section, option, str(fallback)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def set_bool(self, section, option, value):
        """Set boolean configuration value"""
        self.set(section, option, 'true' if value else 'false')
    
    # Convenience methods for common settings
    def get_icon_type(self):
        return self.get('display', 'icon_type', 'keyboard')
    
    def set_icon_type(self, icon_type):
        if icon_type in ['none', 'flag', 'keyboard']:
            self.set('display', 'icon_type', icon_type)
    
    def get_show_text(self):
        return self.get_bool('display', 'show_text', True)
    
    def set_show_text(self, show):
        self.set_bool('display', 'show_text', show)
    
    def get_update_interval(self):
        try:
            return max(1, int(self.get('behavior', 'update_interval', '1')))
        except ValueError:
            return 1