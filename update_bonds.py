import pandas as pd
import asyncpg
import asyncio

async def fetch_and_save():
    url = "https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQCB/securities.csv"
    df = pd.read_csv(url, sep=';', encoding='cp1251')
    cols = {
        'ISIN': 'isin',
        'SHORTNAME': 'name',
        'ISSUER_NAME': 'issuer',
        'COUPON': 'coupon_rate',
        'YIELDATPREVWAPRICE': 'yield_to_maturity',
        'MATDATE': 'maturity_date',
        'FACEUNIT': 'currency'
    }
    df = df.rename(columns=cols)
    df = df[list(cols.values())].fillna('')
    conn = await asyncpg.connect(dsn="postgresql://bondsuser:superpass@localhost/bondsbot")
    await conn.execute("DELETE FROM bonds")
    for row in df.itertuples():
        await conn.execute("""
            INSERT INTO bonds (isin, name, issuer, coupon_rate, yield_to_maturity, maturity_date, currency)
            VALUES ($1,$2,$3,$4,$5,$6,$7)
        """, row.isin, row.name, row.issuer, row.coupon_rate or 0, row.yield_to_maturity or 0, row.maturity_date, row.currency)
    await conn.close()

if __name__ == "__main__":
    asyncio.run(fetch_and_save())
