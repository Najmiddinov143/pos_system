# views/backup_view.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from models.repositories import BackupRepository
from models.models import Backup
from datetime import datetime
import shutil
import os
import zipfile

class BackupView(QWidget):
    def __init__(self):
        super().__init__()
        self.backup_repo = BackupRepository()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_backup_history()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        title = QLabel("💾 Zaxiralash (Backup)")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        backup_btn = QPushButton("🔄 Zaxiralash")
        backup_btn.setObjectName("primaryButton")
        backup_btn.clicked.connect(self.create_backup)
        header_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("📂 Qayta tiklash")
        restore_btn.setObjectName("warningButton")
        restore_btn.clicked.connect(self.restore_backup)
        header_layout.addWidget(restore_btn)
        
        layout.addLayout(header_layout)
        
        # Info
        info_label = QLabel("💡 Zaxiralash fayllari 'backups' papkasida saqlanadi.")
        info_label.setStyleSheet("color: #a0a0b8; font-size: 13px; padding: 10px; background: #1a1a2e; border-radius: 8px;")
        layout.addWidget(info_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Sana', 'Fayl nomi', 'Hajmi', 'Kim tomonidan'
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
            }
            QHeaderView::section {
                background: #1a1a32;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #2a2a4a;
                color: #a0a0b8;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                color: #e0e0e0;
            }
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
    
    def create_backup(self):
        try:
            # Backups papkasini yaratish
            os.makedirs("backups", exist_ok=True)
            
            # Fayl nomi
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_file = f"backups/backup_{now}.zip"
            
            # Database ni zip ga qo'shish
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write("database/pos.db", "pos.db")
            
            # Hajmi
            file_size = os.path.getsize(backup_file)
            
            # Tarixga yozish
            backup = Backup(
                backup_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                file_name=f"backup_{now}.zip",
                file_size=file_size,
                created_by=1
            )
            self.backup_repo.save_backup_record(backup)
            
            QMessageBox.information(self, "Muvaffaqiyat", f"✅ Zaxiralash muvaffaqiyatli!\n📁 {backup_file}")
            self.load_backup_history()
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"❌ Zaxiralashda xatolik: {str(e)}")
    
    def restore_backup(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Zaxira faylni tanlang", "backups", "ZIP Files (*.zip)"
            )
            if not file_path:
                return
            
            reply = QMessageBox.question(
                self, "Tasdiqlash",
                "⚠️ Ma'lumotlar bazasi qayta tiklanadi. Davom etasizmi?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Hozirgi database ni backup qilish
                shutil.copy("database/pos.db", "database/pos.db.backup")
                
                # Yangi database ni o'rnatish
                with zipfile.ZipFile(file_path, 'r') as zipf:
                    zipf.extract("pos.db", "database/")
                    os.rename("database/pos.db", "database/pos.db")
                
                QMessageBox.information(self, "Muvaffaqiyat", "✅ Ma'lumotlar bazasi qayta tiklandi!")
                
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"❌ Qayta tiklashda xatolik: {str(e)}")
    
    def load_backup_history(self):
        try:
            history = self.backup_repo.get_backup_history(30)
            
            self.table.setRowCount(len(history))
            
            for i, b in enumerate(history):
                self.table.setItem(i, 0, QTableWidgetItem(str(b['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(b['backup_date']))
                self.table.setItem(i, 2, QTableWidgetItem(b['file_name']))
                
                size = b['file_size']
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                self.table.setItem(i, 3, QTableWidgetItem(size_str))
                
                self.table.setItem(i, 4, QTableWidgetItem(str(b['created_by'] or '-')))
            
            self.table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error loading backup history: {e}")