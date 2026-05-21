from checks.gateway import ping_gateway, ping_dns
from checks.dns import test_dns
from checks.http import test_http
from alert.telegram import send_alert, send_telegram_message
from healing import execute_healing
from logger import log_info, log_error, log_warning, log_success
from security.ids import check_intrusions
from security.firewall import block_ip
from security.config import AUTO_BLOCK

def show_failure_suggestions(failure_type):
    """Mostra sugestões específicas para o tipo de falha detectada"""
    if failure_type == "gateway":
        log_warning("🔴 Falha de Gateway")
        log_info("   Ação:")
        log_info("   • Verificar interface de rede (cabo/Wi-Fi)")
        log_info("   • Reiniciar interface de rede ou roteador")
        send_alert("[ALERTA] Gateway não responde (problema interno)")
    elif failure_type == "dns":
        log_warning("🟡 Falha de DNS")
        log_info("   Ação:")
        log_info("   • Verificar configuração de DNS")
        log_info("   • Trocar para DNS público (ex: 8.8.8.8)")
        send_alert("[ALERTA] DNS falhou")
    elif failure_type == "http":
        log_warning("🟠 Falha de HTTP (internet indisponível)")
        log_info("   Ação:")
        log_info("   • Verificar conexão com provedor")
        log_info("   • Testar roteador ou reiniciar serviços de rede")
        send_alert("[ALERTA] HTTP falhou")
    elif failure_type == "multiple":
        log_error("🔴 Falha múltipla (ex: DNS + HTTP)")
        log_info("   Ação:")
        log_info("   • Priorizar correção do Gateway se falhar")
        log_info("   • Depois corrigir DNS")
        log_info("   • Finalmente corrigir HTTP")
        send_alert("[ALERTA] Gateway ou DNS falhou (seguir prioridade)")
    elif failure_type == "timeout":
        print("⏱️  Falha temporária / latência")
        print("   Ação:")
        print("   • Implementar timeout curto nos testes")
        print("   • Registrar log para análise futura")
        print("   Alerta: [INFO] Timeout ou lentidão detectada")
        print()
    elif failure_type == "continuous":
        print("🔄 Loop contínuo / teste de estabilidade")
        print("   Ação:")
        print("   • Monitorar histórico de alertas")
        print("   • Garantir que alertas repetidos não sobrecarreguem o sistema")
        print("   Alerta: [INFO] Falha detectada várias vezes consecutivas")
        print()
    elif failure_type == "success":
        log_success("🟢 Tudo funcionando (tudo ok)")
        log_info("   Ação: Nenhuma ação necessária")
        log_info("   Status: rede está operacional")
        send_alert("[INFO] Rede funcionando")
        log_info("💡 Resumo profissional:")
        log_info("   Gateway → DNS → HTTP (prioridade de diagnóstico)")
        log_info("   Registrar logs e alertas claros")
        log_info("   Corrigir primeiro os problemas mais críticos da rede interna, depois externos.")

