# Cria um vNIC Hyper-V com VLAN 1335 sobre a placa "Local" e uma conexao PPPoE "Vivo".
# Executar como Administrador:  powershell -ExecutionPolicy Bypass -File .\vivo-pppoe-vlan1335.ps1
# Uso: sem argumento cria e conecta; -Remove desfaz tudo.
param(
    [string]$Adapter = 'Local',
    [int]$Vlan = 1335,
    [string]$User = 'cliente@cliente',
    [string]$Pass = 'cliente',
    [switch]$Remove
)
$ErrorActionPreference = 'Stop'
$sw = 'VivoSW'; $nic = "Vivo$Vlan"; $conn = 'Vivo'

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Execute como Administrador.'
}

if ($Remove) {
    rasdial $conn /disconnect 2>$null | Out-Null
    Get-VMNetworkAdapter -ManagementOS -Name $nic -ErrorAction SilentlyContinue | Remove-VMNetworkAdapter
    Get-VMSwitch -Name $sw -ErrorAction SilentlyContinue | Remove-VMSwitch -Force
    $pbk = "$env:APPDATA\Microsoft\Network\Connections\Pbk\rasphone.pbk"
    if (Test-Path $pbk) { (Get-Content $pbk -Raw) -replace "(?ms)^\[$conn\].*?(?=^\[|\z)", '' | Set-Content $pbk -Encoding ASCII }
    'Removido.'; return
}

# 1) switch externo; o host mantem o IP (192.168.1.x) em vEthernet ($sw), sem tag, para acessar a ODI
if (-not (Get-VMSwitch -Name $sw -ErrorAction SilentlyContinue)) {
    New-VMSwitch -Name $sw -NetAdapterName $Adapter -AllowManagementOS $true | Out-Null
}

# 2) vNIC do host marcado com a VLAN (e so ele)
if (-not (Get-VMNetworkAdapter -ManagementOS -Name $nic -ErrorAction SilentlyContinue)) {
    Add-VMNetworkAdapter -ManagementOS -Name $nic -SwitchName $sw | Out-Null
}
Set-VMNetworkAdapterVlan -ManagementOS -VMNetworkAdapterName $nic -Access -VlanId $Vlan

# 3) conexao PPPoE de banda larga (o Windows envia o PADI em todos os vNICs; so o da VLAN recebe PADO)
$pbkDir = "$env:APPDATA\Microsoft\Network\Connections\Pbk"
New-Item -ItemType Directory -Force $pbkDir | Out-Null
$pbk = "$pbkDir\rasphone.pbk"
if (-not (Test-Path $pbk) -or -not (Select-String -Path $pbk -Pattern "^\[$conn\]" -Quiet)) {
@"

[$conn]
Encoding=1
PBVersion=4
Type=5
AutoLogon=0
UseRasCredentials=1
DialParamsUID=0
Guid=$([guid]::NewGuid().ToString('N').ToUpper())
VpnStrategy=0
ExcludedProtocols=0
LcpExtensions=1
DataEncryption=8
SwCompression=0
NegotiateMultilinkAlways=0
DialMode=1
IdleDisconnectSeconds=0
RedialOnLinkFailure=1
IpPrioritizeRemote=1
IpAssignment=1
IpNameAssign=1
Ipv6Assign=1
PreferredPort=PPPoE0-0
PreferredDevice=WAN Miniport (PPPOE)

MEDIA=PPPoE
Port=PPPoE0-0
Device=WAN Miniport (PPPOE)

DEVICE=PPPoE
PhoneNumber=
"@ | Add-Content -Path $pbk -Encoding ASCII
}

# 4) conecta
rasdial $conn $User $Pass
ipconfig | Select-String -Context 0,6 $conn
