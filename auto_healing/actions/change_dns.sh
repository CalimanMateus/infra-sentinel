#!/bin/bash
# Alterar DNS para Google DNS (8.8.8.8)

DNS_FILE="/etc/resolv.conf"
DNS_SERVERS="nameserver 8.8.8.8\nnameserver 8.8.4.4"

# Verificar se arquivo existe
if [ ! -f "$DNS_FILE" ]; then
    echo "ERRO: Arquivo $DNS_FILE não encontrado"
    exit 1
fi

# Backup automático antes de alterar
cp "$DNS_FILE" "$DNS_FILE.auto.bkp"

# Alterar DNS
if echo -e "$DNS_SERVERS" > "$DNS_FILE"; then
    echo "SUCCESS: DNS alterado para 8.8.8.8"
    exit 0
else
    echo "ERRO: Falha ao alterar DNS"
    exit 1
fi
