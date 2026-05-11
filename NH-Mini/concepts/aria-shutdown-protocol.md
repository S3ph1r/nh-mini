---
title: "ARIA Shutdown Protocol"
type: concept
tags: [aria, windows, process-management, python]
sources: [main_tray.py, orchestrator.py]
updated: 2026-05-06
---

# ARIA Shutdown Protocol

Protocollo di terminazione deterministica per l'orchestratore ARIA su ambiente Windows. Il protocollo risolve il problema dei thread orfani e dei processi zombie che bloccavano le porte di rete dopo l'uscita dalla Tray Icon.

## Il Problema
Le librerie Python come `pystray` e `redis-py` possono mantenere attivi thread non-daemon in background (es. pool di connessioni, loop di eventi UI). Su Windows, questo impedisce al processo di morire anche dopo che il thread principale ha terminato l'esecuzione, causando conflitti di porta (`8089`, `8082`) al riavvio successivo.

## La Soluzione: 5-Step Robust Shutdown

L'implementazione in `NodeOrchestrator.stop()` segue una sequenza rigorosa:

1. **Logical Stop**: Invio del segnale `self.running = False` e arresto del `CloudManager`.
2. **Backend Kill**: Terminazione forzata dei processi subprocess (Qwen3, Fish, ecc.) tramite `taskkill`.
3. **Dashboard Cleanup**: Esecuzione di un comando Powershell asincrono per killare il processo `server.py` associato.
4. **Asset Server Release**: Chiusura del server HTTP sulla porta 8082.
5. **Nuclear Exit**: Esecuzione di `os._exit(0)` nel thread principale della Tray Icon.

## Esempio Implementativo

```python
# In main_tray.py
def menu_action_exit(icon, item):
    try:
        orchestrator.stop()
        icon.stop()
    finally:
        import os
        os._exit(0) # Forza l'uscita immediata ignorando thread orfani
```

## Benefici
- **Port Reusability**: Le porte 8089 e 8082 vengono liberate istantaneamente.
- **Integrità Logs**: La sequenza è loggata passo dopo passo nel file di sistema.
- **User Experience**: L'icona scompare immediatamente e il sistema è pronto per il riavvio via `aria.bat`.

## Vedi anche
- [[entities/systems/stack-aria-dashboard]]
- [[entities/systems/stack-aria]]
