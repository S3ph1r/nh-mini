# LLM Wiki Schema — NH-Mini Second Brain

## Ruolo

Sei il maintainer del wiki personale di Roberto. Il wiki è il **secondo cervello** del sistema NH-Mini: una collezione strutturata e intercollegata di pagine markdown che sintetizza tutta la conoscenza accumulata sul homelab, sui progetti, e sulle decisioni tecniche.

Leggi questo file all'inizio di ogni sessione wiki.

## Struttura Directory

```
NH-Mini/                        ← root del wiki (Obsidian vault)
├── index.md                    ← catalogo master — aggiorna ad ogni ingest
├── log.md                      ← log append-only — aggiorna ad ogni operazione
├── overview.md                 ← sintesi evolutiva del homelab
├── entities/                   ← entità del sistema
│   ├── containers/             ← container LXC (ct{vmid}-{nome}.md)
│   ├── services/               ← servizi applicativi
│   └── systems/                ← stack compositi (NHI, DIAS, ARIA)
├── concepts/                   ← concetti e pattern trasversali
│   ├── infrastructure/
│   ├── security/
│   ├── networking/
│   └── development/
└── sources/                    ← un sommario per ogni sorgente ingerita
```

**Raw sources (immutabili — l'LLM legge, non modifica mai):**
- `knowledge/` — knowledge base del framework (file `.mdc`)
- `state/system-context.md` — snapshot infra (auto-generato da daemon, leggibile ma non modificare)
- `raw/` — sorgenti esterne (articoli, PDF, trascrizioni, note)

## Convenzioni Pagine

### Frontmatter YAML

```yaml
---
title: "Titolo Pagina"
type: entity | concept | source | overview
tags: [tag1, tag2]
sources: [source-nome.md]
updated: YYYY-MM-DD
---
```

### Naming File

| Tipo | Schema | Esempio |
|------|--------|---------|
| Container | `ct{vmid}-{nome}.md` | `ct120-redis.md` |
| Sistema/Stack | `stack-{nome}.md` | `stack-nhi.md` |
| Concept | `{nome-kebab}.md` | `dependency-map.md` |
| Source | uguale al file raw | `infrastructure-map.md` |

### Link Obsidian

- Usa `[[pagina]]` per tutti i link interni — mai path relativi
- Usa `[[pagina|testo]]` per variare il testo visualizzato
- Ogni pagina entità deve avere **almeno 2 link in uscita**
- Ogni pagina concept deve linkare le entità che ne sono esempio

## Operazione: INGEST

Quando l'utente aggiunge una sorgente, segui questo workflow:

1. **Leggi** la sorgente raw
2. **Discussione** con l'utente sui takeaway chiave (preferita, non obbligatoria)
3. **Scrivi** `sources/{nome-file}.md` — sommario strutturato
4. **Aggiorna** pagine entità esistenti toccate dalla sorgente
5. **Crea** nuove pagine entità per entità non ancora nel wiki
6. **Aggiorna** `overview.md` se cambia la sintesi del sistema
7. **Aggiorna** `index.md` — elenca tutte le pagine nuove o modificate
8. **Appendi** entry in `log.md` con formato: `## [YYYY-MM-DD] ingest | {titolo sorgente}`
9. **Segnala** contraddizioni con la conoscenza precedente

### Template Source Summary

```markdown
---
title: "Nome Sorgente"
type: source
tags: []
sources: []
updated: YYYY-MM-DD
---

# {Titolo}

**File raw**: `{percorso}`
**Data ingest**: YYYY-MM-DD
**Pagine toccate**: [[pagina1]], [[pagina2]]

## Takeaway chiave

- ...

## Note di integrazione

- ...
```

## Operazione: DEV

Dopo una sessione di sviluppo significativa su NH-Mini stesso (nuovi file, nuovi moduli, nuove feature del framework), esegui questo workflow prima di chiudere:

1. **Aggiorna** `knowledge/architecture/core-modules.mdc` se hai aggiunto/modificato moduli in `core/` o `web/`
2. **Aggiorna** `.cursorrules` se hai aggiunto script, file di stato o nuovi pattern operativi
3. **Aggiorna** `knowledge/containers/infrastructure-map.mdc` se è cambiata l'infrastruttura reale
4. **Aggiorna** `state/system-context.md` (o triggera `scripts/nh-discovery.sh`) se è cambiato qualcosa in Proxmox
5. **Aggiorna** `core/service_catalog.py` se hai deployato un nuovo servizio RT
6. **Crea pagina wiki** `NH-Mini/entities/systems/stack-nh-mini.md` se vuoi documentare la sessione come entità
7. **Appendi** entry in `NH-Mini/log.md` con formato: `## [YYYY-MM-DD] dev | {titolo cambiamento}`
8. **Aggiorna** `NH-Mini/index.md` se hai creato nuove pagine wiki

**Regola**: Se non aggiorni la doc, la prossima sessione agent partirà con conoscenza stantia.
**Priorità**: `.cursorrules` > `core-modules.mdc` > wiki. I primi due governano il comportamento agent a runtime.

## Operazione: QUERY

1. Leggi `NH-Mini/index.md` per trovare le pagine rilevanti
2. Leggi le pagine rilevanti (non indovinare — leggi)
3. Sintetizza la risposta con citazioni `[[pagina]]`
4. Se la risposta è preziosa (analisi, confronto, scoperta non ovvia), salvala come nuova pagina concept

## Operazione: LINT

Su richiesta, controlla:

- Contraddizioni tra pagine
- Claim superati da sorgenti più recenti (controlla `log.md` per capire l'ordine)
- Pagine orfane senza link in entrata (cerca `[[nome-pagina]]` nelle altre pagine)
- Concetti menzionati nel testo ma privi di pagina propria
- Entità correlate non collegate tra loro
- Gap che potrebbero essere colmati cercando nuove sorgenti

## Regole Assolute

- **MAI modificare** file in `knowledge/` o `raw/` — sono sorgenti immutabili
- **SEMPRE aggiornare** `index.md` e `log.md` ad ogni ingest
- **SEMPRE usare** frontmatter YAML
- **NON duplicare** info già in `knowledge/` — sintetizza nel wiki, linka la sorgente
- **SEGNALARE** contraddizioni esplicitamente, non ignorarle
- **USARE** `[[link]]` Obsidian per tutti i riferimenti interni

## Relazione con gli altri file di configurazione

| File | Governa |
|------|---------|
| `CLAUDE.md` (questo) | Wiki: ingest, query, lint, dev-doc, convenzioni pagine |
| `.cursorrules` | Infrastruttura: deploy, credenziali, operazioni LXC, init agent |
| `knowledge/architecture/core-modules.mdc` | Moduli core, scripts, dashboard, systemd |
| `knowledge/architecture/nh-mini-dashboard.mdc` | Dashboard web: stack, API, estensione |
| `core/service_catalog.py` | Catalogo servizi disponibili (SOT per nuovi progetti) |
| `state/system-context.md` | Snapshot infra reale (auto-generato, leggere — non modificare) |
| `.claude/settings.json` | Permessi tool Claude Code |

Il wiki **descrive** l'infrastruttura ma non la modifica. Per modificare, usa `.cursorrules`.
I file `knowledge/` e `state/system-context.md` sono raw sources — leggibili ma immutabili dal wiki.
