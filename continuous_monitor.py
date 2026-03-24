#!/usr/bin/env python3
"""
Monitoramento Contínuo com Auto-Healing
"""

import time
import signal
import sys
from main import run_all_tests
from auto_healing import log

class ContinuousMonitor:
    def __init__(self, interval=30):
        self.interval = interval
        self.running = True
        
        # Configurar signal handler para shutdown gracioso
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para shutdown gracioso"""
        log(f"Recebido sinal {signum}, encerrando monitoramento...", "INFO")
        self.running = False
    
    def start(self):
        """Inicia monitoramento contínuo"""
        log("Iniciando monitoramento contínuo de rede", "INFO")
        log(f"Intervalo de verificação: {self.interval} segundos", "INFO")
        
        while self.running:
            try:
                log("Executando verificação de rede...", "INFO")
                run_all_tests()
                
                if self.running:
                    log(f"Aguardando {self.interval} segundos...", "INFO")
                    time.sleep(self.interval)
                    
            except KeyboardInterrupt:
                log("Monitoramento interrompido pelo usuário", "INFO")
                break
            except Exception as e:
                log(f"Erro no monitoramento: {str(e)}", "ERROR")
                time.sleep(5)  # Esperar antes de tentar novamente
        
        log("Monitoramento encerrado", "INFO")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitoramento contínuo de rede")
    parser.add_argument(
        "--interval", 
        type=int, 
        default=30,
        help="Intervalo em segundos entre verificações (padrão: 30)"
    )
    
    args = parser.parse_args()
    
    monitor = ContinuousMonitor(interval=args.interval)
    monitor.start()

if __name__ == "__main__":
    main()
