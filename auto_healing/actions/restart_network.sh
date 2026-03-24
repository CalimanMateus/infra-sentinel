#!/bin/bash
# Reiniciar serviço de rede

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
