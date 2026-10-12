---
tags: [gpon, odi, troubleshooting, armadilhas]
created: 2026-10-12
---

# Armadilhas e troubleshooting

Voltar: [[00 - Índice]]

## Tabela rápida

| Sintoma | Causa provável | Ação |
|---|---|---|
| O5, mas sem Internet | ME45/47 vazios; OLT em download de software | Ajustar ME7: versões do HGU e Valid=1/1 ([[03 - Procedimento passo a passo#5. Versões de software customizadas]]) |
| `StartSwDownload` no log | ONU anuncia imagem inválida/versão diferente | Idem; usar 220817 e `OMCI_OLT_MODE=3` |
| PADI sem PADO | VLAN errada (10, sem tag, 885) | Marcar **1335** |
| PADO some depois de funcionar | HGU ligado/ainda na fibra | Desligar o HGU |
| SSH recusa conexão (`Connection reset`) | Sessão antiga ocupando o dropbear | Matar `ssh.exe` local e tentar de novo |
| `no matching key exchange method` | OpenSSH moderno | Opções `+diffie-hellman-group1-sha1`, `+ssh-rsa`, `+aes128-cbc` |
| Sessão SSH cai ao ir para O5 | Reconfiguração da bridge no momento do provisionamento | Aguardar; a ODI **não** reiniciou (uptime contínuo) |
| `fix_sw_ver.sh` não existe | Firmware 220923 | Usar 220817 |
| `sw_custom_version*` ignorado | Firmware 220923 | Idem |
| Velocidade baixa no teste | Servidor distante / 1 fluxo / PPPoE em software | [[#Teste de velocidade]] |

## Reversão para outra imagem

Em testes antigos, com a 220817 na Image 1 (`sw_commit=1`), ao conectar a fibra a ODI caiu ~2 min e voltou rodando a **220923** (`sw_active=0`), apesar de `sw_commit=1`. A lógica do bootloader não explica isso sozinha. A hipótese sustentada pelo binário `omci_app` é um `ActivateSw` do OLT (não commitado) seguido de reboot. **Não foi reproduzida** no estado final, onde:

- as duas imagens têm a 220817;
- o ME7 anuncia as versões do HGU com Valid=1/1;
- o log mostrou zero mensagens de software.

> [!tip]
> Mesmo que o OLT volte a trocar de slot, com as duas imagens iguais o comportamento da ODI não muda.

## O que não repetir

Depois que a identidade foi aplicada e verificada no MIB, não é preciso repetir: PLOAM, `GPON_SN`, `PON_VENDOR_ID`, `GPON_ONU_MODEL`, `HW_HWVER`, `OMCC_VER`, `OMCI_TM_OPT`, VLAN. Mexer neles de novo só consome tempo.

Enquanto o ME7 não estiver correto, não adianta investigar ME45/47, PPPoE ou Scapy: o OLT nem cria a bridge.

## Falsos positivos que consumiram tempo

- **O5 = serviço provisionado** — falso.
- **`OMCI_OLT_MODE=21`** — persiste, mas não resolveu a versão (`OMCI_SW_VER1` continuou `V1.7.1`).
- **`sw_custom_version*` na 220923** — setar via `nv setenv` não altera o OMCI.
- **VLAN 885** — dado de documentação de terceiros, não do HGU real.
- **Troca de fibra** — desnecessária; o problema era o ME7, não a fibra.

## Teste de velocidade

- Prefira servidor **no Brasil** (Cloudflare GRU, 9 ms). Servidores europeus deram 17–400 Mbit/s.
- Use **vários fluxos paralelos**: 1 fluxo ~446 Mbit/s, 6 fluxos ~641 Mbit/s no plano 600 Mb.
- PPPoE no Windows sobre Hyper-V é em software; para benchmark real use o roteador.

## Pontos em aberto

- Temperatura e potência óptica (DDM) não foram lidas na ODI.
- Não foi testada queda de energia completa (só `reboot` por software).
- A causa exata de a ODI não aplicar a tradução 10→1335 em hardware não foi investigada.
- O método de transferência do `.tar` para a ODI e a gravação da Image 0 com a 220817 não foram registrados.
