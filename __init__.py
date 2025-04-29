from aqt import gui_hooks
from aqt.qt import QTimer
# Copyright 2020 Charles Henry - Modificado

from .gui.popup import ReminderPopup
import time
import sys
import logging
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from .gui.popup import ReminderPopup
from .anki_utils import AnkiUtils
from .gui.options import ReminderOptions
from .dont_stop_scheduler import DontStopScheduler

# Configuração do logger
logger = logging.getLogger(__name__.split('.')[0])
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%H:%M:%S")
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
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
            # Aqui você pode chamar o popup ou alerta desejado
            print("ALERTA: Inatividade no cartão detectada!")
        card_inactivity_timer.timeout.connect(show_inactivity_alert)
        card_inactivity_timer.start(inactivity_extra * 60 * 1000)
    card_max_timer.timeout.connect(start_inactivity_timer)
    card_max_timer.start(max_answer_secs * 1000)

def on_reviewer_did_answer_card(card, ease):
    global card_max_timer, card_inactivity_timer
    if card_max_timer:
        card_max_timer.stop()
    if card_inactivity_timer:
        card_inactivity_timer.stop()

# Conecta os hooks na inicialização do addon
gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
gui_hooks.reviewer_did_answer_card.append(on_reviewer_did_answer_card)
card_max_timer = None
card_inactivity_timer = None

# Variáveis globais
ruzu_popup = None
anki_utils = None
dont_stop_scheduler = None


def show_lembrete():
    """Mostra o lembrete para voltar a estudar"""
    logger.info('Mostrando lembrete: %s' % time.ctime())
    
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
                logger.info(f'Deck configurado estava vazio. Usando o primeiro deck disponível: {deck_name}')
            else:
                logger.warning('Nenhum deck disponível. Não é possível mostrar o lembrete.')
                showInfo("Nenhum deck disponível. Por favor, crie um deck antes de usar o Lembrete de Estudo.")
                return
        except Exception as e:
            logger.error(f'Erro ao obter decks: {str(e)}')
            return
    
    ruzu_popup.show_popup()


def hide_lembrete():
    """Esconde o lembrete"""
    logger.info('Escondendo lembrete: %s' % time.ctime())
    ruzu_popup.hide_card()


def show_options():
    """Mostra a janela de opções"""
    if dont_stop_scheduler is None:
        showInfo("O addon ainda não foi completamente inicializado. Por favor, aguarde um momento e tente novamente.")
        return
    reminder_options = ReminderOptions(mw, dont_stop_scheduler)
    return reminder_options.exec()


def init_addon():
    """Inicializa o addon após o perfil ser carregado"""
    global ruzu_popup, anki_utils, dont_stop_scheduler
    
    logger.info('Inicializando Lembrete de Estudo...')

    # Tenta ler o meta.json se ele existir
    import os
    import json
    meta_path = os.path.join(os.path.dirname(__file__), "meta.json")
    meta_data = None
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)
            logger.info("meta.json carregado com sucesso.")
        except Exception as e:
            logger.warning(f"Falha ao ler meta.json: {e}")
    else:
        logger.info("meta.json não encontrado. Pulando leitura.")
    
    # Inicialização dos componentes principais
    global ruzu_popup
    ruzu_popup = ReminderPopup(mw)
    reminder_popup = ReminderPopup(mw)
    anki_utils = AnkiUtils()
    
    try:
        # Inicialização do agendador
        dont_stop_scheduler = DontStopScheduler(show_lembrete, hide_lembrete)
        dont_stop_scheduler.set_schedule(anki_utils.get_config()['frequency'] * 60)
        
        # Verificar se há decks disponíveis antes de iniciar o agendador
        decks = anki_utils.get_decks()
        if not decks:
            logger.warning('Nenhum deck disponível. O lembrete não será iniciado.')
        else:
            # Verificar se o deck configurado existe
            config = anki_utils.get_config()
            deck_name = config.get('deck', '')
            
            # Se o deck configurado estiver vazio ou não existir, usar o primeiro deck disponível
            # Verifica se o deck salvo existe na lista de decks disponíveis
            deck_names = [d.name if hasattr(d, "name") else d[0] for d in decks]
            if not deck_name or deck_name not in deck_names:
                logger.warning(f"Deck '{deck_name}' não encontrado. Usando o primeiro deck disponível apenas em memória.")
                deck_name = deck_names[0]
                config['deck'] = deck_name
                logger.info(f'Deck configurado estava vazio. Usando o primeiro deck disponível: {deck_name}')
            
            # Iniciar o agendador se estiver habilitado
            if config['enabled']:
                logger.info('Iniciando agendador...')
                dont_stop_scheduler.start_schedule()
    except Exception as e:
        logger.error(f'Erro ao inicializar o addon: {str(e)}')


# Adiciona a ação de configuração ao gerenciador de addons
mw.addonManager.setConfigAction(__name__, lambda: show_options())

# Adiciona a opção ao menu Ferramentas
options_action = QAction("Configurar Lembrete de Estudo", mw)
options_action.triggered.connect(lambda _: show_options())
mw.form.menuTools.addAction(options_action)

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
