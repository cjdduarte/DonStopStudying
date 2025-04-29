# Copyright 2020 Charles Henry - Modificado
from PyQt6 import QtCore
from aqt import Qt, QWidget, QGridLayout, QPushButton, QDialog, QHBoxLayout, QLabel, QVBoxLayout, QComboBox
from aqt.utils import showInfo, tooltip
from anki_utils import AnkiUtils
import logging
from translations import tr


class ReminderPopup(QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.Window)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.resize(400, 260)  # Aumentei a largura total

        self.anki_utils = AnkiUtils()
        self.logger = logging.getLogger(__name__.split('.')[0])

        # Container central
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setGeometry(10, 10, 380, 240)  # Aumentei a largura do container
        self.central_widget.setStyleSheet("""
            #central_widget {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        # Layout principal vertical
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header com ícone e título
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # Ícone do relógio
        self.icon_label = QLabel()
        self.icon_label.setText("⏰")
        self.icon_label.setStyleSheet("""
            font-size: 24px;
            color: #2196F3;
        """)

        # Container para centralizar ícone e título
        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)
        center_layout.addStretch()
        center_layout.addWidget(self.icon_label)

        # Título
        self.title_label = QLabel(tr("popup_message"))
        self.title_label.setStyleSheet("""
            font-size: 18px;
            color: #2196F3;
            font-weight: bold;
        """)
        center_layout.addWidget(self.title_label)
        center_layout.addStretch()

        header_layout.addWidget(center_container)
        layout.addWidget(header_container)

        # Label do deck
        self.deck_label = QLabel(tr("popup_subtitle"))
        self.deck_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            margin-bottom: -5px;
            padding-left: 2px;
        """)
        layout.addWidget(self.deck_label)

        # Container para o combo box (para centralizar)
        combo_container = QWidget()
        combo_layout = QHBoxLayout(combo_container)
        combo_layout.setContentsMargins(0, 0, 0, 0)

        # Combo de decks
        self.deck_select = QComboBox()
        self.deck_select.setFixedWidth(320)
        self.deck_select.setStyleSheet("""
            QComboBox {
                font-size: 15px;
                padding: 5px 12px;
                border-radius: 6px;
                border: 1px solid #ddd;
                background: white;
                min-height: 34px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 8px;
            }
        """)
        combo_layout.addWidget(self.deck_select, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(combo_container)

        # Container para botões
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(20)

        # Botão Estudar
        self.study_button = QPushButton(tr("study_now"))
        self.study_button.setFixedSize(155, 42)
        self.study_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
                padding: 0 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.study_button.clicked.connect(self.start_study)
        button_layout.addWidget(self.study_button)

        # Botão Depois
        self.dismiss_button = QPushButton(tr("later"))
        self.dismiss_button.setFixedSize(155, 42)
        self.dismiss_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
                padding: 0 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.dismiss_button.clicked.connect(self.hide_card)
        button_layout.addWidget(self.dismiss_button)

        layout.addWidget(button_container)
        layout.addStretch()

        # Preencher decks
        try:
            config = self.anki_utils.get_config()
            deck_name = config.get('deck', '')
            decks = self.anki_utils.get_decks()
            deck_names = [deck.name for deck in decks]
            self.deck_select.addItems(deck_names)
            if deck_name in deck_names:
                self.deck_select.setCurrentText(deck_name)
        except Exception as e:
            self.logger.error(f'Erro ao carregar decks: {str(e)}')

    def set_card_position(self):
        """Posiciona o popup conforme a configuração em settings.json"""
        try:
            from PyQt6.QtWidgets import QApplication
            config = self.anki_utils.get_config()
            screen_geometry = QApplication.instance().primaryScreen().availableGeometry()
            geo = self.frameGeometry()
            if config.get("window_location", "center") == "bottom_right":
                x = screen_geometry.x() + screen_geometry.width() - geo.width() - 20
                y = screen_geometry.y() + screen_geometry.height() - geo.height() - 20
                self.move(x, y)
            else:
                center_point = screen_geometry.center()
                geo.moveCenter(center_point)
                self.move(geo.topLeft())
        except Exception as e:
            self.logger.error(f'Erro ao posicionar o popup: {str(e)}')
            self.move(100, 100)

    def on_deck_changed(self, idx):
        # Atualize aqui o comportamento ao trocar o deck, se necessário
        pass
    def start_study(self):
        # Inicia o estudo do deck selecionado, dá foco ao Anki e fecha o popup
        try:
            from aqt import mw
            deck_name = self.deck_select.currentData() or self.deck_select.currentText()
            deck_id = mw.col.decks.id(deck_name)
            mw.col.decks.select(deck_id)
            mw.moveToState("review")
            # Restaura e maximiza a janela
            if mw.isMinimized():
                mw.showNormal()
                mw.showMaximized()
            # Traz a janela para frente
            mw.raise_()
            mw.activateWindow()
            mw.setWindowState(mw.windowState() & ~QtCore.Qt.WindowState.WindowMinimized | QtCore.Qt.WindowState.WindowActive | QtCore.Qt.WindowState.WindowMaximized)
        except Exception as e:
            self.logger.error(f'Erro ao iniciar o estudo: {str(e)}')
        self.close()

    def hide_card(self):
        # Implemente a lógica de esconder o popup aqui, se necessário
        self.close()


    def show_popup(self):
        """Mostra o popup de lembrete"""
        self.logger.info('Mostrando popup de lembrete...')
        try:
            # Toca um beep suave
            from aqt import QApplication
            QApplication.beep()
            
            config = self.anki_utils.get_config()
            deck_name = config.get('deck', '')
            try:
                decks = self.anki_utils.get_decks()
                deck_names = [deck.name for deck in decks]
                if not deck_name or deck_name not in deck_names:
                    if decks:
                        deck_name = decks[0].name
                        config['deck'] = deck_name
                        self.anki_utils.set_config(config)
                        self.logger.info(f'Deck configurado não encontrado. Usando o primeiro deck disponível: {deck_name}')
                    else:
                        self.logger.warning('Nenhum deck disponível. Não é possível mostrar o lembrete.')
                        tooltip(tr("no_deck"))
                        return
            except Exception as e:
                self.logger.error(f'Erro ao verificar decks: {str(e)}')
                if not deck_name:
                    tooltip(tr("no_deck_check"))
                    return
            self.deck_select.blockSignals(True)
            self.deck_select.clear()
            for deck in decks:
                level = deck.name.count("::")
                display_name = "   " * level + deck.name.split("::")[-1] if level > 0 else deck.name
                self.deck_select.addItem(display_name, deck.name)
            idx = self.deck_select.findData(deck_name)
            if idx != -1:
                self.deck_select.setCurrentIndex(idx)
            self.deck_select.blockSignals(False)
            self.set_card_position()
            self.show()
        except Exception as e:
            self.logger.error(f'Erro ao mostrar popup: {str(e)}')
