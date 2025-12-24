from __future__ import annotations

import asyncio
import logging

import aiohttp

from app.config import get_settings

API_URL = "https://pay.crypt.bot/api"


class CryptoBotClient:
    def __init__(self, token: str, timeout: int = 10):
        self.token = token
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {"Crypto-Pay-API-Token": self.token}
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=self._timeout,
            )
        return self._session

    async def _request(self, method: str, payload: dict) -> dict:
        session = await self._get_session()
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                async with session.post(f"{API_URL}/{method}", json=payload) as response:
                    if response.status >= 400:
                        text = await response.text()
                        raise RuntimeError(f"CryptoBot HTTP {response.status}: {text}")
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" not in content_type:
                        text = await response.text()
                        raise RuntimeError(f"CryptoBot non-JSON response: {text}")
                    data = await response.json()
                if not data.get("ok"):
                    raise RuntimeError(data.get("error", "CryptoBot API error"))
                return data["result"]
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                if attempt == max_attempts:
                    raise
                logging.warning(
                    "CryptoBot request failed (attempt %s/%s): %s",
                    attempt,
                    max_attempts,
                    exc,
                )
                await asyncio.sleep(0.5 * attempt)

    async def create_invoice(self, amount: float, asset: str, description: str, payload: str) -> dict:
        body = {
            "amount": str(amount),
            "asset": asset,
            "description": description,
            "payload": payload,
        }
        return await self._request("createInvoice", body)

    async def get_invoice(self, invoice_id: str) -> dict | None:
        result = await self._request("getInvoices", {"invoice_ids": str(invoice_id)})
        items = result.get("items", [])
        return items[0] if items else None


def get_crypto_bot_client() -> CryptoBotClient:
    settings = get_settings()
    if not settings.cryptobot_token:
        raise RuntimeError("CRYPTOBOT_TOKEN environment variable not set")
    return CryptoBotClient(settings.cryptobot_token)


_client_instance: CryptoBotClient | None = None


def get_shared_crypto_bot_client() -> CryptoBotClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = get_crypto_bot_client()
    return _client_instance


async def close_crypto_bot_client() -> None:
    global _client_instance
    if _client_instance is not None:
        await _client_instance.close()
        _client_instance = None
