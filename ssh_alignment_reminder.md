# SSH Alignment Reminder (PC 139 <-> LXC 190)

Questo documento riepiloga le impostazioni necessarie per l'accesso SSH bidirezionale tra il PC Windows (Node ARIA) e l'LXC container (Sviluppo).

## Dati Macchine

| Macchina | Nickname | Indirizzo IP | Utente | Percorso Chiave (~/.ssh/) |
| :--- | :--- | :--- | :--- | :--- |
| **PC Windows** | `pc139` | `192.168.1.139` | `roberto` | `id_ed25519` (.pub) |
| **LXC Container** | `lxc190` | `192.168.1.190` | `root` | `id_ed25519` (.pub) |

## Comandi Rapidi SSH

Dall'interno del container LXC 190, puoi ora collegarti al PC usando il nome abbreviato:
```bash
ssh pc139
```

Dal PC Windows, puoi collegarti al container usando:
```powershell
ssh root@192.168.1.190
# o se hai configurato l'host 'lxc190' in Windows:
ssh lxc190
```

## Dove trovare le chiavi ufficiali
- **LXC 190**: `/root/.ssh/id_ed25519.pub`
- **PC 139**: `C:\Users\roberto\.ssh\id_ed25519.pub`

## Allineamento chiavi (Promemoria tecnico)
Per mantenere l'accesso senza password, la chiave pubblica di ogni macchina deve essere presente nel file `authorized_keys` dell'altra:
- La chiave di LXC 190 è in `C:\Users\roberto\.ssh\authorized_keys` (PC 139)
- La chiave di PC 139 è in `/root/.ssh/authorized_keys` (LXC 190)

> [!TIP]
> Per aggiungere la chiave del container a un nuovo nodo Windows, usa da LXC:
> `cat ~/.ssh/id_ed25519.pub | ssh <user>@<ip> "Add-Content ~/.ssh/authorized_keys"`
