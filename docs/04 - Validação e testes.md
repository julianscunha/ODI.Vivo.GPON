---
tags: [gpon, odi, validacao, pppoe, omci]
created: 2026-10-12
---

# Validação e testes

Voltar: [[00 - Índice]] · Anterior: [[03 - Procedimento passo a passo]] · Próximo: [[05 - Roteador e VLAN 1335]]

## Checklist de saúde (todos devem passar)

| # | Teste | Como | Esperado |
|---|---|---|---|
| 1 | Estado GPON | `diag gpon get onu-state` | `Operation State(O5)` |
| 2 | Versões OMCI | `flash get OMCI_SW_VER1` / `OMCI_SW_VER2` | `100WVK0b1` / `200WVK0b1` |
| 3 | ME7 | `omcicli mib get 7` | Valid=1 nas duas imagens |
| 4 | Bridge criada | `omcicli mib get 45`, `47` | **não vazios** |
| 5 | Regra VLAN | `omcicli mib get 171` | tem regra `VID 10 → 1335` |
| 6 | Sem download de software | log OMCI | sem `StartSwDownload`/`ActivateSw` |
| 7 | PON limpa | `diag gpon show counter global ds-phy` | BIP/FEC/HEC = 0 |
| 8 | Sem reboot espontâneo | `cat /proc/uptime` | só cresce |
| 9 | PADO | PADI em VLAN **1335** | PADO do BNG |
| 10 | Autenticação | PPPoE PAP | `Authentication success` |

## Log OMCI

```sh
omcicli set logfile 3 0xffffffff    # arquivo /var/tmp/omcilog (RAM; some no reboot)
```

O arquivo é hex cru. Formato de cada quadro: `TCI(2) MsgType(1) DevID(1) ME class(2) ME inst(2) …`. `MsgType & 0x1f`:

| Código | Mensagem |
|---|---|
| 4 / 6 / 8 / 9 | Create / Delete / Set / Get |
| 13 / 14 | MIB Upload / Upload Next |
| 17 | AVC |
| 19 / 20 / 21 | StartSwDownload / DownloadSection / EndSwDownload |
| 22 / 23 | **ActivateSw / CommitSw** |
| 25 | **Reboot** |

Bit `0x20` = AK (resposta), `0x40` = AR.

Na captura de referência (não publicada por conter identificadores) havia 801 `MIBUploadNext`, 24 `Create`, 28 `Set` e **zero** mensagens 19–25.

## Medir o caminho real (upstream)

O encaminhamento é por hardware; `ifconfig`/`/proc/net/dev` não mostram. Use:

```sh
diag gpon show counter flow 0     # U/S Eth packets, U/S GEM counts (zeram ao ler)
```

Se o PADI com VID 10 **não** incrementa o U/S e o com 1335 incrementa, a regra de tradução não está em hardware. Foi exatamente o caso; ver [[05 - Roteador e VLAN 1335]].

## Teste PPPoE sem roteador

Scripts em `scripts/`:

- `padi_test.py` — envia PADI (VLAN 10/1335/sem tag) e espera PADO.
- `pppoe_auth_test.py` — PADI/PADR/PADS, LCP, **PAP/CHAP**, IPCP, e PADT ao final.

```sh
python pppoe_auth_test.py cliente@cliente cliente
```

Saída esperada:

```
PADO AC-Name i-br-sp-srr-ncn-hl4-01
PADS sessao <id>
LCP conf-req do servidor, auth= 0xc023
PAP resposta ACK Authentication success,Welcome!
IPCP code 1 ...
RESULTADO PAP-ACK
```

Para capturar com Wireshark/tshark use o filtro `pppoed` e conferir o campo `vlan.id`. O nome da interface Npcap é a da placa ligada à ODI.

## Desempenho (referência medida)

Plano 600 Mb, PC por cabo, PPPoE do Windows sobre vNIC Hyper-V com VLAN 1335, servidor Cloudflare GRU (9 ms):

| Download | 1 fluxo | 4 fluxos | 6 fluxos |
|---|---|---|---|
| Mbit/s | ~446 | ~579 | **~641** |

Upload: 1 fluxo ~104 Mbit/s, 4 fluxos ~360 Mbit/s. Servidores europeus deram 17–400 Mbit/s (distância). Veja [[06 - Armadilhas e troubleshooting#Teste de velocidade]].

## Persistência

Validado com `reboot` por software: após ~140 s a ODI voltou a **O5**, mesma firmware 220817, mesmo `OMCI_SW_VER1/2`, mesmo ME7, PPPoE autenticou de novo.
