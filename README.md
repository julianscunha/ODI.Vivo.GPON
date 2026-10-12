# ODI.Vivo.GPON

![status](https://img.shields.io/badge/status-validado-brightgreen)
![hardware](https://img.shields.io/badge/ONU-DFP--34X--2C2%20%7C%20RTL9601D-blue)
![firmware](https://img.shields.io/badge/firmware-V1.0--220817-orange)
![isp](https://img.shields.io/badge/ISP-Vivo%20Fibra%20(SP)-purple)
![docs](https://img.shields.io/badge/docs-Obsidian-7C3AED)
![license](https://img.shields.io/badge/license-MIT-green)

**Como substituir o HGU MitraStar da Vivo Fibra por uma ONU/SFP ODI DFP-34X-2C2 (RTL9601D)** e obter o provisionamento completo (bridge, VLAN, PPPoE e Internet), explicando a causa raiz que fazia a ODI ficar em **O5 sem serviço**.

> Documentação em português (pt-BR), escrita como vault do **Obsidian** (`docs/`), com scripts de teste e diagnóstico.

**Tags:** `gpon` `onu` `sfp` `odi` `dfp-34x-2c2` `rtl9601d` `realtek` `vivo` `vivo-fibra` `mitrastar` `hgu` `omci` `pppoe` `vlan-1335` `ploam` `olt` `fttH` `obsidian` `pt-br`

---

## O problema

Com a firmware original **V1.0-220923** e a identidade do HGU clonada (SN, PLOAM, vendor, modelo, hardware), a ODI chegava a **O5**, mas:

- as entidades de bridge (**ME45/ME47**) ficavam vazias;
- o PPPoE (PADI) nunca recebia PADO;
- o OLT ficava enviando `StartSwDownload` para a Image 1 (inválida) em vez de provisionar o serviço.

## A solução em resumo

1. Clonar a identidade OMCI do HGU.
2. Gravar a firmware **`M110_sfp_ODI_220817`** (contém `/etc/scripts/fix_sw_ver.sh`).
3. Definir `OMCI_OLT_MODE=3` e `sw_custom_version0/1` com as versões de software do HGU (`100WVK0b1` / `200WVK0b1`).
4. A ONU passa a anunciar as duas imagens **válidas** com as versões do HGU. O OLT para de empurrar software e cria bridge, VLAN e fluxos (ME45/47/84/171).
5. O roteador/PC marca **VLAN 1335** e faz PPPoE.
6. Manter o HGU desligado e fora da fibra.

```text
boot 220817 -> fix_sw_ver.sh -> OMCI_SW_VER1/2 = versões do HGU -> omci_app
            -> OLT lê ME7 (Valid=1/1) -> cria ME45/47/84/171 -> PPPoE em VLAN 1335
```

## Resultado validado

| Item | Resultado |
|---|---|
| Estado GPON | **O5** estável |
| Provisionamento | ME45, ME47, ME84, ME171, ME266, ME268… criados pelo OLT |
| Mensagens de software no OMCI | nenhuma (`StartSwDownload`/`ActivateSw`/`CommitSw`/`Reboot` = 0) |
| PPPoE | PADO + **PAP ACK** com `cliente@cliente` / `cliente` |
| Persistência | validada após `reboot` |
| Desempenho (plano 600 Mb) | ~641 Mbit/s de download com 6 fluxos (PC, Cloudflare GRU) |
| Saúde da PON | BIP/FEC/HEC/FCS = 0 |

## Documentação (`docs/`)

| Nota | Conteúdo |
|---|---|
| [00 - Índice](docs/00%20-%20%C3%8Dndice.md) | Mapa e resumo |
| [01 - Visão geral e causa raiz](docs/01%20-%20Vis%C3%A3o%20geral%20e%20causa%20raiz.md) | O que estava errado e por quê |
| [02 - Pré-requisitos e acesso](docs/02%20-%20Pr%C3%A9-requisitos%20e%20acesso.md) | Material, rede, SSH legado |
| [03 - Procedimento passo a passo](docs/03%20-%20Procedimento%20passo%20a%20passo.md) | Roteiro para repetir com outra ODI |
| [04 - Validação e testes](docs/04%20-%20Valida%C3%A7%C3%A3o%20e%20testes.md) | Checklist, decodificação do log OMCI, desempenho |
| [05 - Roteador e VLAN 1335](docs/05%20-%20Roteador%20e%20VLAN%201335.md) | Configuração do roteador e teste no PC |
| [06 - Armadilhas e troubleshooting](docs/06%20-%20Armadilhas%20e%20troubleshooting.md) | Sintomas, causas e o que não repetir |
| [07 - Referência de comandos](docs/07%20-%20Refer%C3%AAncia%20de%20comandos.md) | `nv`, `flash`, `omcicli`, `diag` |

Para ler com os `[[wikilinks]]`, abra a pasta `docs/` como vault no **Obsidian**.

## Scripts (`scripts/`)

| Arquivo | Função |
|---|---|
| `odi-ssh.sh` | SSH com os algoritmos antigos do dropbear da ODI (senha por `SSH_ASKPASS`, nada gravado) |
| `padi_test.py` | Envia PADI (VLAN 10 / 1335 / sem tag) e detecta PADO (Scapy + Npcap) |
| `pppoe_auth_test.py` | PPPoE completo até **PAP/CHAP**, IPCP e PADT |
| `vivo-pppoe-vlan1335.ps1` | Cria vNIC Hyper-V com VLAN 1335 e conexão PPPoE no Windows |

## Escopo e limites

- Caso documentado: **Vivo Fibra, São Paulo**, HGU **GPT-2741GNAC-N1** (MitraStar). Os números de VLAN, versões de software e o OLT podem variar por região/equipamento; **confirme no dump do seu HGU**.
- Não foi medida a temperatura nem a potência óptica da ODI, e não houve teste de queda de energia completa (só `reboot`).
- A tradução de VLAN 10 → 1335 (ME171) não foi aplicada em hardware pela ODI; o roteador deve marcar **1335** diretamente.
- Detalhes não registrados: método exato de envio do `.tar` e comando da gravação da Image 0.

## Aviso

> [!WARNING]
> Procedimento avançado, **por sua conta e risco**. Gravar firmware e alterar `sw_active`/`sw_commit` pode deixar o módulo sem boot; mantenha acesso serial (UART) se possível. Clonar a identidade de um HGU pode violar os termos do seu provedor. Este repositório **não contém** números de série, senhas PLOAM ou credenciais; obtenha os seus a partir do **seu** equipamento, e não compartilhe esses dados.

## Créditos e referências

- Firmware e scripts: projeto **RTL960x** / README da DFP-34X-2C2 (`M110_sfp_ODI_220817.tar`).
- Investigação, captura OMCI e validação: este repositório.

## Licença

[MIT](LICENSE) — documentação e scripts. Use por sua conta e risco.
