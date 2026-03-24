#!/bin/bash
# Restaurar DNS do backup

BACKUP_FILE="/etc/resolv.conf.bkp"
DNS_FILE="/etc/resolv.conf"

# Verificar se backup existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERRO: Backup $BACKUP_FILE não encontrado"
    exit 1
fi

# Restaurar backup
if cp "$BACKUP_FILE" "$DNS_FILE"; then
    echo "SUCCESS: DNS restaurado do backup"
    exit 0
else
    echo "ERRO: Falha ao restaurar backup"
    exit 1
fi
