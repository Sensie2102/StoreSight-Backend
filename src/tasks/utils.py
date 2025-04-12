import httpx
from datetime import datetime
from typing import List

BASE_HEADERS = {
    "Content-Type": "application/json"
}

async def fetch_shopify_products(token: str, shop_url: str, since: datetime = None) -> List[dict]:
    url = f"https://{shop_url}/admin/api/2023-10/products.json"
    params = {"limit": 250}
    if since:
        params["updated_at_min"] = since.isoformat()

    headers = BASE_HEADERS.copy()
    headers["X-Shopify-Access-Token"] = token

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("products", [])

async def fetch_shopify_orders(token: str, shop_url: str, since: datetime = None) -> List[dict]:
    url = f"https://{shop_url}/admin/api/2023-10/orders.json"
    params = {"limit": 250, "status": "any"}
    if since:
        params["updated_at_min"] = since.isoformat()

    headers = BASE_HEADERS.copy()
    headers["X-Shopify-Access-Token"] = token

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("orders", [])

async def fetch_shopify_customers(token: str, shop_url: str, since: datetime = None) -> List[dict]:
    url = f"https://{shop_url}/admin/api/2023-10/customers.json"
    params = {"limit": 250}
    if since:
        params["updated_at_min"] = since.isoformat()

    headers = BASE_HEADERS.copy()
    headers["X-Shopify-Access-Token"] = token

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("customers", [])
