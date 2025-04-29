# Copyright 2020 Charles Henry - Modificado
from PyQt6.QtCore import QTimer
import time
import logging


class DontStopScheduler:
    """
    Scheduler responsible for study reminder intervals.
    Uses a QTimer to trigger reminders at configurable intervals.
    """

    def __init__(self, alarm_func, cancel_func):
        """
        Inicializa o agendador.
        
        Args:
            alarm_func: Função a ser chamada quando o timer disparar
            cancel_func: Função a ser chamada quando o timer for cancelado
        """
        self.alarm_func = alarm_func
        self.cancel_func = cancel_func
        self.schedule_interval = 1800  # Intervalo padrão em segundos (30 minutos)
        self.timer = QTimer()
        self.timer.timeout.connect(self.exec_schedule)
        self.enabled = False
        self.logger = logging.getLogger(__name__.split('.')[0])

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
            
            # Verifica se o intervalo é válido
            if interval <= 0:
                self.logger.warning(f"Intervalo inválido: {interval}. Usando o valor padrão de 1800 segundos (30 minutos).")
                interval = 1800
                
            self.schedule_interval = interval
            return True
        except Exception as e:
            self.logger.error(f"Erro ao definir o agendamento: {str(e)}")
            return False

    def exec_schedule(self):
        """
        Executa a função de alarme quando o timer dispara.
        """
        try:
            self.logger.info("Executando agendamento: %s" % time.ctime())
            self.alarm_func()
        except Exception as e:
            self.logger.error(f"Erro ao executar o agendamento: {str(e)}")

    def start_schedule(self):
        """
        Inicia o agendamento.
        """
        try:
            self.logger.info("Iniciando agendamento: %s" % time.ctime())
            
            # Verifica se o timer já está ativo
            if self.timer.isActive():
                self.timer.stop()
                
            # Converte segundos para milissegundos
            self.timer.start(self.schedule_interval * 1000)
            self.enabled = True
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
            
            # Verifica se o timer está ativo
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
            # Verifica se o config é válido
            if not isinstance(config, dict):
                self.logger.error(f"Configuração inválida: {config}")
                return False
                
            # Obtém a frequência da configuração
            frequency = config.get('frequency', 30)
            
            # Verifica se a frequência é válida
            if not isinstance(frequency, (int, float)) or frequency <= 0:
                self.logger.warning(f"Frequência inválida: {frequency}. Usando o valor padrão de 30 minutos.")
                frequency = 30
                
            # Converte minutos para segundos
            new_interval = frequency * 60
            
            # Atualiza o intervalo se necessário
            if self.schedule_interval != new_interval:
                self.logger.debug(f'Frequência atual: [{self.schedule_interval}], nova frequência: [{new_interval}]')
                self.schedule_interval = new_interval
                # Reinicia o agendamento se já estiver em execução
                if self.enabled:
                    self.start_schedule()

            # Obtém o estado habilitado da configuração
            enabled = config.get('enabled', False)
            
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