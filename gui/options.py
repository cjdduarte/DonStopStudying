from aqt.qt import QLineEdit
# Copyright 2020 Charles Henry - Modificado
from PyQt6 import QtCore
from aqt import Qt, QWidget, QGridLayout, QPushButton, QDialog, QHBoxLayout, QLabel, QVBoxLayout, QComboBox, QCheckBox, QSpinBox
from aqt.utils import showInfo, tooltip
from anki_utils import AnkiUtils
import logging
from translations import tr

class ReminderOptions(QDialog):

    def __init__(self, parent, dont_stop_scheduler):
        super().__init__(parent=parent)
        self.anki_utils = AnkiUtils()
        self.dont_stop_scheduler = dont_stop_scheduler
        self.logger = logging.getLogger(__name__.split('.')[0])
        
        try:
            self.config = self.anki_utils.get_config()
        except Exception as e:
            self.logger.error(f'Erro ao obter a configuração: {str(e)}')
            self.config = {
                "deck": "",
                "frequency": 30,
                "enabled": True,
                "window_location": "bottom_right"
            }
        
        # Configuração da janela
        self.setWindowTitle(tr("config_title"))
        self.setFixedSize(400, 350)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 7px 12px;
                font-size: 15px;
                font-family: "Segoe UI", Arial, sans-serif;
                padding: 7px 12px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)

        # Seleção de Deck
        self.deck_select_text = QLabel(text=tr("deck_select"))
        self.deck_select = QComboBox()
        
        # Obter todos os decks disponíveis
        try:
            decks = self.anki_utils.get_decks()
            
            # Verificar se há decks disponíveis
            if not decks:
                QMessageBox.warning(self, tr("options_menu"), tr("no_deck_found"))
                self.close()
                return
            
            # Adicionar todos os decks ao combobox
            for deck in decks:
                deck_name = deck.name if hasattr(deck, "name") else deck[0]
                level = deck_name.count("::")
                display_name = "   " * level + deck_name.split("::")[-1] if level > 0 else deck_name
                self.deck_select.addItem(display_name, deck_name)
            
            # Verificar se o deck configurado existe na lista
            configured_deck = self.config.get('deck', '')

            # Procurar pelo nome completo do deck nos dados do combobox
            deck_index = -1
            for i in range(self.deck_select.count()):
                if self.deck_select.itemData(i) == configured_deck:
                    deck_index = i
                    break

            # Se o deck configurado não existir, adicionar ao combobox com indentação hierárquica
            if deck_index == -1:
                level = configured_deck.count("::")
                display_name = "   " * level + configured_deck.split("::")[-1] if level > 0 else configured_deck
                self.deck_select.addItem(display_name, configured_deck)
                self.deck_select.setCurrentIndex(self.deck_select.count() - 1)
            else:
                self.deck_select.setCurrentIndex(deck_index)
        except Exception as e:
            self.logger.error(f'Erro ao obter os decks: {str(e)}')
            QMessageBox.warning(self, tr("options_menu"), tr("get_decks_error"))
            self.close()
            return

        # Frequência
        self.freq_select_text = QLabel(text=tr("freq_select"))
        self.freq_select_map = {
            tr('every_1_min'): 1,
            tr('every_2_min'): 2,
            tr('every_3_min'): 3,
            tr('every_5_min'): 5,
            tr('every_10_min'): 10,
            tr('every_15_min'): 15,
            tr('every_20_min'): 20,
            tr('every_25_min'): 25,
            tr('every_30_min'): 30,
            tr('every_45_min'): 45,
            tr('every_60_min'): 60,
            tr('every_90_min'): 90,
            tr('every_120_min'): 120
        }
        self.freq_select = QComboBox()
        for frequency in self.freq_select_map.keys():
            self.freq_select.addItem(frequency)
        try:
            freq_select_idx = list(self.freq_select_map.values()).index(self.config['frequency'])
        except (ValueError, KeyError) as e:
            self.logger.warning(tr('default_frequency_warning'))
            freq_select_idx = 4  # Padrão para 30 minutos
        finally:
            self.freq_select.setCurrentIndex(freq_select_idx)

        # Habilitar/Desabilitar
        self.enabled_check_text = QLabel(text=tr("enabled_check"))
        self.enabled_check = QCheckBox()
        try:
            self.enabled_check.setChecked(self.config.get('enabled', True))
        except Exception as e:
            self.logger.error(f'Erro ao definir o estado do checkbox: {str(e)}')
            self.enabled_check.setChecked(True)  # Valor padrão

        # --- Inatividade após tempo máximo do cartão ---
        from PyQt6.QtWidgets import QFrame
        self.inactivity_after_max_answer_check = QCheckBox(tr("inactivity_reminder_label"))
        self.inactivity_after_max_answer_check.setChecked(self.config.get('inactivity_after_max_answer', False))

        self.inactivity_divider = QFrame()
        self.inactivity_divider.setFrameShape(QFrame.Shape.HLine)
        self.inactivity_divider.setFrameShadow(QFrame.Shadow.Sunken)

        self.inactivity_extra_minutes_label = QLabel(tr("inactivity_extra_time_label"))
        self.inactivity_extra_minutes_select = QComboBox()
        for freq_label, freq_value in self.freq_select_map.items():
            self.inactivity_extra_minutes_select.addItem(freq_label, freq_value)
        # Seleciona o valor salvo na configuração, se existir
        inactivity_extra_minutes = self.config.get('inactivity_extra_minutes', 3)
        idx = list(self.freq_select_map.values()).index(inactivity_extra_minutes) if inactivity_extra_minutes in self.freq_select_map.values() else 0
        self.inactivity_extra_minutes_select.setCurrentIndex(idx)

        # Botão Salvar
        self.ok_btn = QPushButton(text=tr("save"))
        self.ok_btn.clicked.connect(self.confirm_and_update_config)

        # Botão Fechar
        self.close_btn = QPushButton(text=tr("close"))
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.close_btn.clicked.connect(self.hide)

        # Botão Testar Lembrete
        self.show_card_btn = QPushButton(text=tr("test_reminder"))
        self.show_card_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.show_card_btn.clicked.connect(self.show_next_card_and_close)

        # Layout correto: cria o grid e adiciona todos os widgets na ordem desejada
        self.grid = QGridLayout()
        self.grid.addWidget(self.deck_select_text, 0, 0)
        self.grid.addWidget(self.deck_select, 0, 1)
        self.grid.addWidget(self.freq_select_text, 1, 0)
        self.grid.addWidget(self.freq_select, 1, 1)
        self.grid.addWidget(self.enabled_check_text, 2, 0)
        self.grid.addWidget(self.enabled_check, 2, 1)
        # Linha divisória antes do grupo
        from PyQt6.QtWidgets import QFrame
        self.inactivity_group_divider_top = QFrame()
        self.inactivity_group_divider_top.setFrameShape(QFrame.Shape.HLine)
        self.inactivity_group_divider_top.setFrameShadow(QFrame.Shadow.Sunken)
        self.grid.addWidget(self.inactivity_group_divider_top, 3, 0, 1, 2)

        self.grid.addWidget(self.inactivity_after_max_answer_check, 4, 0, 1, 2)
        self.grid.addWidget(self.inactivity_extra_minutes_label, 5, 0)
        self.grid.addWidget(self.inactivity_extra_minutes_select, 5, 1)

        # Linha divisória depois do grupo
        self.inactivity_group_divider_bottom = QFrame()
        self.inactivity_group_divider_bottom.setFrameShape(QFrame.Shape.HLine)
        self.inactivity_group_divider_bottom.setFrameShadow(QFrame.Shadow.Sunken)
        self.grid.addWidget(self.inactivity_group_divider_bottom, 6, 0, 1, 2)

        self.grid.addWidget(self.show_card_btn, 7, 0, 1, 2)
        self.grid.addWidget(self.ok_btn, 8, 0)
        self.grid.addWidget(self.close_btn, 8, 1)

        self.setLayout(self.grid)

    def center_on_screen(self):
        """Centraliza a janela de opções na tela principal do Anki"""
        try:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                size = self.frameGeometry()
                x = screen_geometry.x() + (screen_geometry.width() - size.width()) // 2
                y = screen_geometry.y() + (screen_geometry.height() - size.height()) // 2
                self.move(x, y)
        except Exception as e:
            self.logger.error(f'Erro ao centralizar a janela: {str(e)}')
        self.center_on_screen()

    def confirm_and_update_config(self):
        """Pede confirmação antes de salvar a configuração do addon"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(tr("confirm_save_title"))
        msg_box.setText(tr("confirm_save_msg"))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        yes_btn = msg_box.button(QMessageBox.StandardButton.Yes)
        no_btn = msg_box.button(QMessageBox.StandardButton.No)
        yes_btn.setText(tr("yes"))
        no_btn.setText(tr("no"))
        reply = msg_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            self.update_config()

    def update_config(self):
        """Atualiza a configuração do addon"""
        self.logger.info('Atualizando configuração...')
        try:
            self.config = {
                "deck": self.deck_select.currentData() or self.deck_select.currentText(),
                "frequency": self.freq_select_map[self.freq_select.currentText()],
                "enabled": self.enabled_check.checkState() == Qt.CheckState.Checked,
                "window_location": "bottom_right",
                "inactivity_after_max_answer": self.inactivity_after_max_answer_check.isChecked(),
                "inactivity_extra_minutes": self.inactivity_extra_minutes_select.currentData()
            }
            success = self.anki_utils.set_config(self.config)
            if success:
                try:
                    self.dont_stop_scheduler.update_state(self.config)
                    self.logger.debug("Novo valor de configuração: %s" % self.anki_utils.get_config())
                    tooltip(tr("config_saved"))
                except Exception as e:
                    self.logger.error(f'Erro ao atualizar o agendador: {str(e)}')
                    QMessageBox.warning(self, tr("options_menu"), tr("config_scheduler_error"))
            else:
                QMessageBox.warning(self, tr("options_menu"), tr("config_save_fail"))
        except Exception as e:
            self.logger.error(f'Erro ao atualizar a configuração: {str(e)}')
            QMessageBox.warning(self, tr("options_menu"), tr("config_save_error"))
        
        self.close()

    def resizeEvent(self, event):
        # Impede redimensionamento manual da janela
        self.setFixedSize(400, 350)
        super().resizeEvent(event)

    def show_next_card_and_close(self):
        """Testa o lembrete e fecha a janela de opções"""
        try:
            self.dont_stop_scheduler.exec_schedule()
        except Exception as e:
            self.logger.error(f'Erro ao executar o agendador: {str(e)}')
            QMessageBox.warning(self, tr("options_menu"), tr("popup_error"))
        
        self.close()
