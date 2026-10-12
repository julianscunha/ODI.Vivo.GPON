---
tags: [gpon, odi, procedimento, firmware]
created: 2026-10-12
---

# Procedimento passo a passo

Voltar: [[00 - Índice]] · Anterior: [[02 - Pré-requisitos e acesso]] · Próximo: [[04 - Validação e testes]]

> [!danger] Antes de começar
> - Grave **toda** saída de console (MobaXterm/PuTTY log). Sem log não dá para reverter.
> - Anote os valores originais da ODI (`flash get`, `nv getenv`) antes de alterar.
> - Mexer em `sw_active`/`sw_commit` e em `mtd` pode deixar a ODI sem boot. Sem acesso serial (UART), não faça experimentos além deste roteiro.

## 1. Coletar a identidade do HGU

Do HGU original (dump OMCI/MIB), anote:

| Item | Exemplo do caso documentado | Onde ficou na ODI |
|---|---|---|
| GPON SN | `MSTC` + 8 hex do **seu** HGU | `GPON_SN` |
| PLOAM (ASCII e HEX) | 10 caracteres ASCII (o HEX é o mesmo em bytes) | senha PLOAM |
| Vendor ID | `MSTC` | `PON_VENDOR_ID` |
| ONU Model (ME257) | `GPT-2741GNAC-N1` | `GPON_ONU_MODEL` |
| Hardware Version (ME256) | `GPT-2741GN` | `HW_HWVER` |
| OMCC Version | `A1` (161) | `OMCC_VER` |
| Traffic Mgmt Option | `2` | `OMCI_TM_OPT` |
| VP Code | `0` | `OMCI_VENDOR_PRODUCT_CODE` |
| Versões de software (ME7) | Image 0 `100WVK0b1` (ativa), Image 1 `200WVK0b1` | `sw_custom_version0/1` |
| VLAN | 10 → 1335 (ME171) | — |

Dados do HGU também permitem conferir: TCONT/Alloc-ID, GEM 266, Service Profile `0x1102`, bridge `0x101`.

## 2. Aplicar a identidade na ODI

```sh
flash set PON_VENDOR_ID MSTC
flash set GPON_ONU_MODEL GPT-2741GNAC-N1
flash set HW_HWVER GPT-2741GN
flash set OMCI_VENDOR_PRODUCT_CODE 0
flash set GPON_SN <SEU_SN>
# senha PLOAM, OMCC_VER e OMCI_TM_OPT: mesmos comandos, com os valores do HGU
```

> [!note]
> Os nomes exatos das variáveis de PLOAM e `OMCC_VER` não ficaram registrados neste documento; confira com `flash get <NOME>` e reinicie a ODI após ajustar. Esses valores foram aplicados e o MIB refletiu: ME256 `MSTC`/`GPT-2741GN`, ME257 `GPT-2741GNAC-N1`, OMCC `A1`.

## 3. Gravar a firmware 220817 na Image 1

1. Enviar `M110_sfp_ODI_220817.tar` para `/tmp` da ODI (método não registrado: `scp`, tftp ou wget).
2. Conferir hashes (Windows e ODI): MD5 `8edd8fd6cca9a2b727e1773b4faa3bb9`.
3. Gravar na **Image 1**, preservando a Image 0:

```sh
sh /etc/scripts/fwu_starter.sh 1 /tmp/M110_sfp_ODI_220817.tar
# esperado: "Integrity of uImage & rootfs is okay" ... "Successfully updated image 1!!"
nv getenv sw_version1     # V1.0-220817
```

MTDs: `mtd4=k0`, `mtd5=r0`, `mtd6=k1`, `mtd7=r1`.

## 4. Fazer a ODI iniciar pela 220817

O bootloader (`bootcmd`) com `sw_tryactive=2` usa `sw_commit` para escolher a imagem:

```
sw_commit=0 → Image 0 (b0)
sw_commit=1 → Image 1 (b1)
```

Para rodar a Image 1: `nv setenv sw_commit 1` e `nv setenv sw_active 1`, depois `reboot`. Confira `cat /etc/version` → `V1.0-220817`.

> [!tip] Estado final recomendado
> No estado em que ficou funcionando, **as duas imagens têm a 220817** (`sw_version0=sw_version1=V1.0-220817`) e a ODI roda a Image 0 (`sw_active=0`, `sw_commit=0`, `sw_tryactive=2`). Assim qualquer troca de slot pelo OLT é inofensiva. A gravação da Image 0 não foi registrada aqui; é o mesmo comando com `fwu_starter.sh 0` (**só faça se você tiver como recuperar**).

## 5. Versões de software customizadas

```sh
nv setenv sw_custom_version0 100WVK0b1     # versão da Image 0 do HGU
nv setenv sw_custom_version1 200WVK0b1     # versão da Image 1 do HGU
flash set OMCI_OLT_MODE 3                   # habilita o fix_sw_ver.sh
```

No boot da 220817, o `rc3` executa na ordem:

```
… /etc/insdrv.sh → /etc/scripts/fix_sw_ver.sh → /etc/runsdk.sh (→ runomci.sh → omci_app)
```

`fix_sw_ver.sh` faz `flash set OMCI_SW_VER1 $SWVER0` e `OMCI_SW_VER2 $SWVER1` quando `OMCI_OLT_MODE=3`.

Teste manual sem reiniciar: `/etc/scripts/fix_sw_ver.sh`, depois `flash get OMCI_SW_VER1` e `omcicli mib get 7`.

## 6. Verificar o ME7 antes de ligar a fibra

`omcicli mib get 7` deve mostrar:

| | Image 0 | Image 1 |
|---|---|---|
| Version | `100WVK0b1` | `200WVK0b1` |
| Valid | **1** | **1** |
| Active/Committed | 1/1 (no HGU) | 0/0 |

## 7. Conectar a fibra e observar

Com `omcicli set logfile 3 0xffffffff` ligado e `HGU` desligado:

1. Estado muda para **O5**.
2. No log aparecem `Create` de ME45, ME47, ME84, ME171, ME266, ME268, ME130…
3. **Não** devem aparecer `StartSwDownload`, `ActivateSw`, `CommitSw`, `Reboot`, nem `fwu_starter` no `ps`.

Ver [[04 - Validação e testes]].

## 8. Configurar o roteador

Veja [[05 - Roteador e VLAN 1335]].
