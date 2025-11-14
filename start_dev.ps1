# =========================================================
# Script de desenvolvimento: ativa venv, inicia PostgreSQL portátil, roda Django
# =========================================================

# --- Configurações ---
$projectPath = "C:\Users\DEV-T-2025\Downloads\Luiz\La-Belle-Bijou"
$venvPath = "$projectPath\venv\Scripts\Activate.ps1"
$pgsqlBin = "C:\Users\DEV-T-2025\postgres\pgsql\bin"
$pgsqlData = "C:\Users\DEV-T-2025\postgres\data"
$pgsqlPort = 5433

# --- Função para checar se porta está ocupada ---
function Test-Port {
    param([int]$Port)
    $tcp = New-Object System.Net.Sockets.TcpClient
    try {
        $tcp.Connect("localhost", $Port)
        $tcp.Close()
        return $true
    } catch {
        return $false
    }
}

# --- 1. Ativa o ambiente virtual ---
Write-Host "Ativando ambiente virtual..."
. $venvPath

# --- 2. Inicia PostgreSQL se necessário ---
if (Test-Port -Port $pgsqlPort) {
    Write-Host "PostgreSQL já está rodando na porta $pgsqlPort."
} else {
    Write-Host "Iniciando PostgreSQL portátil na porta $pgsqlPort..."
    cd $pgsqlBin
    .\pg_ctl -D $pgsqlData -o "-p $pgsqlPort" start
    # Aguarda o servidor subir
    Start-Sleep -Seconds 2
    Write-Host "PostgreSQL iniciado com sucesso!"
}

# --- 3. Rodar Django runserver ---
Write-Host "Iniciando Django runserver..."
cd $projectPath
py manage.py runserver
