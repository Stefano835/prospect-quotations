"""
fetch_teseo.py
─────────────────────
Scarica le quotazioni MENSILI delle 3 linee Teseo Etica di Reale Mutua
da Yahoo Finance e produce data/teseo.json.

Teseo è tenuto in un file separato da quotations.json perché le sue linee
sono quotate con frequenza MENSILE (primo del mese), mentre le linee
Dual Plus sono settimanali: unirle nello stesso allineamento "per date
comuni" azzererebbe le righe (le date settimanali e mensili non coincidono).

Dipendenze: yfinance pandas

Uso locale:
    pip install yfinance pandas
    python fetch_teseo.py

In CI puo' girare nello stesso workflow di fetch_quotations.py, oppure in
un workflow dedicato (una volta al mese e' piu' che sufficiente).
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yfinance as yf

# =========================================================
# CONFIG
# =========================================================
# NOTA: i ticker Yahoo dei fondi Teseo vanno confermati al primo run.
# Reale li identifica come 0P0000G35M / 0P0000G35O / 0P0000G35P; su Yahoo
# il simbolo completo richiede di norma il suffisso di mercato ".F".
# Se il download restituisce "Nessun dato", prova a togliere/cambiare il
# suffisso, oppure verifica il simbolo esatto sulla pagina Yahoo del fondo.
LINEE = [
    # (ticker yahoo,       nome,                 offset di calibrazione)
    ('0P0000G35M.F',       'Teseo Garantita',     0.0),
    ('0P0000G35O.F',       'Teseo Bilanciata',    0.0),
    ('0P0000G35P.F',       'Teseo Sviluppo',      0.0),
]

# Bastano pochi anni: lo storico profondo (dal 2000/2007) e' gia' nel
# simulatore; qui servono solo le mensilita' recenti per tenere fresco il file.
ANNI_STORICO = 5

OUTPUT_PATH = Path(__file__).parent / 'data' / 'teseo.json'


# =========================================================
# FETCH
# =========================================================
def scarica_serie(ticker: str, offset: float):
    """Scarica serie MENSILE e applica eventuale offset."""
    df = yf.download(
        ticker,
        period=f'{ANNI_STORICO}y',
        interval='1mo',
        progress=False,
        auto_adjust=False,
    )
    if df is None or df.empty:
        raise RuntimeError(f"Nessun dato per {ticker}")

    serie = df['Close']
    if hasattr(serie, 'iloc') and serie.ndim > 1:
        serie = serie.iloc[:, 0]
    serie = serie.dropna() + offset
    return serie


def main() -> int:
    print(f"Scarico {len(LINEE)} linee Teseo (mensili) da Yahoo Finance…")

    serie_per_linea = []
    for ticker, nome, offset in LINEE:
        try:
            s = scarica_serie(ticker, offset)
            print(f"  {nome:20s} → {len(s):4d} osservazioni "
                  f"(ultima: {s.index[-1].date()}, offset: {offset:+.2f})")
            serie_per_linea.append(s)
        except Exception as e:
            print(f"  {nome:20s} → ERRORE: {e}", file=sys.stderr)
            return 1

    # Allineo per data: tengo solo le date presenti in tutte le serie Teseo
    date_comuni = set(serie_per_linea[0].index)
    for s in serie_per_linea[1:]:
        date_comuni &= set(s.index)
    date_ordinate = sorted(date_comuni)

    if not date_ordinate:
        print("ERRORE: nessuna data comune fra le serie Teseo", file=sys.stderr)
        return 1

    rows = []
    for d in date_ordinate:
        valori = [round(float(s.loc[d]), 4) for s in serie_per_linea]
        rows.append([d.strftime('%Y-%m-%d'), *valori])

    payload = {
        'updated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'source': 'Yahoo Finance via yfinance',
        'frequency': 'monthly',
        'columns': ['data', 'teseo_gar', 'teseo_bil', 'teseo_svil'],
        'offsets': {},
        'count': len(rows),
        'first_date': rows[0][0],
        'last_date': rows[-1][0],
        'rows': rows,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    print(f"\nOK → {OUTPUT_PATH}")
    print(f"  {len(rows)} righe · {rows[0][0]} → {rows[-1][0]}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