def run_all_tests():
    """
    Sistema de decisão inteligente - Projeto 1
    - Avalia cada teste de rede
    - Envia alerta específico dependendo do problema
    - Funciona modularmente com os arquivos checks/*.py
    """

    log_info("🔍 Verificando rede...")

    # Executar todos os testes
    gateway_result = ping_gateway()
    dns_ping_result = ping_dns()
    dns_resolve_result = test_dns()
    http_result = test_http()

    # Extrair status dos resultados estruturados
    gateway_status = gateway_result["status"]
    dns_ping_status = dns_ping_result["status"]
    dns_resolve_status = dns_resolve_result["status"]
    http_status = http_result["status"]

    # Mostrar resultados de todos os testes
    gateway_msg = f"🌐 Gateway (192.168.1.1): {'✅ OK' if gateway_status else '❌ FALHOU'}"
    dns_ping_msg = f"📍 DNS Ping (8.8.8.8): {'✅ OK' if dns_ping_status else '❌ FALHOU'}"
    dns_resolve_msg = f"🔎 DNS Resolve (google.com): {'✅ OK' if dns_resolve_status else '❌ FALHOU'}"
    http_msg = f"🌍 HTTP (google.com): {'✅ OK' if http_status else '❌ FALHOU'}"
    
    log_info(gateway_msg)
    log_info(dns_ping_msg)
    log_info(dns_resolve_msg)
    log_info(http_msg)
    
    # Enviar resumo para Telegram
    summary_msg = f"Diagnóstico de Rede:\n{gateway_msg}\n{dns_ping_msg}\n{dns_resolve_msg}\n{http_msg}"
    send_telegram_message(summary_msg)

    # Verificar cada componente individualmente e mostrar sugestões específicas
    failure_count = 0
    
    if not gateway_status:
        send_alert("🚨 Gateway caiu → problema interno")
        show_failure_suggestions("gateway")
        
        # Auto-healing para Gateway usando função centralizada
        execute_healing("gateway")
        
        failure_count += 1

    if gateway_status and not dns_ping_status:
        send_alert("🚨 Gateway ok + DNS Ping falha → problema DNS")
        show_failure_suggestions("dns")
        
        # Auto-healing para DNS usando função centralizada
        execute_healing("dns")
        
        failure_count += 1

    if gateway_status and dns_ping_status and not dns_resolve_status:
        send_alert("🚨 DNS Ping ok + DNS Resolve falha → problema DNS")
        show_failure_suggestions("dns")
        
        # Auto-healing para DNS usando função centralizada
        execute_healing("dns")
        
        failure_count += 1

    if gateway_status and dns_ping_status and dns_resolve_status and not http_status:
        send_alert("🚨 DNS ok + HTTP falha → problema internet")
        show_failure_suggestions("http")
        
        # Auto-healing para HTTP usando função centralizada
        execute_healing("http")
        
        failure_count += 1

    # Verificar se há múltiplas falhas
    if failure_count > 1:
        show_failure_suggestions("multiple")

    # Se tudo estiver funcionando
    if gateway_status and dns_ping_status and dns_resolve_status and http_status:
        success_msg = "✅ Rede funcionando perfeitamente!"
        log_success(success_msg)
        log_success("🎉 Todos os testes passaram com sucesso")
        show_failure_suggestions("success")
        
        # Enviar mensagem de sucesso para Telegram
        send_telegram_message(success_msg)

def run_security_checks():
    """
    Sistema de Segurança - Projeto 3
    - Verifica atividades suspeitas via IDS
    - Envia alertas de segurança
    - Bloqueia IPs maliciosos automaticamente (se habilitado)
    """
    log_info("🛡️ Iniciando verificação de segurança...")
    
    try:
        # Executa verificação de intrusões
        intrusion = check_intrusions()
        
        if intrusion["detected"]:
            # Formata mensagem de alerta de segurança
            attack_type = intrusion.get("type", "unknown")
            severity = intrusion.get("severity", "medium")
            ip = intrusion.get("ip", "desconhecido")
            
            alert_msg = f"🚨 Ataque detectado: {attack_type.upper()}"
            if ip != "desconhecido":
                alert_msg += f" | IP: {ip}"
            alert_msg += f" | Severidade: {severity.upper()}"
            
            log_warning(alert_msg)
            send_alert(alert_msg)
            
            # Bloqueio automático se habilitado e IP disponível
            if AUTO_BLOCK and ip and ip != "desconhecido":
                log_info(f"🔥 Iniciando bloqueio automático do IP: {ip}")
                
                if block_ip(ip):
                    block_msg = f"🔒 IP {ip} bloqueado com sucesso"
                    log_success(block_msg)
                    send_alert(block_msg)
                else:
                    error_msg = f"❌ Falha ao bloquear IP {ip}"
                    log_error(error_msg)
                    send_alert(error_msg)
            else:
                if not AUTO_BLOCK:
                    log_info("📝 Bloqueio automático desativado (AUTO_BLOCK=False)")
                elif not ip or ip == "desconhecido":
                    log_info("📝 IP não identificado para bloqueio automático")
        else:
            log_success("✅ Nenhuma ameaça de segurança detectada")
            
    except Exception as e:
        log_error(f"❌ Erro no sistema de segurança: {e}")
        send_alert(f"[ERRO] Falha na verificação de segurança: {e}")

if __name__ == "__main__":
    run_all_tests()
    run_security_checks()