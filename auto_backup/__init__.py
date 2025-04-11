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

def classFactory(iface):
    """Carrega a classe AutoBackup.
    
    :param iface: Uma interface QGIS
    :type iface: QgsInterface
    """
    from .auto_backup import AutoBackup
    return AutoBackup(iface)