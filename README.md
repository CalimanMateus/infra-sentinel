# 🚀 Infra Sentinel — Intelligent Network Monitoring & Auto-Healing

Um sistema modular e inteligente de **monitoramento, diagnóstico e auto-correção de rede**, desenvolvido com foco em automação, confiabilidade e observabilidade.

---

## 🧠 Visão Geral

O **Infra Sentinel** é dividido em dois pilares principais:

### 🧪 Projeto 1 — Diagnóstico de Rede Inteligente

Responsável por detectar falhas com precisão.

### ⚙️ Projeto 2 — Auto-Healing Network

Responsável por corrigir automaticamente os problemas detectados.

👉 Juntos, formam um sistema completo:
**Detecção → Análise → Correção automática → Observabilidade**

---

## 🏗 Arquitetura do Projeto

```
infra-sentinel/
 ├── main.py
 ├── diagnostics/
 │    ├── gateway.py
 │    ├── dns.py
 │    └── http.py
 ├── auto_healing/
 │    ├── healer.py
 │    ├── backup.py
 │    ├── rollback.py
 │    └── actions/
 │         ├── backup_dns.sh
 │         ├── change_dns.sh
 │         ├── rollback_dns.sh
 │         └── restart_network.sh
 ├── logs/
 └── config.json
```

---

## 🔍 Funcionalidades

### 📡 Diagnóstico Inteligente

* 🌐 Teste de Gateway (conectividade local)
* 🛡 Teste de DNS (resolução de nomes)
* 📡 Teste de HTTP (acesso à internet)
* 🧠 Identificação exata da origem da falha

---

### ⚙️ Auto-Healing (Correção Automática)

* 🔄 Reinício de interface de rede
* 🌐 Alteração automática de DNS
* 🔁 Reinício de serviços HTTP
* 🧠 Decisão automática baseada no erro detectado

---

### 🛡 Segurança e Confiabilidade

* 💾 Backup automático antes de alterações críticas
* ♻️ Rollback automático em caso de falha
* 🧪 Execução segura (evita quebrar o ambiente)
* 🕒 Possibilidade de versionamento com timestamp

---

### 📊 Observabilidade

* 📜 Logs estruturados e detalhados
* 🧠 Rastreamento completo de ações
* 🔍 Histórico de falhas e correções

Exemplo de log:

```
[2026-03-24 12:00:00] [INFO] DNS falhou → iniciando correção
[2026-03-24 12:00:01] [SUCCESS] DNS corrigido
[2026-03-24 12:00:02] [ERROR] Falha → rollback executado
```

---

## 🔗 Integração dos Projetos

O sistema funciona de forma contínua:

```
Diagnóstico → Identificação → Auto-Healing → Log
```

* O módulo de diagnóstico detecta falhas
* O módulo de auto-healing executa ações corretivas
* Todo o processo é registrado

---

## 🛠 Tecnologias Utilizadas

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python\&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-Scripting-black?logo=gnubash\&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-orange?logo=linux\&logoColor=white)
![Systemd](https://img.shields.io/badge/Systemd-Service%20Manager-red)
![Networking](https://img.shields.io/badge/Networking-DNS%20%7C%20HTTP%20%7C%20Gateway-blueviolet)
![DevOps](https://img.shields.io/badge/DevOps-Automation-green)
![SRE](https://img.shields.io/badge/SRE-Reliability-critical)
![Logs](https://img.shields.io/badge/Logging-Observability-yellow)

---

## 🔁 Execução

### ▶️ Rodar manualmente

```
python3 main.py
```

---

### 🔄 Execução contínua (loop)

```python
while True:
    run()
    time.sleep(30)
```

---

### ⏰ Via cron

```
*/1 * * * * python3 /caminho/main.py
```

---

## 🚧 Próximos Passos

* 📊 Dashboard de monitoramento
* 🛡 Implementação de Firewall / IDS (Projeto 3)
* ☁️ Deploy em ambiente real

---

## 🎯 Objetivo do Projeto

Construir uma solução completa de:

* Monitoramento de rede
* Diagnóstico inteligente
* Auto-recuperação automática
* Observabilidade e rastreabilidade

---

## 📌 Status

🚧 Em desenvolvimento contínuo
✅ Diagnóstico implementado
✅ Auto-healing com backup e rollback implementado
🔜 Alertas e expansão de funcionalidades

---

## 👨‍💻 Autor

Desenvolvido por Mateus Araujo
