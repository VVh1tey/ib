from PyQt6.QtWidgets import QApplication
from src.db_interactions import DatabaseConnection
from src.device_check import DeviceCheckWindow
from src.action_selection import ActionSelectionWindow
import sys
import configparser as cfgp
import time

if __name__ == "__main__":
    app = QApplication(sys.argv)

    cfg = cfgp.ConfigParser(allow_no_value=False, delimiters='=')
    cfg.read('db_creds.ini', encoding='utf-8')
    
    db_config_read = dict(cfg['read'])
    db_config_write = dict(cfg['write'])

    db_connection_read = DatabaseConnection(db_config_read)
    db_connection_write = DatabaseConnection(db_config_write)
    
    # Проверка устройства
    device_window = DeviceCheckWindow(db_connection_read)
    device_window.show()

    if device_window.check_device():
        device_window.hide()
        aw = ActionSelectionWindow(db_connection_write)
        aw.show()
        
        
    sys.exit(app.exec())
