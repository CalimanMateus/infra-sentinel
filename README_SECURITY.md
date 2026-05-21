# 🛡️ Projeto 3: Camada de Segurança (Firewall + IDS)

## 📋 Visão Geral

Este módulo implementa uma camada de segurança completa para o **Infra Sentinel**, incluindo:

- **IDS (Intrusion Detection System)** baseado em logs do Suricata
- **Firewall Manager** com controle via iptables
- **Parser avançado** para extração de informações de ataques
- **Rate limiting** para evitar spam de alertas
- **Bloqueio automático** de IPs maliciosos (opcional)

## 🏗️ Arquitetura

```
infra-sentinel/
├── security/
│   ├── __init__.py          # Módulo de segurança
│   ├── ids.py               # Sistema de Detecção de Intrusão
│   ├── firewall.py          # Gerenciador de Firewall
│   ├── parser.py            # Parser de Logs do Suricata
│   └── config.py            # Configurações do Sistema
├── logs/
│   └── security.log         # Log específico de segurança
├── main.py                  # Integração com sistema principal
└── test_security.py         # Suite de testes
```

## 🔧 Funcionalidades

### 1. IDS (Intrusion Detection System)

**Arquivo:** `security/ids.py`

**Funções principais:**
- `check_intrusions()` - Verifica atividades suspeitas
- `IntrusionDetector` - Classe com cache e rate limiting
- Detecção de padrões: SCAN, Nmap, DDoS, malware

**Características:**
- ✅ Leitura segura de arquivos de log
- ✅ Rate limiting para evitar falsos positivos
- ✅ Cache de alertas por IP
- ✅ Análise das entradas mais recentes

### 2. Firewall Manager

**Arquivo:** `security/firewall.py`

**Funções principais:**
- `block_ip(ip)` - Bloqueia IP via iptables
- `is_ip_blocked(ip)` - Verifica se IP está bloqueado
- `unblock_ip(ip)` - Remove bloqueio de IP
- `get_blocked_ips()` - Lista todos IPs bloqueados

**Características:**
- ✅ Validação rigorosa de endereços IP
- ✅ Whitelist de redes confiáveis
- ✅ Cache de regras para performance
- ✅ Prevenção de bloqueios duplicados

### 3. Parser de Logs

**Arquivo:** `security/parser.py`

**Funções principais:**
- `parse_suricata_line(line)` - Parser principal
- `validate_ip(ip)` - Validação de IPs
- `detect_attack_type(line)` - Identifica tipo de ataque
- `prioritize_source_ip(ips)` - Seleciona IP para bloqueio

**Extrações:**
- ✅ Timestamp do evento
- ✅ IPs de origem e destino
- ✅ Portas envolvidas
- ✅ Tipo e severidade do ataque
- ✅ Classificação (ET, GPL, etc.)

### 4. Configurações

**Arquivo:** `security/config.py`

**Configurações principais:**
```python
AUTO_BLOCK = False                    # Bloqueio automático (default seguro)
LOG_FILE = "/var/log/suricata/fast.log"  # Arquivo de log do Suricata
MAX_ALERTS_PER_HOUR = 10              # Rate limiting
ALERT_COOLDOWN = 360                  # Cooldown por IP (segundos)
```

**Variáveis de ambiente:**
- `SECURITY_AUTO_BLOCK` - Override para AUTO_BLOCK
- `SURICATA_LOG_FILE` - Override para LOG_FILE
- `MAX_ALERTS_PER_HOUR` - Override para rate limiting

## 🚀 Integração com main.py

O sistema de segurança é integrado ao fluxo principal:

```python
# Imports adicionados
from security.ids import check_intrusions
from security.firewall import block_ip
from security.config import AUTO_BLOCK

# Nova função de segurança
def run_security_checks():
    intrusion = check_intrusions()
    
    if intrusion["detected"]:
        send_alert(f"🚨 Ataque detectado: {intrusion['type']}")
        
        if AUTO_BLOCK and intrusion.get("ip"):
            block_ip(intrusion["ip"])

# Execução no fluxo principal
if __name__ == "__main__":
    run_all_tests()      # Diagnóstico + Auto-healing
    run_security_checks()  # Segurança
```

## 🧪 Testes

**Arquivo:** `test_security.py`

**Testes implementados:**
- ✅ Parser de logs
- ✅ Detecção de intrusões
- ✅ Validação de firewall
- ✅ Configurações

