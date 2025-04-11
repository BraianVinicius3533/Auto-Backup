# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutoBackup
                                 A QGIS plugin
 Cria backup automático das camadas em edição no QGIS
                              -------------------
        begin                : 2025-04-10
 ***************************************************************************/
"""

import os
import time
import datetime
import shutil
from pathlib import Path

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QTimer, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox, QLabel, QDialog
from qgis.PyQt import uic
from qgis.core import QgsProject, QgsVectorLayer, QgsDataSourceUri, Qgis, QgsMessageLog, QgsVectorFileWriter

# Inicializa recursos Qt de arquivo resources.py
from .resources import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'auto_backup_dialog_base.ui'))


class AutoBackupDialog(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Construtor."""
        super(AutoBackupDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        
        # Conecta botões aos métodos
        self.btnSelecionarPasta.clicked.connect(self.selecionar_pasta)
        self.btnIniciar.clicked.connect(self.iniciar_backup)
        self.btnParar.clicked.connect(self.parar_backup)
        
        # Carrega as configurações salvas
        self.carregar_configuracoes()
        
        # Desativa o botão Parar inicialmente
        self.btnParar.setEnabled(False)
        
        # Inicializa o timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.executar_backup)
        
        # Conexão para limpeza ao fechar
        self.finished.connect(self.ao_fechar)

    def carregar_configuracoes(self):
        settings = QSettings("AutoBackup", "AutoBackupPlugin")
        pasta_backup = settings.value("pasta_backup", "")
        intervalo = settings.value("intervalo", 10)
        
        self.txtPastaBackup.setText(pasta_backup)
        self.spinIntervalo.setValue(int(intervalo))

    def selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta para backups")
        if pasta:
            self.txtPastaBackup.setText(pasta)

    def iniciar_backup(self):
        pasta_backup = self.txtPastaBackup.text().strip()
        
        if not pasta_backup:
            QMessageBox.warning(self, "Atenção", "Selecione um diretório para salvar os backups.")
            return
            
        if not os.path.exists(pasta_backup):
            try:
                os.makedirs(pasta_backup)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível criar a pasta: {str(e)}")
                return
                
        intervalo = self.spinIntervalo.value() * 60 * 1000  # Converte minutos para milissegundos
        
        # Salva as configurações
        settings = QSettings("AutoBackup", "AutoBackupPlugin")
        settings.setValue("pasta_backup", pasta_backup)
        settings.setValue("intervalo", self.spinIntervalo.value())
        
        # Inicia o timer
        self.timer.start(intervalo)
        
        # Atualiza os botões
        self.btnIniciar.setEnabled(False)
        self.btnParar.setEnabled(True)
        
        # Executa o primeiro backup imediatamente
        self.executar_backup()
        
        QMessageBox.information(self, "Auto Backup", "Backup automático iniciado.")

    def parar_backup(self):
        self.timer.stop()
        self.btnIniciar.setEnabled(True)
        self.btnParar.setEnabled(False)
        QMessageBox.information(self, "Auto Backup", "Backup automático interrompido.")

    def executar_backup(self):
        # Obtém as camadas em edição
        layers_em_edicao = [layer for layer in QgsProject.instance().mapLayers().values() 
                           if isinstance(layer, QgsVectorLayer) and layer.isEditable()]
        
        if not layers_em_edicao:
            QgsMessageLog.logMessage("Nenhuma camada em edição encontrada. Nenhum backup criado.", "Auto Backup")
            return
            
        pasta_backup = self.txtPastaBackup.text()
        
        # Cria o nome do diretório de backup com timestamp
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y__%H-%M-%S")
        nome_dir_backup = f"backup_QGIS-{timestamp}"
        caminho_dir_backup = os.path.join(pasta_backup, nome_dir_backup)
        
        # Verifica se já existe um backup com essas camadas e remove
        self.limpar_backups_anteriores(pasta_backup, layers_em_edicao)
        
        # Cria o diretório para o novo backup
        try:
            os.makedirs(caminho_dir_backup)
        except Exception as e:
            QgsMessageLog.logMessage(f"Erro ao criar diretório de backup: {str(e)}", "Auto Backup", Qgis.Critical)
            return
            
        # Salva cada camada em edição como geopackage
        for layer in layers_em_edicao:
            nome_arquivo = f"{layer.name()}.gpkg"
            caminho_arquivo = os.path.join(caminho_dir_backup, nome_arquivo)
            
            # Usa o QgsVectorFileWriter para salvar a camada (compatível com QGIS 3.36)
            try:
                error = QgsVectorFileWriter.writeAsVectorFormat(
                    layer,
                    caminho_arquivo,
                    "UTF-8",
                    layer.crs(),
                    "GPKG",
                    layerOptions=['FID=id']
                )
                
                if error[0] != QgsVectorFileWriter.NoError:
                    QgsMessageLog.logMessage(f"Erro ao salvar camada {layer.name()}: {error[1]}", 
                                          "Auto Backup", Qgis.Critical)
            except Exception as e:
                QgsMessageLog.logMessage(f"Exceção ao salvar camada {layer.name()}: {str(e)}", 
                                       "Auto Backup", Qgis.Critical)
                
        # Mostra mensagem de notificação
        self.mostrar_notificacao(f"Backup criado em {nome_dir_backup}")

    def limpar_backups_anteriores(self, pasta_backup, layers_atuais):
        """Verifica e remove backups anteriores que contêm as mesmas camadas"""
        if not os.path.exists(pasta_backup):
            return
            
        # Nomes das camadas atuais em edição
        nomes_layers_atuais = set(layer.name() for layer in layers_atuais)
        
        # Lista as pastas de backup existentes
        for dir_backup in os.listdir(pasta_backup):
            caminho_dir = os.path.join(pasta_backup, dir_backup)
            
            if os.path.isdir(caminho_dir) and dir_backup.startswith("backup_QGIS-"):
                # Verifica se este backup contém as mesmas camadas
                if self.backup_contem_camadas(caminho_dir, nomes_layers_atuais):
                    try:
                        shutil.rmtree(caminho_dir)
                        QgsMessageLog.logMessage(f"Backup anterior removido: {dir_backup}", "Auto Backup")
                    except Exception as e:
                        QgsMessageLog.logMessage(f"Erro ao remover backup anterior {dir_backup}: {str(e)}", 
                                               "Auto Backup", Qgis.Warning)

    def backup_contem_camadas(self, pasta_backup, nomes_camadas):
        """Verifica se um backup contém as mesmas camadas que estão em edição"""
        if not os.path.exists(pasta_backup):
            return False
            
        # Obtem os nomes das camadas no backup
        nomes_gpkg = set()
        for arquivo in os.listdir(pasta_backup):
            if arquivo.endswith(".gpkg"):
                nome_camada = os.path.splitext(arquivo)[0]
                nomes_gpkg.add(nome_camada)
                
        # Verifica se são as mesmas camadas
        return nomes_gpkg == nomes_camadas

    def mostrar_notificacao(self, mensagem):
        """Mostra notificação na interface do QGIS"""
        try:
            self.iface.messageBar().pushMessage(
                "Auto Backup", 
                mensagem, 
                Qgis.Success, 
                duration=5
            )
        except:
            # Fallback se não conseguir acessar a messageBar
            QgsMessageLog.logMessage(mensagem, "Auto Backup", Qgis.Success)
    
    def ao_fechar(self):
        """Chamado quando o diálogo é fechado"""
        if self.timer.isActive():
            # Pergunta se deve continuar executando backups em segundo plano
            resposta = QMessageBox.question(
                self,
                "Auto Backup",
                "Deseja continuar executando backups em segundo plano?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if resposta == QMessageBox.No:
                self.timer.stop()


class AutoBackup:
    """Plugin principal do QGIS"""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr('&Auto Backup')

        # Verifica se o diretório de ícones existe
        if os.path.exists(os.path.join(self.plugin_dir, 'icon')):
            self.icon_path = os.path.join(self.plugin_dir, 'icon', 'icon.png')
        else:
            self.icon_path = ':/plugins/auto_backup/icon.png'

        # Inicializa o timer
        self.timer = None
        self.dlg = None

    def tr(self, message):
        """Tradução"""
        return QCoreApplication.translate('AutoBackup', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Adiciona um ícone à barra de ferramentas"""

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Cria as entradas do menu e os ícones de ferramentas"""
        self.add_action(
            self.icon_path,
            text=self.tr('Auto Backup'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Remove o plugin do QGIS"""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr('&Auto Backup'),
                action)
            self.iface.removeToolBarIcon(action)

        # Fecha o timer se estiver ativo
        if hasattr(self, 'dlg') and self.dlg and hasattr(self.dlg, 'timer') and self.dlg.timer.isActive():
            self.dlg.timer.stop()

    def run(self):
        """Executa o método quando o botão do plugin é clicado"""
        if not self.dlg:
            self.dlg = AutoBackupDialog(self.iface, parent=self.iface.mainWindow())
        else:
            # Se o diálogo já existe, atualiza o status dos botões
            if hasattr(self.dlg, 'timer') and self.dlg.timer.isActive():
                self.dlg.btnIniciar.setEnabled(False)
                self.dlg.btnParar.setEnabled(True)
            else:
                self.dlg.btnIniciar.setEnabled(True)
                self.dlg.btnParar.setEnabled(False)
            
        # Mostra o diálogo
        self.dlg.show()
        self.dlg.raise_()  # Traz para frente