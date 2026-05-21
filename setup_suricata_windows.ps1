# Script de Instalação do Suricata para Windows
# Para ambiente de teste do Infra Sentinel

Write-Host "🔧 Configurando ambiente de teste do Suricata..." -ForegroundColor Yellow

# Verifica se está rodando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Execute este script como Administrador!" -ForegroundColor Red
    exit 1
}

# Instala Chocolatey se não existir
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Instalando Chocolatey..." -ForegroundColor Blue
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Instala dependências
Write-Host "📦 Instalando dependências..." -ForegroundColor Blue
choco install -y python3 git visualstudio2019buildtools

# Baixa Suricata para Windows
Write-Host "⬇️ Baixando Suricata..." -ForegroundColor Blue
$suricataUrl = "https://github.com/OISF/suricata/releases/download/suricata-6.0.8/suricata-6.0.8.zip"
$ outputPath = "C:\suricata"

if (!(Test-Path $outputPath)) {
    New-Item -ItemType Directory -Path $outputPath -Force
}

Invoke-WebRequest -Uri $suricataUrl -OutFile "$outputPath\suricata.zip"
Expand-Archive -Path "$outputPath\suricata.zip" -DestinationPath $outputPath -Force

# Cria diretório de logs
$logDir = "C:\suricata\logs"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force
}

# Cria arquivo de configuração básico
$configContent = @"
# Configuração básica do Suricata para teste
%YAML 1.1

# Configurações de log
outputs:
  - fast:
      enabled: yes
      filename: fast.log
      append: yes
  - eve-log:
      enabled: yes
      type: file
      filename: eve.json
  - stats:
      enabled: yes
      filename: stats.log

# Configurações da rede
af-packet:
  - interface: "Ethernet"
    cluster-id: 99
    cluster-type: cluster_flow

# Regras de detecção
default-rule-path: "C:\suricata\rules"
rule-files:
  - "suricata.rules"
"@

Set-Content -Path "$outputPath\suricata.yaml" -Value $configContent

# Cria regra de teste para detecção de port scan
$ruleContent = @"
# Regras de teste para Infra Sentinel
# Detecta port scans
alert tcp any any -> $env:COMPUTERNAME any (msg:"ET SCAN Potential Port Scan Detected"; flags:S; threshold:type both, track by_src, count 10, seconds 2; sid:1000001; rev:1;)

# Detecta Nmap
alert tcp any any -> $env:COMPUTERNAME any (msg:"Nmap Scan Detected"; content:"|4D 50 52 51|"; depth:4; offset:0; sid:1000002; rev:1;)

# Detecta atividade suspeita
alert ip any any -> $env:COMPUTERNAME any (msg:"Possible Attack Detected"; threshold:type both, track by_src, count 50, seconds 10; sid:1000003; rev:1;)
"@

$rulesDir = "$outputPath\rules"
if (!(Test-Path $rulesDir)) {
    New-Item -ItemType Directory -Path $rulesDir -Force
}

Set-Content -Path "$rulesDir\suricata.rules" -Value $ruleContent

# Cria script de inicialização
$startScript = @"
@echo off
echo Iniciando Suricata em modo de teste...
cd /d C:\suricata
suricata.exe -c suricata.yaml -i Ethernet -l logs
pause
"@

Set-Content -Path "$outputPath\start_suricata.bat" -Value $startScript

Write-Host "✅ Suricata configurado!" -ForegroundColor Green
Write-Host "📍 Diretório: C:\suricata" -ForegroundColor Blue
Write-Host "🚀 Para iniciar: C:\suricata\start_suricata.bat" -ForegroundColor Blue
Write-Host "📋 Logs serão salvos em: C:\suricata\logs" -ForegroundColor Blue
