import sys
import os

# Papka yo'lini to'g'rilash: client/ dan yuqoriga chiqamiz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from PyQt6.QtWidgets import QApplication
from api_client import api
from config import config

# views papkasi asosiy papkada (pos_system/views)
from views.login_window import LoginWindow

def main():
    api.base_url = config.SERVER_URL
    print(f"🔗 Server: {api.base_url}")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = LoginWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()