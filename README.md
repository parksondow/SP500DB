# S&P 500 股票數據下載工具

這是一個用於下載和管理 S&P 500 成分股歷史數據的 Python 程式。

## 功能特點

- 自動從維基百科抓取最新的 S&P 500 成分股列表
- 支援增量更新和完整重新下載兩種模式
- 將數據同時保存為 CSV 文件和 SQLite 數據庫
- 內建錯誤處理和進度顯示

## 安裝需求

```bash
pip install pandas
pip install yfinance
pip install requests
pip install beautifulsoup4
```

## 使用方法

1. 執行程式：
   ```bash
   python Claude500_250321b.py
   ```

2. 選擇更新模式：
   - 1: 增量更新（從上次更新日期到今天）
   - 2: 完整重新下載（從 2023 年開始）
   - 3: 退出程式

## 數據存儲

- CSV 文件：儲存在 `Stk_data` 目錄下
- SQLite 數據庫：`sp500_stock_data.db`

## 數據庫結構

stock_prices 表格包含以下欄位：
- ticker: 股票代碼
- date: 交易日期
- open: 開盤價
- high: 最高價
- low: 最低價
- close: 收盤價
- volume: 成交量

## 注意事項

- 程式會自動控制 API 請求頻率，避免超過限制
- 完整重新下載會刪除所有現有數據
- 建議定期執行增量更新以維持數據最新

## 作者

[Parkson Dow]

## 授權

MIT License
