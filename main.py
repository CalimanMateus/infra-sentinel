from checks.gateway import ping_gateway, ping_dns
from checks.dns import test_dns
from checks.http import test_http
from alert.telegram import send_alert, send_telegram_message
from auto_healing import heal

def show_failure_suggestions(failure_type):
    """Mostra sugestões específicas para o tipo de falha detectada"""
    if failure_type == "gateway":
        print("🔴 Falha de Gateway")
        print("   Ação:")
        print("   • Verificar interface de rede (cabo/Wi-Fi)")
        print("   • Reiniciar interface de rede ou roteador")
        print("   Alerta: [ALERTA] Gateway não responde (problema interno)")
        print()
    elif failure_type == "dns":
        print("🟡 Falha de DNS")
        print("   Ação:")
        print("   • Verificar configuração de DNS")
        print("   • Trocar para DNS público (ex: 8.8.8.8)")
        print("   Alerta: [ALERTA] DNS falhou")
        print()
    elif failure_type == "http":
        print("🟠 Falha de HTTP (internet indisponível)")
        print("   Ação:")
        print("   • Verificar conexão com provedor")
        print("   • Testar roteador ou reiniciar serviços de rede")
        print("   Alerta: [ALERTA] HTTP falhou")
        print()
    elif failure_type == "multiple":
        print("🔴 Falha múltipla (ex: DNS + HTTP)")
        print("   Ação:")
        print("   • Priorizar correção do Gateway se falhar")
        print("   • Depois corrigir DNS")
        print("   • Finalmente corrigir HTTP")
        print("   Alerta: [ALERTA] Gateway ou DNS falhou (seguir prioridade)")
        print()
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
        print("🟢 Tudo funcionando (tudo ok)")
        print("   Ação: Nenhuma ação necessária")
        print("   Status: rede está operacional")
        print("   Log/Alerta: [INFO] Rede funcionando")
        print()
        print("💡 Resumo profissional:")
        print("   Gateway → DNS → HTTP (prioridade de diagnóstico)")
        print("   Registrar logs e alertas claros")
        print("   Corrigir primeiro os problemas mais críticos da rede interna, depois externos.")

def run_all_tests():
    """
    Sistema de decisão inteligente - Projeto 1
    - Avalia cada teste de rede
    - Envia alerta específico dependendo do problema
    - Funciona modularmente com os arquivos checks/*.py
    """

    print("🔍 Verificando rede...\n")

    # Executar todos os testes
    gateway_status = ping_gateway()
    dns_ping_status = ping_dns()
    dns_resolve_status = test_dns()
    http_status = test_http()

    # Mostrar resultados de todos os testes
    gateway_msg = f"🌐 Gateway (192.168.1.1): {'✅ OK' if gateway_status else '❌ FALHOU'}"
    dns_ping_msg = f"📍 DNS Ping (8.8.8.8): {'✅ OK' if dns_ping_status else '❌ FALHOU'}"
    dns_resolve_msg = f"🔎 DNS Resolve (google.com): {'✅ OK' if dns_resolve_status else '❌ FALHOU'}"
    http_msg = f"🌍 HTTP (google.com): {'✅ OK' if http_status else '❌ FALHOU'}"
    
    print(gateway_msg)
    print(dns_ping_msg)
    print(dns_resolve_msg)
    print(http_msg)
    print()
    
    # Enviar resumo para Telegram
    summary_msg = f"Diagnóstico de Rede:\n{gateway_msg}\n{dns_ping_msg}\n{dns_resolve_msg}\n{http_msg}"
    send_telegram_message(summary_msg)

    # Verificar cada componente individualmente e mostrar sugestões específicas
    failure_count = 0
    
    if not gateway_status:
        send_alert("🚨 Gateway caiu → problema interno")
        show_failure_suggestions("gateway")
        
        # Auto-healing para Gateway
        print("🔧 Iniciando auto-healing para Gateway...")
        if heal("gateway"):
            print("✅ Auto-healing Gateway concluído com sucesso")
            send_alert("✅ Gateway corrigido automaticamente")
        else:
            print("❌ Falha no auto-healing Gateway")
            send_alert("❌ Falha ao corrigir Gateway automaticamente")
        
        failure_count += 1

    if gateway_status and not dns_ping_status:
        send_alert("🚨 Gateway ok + DNS Ping falha → problema DNS")
        show_failure_suggestions("dns")
        
        # Auto-healing para DNS
        print("🔧 Iniciando auto-healing para DNS...")
        if heal("dns"):
            print("✅ Auto-healing DNS concluído com sucesso")
            send_alert("✅ DNS corrigido automaticamente")
        else:
            print("❌ Falha no auto-healing DNS")
            send_alert("❌ Falha ao corrigir DNS automaticamente")
        
        failure_count += 1

    if gateway_status and dns_ping_status and not dns_resolve_status:
        send_alert("🚨 DNS Ping ok + DNS Resolve falha → problema DNS")
        show_failure_suggestions("dns")
        
        # Auto-healing para DNS
        print("🔧 Iniciando auto-healing para DNS...")
        if heal("dns"):
            print("✅ Auto-healing DNS concluído com sucesso")
            send_alert("✅ DNS corrigido automaticamente")
        else:
            print("❌ Falha no auto-healing DNS")
            send_alert("❌ Falha ao corrigir DNS automaticamente")
        
        failure_count += 1

    if gateway_status and dns_ping_status and dns_resolve_status and not http_status:
        send_alert("🚨 DNS ok + HTTP falha → problema internet")
        show_failure_suggestions("http")
        
        # Auto-healing para HTTP
        print("🔧 Iniciando auto-healing para HTTP...")
        if heal("http"):
            print("✅ Auto-healing HTTP concluído com sucesso")
            send_alert("✅ HTTP corrigido automaticamente")
        else:
            print("❌ Falha no auto-healing HTTP")
            send_alert("❌ Falha ao corrigir HTTP automaticamente")
        
        failure_count += 1

    # Verificar se há múltiplas falhas
    if failure_count > 1:
        show_failure_suggestions("multiple")

    # Se tudo estiver funcionando
    if gateway_status and dns_ping_status and dns_resolve_status and http_status:
        success_msg = "✅ Rede funcionando perfeitamente!"
        print(success_msg)
        print("🎉 Todos os testes passaram com sucesso")
        show_failure_suggestions("success")
        
        # Enviar mensagem de sucesso para Telegram
        send_telegram_message(success_msg)

if __name__ == "__main__":
    run_all_tests()