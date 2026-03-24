#!/usr/bin/env python3
"""
Sistema de Backup para Auto-Healing
"""

import subprocess
import sys
from pathlib import Path
from .logger import log

def backup_dns():
    """
    Executa backup do DNS
    Returns:
        bool: True se sucesso, False se falha
    """
    try:
        script_path = Path(__file__).parent / "actions" / "backup_dns.sh"
        
        if not script_path.exists():
            log(f"Script de backup não encontrado: {script_path}", "ERROR")
            return False
        
        # Executar script de backup
        result = subprocess.run(
            ["bash", str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            log(f"Backup DNS executado: {result.stdout.strip()}", "SUCCESS")
            return True
        else:
            log(f"Falha no backup DNS: {result.stderr.strip()}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        log("Timeout ao executar backup DNS", "ERROR")
        return False
    except Exception as e:
        log(f"Erro inesperado no backup DNS: {str(e)}", "ERROR")
        return False