**Execução:**
```bash
python test_security.py
```

## 📊 Fluxo Completo

```
1. Diagnóstico de Rede
   ├── Gateway ✅/❌
   ├── DNS ✅/❌
   └── HTTP ✅/❌

2. Auto-healing (se necessário)
   ├── Backup de configurações
   ├── Aplicação de correções
   └── Rollback se falhar

3. Segurança
   ├── Análise de logs do Suricata
   ├── Detecção de padrões suspeitos
   ├── Envio de alertas
   └── Bloqueio automático (se habilitado)

4. Alertas
   ├── Telegram (configurado)
   ├── Logs locais
   └── Console
```

## ⚙️ Configuração do Suricata

Para uso em produção, configure o Suricata:

```bash
# Instalação (Ubuntu/Debian)
sudo apt update
sudo apt install suricata

# Configurar arquivo de log
sudo nano /etc/suricata/suricata.yaml

# Habilitar fast.log
- fast:
    enabled: yes
    filename: fast.log
    append: yes

# Iniciar serviço
sudo systemctl start suricata
sudo systemctl enable suricata
```

## 🔒 Boas Práticas de Segurança

### 1. Configuração Inicial
```python
# Mantenha AUTO_BLOCK=False inicialmente
AUTO_BLOCK = False

# Monitore alertas antes de habilitar bloqueio
# Verifique falsos positivos
```

### 2. Whitelist de IPs
```python
# Configure redes confiáveis em config.py
TRUSTED_IPS = [
    "127.0.0.1",
    "192.168.0.0/16",  # Sua rede local
    "10.0.0.0/8"
]
```

### 3. Rate Limiting
```python
# Evite spam de alertas
MAX_ALERTS_PER_HOUR = 10
ALERT_COOLDOWN = 360  # 6 minutos por IP
```

## 🚨 Tipos de Ataques Detectados

| Tipo | Padrões | Severidade |
|------|---------|------------|
| `port_scan` | SCAN, ET SCAN, Nmap | Medium |
| `possible_attack` | Possible Attack | High |
| `ddos` | DDoS, flood, amplification | Critical |
| `malware` | malware, trojan, exploit | Critical |

## 📈 Monitoramento e Logs

### Logs de Segurança
- **Local:** `logs/security.log`
- **Formato:** Timestamp - Nível - Mensagem
- **Rotation:** 10MB máximo

### Métricas Monitoradas
- ✅ Tentativas de bloqueio
- ✅ IPs bloqueados ativos
- ✅ Taxa de falsos positivos
- ✅ Performance do parser

## 🔄 Rate Limiting

O sistema implementa múltiplas camadas de rate limiting:

1. **Por Hora:** Máximo de alertas configurado
2. **Por IP:** Cooldown entre alertas do mesmo IP
3. **Cache:** Cache de IPs bloqueados para performance

## 🛠️ Solução de Problemas

### Problemas Comuns

**1. "Arquivo de log não encontrado"**
```bash
# Verifique se o Suricata está rodando
sudo systemctl status suricata

# Verifique caminho do log
sudo find /var/log -name "fast.log" 2>/dev/null
```

**2. "Sem permissão para ler arquivo"**
```bash
# Adicione usuário ao grupo suricata
sudo usermod -a -G suricata $USER

# Ou ajuste permissões
sudo chmod 644 /var/log/suricata/fast.log
```

**3. "iptables command not found"**
```bash
# Instale iptables
sudo apt update
sudo apt install iptables

# Verifique se está no PATH
which iptables
```

## 🎯 Próximos Passos

### Implementações Futuras

1. **Machine Learning** para classificação de ataques
2. **Integração com SIEM** (Splunk, ELK)
3. **Dashboard web** para visualização
4. **API REST** para gestão remota
5. **Correlação de eventos** múltiplas fontes

### Extensões Possíveis

- **Honeypots** para atrair atacantes
- **Threat Intelligence** feeds
- **Análise de comportamento** (behavioral analysis)
- **Integração com Shodan** para reconhecimento

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique os logs em `logs/security.log`
2. Execute `test_security.py` para validação
3. Revise configurações em `security/config.py`
4. Consulte documentação do Suricata

---

**Desenvolvido por:** Infra Sentinel Security Team  
**Versão:** 1.0.0  
**Status:** ✅ Produção Ready
