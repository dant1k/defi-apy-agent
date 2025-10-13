"""Token parsing and classification helpers."""

from __future__ import annotations

import re
from typing import Iterable, List, Sequence

STABLE_TOKENS = {
    "USDT",
    "USDC",
    "USDC.E",
    "USDT.E",
    "DAI",
    "BUSD",
    "TUSD",
    "FRAX",
    "USDD",
    "LUSD",
    "GUSD",
    "USDJ",
    "SUSD",
    "USDP",
    "EURC",
    "EURS",
    "UST",
}

WRAPPER_PREFIXES = (
    "W",
    "ST",
    "L",
    "A",
    "R",
    "CB",
    "WB",
    "S",
    "C",
)


def parse_tokens(symbol: str) -> List[str]:
    return [tok for tok in re.split(r"[^\w]+", (symbol or "").upper()) if tok]


def normalize_pair(symbol: str) -> str:
    tokens = parse_tokens(symbol)
    if not tokens:
        return symbol.upper()
    return "-".join(sorted(tokens))


def classify_pair(tokens: Sequence[str]) -> str:
    if not tokens:
        return "unknown"
    upper_tokens = [token.upper() for token in tokens]
    stable_count = sum(token in STABLE_TOKENS for token in upper_tokens)
    wrapper_count = sum(any(token.startswith(prefix) for prefix in WRAPPER_PREFIXES) for token in upper_tokens)
    distinct_tokens = len(set(upper_tokens))

    if distinct_tokens == 1:
        token = upper_tokens[0]
        if token in STABLE_TOKENS:
            return "stable-stable"
        if any(token.startswith(prefix) for prefix in WRAPPER_PREFIXES):
            return "wrapper-single"
        return "single"

    if stable_count >= 1 and stable_count < len(upper_tokens):
        return "token-stable"
    if wrapper_count >= 1:
        return "token-wrapper"
    if stable_count == len(upper_tokens):
        return "stable-stable"
    return "mixed"


def contains_wrapper(tokens: Iterable[str]) -> bool:
    upper_tokens = [token.upper() for token in tokens]
    if any(any(token.startswith(prefix) for prefix in WRAPPER_PREFIXES) for token in upper_tokens):
        return True
    if any(token.endswith("WRAP") or token.endswith("WRAPPED") for token in upper_tokens):
        return True
    return False
