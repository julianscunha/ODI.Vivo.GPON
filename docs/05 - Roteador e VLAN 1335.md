---
tags: [gpon, vivo, vlan, pppoe, roteador]
created: 2026-10-12
---

# Roteador e VLAN 1335

Voltar: [[00 - Índice]] · Anterior: [[04 - Validação e testes]] · Próximo: [[06 - Armadilhas e troubleshooting]]

## Regra principal

A ODI atua como **bridge**. O dispositivo ligado a ela precisa enviar o PPPoE **marcado com VLAN 1335** (tag 802.1Q). PPPoE sem tag ou com VLAN 10 **não** gera PADO nesta ODI.

> [!info] Por que no HGU funcionava com VLAN 10
> O HGU converte 10 → 1335 internamente. Na ODI a regra aparece no ME171 mas, na prática, só quadros já em 1335 chegam ao fluxo upstream.

## Parâmetros PPPoE

| Campo | Valor |
|---|---|
| VLAN ID | **1335** |
| Usuário | `cliente@cliente` |
| Senha | `cliente` |
| Autenticação | PAP (aceita; CHAP também implementado nos testes) |
| MTU/MRU | 1492 |
| Concentrador observado | `i-br-sp-srr-ncn-hl4-01` (SP) |

> [!note]
> `cliente@cliente`/`cliente` é o padrão da Vivo para PPPoE; algumas contas usam credenciais próprias. Os valores reais da sua conta é que valem.

## Roteadores/switches

Qualquer equipamento com WAN/porta com VLAN tagueada serve (ER7206, Mikrotik, OpenWrt, pfSense…). Esquema:

1. Interface/porta ligada à ODI com **VLAN 1335 tagueada** (WAN).
2. Sobre a VLAN 1335, criar a WAN **PPPoE** com usuário/senha.
3. NAT/DHCP normais na LAN.

## Teste no PC Windows (sem roteador)

O driver Realtek do PC não permite fixar VLAN ID pela interface padrão. Use Hyper-V para criar um vNIC com a tag. O script `scripts/vivo-pppoe-vlan1335.ps1`:

1. cria o switch externo `VivoSW` sobre a placa que liga à ODI (o host mantém `192.168.1.x` sem tag);
2. cria o vNIC `Vivo1335` com **VLAN 1335**;
3. cria a conexão PPPoE `Vivo` e conecta (`rasdial`).

```powershell
# como Administrador
powershell -ExecutionPolicy Bypass -File .\vivo-pppoe-vlan1335.ps1
powershell -ExecutionPolicy Bypass -File .\vivo-pppoe-vlan1335.ps1 -Remove
```

> [!warning] Detalhes do script
> - Ao criar o switch, a rede da placa cai por alguns segundos.
> - Em Windows em português, `IsInRole('Administrator')` falha; o script usa `[WindowsBuiltInRole]::Administrator`.
> - Essa conexão sai pelo PPPoE do Windows em software, então a vazão pode ficar abaixo do que a ODI entrega com um roteador de verdade.
