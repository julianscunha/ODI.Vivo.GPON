---
tags: [gpon, vivo, odi, onu, moc]
aliases: [ODI Vivo, DFP-34X-2C2 Vivo]
created: 2026-10-12
status: validado
---

# ODI DFP-34X-2C2 no lugar do HGU da Vivo

> [!success] Resultado
> A ODI **DFP-34X-2C2 (RTL9601D)** substituiu o HGU MitraStar GPT-2741GNAC-N1 da Vivo Fibra (São Paulo). ONU em **O5**, provisionamento completo pelo OLT, PPPoE autenticado (`PAP ACK`) em **VLAN 1335**, e ~640 Mbit/s medidos em plano de 600 Mb. Validado também após `reboot`.

## Mapa das notas

1. [[01 - Visão geral e causa raiz]] — o que estava errado e por que funcionou
2. [[02 - Pré-requisitos e acesso]] — material, rede do PC, SSH
3. [[03 - Procedimento passo a passo]] — o roteiro para repetir com outra ODI
4. [[04 - Validação e testes]] — como provar que está funcionando
5. [[05 - Roteador e VLAN 1335]] — configuração do roteador / PC
6. [[06 - Armadilhas e troubleshooting]] — erros que custaram meses
7. [[07 - Referência de comandos]] — comandos e ferramentas

## Resumo em 6 linhas

1. Clonar a identidade OMCI do HGU (SN, PLOAM, vendor, modelo, hw).
2. Gravar o firmware **V1.0-220817** (tem `fix_sw_ver.sh`).
3. `OMCI_OLT_MODE=3` + `sw_custom_version0/1` = versões de software do HGU (`100WVK0b1` / `200WVK0b1`).
4. A ONU anuncia as duas imagens **válidas** e com as versões do HGU; o OLT para de empurrar software e cria bridge/VLAN (ME45/47/84/171).
5. O roteador marca **VLAN 1335** e faz PPPoE com `cliente@cliente` / `cliente`.
6. Manter o HGU desligado/fora da fibra.

## Arquivos

- `scripts/` — [[07 - Referência de comandos#Scripts incluídos|scripts de teste PPPoE e conexão no Windows]]
