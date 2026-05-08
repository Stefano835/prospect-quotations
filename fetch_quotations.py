"""
fetch_quotations.py
─────────────────────
Scarica le quotazioni settimanali delle 4 linee unit linked di Reale Mutua
(Dual Plus Premio Unico) da Yahoo Finance e produce data/quotations.json
nel formato consumato dal simulatore Prospect.

Dipendenze: yfinance pandas

Uso locale:
    pip install yfinance pandas
    python fetch_quotations.py

In CI viene eseguito automaticamente da .github/workflows/update.yml
ogni lunedì alle 08:00 UTC.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yfinance as yf

# =========================================================
# CONFIG
# =========================================================
LINEE = [
    # (ticker yahoo,    nome,                offset di calibrazione)
    ('0P00017ICP.F',    'Mercato Globale',   0.0),
    ('0P00017ICV.F',    'Bilanciata Attiva', 0.0),
    ('0P00017ICX.F',    'Obbligazionaria',  -0.28),  # offset empirico
    ('0P00017ICR.F',    'Impresa Italia',    0.0),
]

# Quanti anni di storico scaricare (più che sufficienti per il simulatore,
# che ha già l'embedded fino a marzo 2026; servono solo le righe nuove)
ANNI_STORICO = 6

OUTPUT_PATH = Path(__file__).parent / 'data' / 'quotations.json'


# =========================================================
# FETCH
# =========================================================
def scarica_serie(ticker: str, offset: float):
    """Scarica serie settimanale e applica eventuale offset."""
    df = yf.download(
        ticker,
        period=f'{ANNI_STORICO}y',
        interval='1wk',
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
    print(f"Scarico {len(LINEE)} linee Reale Mutua da Yahoo Finance…")

    serie_per_linea = []
    for ticker, nome, offset in LINEE:
        try:
            s = scarica_serie(ticker, offset)
            print(f"  {nome:22s} → {len(s):4d} osservazioni "
                  f"(ultima: {s.index[-1].date()}, offset: {offset:+.2f})")
            serie_per_linea.append(s)
        except Exception as e:
            print(f"  {nome:22s} → ERRORE: {e}", file=sys.stderr)
            return 1

    # Allineo per data: tengo solo le date presenti in tutte e 4 le serie
    date_comuni = set(serie_per_linea[0].index)
    for s in serie_per_linea[1:]:
        date_comuni &= set(s.index)
    date_ordinate = sorted(date_comuni)

    if not date_ordinate:
        print("ERRORE: nessuna data comune fra le 4 serie", file=sys.stderr)
        return 1

    rows = []
    for d in date_ordinate:
        valori = [round(float(s.loc[d]), 4) for s in serie_per_linea]
        rows.append([d.strftime('%Y-%m-%d'), *valori])

    payload = {
        'updated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'source': 'Yahoo Finance via yfinance',
        'columns': ['data', 'mercato', 'bilanciata', 'obbligazionaria', 'italia'],
        'offsets': {'obbligazionaria': -0.28},
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
