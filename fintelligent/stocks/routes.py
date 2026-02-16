from flask import Blueprint, render_template, request, jsonify
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import requests

stocks = Blueprint('stocks', __name__)


@stocks.route('/analyze-stock')
def analyze_stock_page():
    return render_template('analyze_stock.html')


@stocks.route('/get_clusters', methods=['GET'])
def get_clusters():
    """
    Fetch stock data using yfinance (free, robust for Indian markets)
    and perform clustering on volatility/returns.
    """
    symbol = request.args.get('symbol', 'INFY')
    
    # Auto-append .NS if not present and looks like Indian stock
    if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
        # Assumption: If it's a known Indian stock, append .NS. 
        # For simplicity, we default to NSE for common Indian tickers.
        # Ideally, user should provide the suffix, but we can be smart.
        symbol = f"{symbol}.NS"

    try:
        import yfinance as yf
        
        # Fetch last 1 year of data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")
        
        if df.empty:
             return jsonify({"error": f"No data found for symbol {symbol}. Try adding .NS or .BO suffix."}), 400

        # yfinance returns properly typed index (DatetimeIndex)
        df['Return'] = df['Close'].pct_change()
        df['Volatility'] = df['Return'].rolling(window=20).std()
        
        features = df[['Return', 'Volatility']].dropna()

        if len(features) < 10:
             return jsonify({"error": "Not enough historical data for analysis"}), 400

        # Clustering
        scaler = StandardScaler()
        X = scaler.fit_transform(features)
        
        # Adjust clusters based on data size
        n_clusters = 3
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        
        # Assign clusters to the features dataframe first
        features['Cluster'] = kmeans.fit_predict(X)
        
        # Join back to main df
        df = df.join(features[['Cluster']], how='left')
        
        # Prepare result (last 60 days)
        result_df = df.tail(60).reset_index()
        
        # Handle date formatting
        output = []
        for _, row in result_df.iterrows():
            output.append({
                "Date": row['Date'].isoformat(),
                "Close": row['Close'],
                "Return": row['Return'] if pd.notna(row['Return']) else 0,
                "Volatility": row['Volatility'] if pd.notna(row['Volatility']) else 0,
                "Cluster": int(row['Cluster']) if pd.notna(row['Cluster']) else -1
            })

        return jsonify({"clusters": output, "total_clusters": n_clusters, "symbol": symbol})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


