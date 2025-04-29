from PyQt6.QtCore import QLocale

def get_language():
    lang = QLocale().name()
    #print(lang)
    if lang.startswith("pt"):
        return "pt_BR"
    return "en"

translations = {
    "pt_BR": {
        "app_title": "Lembrete de Estudo",
        "popup_title": "Lembrete de Estudo",
        "popup_message": "Hora de voltar a estudar!",
        "popup_subtitle": "Deck atual",
        "popup_deck": "Deck atual: {deck}",
        "study_now": "Estudar Agora",
        "later": "Mais Tarde",
        "no_deck": "Nenhum deck disponível. Por favor, crie um deck antes de usar o Lembrete de Estudo.",
        "no_deck_config": "Nenhum deck configurado. Por favor, configure um deck nas opções do addon.",
        "no_deck_check": "Não foi possível verificar os decks disponíveis. Tente reiniciar o Anki.",
        "review_fail": "Não foi possível iniciar a revisão do deck '{deck}'. Verifique se o deck existe e tem cartões para revisar.",
        "review_error": "Erro ao iniciar o estudo. Verifique o log para mais detalhes.",
        "popup_error": "Erro ao mostrar o lembrete. Verifique o log para mais detalhes.",
        "config_title": "Configurações do Lembrete de Estudo",
        "deck_select": "Deck para estudo:",
        "freq_select": "Frequência do lembrete:",
        "enabled_check": "Ativar lembretes:",
        "save": "Salvar",
        "close": "Fechar",
        "test_reminder": "Testar Lembrete",
        "config_saved": "Configurações salvas com sucesso! Reinicie o Anki para aplicar as alterações.",
        "config_save_error": "Ocorreu um erro ao salvar as configurações. Tente reiniciar o Anki.",
        "config_scheduler_error": "Configurações salvas, mas houve um erro ao atualizar o agendador. Tente reiniciar o Anki.",
        "config_save_fail": "Não foi possível salvar as configurações. Tente reiniciar o Anki.",
        "get_decks_error": "Não foi possível obter a lista de decks. Tente reiniciar o Anki.",
        "no_deck_found": "Nenhum deck encontrado. Por favor, crie um deck antes de usar este addon.",
        "options_menu": "Configurar Lembrete de Estudo",
        "confirm_save_title": "Confirmar salvamento",
        "confirm_save_msg": "Deseja realmente salvar as configurações do addon?",
        "yes": "Sim",
        "no": "Não",
    },
    "en": {
        "app_title": "Study Reminder",
        "popup_title": "Study Reminder",
        "popup_message": "Time to get back to studying!",
        "popup_subtitle": "Select the deck and click 'Study Now' to start.",
        "popup_deck": "Deck: {deck}",
        "study_now": "Study Now",
        "later": "Later",
        "no_deck": "No deck available. Please create a deck before using the Study Reminder.",
        "no_deck_config": "No deck configured. Please set a deck in the addon options.",
        "no_deck_check": "Could not check available decks. Try restarting Anki.",
        "review_fail": "Could not start review for deck '{deck}'. Check if the deck exists and has cards to review.",
        "review_error": "Error starting study. Check the log for more details.",
        "popup_error": "Error showing reminder. Check the log for more details.",
        "config_title": "Study Reminder Settings",
        "deck_select": "Deck to study:",
        "freq_select": "Reminder frequency:",
        "enabled_check": "Enable reminders:",
        "save": "Save",
        "close": "Close",
        "test_reminder": "Test Reminder",
        "config_saved": "Settings saved successfully! Restart Anki to apply the changes.",
        "config_save_error": "An error occurred while saving settings. Try restarting Anki.",
        "config_scheduler_error": "Settings saved, but there was an error updating the scheduler. Try restarting Anki.",
        "config_save_fail": "Could not save settings. Try restarting Anki.",
        "get_decks_error": "Could not get the list of decks. Try restarting Anki.",
        "no_deck_found": "No deck found. Please create a deck before using this addon.",
        "options_menu": "Configure Study Reminder",
        "confirm_save_title": "Confirm save",
        "confirm_save_msg": "Do you really want to save the addon's settings?",
        "yes": "Yes",
        "no": "No",
    }
}

def tr(key, **kwargs):
    lang = get_language()
    text = translations.get(lang, translations["en"]).get(key, key)
    return text.format(**kwargs) if kwargs else text