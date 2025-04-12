from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_session
from src.db.db_schema import Integrations, Product, Customer, Order, Variant, OrderItem
from src.schema import ProductCreate, CustomerCreate, OrderCreate, VariantCreate, OrderItemCreate
from src.tasks.utils import fetch_shopify_products, fetch_shopify_orders, fetch_shopify_customers
from src import add_key_value_redis
from datetime import datetime, timedelta
import json
import asyncio
from sqlalchemy.sql import select

async def _sync_shopify_data(user_id: str, mode: str):
    async with get_session() as session:

        result = await session.execute(
            select(Integrations).where(
                Integrations.user_id == user_id,
                Integrations.platform == "shopify"
            )
        )
        integration = result.scalar_one_or_none()
        if not integration:
            print("No integration found")
            return

        access_token = integration.refresh_token 


        if mode == "full":
            products = await fetch_shopify_products(access_token, integration.shop_url)
            customers = await fetch_shopify_customers(access_token, integration.shop_url)
            orders = await fetch_shopify_orders(access_token, integration.shop_url)
        else: 
            last_sync = integration.last_synced_at or datetime.utcnow() - timedelta(days=7)
            products = await fetch_shopify_products(access_token, integration.shop_url, since=last_sync)
            customers = await fetch_shopify_customers(access_token, integration.shop_url, since=last_sync)
            orders = await fetch_shopify_orders(access_token, integration.shop_url, since=last_sync)


            await add_key_value_redis(f"shopify:products:{user_id}", json.dumps(products), expire=86400)
            await add_key_value_redis(f"shopify:customers:{user_id}", json.dumps(customers), expire=86400)
            await add_key_value_redis(f"shopify:orders:{user_id}", json.dumps(orders), expire=86400)


        await save_data_to_db(session, user_id, products, customers, orders)


        integration.last_synced_at = datetime.utcnow()
        await session.commit()

async def save_data_to_db(session: AsyncSession, user_id: str, products, customers, orders):
    for product_data in products:
        product_in = ProductCreate(**product_data)
        product = Product(**product_in.dict(), user_id=user_id)
        session.add(product)

    for customer_data in customers:
        customer_in = CustomerCreate(**customer_data)
        customer = Customer(**customer_in.dict(), user_id=user_id)
        session.add(customer)

    for order_data in orders:
        order_in = OrderCreate(**order_data)
        order = Order(**order_in.dict(), user_id=user_id)
        session.add(order)

    await session.commit()

@shared_task
def sync_shopify_data(user_id: str, mode: str = "full"):  # mode = "full" or "incremental"
    asyncio.run(_sync_shopify_data(user_id, mode))



