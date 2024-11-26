from PyQt6.QtWidgets import QApplication, QMessageBox
from src.db_interactions import Device, Credentials
from src.ui import LoginWindow, RegistrationWindow, MainMenu


if __name__ == '__main__':
    creds = Credentials()
    device = Device(creds=creds.get_read())

    if not device.continue_actions:
        print("Программа не может быть запущена на этом устройстве.")
        exit()
    else:
        print("Устройство подтверждено. Запуск программы.")

    # Запуск интерфейса
    app = QApplication([])
    main_menu = MainMenu()
    main_menu.show()
    app.exec()