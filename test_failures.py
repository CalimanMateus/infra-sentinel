#!/usr/bin/env python3
"""
Script para simular falhas e testar o sistema de detecção
"""

import subprocess
import time
from main import run_all_tests, show_failure_suggestions
from checks.gateway import ping_gateway, ping_dns
from checks.dns import test_dns
from checks.http import test_http
from alert.telegram import send_alert

def print_suggestions():
    """Mostra sugestões de ações para cada cenário de falha"""
    print("✅ Sugestões de ações para cada cenário:")
    print()
    print("🟢 Tudo funcionando (tudo ok)")
    print("   Ação: Nenhuma ação necessária")
    print("   Status: rede está operacional")
    print("   Log/Alerta: [INFO] Rede funcionando")
    print()
    print("🔴 Falha de Gateway")
    print("   Ação:")
    print("   • Verificar interface de rede (cabo/Wi-Fi)")
    print("   • Reiniciar interface de rede ou roteador")
    print("   Alerta: [ALERTA] Gateway não responde (problema interno)")
    print()
    print("🟡 Falha de DNS")
    print("   Ação:")
    print("   • Verificar configuração de DNS")
    print("   • Trocar para DNS público (ex: 8.8.8.8)")
    print("   Alerta: [ALERTA] DNS falhou")
    print()
    print("🟠 Falha de HTTP (internet indisponível)")
    print("   Ação:")
    print("   • Verificar conexão com provedor")
    print("   • Testar roteador ou reiniciar serviços de rede")
    print("   Alerta: [ALERTA] HTTP falhou")
    print()
    print("🔴 Falha múltipla (ex: DNS + HTTP)")
    print("   Ação:")
    print("   • Priorizar correção do Gateway se falhar")
    print("   • Depois corrigir DNS")
    print("   • Finalmente corrigir HTTP")
    print("   Alerta: [ALERTA] Gateway ou DNS falhou (seguir prioridade)")
    print()
    print("⏱️  Falha temporária / latência")
    print("   Ação:")
    print("   • Implementar timeout curto nos testes")
    print("   • Registrar log para análise futura")
    print("   Alerta: [INFO] Timeout ou lentidão detectada")
    print()
    print("🔄 Loop contínuo / teste de estabilidade")
    print("   Ação:")
    print("   • Monitorar histórico de alertas")
    print("   • Garantir que alertas repetidos não sobrecarreguem o sistema")
    print("   Alerta: [INFO] Falha detectada várias vezes consecutivas")
    print()
    print("💡 Resumo profissional:")
    print("   Gateway → DNS → HTTP (prioridade de diagnóstico)")
    print("   Registrar logs e alertas claros")
    print("   Corrigir primeiro os problemas mais críticos da rede interna, depois externos.")
    print()

def print_detection_flow():
    """Mostra como funciona o sistema de detecção"""
    print("⚙️ Como funciona o sistema de detecção:")
    print("📋 Exemplo de fluxo de identificação de problemas:")
    print("   • Gateway caiu → problema interno")
    print("   • Gateway ok + DNS falha → problema DNS")
    print("   • DNS ok + HTTP falha → problema internet")
    print("   • Tudo ok → rede funcionando perfeitamente")
    print()

def simulate_gateway_failure():
    """Simula falha do gateway forçando False no resultado."""
    print("🧪 Simulando falha do Gateway...")
    print("🎯 Problema esperado: Gateway caiu → problema interno")
    print("📋 Ação sugerida: Verificar interface de rede (cabo/Wi-Fi) e reiniciar roteador")
    
    # Criar uma versão modificada do run_all_tests com gateway False
    def run_with_gateway_failure():
        print("🔍 Verificando rede...\n")
        
        # Forçar gateway como False
        gateway_status = False
        dns_ping_status = ping_dns()
        dns_resolve_status = test_dns()
        http_status = test_http()
        
        # Mostrar resultados
        print(f"🌐 Gateway (192.168.1.1): {'✅ OK' if gateway_status else '❌ FALHOU'}")
        print(f"📍 DNS Ping (8.8.8.8): {'✅ OK' if dns_ping_status else '❌ FALHOU'}")
        print(f"🔎 DNS Resolve (google.com): {'✅ OK' if dns_resolve_status else '❌ FALHOU'}")
        print(f"🌍 HTTP (google.com): {'✅ OK' if http_status else '❌ FALHOU'}")
        print()
        
        # Enviar alerta
        send_alert("🚨 Gateway caiu → problema interno")
        show_failure_suggestions("gateway")
    
    run_with_gateway_failure()

