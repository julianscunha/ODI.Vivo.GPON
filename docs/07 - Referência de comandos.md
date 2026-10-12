---
tags: [gpon, odi, comandos, referencia]
created: 2026-10-12
---

# Referência de comandos

Voltar: [[00 - Índice]]

## Estado da imagem e boot

```sh
cat /etc/version
for v in sw_active sw_commit sw_tryactive sw_valid0 sw_valid1 sw_version0 sw_version1 \
         sw_custom_version0 sw_custom_version1; do nv getenv $v; done
nv setenv <var> <valor>
```

Lógica do bootloader (`sw_tryactive=2`): `boot_by_commit` → `sw_commit==0 → b0 (Image 0)`, caso contrário `b1`. `set_act0/1` regravam `sw_active`.

## Parâmetros OMCI (persistentes)

```sh
flash get OMCI_OLT_MODE      # 3 = usa fix_sw_ver.sh
flash get OMCI_SW_VER1
flash get OMCI_SW_VER2
flash get GPON_SN
/etc/scripts/fix_sw_ver.sh   # aplica sw_custom_version0/1 em OMCI_SW_VER1/2
```

## OMCI

```sh
omcicli mib get 7      # Software Image
omcicli mib get 45     # MAC Bridge Service Profile
omcicli mib get 47     # MAC Bridge Port Config Data
omcicli mib get 84     # VLAN Tagging Filter Data
omcicli mib get 171    # Extended VLAN Tagging
omcicli mib get 256    # ONU-G
omcicli mib get 257    # ONU2-G
omcicli dump srvflow   # service flows instalados
omcicli dump conn
omcicli set logfile 3 0xffffffff
omcicli get logfile
```

Log em `/var/tmp/omcilog` (RAM).

## GPON / switch (`diag`)

```sh
diag gpon get onu-state
diag gpon show us-flow
diag gpon show counter flow 0
diag gpon show counter global ds-phy     # BIP / FEC / HEC
diag gpon show counter global ds-eth
diag gpon show counter global ds-gem
diag port get status port all            # velocidade/duplex dos links
```

> [!note] Sintaxe
> Em caso de dúvida use `?` no final: `diag gpon show counter global ?`.

## Firmware

```sh
sh /etc/scripts/fwu_starter.sh <0|1> /tmp/<arquivo>.tar
```

MTDs: `mtd4=k0`, `mtd5=r0`, `mtd6=k1`, `mtd7=r1`.

## Scripts incluídos

| Arquivo | Função |
|---|---|
| `scripts/odi-ssh.sh` | SSH com os algoritmos antigos; senha por `SSH_ASKPASS` (não fica gravada) |
| `scripts/padi_test.py` | PADI em VLAN 10 / sem tag; só detecta PADO |
| `scripts/pppoe_auth_test.py` | PPPoE completo até PAP/CHAP, IPCP e PADT |
| `scripts/vivo-pppoe-vlan1335.ps1` | vNIC Hyper-V com VLAN 1335 + conexão PPPoE no Windows |

> [!warning] Scapy no Windows
> `padi_test.py` e `pppoe_auth_test.py` assumem um adaptador chamado **Local**; ajuste o nome. Precisam do Npcap (vem com o Wireshark).
