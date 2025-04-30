import os
import sys

# Adiciona o diretório do addon ao PYTHONPATH
addon_dir = os.path.dirname(os.path.abspath(__file__))
if addon_dir not in sys.path:
    sys.path.append(addon_dir)

from aqt import gui_hooks
from aqt.qt import QTimer, QAction
from aqt import mw
from aqt.utils import showInfo
from gui.popup import ReminderPopup
from anki_utils import AnkiUtils
from gui.options import ReminderOptions
from dont_stop_scheduler import DontStopScheduler
from translations import tr
import time
import logging

# Configuração do logger
logger = logging.getLogger(__name__.split('.')[0])
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%H:%M:%S")
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
sh.setStream(sys.stdout)  # Força o uso do stdout
sh.encoding = 'utf-8'  # Define o encoding como UTF-8
logger.addHandler(sh)
logger.setLevel(logging.WARNING)
# Timers para controle de inatividade na revisão
card_max_timer = None
card_inactivity_timer = None

def on_reviewer_did_show_question(card):
    global card_max_timer, card_inactivity_timer

    # Carrega configurações do addon
    import json, os
    settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
    with open(settings_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Se não ativou o recurso, não faz nada
    if not config.get("inactivity_after_max_answer", False):
        return

    # Lê o tempo máximo do cartão do Anki (em segundos)
    mw = card.reviewer.mw if hasattr(card, "reviewer") else None
    max_answer_secs = 120  # padrão
    if mw and hasattr(mw.col, "conf"):
        max_answer_secs = mw.col.conf.get("maxAnswerSecs", 120)

    # Tempo extra de inatividade (em minutos)
    inactivity_extra = config.get("inactivity_extra_minutes", 3)

    # Cancela timers anteriores
    if card_max_timer:
        card_max_timer.stop()
    if card_inactivity_timer:
        card_inactivity_timer.stop()

    # Inicia timer do cartão
    card_max_timer = QTimer()
    card_max_timer.setSingleShot(True)
    def start_inactivity_timer():
        global card_inactivity_timer
        card_inactivity_timer = QTimer()
        card_inactivity_timer.setSingleShot(True)
        def show_inactivity_alert():
            # Mostra o popup de inatividade
            show_lembrete()
        card_inactivity_timer.timeout.connect(show_inactivity_alert)
        card_inactivity_timer.start(inactivity_extra * 60 * 1000)
    card_max_timer.timeout.connect(start_inactivity_timer)
    card_max_timer.start(max_answer_secs * 1000)

def on_reviewer_did_answer_card(card, ease, reviewer):
    global card_max_timer, card_inactivity_timer
    if card_max_timer:
        card_max_timer.stop()
    if card_inactivity_timer:
        card_inactivity_timer.stop()

# Conecta os hooks na inicialização do addon
gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
gui_hooks.reviewer_did_answer_card.append(on_reviewer_did_answer_card)

# Adiciona hooks para pausar/retomar o timer durante revisão
def on_state_will_change(new_state, old_state):
    """Gerencia o timer baseado na mudança de estado"""
    if dont_stop_scheduler:
        if new_state == "review":
            dont_stop_scheduler.pause_schedule()
        elif old_state == "review":
            dont_stop_scheduler.resume_schedule()

gui_hooks.state_will_change.append(on_state_will_change)

card_max_timer = None
card_inactivity_timer = None

# Variáveis globais
reminder_popup = None
anki_utils = None
dont_stop_scheduler = None


def show_lembrete():
    """Mostra o lembrete para voltar a estudar"""
    logger.info(tr('log_showing_reminder').format(time.ctime()))
    
    # Verificar se o deck configurado existe
    config = anki_utils.get_config()
    deck_name = config.get('deck', '')
    
    # Se o deck configurado estiver vazio ou não existir, usar o primeiro deck disponível
    if not deck_name:
        try:
            decks = anki_utils.get_decks()
            if decks:
                deck_name = decks[0].name
                config['deck'] = deck_name
                logger.info(tr('log_empty_deck').format(deck_name))
            else:
                logger.warning(tr('log_no_deck'))
                showInfo(tr("no_deck"))
                return
        except Exception as e:
            logger.error(tr('error_get_decks').format(str(e)))
            return
    
    reminder_popup.show_popup()


def hide_lembrete():
    """Esconde o lembrete"""
    logger.info(tr('log_hiding_reminder').format(time.ctime()))
    reminder_popup.hide_card()


def show_options():
    """Mostra a janela de opções"""
    if dont_stop_scheduler is None:
        showInfo("O addon ainda não foi completamente inicializado. Por favor, aguarde um momento e tente novamente.")
        return
    reminder_options = ReminderOptions(mw, dont_stop_scheduler)
    return reminder_options.exec()


def init_addon():
    """Inicializa o addon"""
    global reminder_popup, anki_utils, dont_stop_scheduler
    logger.info(tr('log_initializing'))
    
    try:
        # Inicializa utilitários
        anki_utils = AnkiUtils()
        
        # Verifica se existe configurações do usuário
        user_settings_path = os.path.join(os.path.dirname(__file__), "settings_user.json")
        if os.path.exists(user_settings_path):
            # Restaura as configurações do usuário
            anki_utils.restore_config()
        
        # Inicializa o popup e o agendador
        reminder_popup = ReminderPopup(mw)
        dont_stop_scheduler = DontStopScheduler(
            alarm_func=show_lembrete,
            cancel_func=hide_lembrete,
            anki_utils=anki_utils
        )
        
        # Configura o menu de opções
        action = QAction(tr("options_menu"), mw)
        action.triggered.connect(show_options)
        mw.form.menuTools.addAction(action)
        
        # Inicia o agendador
        dont_stop_scheduler.start_schedule()
        
    except Exception as e:
        logger.error(tr('error_init_addon').format(str(e)))


# Adiciona a ação de configuração ao gerenciador de addons
mw.addonManager.setConfigAction(__name__, lambda: show_options())

# Inicializa o addon quando o perfil for carregado
mw.addonManager.setConfigUpdatedAction(__name__, lambda: dont_stop_scheduler.update_state(anki_utils.get_config()) if dont_stop_scheduler else None)

# Inicialização imediata para compatibilidade com diferentes versões do Anki
try:
    # Tenta usar o sistema de hooks mais recente
    from aqt import gui_hooks
    gui_hooks.profile_did_open.append(init_addon)
except (ImportError, AttributeError):
    # Fallback para inicialização direta
    try:
        init_addon()
    except Exception as e:
        logger.error(f'Erro na inicialização direta: {str(e)}')
        
        # Tenta adiar a inicialização usando QTimer
        def delayed_init():
            try:
                init_addon()
            except Exception as e:
                logger.error(f'Erro na inicialização adiada: {str(e)}')
        
        QTimer.singleShot(1000, delayed_init)  # Tenta inicializar após 1 segundo
