from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSpinBox, 
    QLineEdit, QPushButton, QHBoxLayout, QFileDialog
)


class AutoBackupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações do Auto Backup")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Intervalo de backup
        layout.addWidget(QLabel("Intervalo entre backups (minutos):"))
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(1440)  # 24 horas
        layout.addWidget(self.interval_spinbox)

        # Diretório de backup
        layout.addWidget(QLabel("Diretório para salvar backups:"))
        
        hbox = QHBoxLayout()
        self.path_lineedit = QLineEdit()
        hbox.addWidget(self.path_lineedit)
        
        self.browse_button = QPushButton("Procurar...")
        self.browse_button.clicked.connect(self.browse_directory)
        hbox.addWidget(self.browse_button)
        
        layout.addLayout(hbox)

        # Botões
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Selecione o diretório para salvar backups", 
            self.path_lineedit.text()
        )
        if directory:
            self.path_lineedit.setText(directory)

    def set_values(self, interval, path):
        self.interval_spinbox.setValue(interval)
        self.path_lineedit.setText(path)