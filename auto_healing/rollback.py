#!/usr/bin/env python3
"""
Sistema de Rollback para Auto-Healing
"""

import subprocess
import sys
from pathlib import Path
from .logger import log

def rollback_dns():
    """
    Executa rollback do DNS
    Returns:
        bool: True se sucesso, False se falha
    """
    try:
        script_path = Path(__file__).parent / "actions" / "rollback_dns.sh"
        
        if not script_path.exists():
            log(f"Script de rollback não encontrado: {script_path}", "ERROR")
            return False
        
        # Executar script de rollback
        result = subprocess.run(
            ["bash", str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            log(f"Rollback DNS executado: {result.stdout.strip()}", "SUCCESS")
            return True
        else:
            log(f"Falha no rollback DNS: {result.stderr.strip()}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        log("Timeout ao executar rollback DNS", "ERROR")
        return False
    except Exception as e:
        log(f"Erro inesperado no rollback DNS: {str(e)}", "ERROR")
        return False
