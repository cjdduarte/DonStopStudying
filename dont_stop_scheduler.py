# Copyright 2025 Carlos Duarte
from aqt.qt import QTimer
import time
import logging
from aqt import mw


class DontStopScheduler:
    """
    Scheduler responsible for study reminder intervals.
    Uses a QTimer to trigger reminders at configurable intervals.
    """

    def __init__(self, alarm_func, cancel_func, anki_utils):
        """
        Inicializa o agendador.
        
        Args:
            alarm_func: Função a ser chamada quando o timer disparar
            cancel_func: Função a ser chamada quando o timer for cancelado
            anki_utils: Instância do módulo aqt.utils
        """
        self.alarm_func = alarm_func
        self.cancel_func = cancel_func
        self.anki_utils = anki_utils
        self.logger = logging.getLogger(__name__.split('.')[0])
        
        # Lê a configuração inicial
        try:
            config = self.anki_utils.get_config()
            frequency = config.get('frequency', 1)  # Valor padrão de 1 minuto
            self.schedule_interval = frequency * 60  # Converte minutos para segundos
            self.logger.debug(f'Frequência inicial lida do config: {frequency} minutos')
        except Exception as e:
            self.logger.error(f'Erro ao ler configuração inicial: {str(e)}')
            self.schedule_interval = 60  # Valor padrão em segundos (1 minuto)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.exec_schedule)
        self.enabled = False
        self.paused = False
        self.in_review = False
        self.last_card_time = 0

    def reset_and_start_timer(self):
        """Reseta e inicia o timer de lembrete com o intervalo atual."""
        self.timer.stop()
        if self.enabled:
            interval_ms = self.schedule_interval * 1000
            self.timer.start(interval_ms)
            self.logger.debug(f"Timer de lembrete resetado para {self.schedule_interval // 60} minutos")

    def set_schedule(self, interval):
        """
        Define o intervalo do agendamento.
        
        Args:
            interval: Intervalo em segundos
        """
        try:
            self.logger.info("Definindo agendamento: %s" % time.ctime())
            
            if interval <= 0:
                self.logger.warning(f"Intervalo inválido: {interval}. Usando o valor padrão de 60 segundos (1 minuto).")
                interval = 60
                
            self.schedule_interval = interval
            self.reset_and_start_timer()
            return True
        except Exception as e:
            self.logger.error(f"Erro ao definir o agendamento: {str(e)}")
            return False

    def exec_schedule(self):
        """Executa o agendamento"""
        try:
            config = self.anki_utils.get_config()
            
            # Verifica se o addon está habilitado
            if not config.get('enabled', True):
                self.logger.info("Addon desabilitado, pulando lembrete")
                return

            # Verifica se está em modo de revisão
            if mw.state == "review":
                self.logger.debug(f'Em modo de revisão. Inatividade após resposta máxima: {config.get("inactivity_after_max_answer", False)}')
                if config.get("inactivity_after_max_answer", False):
                    # Em revisão com inatividade ativada, usa o timer do cartão
                    extra_minutes = config.get('inactivity_extra_minutes', 1)
                    self.logger.info(f'Timer extra de inatividade configurado: {extra_minutes} minutos')
                    return
                else:
                    # Em revisão sem inatividade, não mostra popup
                    self.logger.info("Em modo de revisão e inatividade desativada, pulando lembrete")
                    return
            
            # Fora da revisão ou em revisão sem inatividade, mostra popup normal
            self.logger.debug(f'Timer normal ativo com intervalo de {self.schedule_interval // 60} minutos')
            self.alarm_func()
            
        except Exception as e:
            self.logger.error(f'Erro ao executar agendamento: {str(e)}')

    def start_schedule(self):
        """
        Inicia o agendamento.
        """
        try:
            self.logger.info("Iniciando agendamento: %s" % time.ctime())
            
            if self.timer.isActive():
                self.timer.stop()
                
            self.timer.start(self.schedule_interval * 1000)
            self.enabled = True
            self.paused = False
            self.in_review = False
            self.logger.info(f"Timer iniciado com intervalo de {self.schedule_interval // 60} minutos")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao iniciar o agendamento: {str(e)}")
            self.enabled = False
            return False

    def stop_schedule(self):
        """
        Para o agendamento.
        """
        try:
            self.logger.info("Parando agendamento: %s" % time.ctime())
            
            if self.timer.isActive():
                self.timer.stop()
                
            try:
                self.cancel_func()
            except Exception as e:
                self.logger.error(f"Erro ao executar a função de cancelamento: {str(e)}")
                
            self.enabled = False
            return True
        except Exception as e:
            self.logger.error(f"Erro ao parar o agendamento: {str(e)}")
            return False

    def update_state(self, config):
        """
        Atualiza o estado do agendamento com base nas configurações.
        
        Args:
            config: Dicionário com as configurações
        """
        try:
            if not isinstance(config, dict):
                self.logger.error(f"Configuração inválida: {config}")
                return False
                
            # Obtém a frequência da configuração
            self.logger.debug(f'Config recebida: {config}')
            frequency = config.get('frequency', 1)  # Valor padrão de 1 minuto
            self.logger.debug(f'Frequência obtida do config: {frequency}')
            
            # Obtém o tempo extra de inatividade
            extra_minutes = config.get('inactivity_extra_minutes', 1)  # Valor padrão de 1 minuto
            self.logger.info(f'Timer extra de inatividade configurado: {extra_minutes} minutos')
            
            # Verifica se a frequência é válida
            if not isinstance(frequency, (int, float)) or frequency <= 0:
                self.logger.warning(f"Frequência inválida: {frequency}. Usando o valor padrão de 1 minuto.")
                frequency = 1
                
            # Verifica se o tempo extra é válido
            if not isinstance(extra_minutes, (int, float)) or extra_minutes <= 0:
                self.logger.warning(f"Tempo extra inválido: {extra_minutes}. Usando o valor padrão de 1 minuto.")
                extra_minutes = 1
                
            # Converte minutos para segundos
            new_interval = frequency * 60
            self.logger.debug(f'Novo intervalo em segundos: {new_interval}')
            
            # Atualiza o intervalo se necessário
            if self.schedule_interval != new_interval:
                self.logger.info(f'Timer normal atualizado: {self.schedule_interval // 60} -> {frequency} minutos')
                self.schedule_interval = new_interval
                if self.enabled:
                    self.start_schedule()

            # Obtém o estado habilitado da configuração
            enabled = config.get('enabled', True)  # Valor padrão True
            
            # Reinicia o agendamento se o estado habilitado/desabilitado mudou
            if self.enabled != enabled:
                self.logger.debug(f'Estado habilitado mudou de [{self.enabled}] para [{enabled}]')
                if enabled:
                    self.start_schedule()
                else:
                    self.stop_schedule()
                    
            return True
        except Exception as e:
            self.logger.error(f"Erro ao atualizar o estado do agendamento: {str(e)}")
            return False

    def pause_schedule(self):
        """Pausa o agendamento temporariamente"""
        try:
            self.logger.info("Pausando agendamento")
            if self.timer.isActive():
                self.timer.stop()
            self.paused = True
            self.in_review = True
        except Exception as e:
            self.logger.error(f"Erro ao pausar agendamento: {str(e)}")

    def resume_schedule(self):
        """Retoma o agendamento após pausa"""
        try:
            self.logger.info("Retomando agendamento")
            if self.paused and self.enabled:
                self.timer.start(self.schedule_interval * 1000)
                self.paused = False
                self.in_review = False
                self.logger.info(f"Timer reiniciado com intervalo de {self.schedule_interval // 60} minutos")
            else:
                self.logger.info("Não foi possível retomar o agendamento: paused={}, enabled={}".format(self.paused, self.enabled))
        except Exception as e:
            self.logger.error(f"Erro ao retomar agendamento: {str(e)}")