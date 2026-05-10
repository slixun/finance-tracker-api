from decimal import Decimal
from typing import Dict, Tuple

import requests
import aiohttp
from app.enum import CurrencyEnum

FALLBACK_RATES: Dict[Tuple[str, str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal(str(95.0)),
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal(str(0.92)),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal(str(103.26)),
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal(str(0.0105)),
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal(str(0.92)),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal(str(0.0097)),
    (CurrencyEnum.USD, CurrencyEnum.KZT): Decimal(str(462.12)),
    (CurrencyEnum.EUR, CurrencyEnum.KZT): Decimal(str(543.71)),
    (CurrencyEnum.RUB, CurrencyEnum.KZT): Decimal(str(6.23)),
    (CurrencyEnum.KZT, CurrencyEnum.USD): Decimal(str(0.0022)),
    (CurrencyEnum.KZT, CurrencyEnum.EUR): Decimal(str(0.0018)),
    (CurrencyEnum.KZT, CurrencyEnum.RUB): Decimal(str(0.16)),
    (CurrencyEnum.USD, CurrencyEnum.BTC): Decimal("0.000010"),
    (CurrencyEnum.BTC, CurrencyEnum.USD): Decimal("100000"),
    (CurrencyEnum.EUR, CurrencyEnum.BTC): Decimal("0.0000092"),
    (CurrencyEnum.BTC, CurrencyEnum.EUR): Decimal("108700"),
    (CurrencyEnum.RUB, CurrencyEnum.BTC): Decimal("0.00000011"),
    (CurrencyEnum.BTC, CurrencyEnum.RUB): Decimal("9500000"),
    (CurrencyEnum.KZT, CurrencyEnum.BTC): Decimal("0.000000023"),
    (CurrencyEnum.BTC, CurrencyEnum.KZT): Decimal("46200000"),
}


async def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:
    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json"

    timeout = aiohttp.ClientTimeout(total=5.0)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                base_map = data.get(base, {})
                rate = base_map.get(target)

        if rate is not None and isinstance(rate, (int, float)):
            return Decimal(rate)
        raise KeyError("Rate not found")

    except Exception:
        return FALLBACK_RATES.get((base, target), Decimal(1))
