#!/bin/bash
# Backup do DNS com validação

BACKUP_FILE="/etc/resolv.conf.bkp"
SOURCE_FILE="/etc/resolv.conf"

# Verificar se arquivo original existe
if [ ! -f "$SOURCE_FILE" ]; then
    echo "ERRO: Arquivo $SOURCE_FILE não encontrado"
    exit 1
fi

# Criar backup
if cp "$SOURCE_FILE" "$BACKUP_FILE"; then
    echo "SUCCESS: Backup criado em $BACKUP_FILE"
    exit 0
else
    echo "ERRO: Falha ao criar backup"
    exit 1
fi
