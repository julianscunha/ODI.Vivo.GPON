---
tags: [gpon, odi, ssh, pre-requisitos]
created: 2026-10-12
---

# Pré-requisitos e acesso

Voltar: [[00 - Índice]] · Próximo: [[03 - Procedimento passo a passo]]

## Material

- ODI **DFP-34X-2C2** (chip **RTL9601D**), módulo SFP GPON.
- Media converter SFP → RJ45 (ou slot SFP no roteador/switch).
- PC com porta Ethernet e **Wireshark/tshark** (traz Npcap) e **Python 3 + Scapy** para testes.
- Acesso ao **HGU original** para extrair a identidade (dump OMCI/ME) — ver [[03 - Procedimento passo a passo#1. Coletar a identidade do HGU]].
- Fibra Vivo (ONU em O5 ao final do processo).
- Firmware `M110_sfp_ODI_220817.tar` com os hashes abaixo.

| Verificação | Valor |
|---|---|
| SHA-256 do `.tar` oficial | `B5E19FE71FAA9F46CC6FBE911A73046DC8217A637063E86AF785ED84CBE452C3` |
| MD5 do `.tar` | `8edd8fd6cca9a2b727e1773b4faa3bb9` |
| Versão interna | `V1.0-220817` |

## Rede do PC

- Adaptador Ethernet do PC com IP fixo **`192.168.1.10/24`** (ou `.2`), sem gateway.
- A ODI responde em **`192.168.1.1`**.

## SSH na ODI

O dropbear da ODI só oferece algoritmos antigos. Com OpenSSH moderno é preciso habilitá-los:

```sh
ssh -o KexAlgorithms=+diffie-hellman-group1-sha1 \
    -o HostKeyAlgorithms=+ssh-rsa \
    -o Ciphers=+aes128-cbc,3des-cbc \
    admin@192.168.1.1
```

Sem isso o erro é `no matching key exchange method found. Their offer: diffie-hellman-group1-sha1`. O telnet (porta 23) também responde.

> [!note] Shell da ODI
> O busybox é mínimo: **não** há `head`, `tail`, `wc`, `tr`, `which`. Use `ls -l` + `set -- $(...)` para tamanhos, `grep`, `cat`.

## Ferramentas úteis dentro da ODI

| Comando | Para quê |
|---|---|
| `omcicli mib get <ME>` | Ler uma Managed Entity (ex.: `7`, `45`, `47`, `171`) |
| `omcicli set logfile 3 0xffffffff` | Ligar log OMCI em `/var/tmp/omcilog` (raw+parsed) |
| `diag gpon get onu-state` | Estado O1…O7 |
| `diag gpon show counter flow 0` | Contadores GEM/Eth do fluxo upstream/downstream |
| `diag gpon show counter global ds-phy` | BIP/FEC/HEC (saúde da PON) |
| `nv getenv/setenv <var>` | Variáveis do bootloader (`sw_*`) |
| `flash get/set <var>` | Parâmetros persistentes do MIB (`OMCI_*`, `GPON_*`) |

Mais em [[07 - Referência de comandos]].
