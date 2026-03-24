#!/usr/bin/env python3
"""
Sistema de Auto-Healing - Cérebro Principal
"""

import subprocess
import time
from pathlib import Path
from .backup import backup_dns
from .rollback import rollback_dns
from .logger import log

def change_dns():
    """
    Altera DNS para Google DNS
    Returns:
        bool: True se sucesso, False se falha
    """
    try:
        script_path = Path(__file__).parent / "actions" / "change_dns.sh"
        
        if not script_path.exists():
            log(f"Script de alteração DNS não encontrado: {script_path}", "ERROR")
            return False
        
        result = subprocess.run(
            ["bash", str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            log(f"DNS alterado: {result.stdout.strip()}", "SUCCESS")
            return True
        else:
            log(f"Falha ao alterar DNS: {result.stderr.strip()}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        log("Timeout ao alterar DNS", "ERROR")
        return False
    except Exception as e:
        log(f"Erro inesperado ao alterar DNS: {str(e)}", "ERROR")
        return False

def restart_network():
    """
    Reinicia serviço de rede
    Returns:
        bool: True se sucesso, False se falha
    """
    try:
        script_path = Path(__file__).parent / "actions" / "restart_network.sh"
        
        if not script_path.exists():
            log(f"Script de restart não encontrado: {script_path}", "ERROR")
            return False
        
        result = subprocess.run(
            ["bash", str(script_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log(f"Rede reiniciada: {result.stdout.strip()}", "SUCCESS")
            return True
        else:
            log(f"Falha ao reiniciar rede: {result.stderr.strip()}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        log("Timeout ao reiniciar rede", "ERROR")
        return False
    except Exception as e:
        log(f"Erro inesperado ao reiniciar rede: {str(e)}", "ERROR")
        return False

def heal(problem: str):
    """
    Função principal de auto-healing
    Args:
        problem (str): Tipo de problema ("dns", "gateway", "http")
    Returns:
        bool: True se sucesso, False se falha
    """
    log(f"Iniciando auto-healing para: {problem}", "INFO")
    
    if problem == "dns":
        return _heal_dns()
    elif problem == "gateway":
        return _heal_gateway()
    elif problem == "http":
        return _heal_http()
    else:
        log(f"Problema não reconhecido: {problem}", "ERROR")
        return False

def _heal_dns():
    """Auto-healing específico para DNS"""
    try:
        # 1. Fazer backup
        log("Criando backup do DNS...", "INFO")
        if not backup_dns():
            log("Falha ao criar backup DNS", "ERROR")
            return False
        
        # 2. Tentar corrigir
        log("Tentando corrigir DNS...", "INFO")
        if not change_dns():
            log("Falha ao corrigir DNS", "ERROR")
            # 3. Rollback em caso de falha
            log("Executando rollback DNS...", "WARNING")
            rollback_dns()
            return False
        
        # 4. Reiniciar rede
        log("Reiniciando serviço de rede...", "INFO")
        if not restart_network():
            log("Falha ao reiniciar rede", "WARNING")
            # DNS foi alterado mas rede não reiniciou
            # Considerar sucesso parcial
            log("DNS corrigido, mas rede não reiniciada", "WARNING")
            return True
        
        # 5. Aguardar estabilização
        log("Aguardando estabilização da rede...", "INFO")
        time.sleep(5)
        
        log("Auto-healing DNS concluído com sucesso", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"Erro inesperado no healing DNS: {str(e)}", "ERROR")
        rollback_dns()
        return False

def _heal_gateway():
    """Auto-healing específico para Gateway"""
    log("Iniciando healing para Gateway...", "INFO")
    
    # Tentar reiniciar interface de rede
    if restart_network():
        log("Gateway healing concluído", "SUCCESS")
        return True
    else:
        log("Falha no healing Gateway", "ERROR")
        return False

def _heal_http():
    """Auto-healing específico para HTTP"""
    log("Iniciando healing para HTTP...", "INFO")
    
    # Tentar reiniciar rede (pode ser problema de roteamento)
    if restart_network():
        log("HTTP healing concluído", "SUCCESS")
        return True
    else:
        log("Falha no healing HTTP", "ERROR")
        return False
