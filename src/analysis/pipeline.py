import pandas as pd
from pandas.core.frame import DataFrame

base_path = 'C:\\Projects\\Contests\\Recruitment\\Ecommerce Order Dataset\\test'

def load_data() -> tuple[DataFrame, DataFrame, DataFrame]:
    try:
        df_orders = pd.read_csv(f'{base_path}\\df_Orders.csv')
        df_order_items = pd.read_csv(f'{base_path}\\df_OrderItems.csv')
        df_customers = pd.read_csv(f'{base_path}\\df_Customers.csv')
        return df_order_items, df_orders, df_customers
    except Exception as e:
        raise FileNotFoundError(f"Error loading data due to file not present: {e}")

def prepare_data(df_order_items: DataFrame, df_orders: DataFrame, df_customers: DataFrame) -> DataFrame:
    try:
        df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])
        df_orders['order_approved_at'] = pd.to_datetime(df_orders['order_approved_at'])
        df_order_items['revenue'] = df_order_items['price'] + df_order_items['shipping_charges']
        df_order_items.drop(['price', 'shipping_charges'], axis=1, inplace=True)
        df_orders_customers = pd.merge(df_orders, df_customers, on='customer_id')
        df_full = pd.merge(df_order_items, df_orders_customers, on='order_id', how='left')
        return df_full
    except Exception as e:
        raise ValueError(f"Cannot merge data: {e}")

def compute_kpis(df_full: DataFrame):
    try:
        order_volume = df_full['order_id'].nunique()
        total_revenue = df_full['revenue'].sum()
        customer_spending = df_full.groupby('customer_id')['revenue'].sum().reset_index(name='total_spent')
        orders_per_customer = df_full.groupby('customer_id')['order_id'].nunique().reset_index(name='order_count')
        avg_customer_order = total_revenue / order_volume if order_volume else 0
        return {
            "order_volume": order_volume,
            "total_revenue": total_revenue,
            "customer_spending": customer_spending,
            "orders_per_customer": orders_per_customer,
            "avg_customer_order": avg_customer_order
        }
    except Exception as e:
        raise LookupError(f"Column not found or computation error: {e}")

def compute_weekly_monthly_revenue(df_full: DataFrame):
    try:
        weekly_revenue = df_full.groupby(pd.Grouper(key='order_purchase_timestamp', freq='W'))['revenue'].sum().reset_index()
        weekly_revenue.columns = ['week_end_date', 'weekly_revenue']
        monthly_revenue = df_full.groupby(pd.Grouper(key='order_purchase_timestamp', freq='M'))['revenue'].sum().reset_index()
        monthly_revenue.columns = ['month_end_date', 'monthly_revenue']
        return weekly_revenue, monthly_revenue
    except Exception as e:
        raise ValueError(f"Error computing revenue aggregations: {e}")

def revenue_chart_data_batch(freq: str = 'W', offset: int = 0, limit: int = 10,
                             start_date: str = None, end_date: str = None) -> dict:
    try:
        df_order_items, df_orders, df_customers = load_data()
        df_full = prepare_data(df_order_items, df_orders, df_customers)
        if start_date and end_date:
            mask = (
                (df_full['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & 
                (df_full['order_purchase_timestamp'] <= pd.to_datetime(end_date))
            )
            df_full = df_full.loc[mask]
        revenue_df = df_full.groupby(pd.Grouper(key='order_purchase_timestamp', freq=freq))['revenue'].sum().reset_index()
        revenue_df.columns = ['date', 'revenue']
        revenue_df.sort_values(by='date', inplace=True)
        batch_data = revenue_df.iloc[offset:offset+limit]
        return {"data": batch_data.to_dict(orient="records")}
    except Exception as e:
        raise ValueError(f"Error in revenue_chart_data_batch: {e}")
