#!/bin/bash
# Reiniciar serviço de rede COM SEGURANÇA

# ⚠️ AVISO: Esta operação pode derrubar conexão SSH
echo "WARNING: Reiniciando serviço de rede - PODE HAVER DESCONEXÃO"

# Verificar se estamos em sessão SSH
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "WARNING: Detectada sessão SSH - Risco de desconexão!"
    echo "INFO: Aguardando 10 segundos para possível cancelamento..."
    sleep 10
fi

# Verificar se systemctl está disponível
if command -v systemctl >/dev/null 2>&1; then
    # Systemd systems
    if systemctl restart NetworkManager; then
        echo "SUCCESS: NetworkManager reiniciado"
        exit 0
    else
        echo "ERRO: Falha ao reiniciar NetworkManager"
        exit 1
    fi
elif command -v service >/dev/null 2>&1; then
    # SysV init systems
    if service network-manager restart; then
        echo "SUCCESS: network-manager reiniciado"
        exit 0
    else
        echo "ERRO: Falha ao reiniciar network-manager"
        exit 1
    fi
else
    echo "ERRO: Nenhum gerenciador de serviço encontrado"
    exit 1
fi
