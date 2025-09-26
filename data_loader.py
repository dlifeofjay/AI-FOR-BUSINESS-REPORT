import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import date, timedelta
from dotenv import load_dotenv
from utils import load_config
from datetime import datetime, timedelta

def entry_db():

    cfg = load_config()
    server = cfg["server"]
    database = cfg["database"]


    connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    engine = create_engine(connection_string)

    query = """
    select concat(c.FirstName, ' ', LastName, ' ', MiddleInitial) as CustomerName, p.ProductName,
    concat(e.Employee_FirstName, ' ', e.Employee_LastName, ' ', e.Employee_middleInitial) as SalesPersonName,
    p.price, s.Quantity, s.Discount, ci.CityName
    from cities ci
    inner join customers c
    on ci.CityID = c.CityID
    inner join sales s
    on c.CustomerID = s.CustomerID
    inner join products p
    on s.ProductID = p.ProductId
    inner join employee e
    on e.EmployeeID = s.SalesPersonID
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def clean_data(df):
    df = df.copy()
    
    df['Revenue'] = df['price'] * df['Quantity'] * (1-df['Discount'])
    
    #creating a date column
    n = len(df)
    start_date = pd.Timestamp("2025-01-01")
    end_date = pd.Timestamp("2025-12-18")
    all_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    num_dates = len(all_dates)

    rows_per_date = n // num_dates

    dates_repeated = np.repeat(all_dates, rows_per_date)

    extra_rows = n - len(dates_repeated)
    if extra_rows > 0:
        dates_repeated = np.concatenate([dates_repeated, all_dates[:extra_rows]])
    df["Date"] = dates_repeated
    return df

def curr_prev_mon(df):
    today = datetime.now()
    current_month = today.month
    current_year = today.year

    prev_month_date = today.replace(day=1) - timedelta(days=1)
    prev_month = prev_month_date.month
    prev_year = prev_month_date.year

    current_df = df[(df['Date'].dt.month == current_month) & (df['Date'].dt.year == current_year)]
    prev_df= df[(df['Date'].dt.month == prev_month) & (df['Date'].dt.year == prev_year)]

    return current_df, prev_df