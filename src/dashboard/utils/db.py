from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

PROJECT_ROOT=Path(__file__).resolve().parents[3]
DB_PATH=PROJECT_ROOT/"data"/"db"/"nifty100.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def _read_sql(query,params=None):
    conn=get_connection()
    try:
        return pd.read_sql(query,conn,params=params or [])
    finally:
        conn.close()

@st.cache_data(ttl=600)
def get_companies():
    return _read_sql("SELECT * FROM companies ORDER BY company_name")

@st.cache_data(ttl=600)
def get_ratios(ticker,year=None):
    q="SELECT * FROM financial_ratios WHERE company_id=?"
    p=[ticker]
    if year is not None:
        q+=" AND year=?"
        p.append(year)
    q+=" ORDER BY year"
    return _read_sql(q,p)

@st.cache_data(ttl=600)
def get_pl(ticker):
    return _read_sql("SELECT * FROM profitandloss WHERE company_id=? ORDER BY year",[ticker])

@st.cache_data(ttl=600)
def get_bs(ticker):
    return _read_sql("SELECT * FROM balancesheet WHERE company_id=? ORDER BY year",[ticker])

@st.cache_data(ttl=600)
def get_cf(ticker):
    return _read_sql("SELECT * FROM cashflow WHERE company_id=? ORDER BY year",[ticker])

@st.cache_data(ttl=600)
def get_sectors():
    return _read_sql("SELECT * FROM sectors ORDER BY broad_sector, company_id")

@st.cache_data(ttl=600)
def get_peers(group_name):
    return _read_sql("SELECT * FROM peer_groups WHERE peer_group_name=? ORDER BY company_id",[group_name])

@st.cache_data(ttl=600)
def get_peer_groups():
    return _read_sql("SELECT DISTINCT peer_group_name FROM peer_groups ORDER BY peer_group_name")

@st.cache_data(ttl=600)
def get_valuation(ticker):
    conn=get_connection()
    try:
        t=pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' AND name='valuation'",conn)
        if t.empty:
            return pd.DataFrame()
        return pd.read_sql("SELECT * FROM valuation WHERE company_id=?",conn,params=[ticker])
    finally:
        conn.close()

@st.cache_data(ttl=600)
def latest_ratios():
    return _read_sql("""
    WITH ranked AS(
      SELECT *,ROW_NUMBER() OVER(PARTITION BY company_id ORDER BY CAST(substr(year,-4) AS INTEGER) DESC) rn
      FROM financial_ratios WHERE year<>'TTM'
    )
    SELECT * FROM ranked WHERE rn=1
    """)

@st.cache_data(ttl=600)
def latest_market_data():
    return _read_sql("SELECT * FROM market_cap WHERE year=(SELECT MAX(year) FROM market_cap)")
