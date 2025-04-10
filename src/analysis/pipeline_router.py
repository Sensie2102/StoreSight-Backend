from fastapi import APIRouter, Depends, Request, HTTPException
from .pipeline import load_data,prepare_data,compute_kpis, revenue_chart_data_batch, compute_weekly_monthly_revenue
from ..authentication.utils import get_current_user
from ..schema import UserResponse

pipeline_router=APIRouter(prefix="/analytics",tags=["analytics"])

@pipeline_router.get('/kpis')
def get_kpis(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        df_order_items, df_orders, df_customers = load_data()
        df_full = prepare_data(df_order_items, df_orders, df_customers)
        result = compute_kpis(df_full)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@pipeline_router.get('/revenue_batch')
def get_revenue_batch(freq: str = 'W', offset: int = 0, limit: int = 10, start_date: str = None, end_date: str = None,current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        result = revenue_chart_data_batch(freq=freq, offset=offset, limit=limit, start_date=start_date, end_date=end_date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@pipeline_router.get('/revenue_all')
def get_revenue_all(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        df_order_items, df_orders, df_customers = load_data()
        df_full = prepare_data(df_order_items, df_orders, df_customers)
        weekly, monthly = compute_weekly_monthly_revenue(df_full)
        return {
            "weekly_revenue": weekly.to_dict(orient='records'),
            "monthly_revenue": monthly.to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))