def simulate_dns_failure():
    """Simula falha de DNS forçando False no resultado."""
    print("🧪 Simulando falha de DNS...")
    print("🎯 Problema esperado: Gateway ok + DNS falha → problema DNS")
    print("📋 Ação sugerida: Verificar configuração de DNS e trocar para DNS público (8.8.8.8)")
    
    # Criar versão modificada com DNS False
    def run_with_dns_failure():
        print("🔍 Verificando rede...\n")
        
        gateway_status = ping_gateway()
        dns_ping_status = False  # Forçado
        dns_resolve_status = test_dns()
        http_status = test_http()
        
        # Mostrar resultados
        print(f"🌐 Gateway (192.168.1.1): {'✅ OK' if gateway_status else '❌ FALHOU'}")
        print(f"📍 DNS Ping (8.8.8.8): {'✅ OK' if dns_ping_status else '❌ FALHOU'}")
        print(f"🔎 DNS Resolve (google.com): {'✅ OK' if dns_resolve_status else '❌ FALHOU'}")
        print(f"🌍 HTTP (google.com): {'✅ OK' if http_status else '❌ FALHOU'}")
        print()
        
        # Enviar alerta
        send_alert("🚨 Gateway ok + DNS Ping falha → problema DNS")
        show_failure_suggestions("dns")
    
    run_with_dns_failure()

def simulate_http_failure():
    """Simula falha HTTP forçando False no resultado."""
    print("🧪 Simulando falha HTTP...")
    print("🎯 Problema esperado: DNS ok + HTTP falha → problema internet")
    print("📋 Ação sugerida: Verificar conexão com provedor e testar/reiniciar roteador")
    
    # Criar versão modificada com HTTP False
    def run_with_http_failure():
        print("🔍 Verificando rede...\n")
        
        gateway_status = ping_gateway()
        dns_ping_status = ping_dns()
        dns_resolve_status = test_dns()
        http_status = False  # Forçado
        
        # Mostrar resultados
        print(f"🌐 Gateway (192.168.1.1): {'✅ OK' if gateway_status else '❌ FALHOU'}")
        print(f"📍 DNS Ping (8.8.8.8): {'✅ OK' if dns_ping_status else '❌ FALHOU'}")
        print(f"🔎 DNS Resolve (google.com): {'✅ OK' if dns_resolve_status else '❌ FALHOU'}")
        print(f"🌍 HTTP (google.com): {'✅ OK' if http_status else '❌ FALHOU'}")
        print()
        
        # Enviar alerta
        send_alert("🚨 DNS ok + HTTP falha → problema internet")
        show_failure_suggestions("http")
    
    run_with_http_failure()

if __name__ == "__main__":
    print("🚀 Iniciando testes de falha simulados...")
    print("🧪 Forçando falhas no código para testar detecção\n")
    
    # Mostrar como funciona o sistema
    print_detection_flow()
    print()
    
    # Mostrar sugestões de ações
    print_suggestions()
    print("="*80 + "\n")
    
    # Teste normal primeiro
    print("1️⃣ Teste normal (sem falhas):")
    print("🎯 Problema esperado: Tudo ok → rede funcionando perfeitamente")
    print("📋 Ação sugerida: Nenhuma ação necessária")
    run_all_tests()
    print("\n" + "="*50 + "\n")
    
    # Simular falhas
    print("2️⃣ Simulando falha de Gateway:")
    simulate_gateway_failure()
    print("\n" + "="*50 + "\n")
    
    print("3️⃣ Simulando falha de DNS:")
    simulate_dns_failure()
    print("\n" + "="*50 + "\n")
    
    print("4️⃣ Simulando falha HTTP:")
    simulate_http_failure()
    print("\n" + "="*50 + "\n")
    
    print("✅ Testes de falha concluídos!")
