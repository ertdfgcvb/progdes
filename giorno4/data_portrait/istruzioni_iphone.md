# Estrazione dati da backup iPhone (macOS) — guida rapida

> Obiettivo: creare un backup locale cifrato, preparare Python + librerie, eseguire lo script `extract_iphone_backup.py` e verificare i database estratti.

---

# 1. Backup locale iPhone (via Finder)

1. Collega iPhone al Mac via cavo.
2. Sblocca iPhone → premi **Autorizza** se richiesto.
3. Apri **Finder** → seleziona iPhone nella barra laterale.
4. Sezione **Backup**:

   * Seleziona **Esegui backup di tutti i dati su questo Mac**
   * Spunta **Cifra backup locale**
   * Imposta password e salvala
5. Clicca **Esegui backup adesso**
6. Attendi completamento (può richiedere tempo)

Verifica: Finder deve mostrare **data/ora ultimo backup**.

---

# 2. Individua la cartella del backup

Apri Terminale:

```bash
cd ~/Library/Application\ Support/MobileSync/Backup
ls -lt
```

Troverai cartelle con nomi lunghi (esadecimali).
La più recente = backup appena creato.

Annota il nome → servirà come `BACKUP_DIR`.


## Nota importante: permessi Terminale su macOS

Se durante l’accesso alla cartella backup compare l’errore:

```
Operation not permitted
```

oppure non riesci a entrare in:

```
~/Library/Application Support/MobileSync/Backup
```

significa che macOS blocca l’accesso per motivi di privacy.

### Soluzione

Concedi al Terminale l’accesso completo al disco:

1. Apri **Impostazioni di Sistema**
2. Vai su **Privacy e Sicurezza**
3. Apri **Accesso completo al disco**
4. Aggiungi **Terminale** (o iTerm se usato)
5. Attiva l’interruttore
6. Chiudi e riapri il Terminale

Dopo questo, i comandi `cd` e `ls` nella cartella dei backup funzioneranno normalmente.


---

# 3. Verifica Python

Controllo:

```bash
python3 --version
```

Se non presente o troppo vecchio → installa tramite Homebrew.

---

# 4. Installa Homebrew (se necessario)

Controllo:

```bash
brew --version
```

Se non esiste:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Poi installa Python e sqlite:

```bash
brew install python sqlite
```

---

# 5. Crea ambiente virtuale Python (venv)

```bash
python3 -m venv ~/venvs/iphone
source ~/venvs/iphone/bin/activate
```

Aggiorna pip:

```bash
python -m pip install --upgrade pip
```

Installa libreria necessaria:

```bash
python -m pip install iphone_backup_decrypt
```

Verifica:

```bash
python -c "import iphone_backup_decrypt; print('OK')"
```

Se vedi `(iphone)` nel prompt → venv attiva.

---

# 6. Esegui lo script di estrazione

Vai nella cartella dove si trova lo script:

```bash
cd /percorso/dove/si/trova/extract_iphone_backup.py
```

Imposta variabili (sostituisci valori):

```bash
BACKUP_DIR="$HOME/Library/Application Support/MobileSync/Backup/NOME_CARTELLA_BACKUP"
OUT_DIR="$HOME/iphone_decrypted"
PASS="PASSWORD_DEL_BACKUP"
```

Esegui:

```bash
python extract_iphone_backup.py "$BACKUP_DIR" "$OUT_DIR" "$PASS"
```

Al termine dovresti avere:

* `~/iphone_decrypted/sms.db`
* `~/iphone_decrypted/addressbook.sqlitedb`
* `~/iphone_decrypted/call_history.storedata`
* `~/iphone_decrypted/Manifest.decrypted.db`

---

# 7. Verifiche finali database

## 7.1 Verifica file SQLite

```bash
file ~/iphone_decrypted/sms.db
file ~/iphone_decrypted/addressbook.sqlitedb
```

## 7.2 Controllo integrità

```bash
sqlite3 ~/iphone_decrypted/sms.db "PRAGMA integrity_check;"
sqlite3 ~/iphone_decrypted/addressbook.sqlitedb "PRAGMA integrity_check;"
```

Valore atteso: `ok`

---

## 7.3 Conteggio messaggi

```bash
sqlite3 ~/iphone_decrypted/sms.db "SELECT COUNT(*) FROM message;"
```

---

## 7.4 Numero conversazioni

```bash
sqlite3 ~/iphone_decrypted/sms.db "SELECT COUNT(*) FROM chat;"
```

---

## 7.5 Conteggio contatti

Prima vedere tabelle:

```bash
sqlite3 ~/iphone_decrypted/addressbook.sqlitedb ".tables"
```

Poi provare:

```bash
sqlite3 ~/iphone_decrypted/addressbook.sqlitedb "SELECT COUNT(*) FROM ABPerson;"
```

oppure (schema più recente):

```bash
sqlite3 ~/iphone_decrypted/addressbook.sqlitedb "SELECT COUNT(*) FROM ZCONTACT;"
```

---

# Fine

Se i conteggi risultano corretti → estrazione completata con successo.
I database sono pronti per analisi e visualizzazione dati.
