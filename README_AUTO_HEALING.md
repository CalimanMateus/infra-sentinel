# 🤖 Sistema de Auto-Healing

Sistema inteligente de recuperação automática de falhas de rede com backup e rollback seguro.

## 🏗️ Estrutura

```
auto_healing/
├── __init__.py          # Módulo principal
├── healer.py           # Cérebro do sistema
├── backup.py           # Sistema de backup
├── rollback.py         # Sistema de rollback
├── logger.py          # Logs profissionais
└── actions/           # Scripts bash
    ├── backup_dns.sh
    ├── change_dns.sh
    ├── rollback_dns.sh
    └── restart_network.sh

logs/
└── healing.log        # Logs de operações
```

## 🚀 Como Usar

### 1. Diagnóstico Único
```bash
python main.py
```

### 2. Monitoramento Contínuo
```bash
python continuous_monitor.py
# Intervalo personalizado
python continuous_monitor.py --interval 60
```

## 🛠️ Funcionalidades

### Auto-Healing DNS
- ✅ Backup automático do `/etc/resolv.conf`
- ✅ Alteração para DNS Google (8.8.8.8)
- ✅ Rollback automático em caso de falha
- ✅ Reinício do serviço de rede

### Auto-Healing Gateway
- ✅ Reinício do serviço NetworkManager
- ✅ Suporte para systemd e SysV init

### Auto-Healing HTTP
- ✅ Reinício da rede (problemas de roteamento)
- ✅ Validação de conectividade

## 📊 Logs

Todos os eventos são registrados em `logs/healing.log`:

```
[2026-03-24 12:00:00] [INFO] Iniciando auto-healing para: dns
[2026-03-24 12:00:01] [SUCCESS] Backup DNS executado: SUCCESS: Backup criado em /etc/resolv.conf.bkp
[2026-03-24 12:00:02] [SUCCESS] DNS alterado: SUCCESS: DNS alterado para 8.8.8.8
[2026-03-24 12:00:03] [SUCCESS] Rede reiniciada: SUCCESS: NetworkManager reiniciado
[2026-03-24 12:00:08] [SUCCESS] Auto-healing DNS concluído com sucesso
```

## 🔧 Configuração

### Permissões
```bash
chmod +x auto_healing/actions/*.sh
```

### Requisitos
- Python 3.6+
- Acesso sudo para scripts bash
- Systemd ou SysV init

## 🚨 Segurança

- ✅ Backup automático antes de qualquer alteração
- ✅ Rollback automático em caso de falha
- ✅ Logs detalhados de todas as operações
- ✅ Validação de arquivos antes de operações
- ✅ Timeout em execuções para evitar deadlocks

## 🔄 Fluxo de Healing

1. **Detecção** → Falha identificada pelo sistema
2. **Backup** → Estado atual salvo
3. **Correção** → Tentativa de reparo automático
4. **Validação** → Verificação se funcionou
5. **Rollback** → Se falhou, restaura backup
6. **Log** → Tudo registrado profissionalmente

## 📈 Expansão

O sistema foi projetado para ser facilmente extensível:

```python
# Adicionar novo tipo de healing
def _heal_mysql(self):
    """Auto-healing para MySQL"""
    # Implementar lógica específica
    pass

# Adicionar ao healer.py
def heal(problem: str):
    if problem == "mysql":
        return self._heal_mysql()
```

## 🆘 Troubleshooting

### Scripts não executam
```bash
chmod +x auto_healing/actions/*.sh
```

### Permissões negadas
```bash
sudo python main.py
# ou
sudo python continuous_monitor.py
```

### Logs não aparecem
Verifique se o diretório `logs/` existe e tem permissão de escrita.

## 📞 Suporte

Em caso de problemas, verifique:
1. Logs em `logs/healing.log`
2. Permissões dos scripts bash
3. Acesso sudo para operações de sistema
