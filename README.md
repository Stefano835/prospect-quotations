# Prospect — Aggiornamento automatico quotazioni

Repository di supporto al simulatore **Prospect** (Reale Mutua Dual Plus Premio Unico).

Ogni lunedì mattina una **GitHub Action** scarica automaticamente le quotazioni
settimanali delle 4 linee unit linked da Yahoo Finance, le allinea, applica
l'offset di calibrazione sull'Obbligazionaria e aggiorna `data/quotations.json`.

Il simulatore Prospect, all'apertura, fa fetch di quel JSON e mostra all'agente
le quotazioni sempre fresche. Zero interventi manuali.

---

## Setup iniziale (una sola volta)

### 1. Crea la repo su GitHub

1. Vai su https://github.com/new
2. **Repository name**: `prospect-quotations` (o quello che preferisci)
3. **Public** (necessario per attivare GitHub Pages gratuito)
4. Spunta **Add a README file** se vuoi, ma poi lo sovrascrivi con questo
5. Click **Create repository**

### 2. Carica i file

Hai due opzioni:

**Opzione A — Drag & drop dal browser** (più semplice se non usi git)

1. Sulla repo appena creata, click su **Add file → Upload files**
2. Trascina dentro:
   - `fetch_quotations.py`
   - `data/quotations.json` (mantieni la cartella!)
   - `.github/workflows/update.yml` (mantieni la cartella!)
   - questo `README.md`
3. Click **Commit changes**

> ⚠️ Per caricare file dentro le cartelle `data/` e `.github/workflows/`,
> trascinali con la cartella oppure scrivi il path completo nel campo
> "Name your file" quando lo crei a mano (es. `data/quotations.json`).

**Opzione B — Da terminale con git**

```bash
git clone https://github.com/TUO_USERNAME/prospect-quotations.git
cd prospect-quotations
# copia dentro tutti i file
git add .
git commit -m "Setup iniziale"
git push
```

### 3. Attiva GitHub Pages

1. Sulla repo → **Settings** → menu laterale **Pages**
2. **Source**: **Deploy from a branch**
3. **Branch**: `main` (o `master`), folder `/ (root)`
4. **Save**
5. Aspetta 1-2 minuti, poi ricarica: in alto comparirà
   `Your site is live at https://TUO_USERNAME.github.io/prospect-quotations/`

L'URL del JSON sarà:
```
https://TUO_USERNAME.github.io/prospect-quotations/data/quotations.json
```

### 4. Lancia il primo aggiornamento

1. Tab **Actions** della repo
2. Click sul workflow **Aggiorna quotazioni** (a sinistra)
3. Bottone **Run workflow → Run workflow** (verde)
4. Aspetta ~1 minuto: l'azione gira e committa il JSON aggiornato

Da questo momento in poi gira da sola ogni lunedì alle 08:00 UTC.

### 5. Configura il simulatore Prospect

1. Apri Prospect
2. Espandi **🔄 Aggiorna quotazioni**
3. Incolla l'URL `https://TUO_USERNAME.github.io/prospect-quotations/data/quotations.json`
   nel campo URL
4. Click **Salva URL e aggiorna**

Il simulatore farà fetch ogni volta che viene aperto. Le quotazioni in
localStorage vengono aggiornate automaticamente.

---

## Test locale (opzionale)

Per verificare lo script senza GitHub:

```bash
pip install yfinance pandas
python fetch_quotations.py
```

Apri `data/quotations.json` per vedere il risultato.

---

## Manutenzione

- **Cambiare la frequenza**: modifica la stringa `cron` in `.github/workflows/update.yml`
  (sintassi standard cron: minuto ora giorno mese giorno-settimana)
- **Forzare un aggiornamento**: tab Actions → Run workflow
- **Vedere i log**: tab Actions → click sull'esecuzione → click sul job
- **Cambiare l'offset Obbligazionaria**: variabile `LINEE` in `fetch_quotations.py`
- **Aggiungere altre linee**: aggiungi tuple in `LINEE` (richiede modifiche
  anche al simulatore lato consumer)

---

## Costi

Tutto gratis. GitHub Free copre:
- Repository pubbliche illimitate
- 2.000 minuti/mese di GitHub Actions (lo script gira in ~30 secondi → ~2 minuti/mese)
- GitHub Pages illimitato per repo pubbliche
