from auto_healing import heal
from alert.telegram import send_alert
from logger import log_info, log_error, log_success

def execute_healing(service):
    """
    Executa processo de auto-healing para um serviço específico.
    Elimina código repetido e centraliza o processo.
    
    Args:
        service (str): Nome do serviço ('gateway', 'dns', 'http')
    
    Returns:
        dict: {"success": bool, "message": str}
    """
    log_info(f"🔧 Iniciando auto-healing para {service.upper()}...")
    
    try:
        if heal(service):
            success_msg = f"✅ Auto-healing {service.upper()} concluído com sucesso"
            log_success(success_msg)
            send_alert(success_msg)
            return {"success": True, "message": success_msg}
        else:
            error_msg = f"❌ Falha no auto-healing {service.upper()}"
            log_error(error_msg)
            send_alert(error_msg)
            return {"success": False, "message": error_msg}
    except Exception as e:
        error_msg = f"❌ Erro crítico no auto-healing {service.upper()}: {str(e)}"
        log_error(error_msg)
        send_alert(error_msg)
        return {"success": False, "message": error_msg}
