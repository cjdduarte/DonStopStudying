# Copyright 2020 Charles Henry - Modificado
import aqt
import logging


class AnkiUtils:
    """
    Classe utilitária para interagir com a API do Anki.
    Fornece métodos para acessar componentes do Anki e realizar operações comuns.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__.split('.')[0])

    def main_window(self):
        """Retorna a janela principal do Anki"""
        return aqt.mw

    def reviewer(self):
        """Retorna o revisor de cartões do Anki"""
        try:
            reviewer = self.main_window().reviewer
            if reviewer is None:
                raise Exception('Revisor não disponível')
            return reviewer
        except Exception as e:
            self.logger.error(f'Erro ao obter o revisor: {str(e)}')
            raise Exception('Houve um problema ao obter o revisor')

    def collection(self):
        """Retorna a coleção de cartões do Anki"""
        try:
            collection = self.main_window().col
            if collection is None:
                raise Exception('Coleção não disponível')
            return collection
        except Exception as e:
            self.logger.error(f'Erro ao obter a coleção: {str(e)}')
            raise Exception('Houve um problema ao obter a coleção')

    def selected_deck(self):
        """Retorna o nome do deck selecionado atualmente"""
        try:
            return self.main_window()._selectedDeck()['name']
        except Exception as e:
            self.logger.error(f'Erro ao obter o deck selecionado: {str(e)}')
            return ""

    def get_decks(self):
        """Retorna todos os decks disponíveis"""
        try:
            decks = self.collection().decks
            if decks is None:
                raise Exception('Decks não disponíveis')
            return decks.all_names_and_ids()
        except Exception as e:
            self.logger.error(f'Erro ao obter os decks: {str(e)}')
            raise Exception('Houve um problema ao obter os decks')

    def scheduler(self):
        """Retorna o agendador do Anki"""
        try:
            scheduler = self.collection().sched
            if scheduler is None:
                raise Exception('Agendador não disponível')
            return scheduler
        except Exception as e:
            self.logger.error(f'Erro ao obter o agendador: {str(e)}')
            raise Exception('Houve um problema ao obter o agendador')

    def review_is_active(self):
        """Verifica se a revisão está ativa"""
        try:
            return self.reviewer().card is not None and self.main_window().state == 'review'
        except Exception:
            return False

    def show_question(self):
        """Mostra a pergunta do cartão atual"""
        try:
            if self.review_is_active():
                self.reviewer()._showQuestion()
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f'Erro ao mostrar a pergunta: {str(e)}')
            return False

    def show_answer(self):
        """Mostra a resposta do cartão atual"""
        try:
            if self.review_is_active():
                self.main_window().reviewer._showAnswer()
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f'Erro ao mostrar a resposta: {str(e)}')
            return False

    def answer_card(self, ease):
        """
        Responde ao cartão atual com a facilidade especificada
        
        Args:
            ease: Nível de facilidade (1-4)
        
        Returns:
            bool: True se o cartão foi respondido com sucesso, False caso contrário
        """
        try:
            if not self.review_is_active():
                return False

            reviewer = self.reviewer()
            if reviewer.state != 'answer':
                return False
            if ease <= 0 or ease > self.scheduler().answerButtons(reviewer.card):
                return False

            reviewer._answerCard(ease)
            return True
        except Exception as e:
            self.logger.error(f'Erro ao responder o cartão: {str(e)}')
            return False

    def move_to_overview_state(self, name):
        """
        Move para a visão geral do deck especificado
        
        Args:
            name: Nome do deck
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            collection = self.collection()
            if collection is not None:
                deck = collection.decks.by_name(name)
                if deck is not None:
                    collection.decks.select(deck['id'])
                    try:
                        self.main_window().onOverview()
                    except AttributeError:
                        pass
                    return True
            return False
        except Exception as e:
            self.logger.error(f'Erro ao mover para o estado de visão geral: {str(e)}')
            return False

    def move_to_review_state(self, name):
        """
        Move para o estado de revisão do deck especificado
        
        Args:
            name: Nome do deck
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            # Primeiro, seleciona o deck
            collection = self.collection()
            if collection is None:
                self.logger.error("Coleção não disponível")
                return False
                
            deck = collection.decks.by_name(name)
            if deck is None:
                self.logger.error(f"Deck '{name}' não encontrado")
                return False
                
            # Seleciona o deck
            collection.decks.select(deck['id'])
            
            # Método 1: Tenta usar o método direto para iniciar o estudo
            try:
                self.main_window().moveToState('review')
                return True
            except Exception as e:
                self.logger.warning(f"Método 1 falhou: {str(e)}")
            
            # Método 2: Tenta usar o método onOverview e depois onStudyKey
            try:
                self.main_window().onOverview()
                self.main_window().onStudyKey()
                return True
            except Exception as e:
                self.logger.warning(f"Método 2 falhou: {str(e)}")
            
            # Método 3: Tenta usar o método onDeckBrowser e depois onStudyDeck
            try:
                self.main_window().onDeckBrowser()
                self.main_window().onStudyDeck()
                return True
            except Exception as e:
                self.logger.warning(f"Método 3 falhou: {str(e)}")
                
            # Se chegamos aqui, todos os métodos falharam
            self.logger.error("Todos os métodos para iniciar o estudo falharam")
            return False
        except Exception as e:
            self.logger.error(f'Erro ao mover para o estado de revisão: {str(e)}')
            return False

    def get_question(self, card):
        """Obtém a pergunta de um cartão"""
        try:
            if getattr(card, 'question', None) is None:
                question = card._getQA()['q']
            else:
                question = card.question(),
            return question
        except Exception as e:
            self.logger.error(f'Erro ao obter a pergunta: {str(e)}')
            return ""

    def get_answer(self, card):
        """Obtém a resposta de um cartão"""
        try:
            if getattr(card, 'answer', None) is None:
                answer = card._getQA()['a']
            else:
                answer = card.answer()
            return answer
        except Exception as e:
            self.logger.error(f'Erro ao obter a resposta: {str(e)}')
            return ""

    def get_current_card(self):
        """Obtém informações sobre o cartão atual"""
        try:
            if not self.review_is_active():
                raise Exception('Não foi possível obter o cartão atual porque a revisão não está ativa.')

            reviewer = self.reviewer()
            card = reviewer.card
            note_type = card.note_type()

            if card is not None:
                button_list = reviewer._answerButtonList()
                response = {
                    'card_id': card.id,
                    'question': self.get_question(card)[0],  # Uma tupla é retornada aqui
                    'answer': self.get_answer(card),
                    'css': note_type['css'],
                    'button_list': button_list
                }
                return response
            else:
                raise Exception('Cartão não disponível')
        except Exception as e:
            self.logger.error(f'Erro ao obter o cartão atual: {str(e)}')
            raise Exception('Houve um problema ao obter o cartão atual')

    def get_config(self):
        """Obtém a configuração do addon a partir de settings.json.

        - Lê o arquivo settings.json na raiz do addon.
        - Se não existir, usa valores padrão internos.
        - Sempre salva o resultado em settings.json na primeira execução.
        """
        import os
        import json
        settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
        default_config = {
            "deck": "",
            "frequency": 30,
            "enabled": True,
            "window_location": "bottom_right"
        }
        try:
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                # print("DEBUG: Configuração lida de settings.json:", config)  # LOG TEMPORÁRIO
                # Garante que todos os campos necessários estejam presentes
                for k, v in default_config.items():
                    if k not in config:
                        config[k] = v
                return config
            else:
                # Usa apenas os valores padrão internos e salva em settings.json
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=4)
                return default_config
        except Exception as e:
            self.logger.error(f'Erro ao obter a configuração: {str(e)}')
            return default_config

    def set_config(self, config):
        """Salva a configuração do addon em settings.json"""
        import os
        import json
        settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            self.logger.error(f'Erro ao salvar a configuração: {str(e)}')
            return False
