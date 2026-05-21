"""
Intrusion Detection System (IDS)
Responsável por monitorar logs do Suricata e detectar atividades suspeitas
"""

import os
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .config import get_config, SCAN_KEYWORDS, ATTACK_PATTERNS
from .parser import parse_suricata_line, prioritize_source_ip
from ..logger import log_info, log_error, log_warning, log_success

class IntrusionDetector:
    """
    Classe principal para detecção de intrusões
    Implementa rate limiting e cache para evitar falsos positivos
    """
    
    def __init__(self):
        self.config = get_config()
        self._last_alerts = {}  # Cache de últimos alertas por IP
        self._alert_count = 0   # Contador de alertas na última hora
        self._last_reset = datetime.now()
    
    def _should_rate_limit(self, ip: str) -> bool:
        """
        Verifica se deve aplicar rate limiting para este IP
        Evita spam de alertas para o mesmo IP
        """
        now = datetime.now()
        
        # Reset contador a cada hora
        if now - self._last_reset > timedelta(hours=1):
            self._alert_count = 0
            self._last_reset = now
            self._last_alerts.clear()
        
        # Verifica limite de alertas por hora
        if self._alert_count >= self.config["max_alerts_per_hour"]:
            return True
        
        # Verifica cooldown para o mesmo IP
        if ip in self._last_alerts:
            last_alert_time = self._last_alerts[ip]
            if now - last_alert_time < timedelta(seconds=self.config["alert_cooldown"]):
                return True
        
        return False
    
    def _register_alert(self, ip: str):
        """
        Registra um alerta no sistema de rate limiting
        """
        self._last_alerts[ip] = datetime.now()
        self._alert_count += 1
    
    def _read_log_file_safe(self, log_file: str) -> List[str]:
        """
        Lê arquivo de log de forma segura, tratando erros específicos
        """
        try:
            if not os.path.exists(log_file):
                log_warning(f"Arquivo de log não encontrado: {log_file}")
                return []
            
            # Verifica se o arquivo é muito grande (evita problemas de memória)
            file_size = os.path.getsize(log_file)
            if file_size > 50 * 1024 * 1024:  # 50MB
                log_warning(f"Arquivo de log muito grande: {file_size} bytes")
                return []
            
            # Lê apenas as últimas 1000 linhas (mais recentes)
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # Pega apenas as últimas linhas para análise recente
                recent_lines = lines[-1000:] if len(lines) > 1000 else lines
                return [line.strip() for line in recent_lines if line.strip()]
        
        except PermissionError:
            log_error(f"Sem permissão para ler arquivo: {log_file}")
            return []
        except UnicodeDecodeError as e:
            log_error(f"Erro de decodificação ao ler {log_file}: {e}")
            return []
        except OSError as e:
            log_error(f"Erro de sistema ao ler {log_file}: {e}")
            return []
        except Exception as e:
            log_error(f"Erro inesperado ao ler {log_file}: {e}")
            return []
    
    def _contains_suspicious_patterns(self, line: str) -> bool:
        """
        Verifica se a linha contém padrões suspeitos
        """
        line_upper = line.upper()
        
        # Verifica palavras-chave de ataque
        for keyword in SCAN_KEYWORDS:
            if keyword.upper() in line_upper:
                return True
        
        # Verifica padrões regex de ataque
        for attack_type, patterns in ATTACK_PATTERNS.items():
            for pattern in patterns:
                if pattern.upper() in line_upper:
                    return True
        
        return False
    
    def _analyze_recent_entries(self, lines: List[str]) -> Optional[Dict]:
        """
        Analisa as entradas mais recentes do log em busca de atividades suspeitas
        """
        if not lines:
            return None
        
        # Analisa as últimas 50 linhas (mais recentes primeiro)
        recent_lines = lines[-50:] if len(lines) > 50 else lines
        
        for line in reversed(recent_lines):  # Começa do mais recente
            if self._contains_suspicious_patterns(line):
                try:
                    # Faz parsing detalhado da linha
                    parsed = parse_suricata_line(line)
                    
                    # Prioriza IP de origem para bloqueio
                    source_ip = prioritize_source_ip(parsed["source_ips"])
                    
                    # Verifica rate limiting
                    if source_ip and self._should_rate_limit(source_ip):
                        log_info(f"Rate limiting aplicado para IP: {source_ip}")
                        continue
                    
                    # Registra o alerta
                    if source_ip:
                        self._register_alert(source_ip)
                    
                    return {
                        "detected": True,
                        "type": parsed["attack_type"],
                        "raw": line,
                        "parsed": parsed,
                        "ip": source_ip,
                        "severity": parsed["severity"],
                        "timestamp": parsed["timestamp"]
                    }
                    
                except Exception as e:
                    log_error(f"Erro ao analisar linha de ataque: {e}")
                    # Fallback para detecção simples
                    continue
        
        return None
    
    def check_intrusions(self, log_file: Optional[str] = None) -> Dict:
        """
        Função principal de verificação de intrusões
        
        Args:
            log_file: Caminho do arquivo de log (opcional, usa config se não fornecido)
            
        Returns:
            Dict com resultado da detecção:
            {
                "detected": bool,
                "type": str,
                "raw": str,
                "ip": str (opcional),
                "severity": str,
                "timestamp": datetime (opcional)
            }
        """
        # Usa arquivo de log da configuração se não fornecido
        target_log_file = log_file or self.config["log_file"]
        
        log_info(f"🔍 Verificando intrusões em: {target_log_file}")
        
        # Lê arquivo de log de forma segura
        lines = self._read_log_file_safe(target_log_file)
        
        if not lines:
            log_info("Nenhuma entrada de log encontrada ou arquivo inacessível")
            return {
                "detected": False,
                "type": "none",
                "raw": "",
                "message": "Nenhuma entrada de log encontrada"
            }
        
        log_info(f"Analisando {len(lines)} entradas de log...")
        
        # Analisa entradas recentes
        result = self._analyze_recent_entries(lines)
        
        if result:
            log_warning(f"🚨 Intrusão detectada: {result['type']}")
            if result.get("ip"):
                log_warning(f"   IP suspeito: {result['ip']}")
            log_warning(f"   Severidade: {result.get('severity', 'unknown')}")
            return result
        else:
            log_success("✅ Nenhuma atividade suspeita detectada")
            return {
                "detected": False,
                "type": "none",
                "raw": "",
                "message": "Nenhuma atividade suspeita detectada"
            }

# Instância global do detector
_detector = None

def get_detector() -> IntrusionDetector:
    """
    Retorna instância singleton do detector de intrusões
    """
    global _detector
    if _detector is None:
        _detector = IntrusionDetector()
    return _detector

def check_intrusions(log_file: str = "/var/log/suricata/fast.log") -> Dict:
    """
    Função conveniência para verificação de intrusões
    Mantém compatibilidade com a interface original
    
    Args:
        log_file: Caminho do arquivo de log do Suricata
        
    Returns:
        Dict com resultado da detecção
    """
    detector = get_detector()
    return detector.check_intrusions(log_file)
