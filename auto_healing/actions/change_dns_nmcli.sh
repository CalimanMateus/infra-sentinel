#!/bin/bash
# Alterar DNS usando nmcli (persistente contra NetworkManager)

DNS_SERVERS="8.8.8.8 8.8.4.4"
CONNECTION_NAME=$(nmcli -t -f NAME connection show --active | head -1)

# Verificar se nmcli está disponível
if ! command -v nmcli &> /dev/null; then
    echo "ERRO: nmcli não encontrado. Usando método fallback."
    # Fallback para método tradicional
    DNS_FILE="/etc/resolv.conf"
    DNS_CONFIG="nameserver 8.8.8.8\nnameserver 8.8.4.4"
    
    if [ ! -f "$DNS_FILE" ]; then
        echo "ERRO: Arquivo $DNS_FILE não encontrado"
        exit 1
    fi
    
    if echo -e "$DNS_CONFIG" > "$DNS_FILE"; then
        echo "SUCCESS: DNS alterado (fallback)"
        exit 0
    else
        echo "ERRO: Falha ao alterar DNS (fallback)"
        exit 1
    fi
fi

# Verificar se existe conexão ativa
if [ -z "$CONNECTION_NAME" ]; then
    echo "ERRO: Nenhuma conexão ativa encontrada"
    exit 1
fi

# Alterar DNS usando nmcli (método preferido)
if nmcli connection modify "$CONNECTION_NAME" ipv4.dns "$DNS_SERVERS" && \
   nmcli connection modify "$CONNECTION_NAME" ipv4.ignore-auto-dns yes && \
   nmcli connection up "$CONNECTION_NAME"; then
    echo "SUCCESS: DNS alterado via nmcli para $DNS_SERVERS"
    exit 0
else
    echo "ERRO: Falha ao alterar DNS via nmcli"
    exit 1
fi
