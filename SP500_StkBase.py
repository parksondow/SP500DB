import pandas as pd
import yfinance as yf
import sqlite3
import datetime
import time
import requests
from bs4 import BeautifulSoup
import os

def get_sp500_tickers():
    """從維基百科獲取S&P500股票代碼"""
    print("正在從維基百科下載S&P500股票代碼...")
    
    # 維基百科S&P500成分股頁面
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    # 發送請求並解析HTML
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 找到包含股票信息的表格
    table = soup.find('table', {'class': 'wikitable'})
    
    # 初始化列表
    tickers = []
    company_names = []
    
    # 解析表格數據
    for row in table.find_all('tr')[1:]:  # 跳過表頭
        cols = row.find_all('td')
        if len(cols) >= 2:
            ticker = cols[0].text.strip()
            company = cols[1].text.strip()
            tickers.append(ticker)
            company_names.append(company)
    
    # 創建DataFrame
    df = pd.DataFrame({
        'ticker': tickers,
        'company': company_names
    })
    
    # 保存到CSV文件
    df.to_csv("sp500StkCode.csv", index=False)
    print(f"已將{len(df)}個股票代碼保存到sp500StkCode.csv")
    
    return df

def get_latest_date_from_db():
    """取得資料庫中最新的日期"""
    try:
        conn = sqlite3.connect('sp500_stock_data.db')
        cursor = conn.cursor()
        
        # 檢查表格是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='stock_prices'
        """)
        
        if cursor.fetchone() is None:
            conn.close()
            return None
            
        cursor.execute("SELECT MAX(date) FROM stock_prices")
        latest_date = cursor.fetchone()[0]
        conn.close()
        return latest_date
    except sqlite3.OperationalError:
        return None

def get_update_choice():
    """取得使用者更新選擇"""
    while True:
        print("\n請選擇更新模式：")
        print("1. 增量更新（從上次更新日期到今天）")
        print("2. 完整重新下載")
        print("3. 退出程式")
        choice = input("請輸入選擇 (1-3): ")
        if choice in ['1', '2', '3']:
            return choice

def download_stock_data(tickers, start_date, is_update=False):
    """使用yfinance下載股票資料"""
    if is_update:
        print(f"正在更新從 {start_date} 到今天的資料...")
    else:
        print(f"開始完整下載從 {start_date} 起的股價資料...")
    
    # 建立Stk_data目錄
    os.makedirs("Stk_data", exist_ok=True)
    
    # 連接SQLite資料庫
    conn = sqlite3.connect('sp500_stock_data.db')
    cursor = conn.cursor()
    
    # 創建表格
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_prices (
        ticker TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        PRIMARY KEY (ticker, date)
    )
    ''')
    
    # 設置下載進度追蹤
    total = len(tickers)
    
    # 迭代每個股票代碼
    for i, ticker in enumerate(tickers, 1):
        try:
            print(f"處理 {ticker} ({i}/{total})...")
            
            # 下載數據
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date)
            
            if data.empty:
                print(f"警告: {ticker} 沒有數據")
                continue
            
            # 儲存為CSV檔案（直接使用yfinance的股票代碼）
            csv_filename = os.path.join("Stk_data", f"{ticker.replace('.', '-')}.csv")
            data.to_csv(csv_filename)
            print(f"已將{ticker}的資料儲存到 {csv_filename}")
            
            # 準備插入資料庫的數據
            for date, row in data.iterrows():
                cursor.execute('''
                INSERT OR REPLACE INTO stock_prices (ticker, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticker,
                    date.strftime('%Y-%m-%d'),
                    row['Open'],
                    row['High'],
                    row['Low'],
                    row['Close'],
                    row['Volume']
                ))
            
            # 每5個公司提交一次，避免過多待處理事務
            if i % 5 == 0:
                conn.commit()
                print(f"已完成 {i}/{total} 公司的數據下載")
            
            # 避免超過API限制
            time.sleep(1)
        
        except Exception as e:
            print(f"下載 {ticker} 時發生錯誤: {e}")
    
    # 最後的提交
    conn.commit()
    print("所有數據已成功下載並存儲到資料庫")
    
    # 建立索引以加快查詢
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker ON stock_prices (ticker)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON stock_prices (date)')
    
    # 關閉資料庫連接
    conn.close()

def main():
    """主函數"""
    choice = get_update_choice()
    
    if choice == '3':
        print("程式結束")
        return
        
    # 下載S&P500股票代碼
    sp500_df = get_sp500_tickers()
    
    if choice == '1':  # 增量更新
        latest_date = get_latest_date_from_db()
        if latest_date:
            # 將日期字串轉換為datetime物件
            latest_date = datetime.datetime.strptime(latest_date, '%Y-%m-%d')
            today = datetime.datetime.now()
            
            # 計算下一天的日期
            next_date = latest_date + datetime.timedelta(days=1)
            
            # 如果最新數據日期是今天或未來日期，則不需更新
            if next_date.date() >= today.date():
                print(f"資料已經是最新的（最新日期：{latest_date.strftime('%Y-%m-%d')}）")
                return
                
            # 設定為下一天開始更新
            start_date = next_date.strftime('%Y-%m-%d')
            print(f"將從 {start_date} 開始更新資料...")
            download_stock_data(sp500_df['ticker'].tolist(), start_date, is_update=True)
        else:
            print("\n找不到現有資料庫或表格。")
            while True:
                subchoice = input("是否要執行完整下載？(y/n): ")
                if subchoice.lower() == 'y':
                    print("開始執行完整下載...")
                    download_stock_data(sp500_df['ticker'].tolist(), "2023-01-01")
                    break
                elif subchoice.lower() == 'n':
                    print("操作已取消")
                    return
                else:
                    print("請輸入 y 或 n")
    
    elif choice == '2':  # 完整重新下載
        confirm = input("這將會覆蓋所有現有資料，確定要繼續嗎？(y/n): ")
        if confirm.lower() == 'y':
            # 刪除現有的資料庫和CSV文件
            if os.path.exists('sp500_stock_data.db'):
                os.remove('sp500_stock_data.db')
            if os.path.exists('Stk_data'):
                import shutil
                shutil.rmtree('Stk_data')
            download_stock_data(sp500_df['ticker'].tolist(), "2023-01-01")
        else:
            print("操作已取消")
            return
    
    # 確認更新後的資料
    conn = sqlite3.connect('sp500_stock_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM stock_prices")
    count = cursor.fetchone()[0]
    print(f"\n資料庫中共有 {count} 條股價記錄")
    
    # 顯示最新的資料日期
    cursor.execute("SELECT MAX(date) FROM stock_prices")
    latest_date = cursor.fetchone()[0]
    print(f"資料更新至: {latest_date}")
    
    conn.close()

if __name__ == "__main__":
    main()