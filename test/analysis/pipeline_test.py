import pytest
import pandas as pd
from datetime import datetime
from src.analysis.pipeline import (
    load_data,
    prepare_data,
    compute_kpis,
    compute_weekly_monthly_revenue,
    revenue_chart_data_batch
)

@pytest.fixture
def sample_data():
    orders_data = {
        'order_id': ['order1', 'order2'],
        'customer_id': ['cust1', 'cust2'],
        'order_purchase_timestamp': ['2023-01-01', '2023-01-02'],
        'order_approved_at': ['2023-01-01', '2023-01-02']
    }
    
    order_items_data = {
        'order_id': ['order1', 'order2'],
        'price': [100.0, 200.0],
        'shipping_charges': [10.0, 20.0]
    }
    
    customers_data = {
        'customer_id': ['cust1', 'cust2'],
        'customer_name': ['John', 'Jane']
    }
    
    return (
        pd.DataFrame(order_items_data),
        pd.DataFrame(orders_data),
        pd.DataFrame(customers_data)
    )

def test_load_data(monkeypatch):
    mock_data = [
        pd.DataFrame({'order_id': ['order1']}),
        pd.DataFrame({'order_id': ['order1']}),
        pd.DataFrame({'customer_id': ['cust1']})
    ]
    
    def mock_read_csv(*args, **kwargs):
        return mock_data.pop(0)
    
    monkeypatch.setattr(pd, 'read_csv', mock_read_csv)
    
    result = load_data()
    assert len(result) == 3
    assert isinstance(result[0], pd.DataFrame)
    assert isinstance(result[1], pd.DataFrame)
    assert isinstance(result[2], pd.DataFrame)

def test_prepare_data(sample_data):
    df_order_items, df_orders, df_customers = sample_data
    result = prepare_data(df_order_items, df_orders, df_customers)
    
    assert isinstance(result, pd.DataFrame)
    assert 'revenue' in result.columns
    assert 'customer_id' in result.columns
    assert 'order_id' in result.columns
    assert result['revenue'].sum() == 330.0

def test_compute_kpis(sample_data):
    df_order_items, df_orders, df_customers = sample_data
    df_full = prepare_data(df_order_items, df_orders, df_customers)
    result = compute_kpis(df_full)
    
    assert isinstance(result, dict)
    assert 'order_volume' in result
    assert 'total_revenue' in result
    assert 'customer_spending' in result
    assert 'orders_per_customer' in result
    assert 'avg_customer_order' in result
    assert result['order_volume'] == 2
    assert result['total_revenue'] == 330.0

def test_compute_weekly_monthly_revenue(sample_data):
    df_order_items, df_orders, df_customers = sample_data
    df_full = prepare_data(df_order_items, df_orders, df_customers)
    weekly, monthly = compute_weekly_monthly_revenue(df_full)
    
    assert isinstance(weekly, pd.DataFrame)
    assert isinstance(monthly, pd.DataFrame)
    assert 'week_end_date' in weekly.columns
    assert 'weekly_revenue' in weekly.columns
    assert 'month_end_date' in monthly.columns
    assert 'monthly_revenue' in monthly.columns

def test_revenue_chart_data_batch(monkeypatch, sample_data):
    def mock_load_data():
        return sample_data
    
    def mock_prepare_data(*args):
        return prepare_data(*sample_data)
    
    monkeypatch.setattr('src.analysis.pipeline.load_data', mock_load_data)
    monkeypatch.setattr('src.analysis.pipeline.prepare_data', mock_prepare_data)
    
    result = revenue_chart_data_batch(freq='W', offset=0, limit=2)
    
    assert isinstance(result, dict)
    assert 'data' in result
    assert len(result['data']) <= 2

def test_revenue_chart_data_batch_with_dates(monkeypatch, sample_data):
    def mock_load_data():
        return sample_data
    
    def mock_prepare_data(*args):
        return prepare_data(*sample_data)
    
    monkeypatch.setattr('src.analysis.pipeline.load_data', mock_load_data)
    monkeypatch.setattr('src.analysis.pipeline.prepare_data', mock_prepare_data)
    
    result = revenue_chart_data_batch(
        freq='W',
        offset=0,
        limit=2,
        start_date='2023-01-01',
        end_date='2023-01-02'
    )
    
    assert isinstance(result, dict)
    assert 'data' in result
    assert len(result['data']) <= 2

def test_load_data_file_not_found(monkeypatch):
    def mock_read_csv(*args, **kwargs):
        raise FileNotFoundError("File not found")
    
    monkeypatch.setattr(pd, 'read_csv', mock_read_csv)
    
    with pytest.raises(FileNotFoundError):
        load_data()

def test_prepare_data_invalid_input():
    with pytest.raises(ValueError):
        prepare_data(
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame()
        )

def test_compute_kpis_empty_dataframe():
    with pytest.raises(LookupError):
        compute_kpis(pd.DataFrame())
