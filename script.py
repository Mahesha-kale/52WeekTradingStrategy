"""
Indian Stock Screening Strategy
================================

This script screens Indian stocks based on specific technical criteria:
1. Stock is in the first half of its 52-week range
2. Price is in 75%-100% of current month candle range
3. Weekly candle is green or shows increased buying

Supported Indian Market Indices:
--------------------------------
INDEX CODE      | NAME                  | # STOCKS | MARKET CAP
----------------|----------------------|----------|-------------------
^NSEI           | NIFTY 50             | 50       | Large Cap
^CRSLDX         | NIFTY 500            | 200+     | Large + Mid + Small
^BSESN          | SENSEX               | 30       | Large Cap (BSE)
^CNX100         | NIFTY 100            | 100      | Large Cap
NIFTY_MIDCAP    | NIFTY Midcap         | 50       | Mid Cap

Usage:
------
1. Configure PORTFOLIO_CAPITAL and INDEX at the bottom of this file
2. Run the script: python script.py
3. Review the qualifying stocks that meet all criteria

"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class IndianStockStrategy:
    def __init__(self, portfolio_capital=10000, index="^NSEI"):
        """
        Initialize the strategy with portfolio capital and index selection
        
        Args:
            portfolio_capital: Total capital available for trading
            index: Index to screen stocks from
                   - "^NSEI" : NIFTY 50 (50 stocks)
                   - "^CRSLDX" : NIFTY 500 (500 stocks)
                   - "^BSESN" : SENSEX (30 stocks)
                   - "^CNX100" : NIFTY 100 (100 stocks)
                   - "NIFTY_MIDCAP" : NIFTY Midcap (custom list)
        """
        self.portfolio_capital = portfolio_capital
        self.max_risk_per_trade = 0.02  # 2%
        self.max_position_size = 0.10   # 10%
        self.max_risk_amount = self.portfolio_capital * self.max_risk_per_trade
        self.max_position_amount = self.portfolio_capital * self.max_position_size
        
        # Fetch list of Indian stocks using yfinance NSE indices
        self.indian_stocks = self._get_nifty_symbols(index=index)
        print(f"\n✓ Loaded {len(self.indian_stocks)} stocks for screening\n")

    def _get_fallback_stocks(self, index):
        """
        Get fallback stock lists for different Indian indices
        """
        fallback_lists = {
            # NIFTY 50 - Top 50 large-cap stocks
            "^NSEI": [
                'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
                'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
                'LT.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS', 'WIPRO.NS',
                'TITAN.NS', 'ULTRACEMCO.NS', 'ONGC.NS', 'TATASTEEL.NS', 'ADANIPORTS.NS',
                'POWERGRID.NS', 'NESTLEIND.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS',
                'TECHM.NS', 'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS',
                'COALINDIA.NS', 'NTPC.NS', 'JSWSTEEL.NS', 'TATAMOTORS.NS', 'M&M.NS',
                'GRASIM.NS', 'BRITANNIA.NS', 'SHREECEM.NS', 'EICHERMOT.NS', 'UPL.NS',
                'HINDALCO.NS', 'BAJAJ-AUTO.NS', 'APOLLOHOSP.NS', 'HEROMOTOCO.NS',
                'BPCL.NS', 'IOC.NS', 'INDUSINDBK.NS', 'AXISBANK.NS', 'VEDL.NS',
                'ADANITRANS.NS', 'TATACONSUM.NS'
            ],
            
            # SENSEX - Top 30 stocks
            "^BSESN": [
                'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
                'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
                'LT.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS', 'BAJFINANCE.NS',
                'TITAN.NS', 'ULTRACEMCO.NS', 'ONGC.NS', 'TATASTEEL.NS', 'POWERGRID.NS',
                'NESTLEIND.NS', 'BAJAJFINSV.NS', 'TECHM.NS', 'SUNPHARMA.NS',
                'NTPC.NS', 'JSWSTEEL.NS', 'TATAMOTORS.NS', 'M&M.NS', 'AXISBANK.NS', 'INDUSINDBK.NS'
            ],
            
            # NIFTY 100 - Includes NIFTY 50 + Next 50
            "^CNX100": [
                # NIFTY 50 stocks
                'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
                'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
                'LT.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS', 'WIPRO.NS',
                'TITAN.NS', 'ULTRACEMCO.NS', 'ONGC.NS', 'TATASTEEL.NS', 'ADANIPORTS.NS',
                'POWERGRID.NS', 'NESTLEIND.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS',
                'TECHM.NS', 'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS',
                'COALINDIA.NS', 'NTPC.NS', 'JSWSTEEL.NS', 'TATAMOTORS.NS', 'M&M.NS',
                'GRASIM.NS', 'BRITANNIA.NS', 'SHREECEM.NS', 'EICHERMOT.NS', 'UPL.NS',
                'HINDALCO.NS', 'BAJAJ-AUTO.NS', 'APOLLOHOSP.NS', 'HEROMOTOCO.NS',
                'BPCL.NS', 'IOC.NS', 'INDUSINDBK.NS', 'AXISBANK.NS', 'VEDL.NS',
                'ADANITRANS.NS', 'TATACONSUM.NS',
                # Next 50 stocks
                'ADANIENT.NS', 'SIEMENS.NS', 'DLF.NS', 'GODREJCP.NS', 'DABUR.NS',
                'HAVELLS.NS', 'TRENT.NS', 'BEL.NS', 'BANKBARODA.NS', 'PNB.NS',
                'CANBK.NS', 'UNIONBANK.NS', 'INDHOTEL.NS', 'CONCOR.NS', 'BOSCHLTD.NS',
                'TATAPOWER.NS', 'TORNTPHARM.NS', 'COLPAL.NS', 'MARICO.NS', 'PIDILITIND.NS',
                'GLAND.NS', 'BERGEPAINT.NS', 'LUPIN.NS', 'AMBUJACEM.NS', 'ACC.NS',
                'ICICIPRULI.NS', 'SBILIFE.NS', 'HDFCLIFE.NS', 'BAJAJHLDNG.NS', 'MOTHERSON.NS',
                'VOLTAS.NS', 'AUBANK.NS', 'BANDHANBNK.NS', 'IDFCFIRSTB.NS', 'PEL.NS',
                'GODREJPROP.NS', 'OBEROIRLTY.NS', 'PRESTIGE.NS', 'MCDOWELL-N.NS', 'ABB.NS',
                'SBICARD.NS', 'INDIGO.NS', 'PETRONET.NS', 'MRF.NS', 'PAGEIND.NS',
                'ALKEM.NS', 'BIOCON.NS', 'DMART.NS', 'NAUKRI.NS', 'ZOMATO.NS'
            ],
            
            # NIFTY 500 - Comprehensive list (top stocks from NIFTY 500)
            "^CRSLDX": [
                # All NIFTY 100 stocks plus additional mid-cap and small-cap stocks
                'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
                'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
                'LT.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS', 'WIPRO.NS',
                'TITAN.NS', 'ULTRACEMCO.NS', 'ONGC.NS', 'TATASTEEL.NS', 'ADANIPORTS.NS',
                'POWERGRID.NS', 'NESTLEIND.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS',
                'TECHM.NS', 'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS',
                'COALINDIA.NS', 'NTPC.NS', 'JSWSTEEL.NS', 'TATAMOTORS.NS', 'M&M.NS',
                'GRASIM.NS', 'BRITANNIA.NS', 'SHREECEM.NS', 'EICHERMOT.NS', 'UPL.NS',
                'HINDALCO.NS', 'BAJAJ-AUTO.NS', 'APOLLOHOSP.NS', 'HEROMOTOCO.NS',
                'BPCL.NS', 'IOC.NS', 'INDUSINDBK.NS', 'AXISBANK.NS', 'VEDL.NS',
                'ADANITRANS.NS', 'TATACONSUM.NS', 'ADANIENT.NS', 'SIEMENS.NS', 'DLF.NS',
                # Additional NIFTY 500 stocks
                'GODREJCP.NS', 'DABUR.NS', 'HAVELLS.NS', 'TRENT.NS', 'BEL.NS',
                'BANKBARODA.NS', 'PNB.NS', 'CANBK.NS', 'UNIONBANK.NS', 'INDHOTEL.NS',
                'CONCOR.NS', 'BOSCHLTD.NS', 'TATAPOWER.NS', 'TORNTPHARM.NS', 'COLPAL.NS',
                'MARICO.NS', 'PIDILITIND.NS', 'GLAND.NS', 'BERGEPAINT.NS', 'LUPIN.NS',
                'AMBUJACEM.NS', 'ACC.NS', 'ICICIPRULI.NS', 'SBILIFE.NS', 'HDFCLIFE.NS',
                'BAJAJHLDNG.NS', 'MOTHERSON.NS', 'VOLTAS.NS', 'AUBANK.NS', 'BANDHANBNK.NS',
                'IDFCFIRSTB.NS', 'PEL.NS', 'GODREJPROP.NS', 'OBEROIRLTY.NS', 'PRESTIGE.NS',
                'MCDOWELL-N.NS', 'ABB.NS', 'SBICARD.NS', 'INDIGO.NS', 'PETRONET.NS',
                'MRF.NS', 'PAGEIND.NS', 'ALKEM.NS', 'BIOCON.NS', 'DMART.NS',
                'NAUKRI.NS', 'ZOMATO.NS', 'PAYTM.NS', 'POLICYBZR.NS', 'ZEEL.NS',
                'DIXON.NS', 'LTIM.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'MPHASIS.NS',
                'LTTS.NS', 'HAPPSTMNDS.NS', 'CROMPTON.NS', 'WHIRLPOOL.NS', 'CUMMINSIND.NS',
                'ESCORTS.NS', 'ASHOKLEY.NS', 'BALKRISIND.NS', 'APOLLOTYRE.NS', 'CEATLTD.NS',
                'EXIDEIND.NS', 'AMARAJABAT.NS', 'FORCEMOT.NS', 'TVSMOTOR.NS', 'BAJAJHIND.NS',
                'METROPOLIS.NS', 'LALPATHLAB.NS', 'AUROPHARMA.NS', 'IPCALAB.NS', 'LAURUSLABS.NS',
                'NATCOPHARM.NS', 'PFIZER.NS', 'ABBOTINDIA.NS', 'GLAXO.NS', 'SANOFI.NS',
                'CENTRALBK.NS', 'INDIANB.NS', 'MAHABANK.NS', 'CHOLAFIN.NS',
                'LICHSGFIN.NS', 'SHRIRAMFIN.NS', 'IIFL.NS', 'RECLTD.NS', 'PFC.NS',
                'IRCTC.NS', 'IEX.NS', 'IRFC.NS', 'RAILTEL.NS', 'HAL.NS',
                'BDL.NS', 'COCHINSHIP.NS', 'MAZDA.NS', 'GAIL.NS', 'GMRINFRA.NS',
                'ADANIGREEN.NS', 'ADANIPOWER.NS', 'TATAELXSI.NS', 'MFSL.NS', 'GNFC.NS',
                'DEEPAKNTR.NS', 'BALRAMCHIN.NS', 'TATACHEM.NS', 'PIIND.NS',
                'SRF.NS', 'ATUL.NS', 'CHAMBLFERT.NS', 'COROMANDEL.NS', 'MANAPPURAM.NS',
                'MUTHOOTFIN.NS', 'SJVN.NS', 'NHPC.NS', 'ZENSARTECH.NS', 'INFY.NS',
                'INTELLECT.NS', 'SONATSOFTW.NS', 'KPITTECH.NS', 'CYIENT.NS', 'RBLBANK.NS',
                'FEDERALBNK.NS', 'IDBI.NS', 'CESC.NS', 'ADANIENSOL.NS', 'JSL.NS',
                'SAIL.NS', 'JINDALSTEL.NS', 'NMDC.NS', 'NATIONALUM.NS', 'RATNAMANI.NS',
                'WELCORP.NS', 'RELAXO.NS', 'BATA.NS', 'VBL.NS', 'TATACOMM.NS',
                'BHARATFORG.NS', 'TIMKEN.NS', 'SCHNEIDER.NS', 'CROMPTON.NS', 'KEI.NS',
                'POLYCAB.NS', 'APLAPOLLO.NS', 'ASTRAL.NS', 'SUPREMEIND.NS', 'NILKAMAL.NS',
                'SYMPHONY.NS', 'BLUESTARCO.NS', 'VGUARD.NS', 'FINEORG.NS', 'EIDPARRY.NS',
                'RAJESHEXPO.NS', 'TITAN.NS', 'MANYAVAR.NS', 'ABFRL.NS',
                'TRENT.NS', 'SHOPERSTOP.NS', 'JUBLFOOD.NS', 'WESTLIFE.NS', 'SAPPHIRE.NS',
                'GOCOLORS.NS', 'VMART.NS', 'BSOFT.NS', 'IRCON.NS', 'NBCC.NS',
                'REDINGTON.NS', 'AMBER.NS', 'ROUTE.NS', 'GICRE.NS', 'NIACL.NS',
                'STARHEALTH.NS', 'MAHLIFE.NS', 'ITI.NS', 'MTNL.NS', 'PVR.NS',
                'PVRINOX.NS', 'BASF.NS', 'HONAUT.NS', '3MINDIA.NS',
                'GILLETTE.NS', 'BAYERCROP.NS', 'GRINDWELL.NS', 'CARBORUNIV.NS', 'SKFINDIA.NS'
            ],
            
            # NIFTY Midcap
            "NIFTY_MIDCAP": [
                'GODREJCP.NS', 'DABUR.NS', 'HAVELLS.NS', 'TRENT.NS', 'BEL.NS',
                'BANKBARODA.NS', 'PNB.NS', 'CANBK.NS', 'UNIONBANK.NS', 'INDHOTEL.NS',
                'BOSCHLTD.NS', 'TATAPOWER.NS', 'TORNTPHARM.NS', 'COLPAL.NS', 'MARICO.NS',
                'PIDILITIND.NS', 'GLAND.NS', 'BERGEPAINT.NS', 'LUPIN.NS', 'AMBUJACEM.NS',
                'ACC.NS', 'ICICIPRULI.NS', 'SBILIFE.NS', 'HDFCLIFE.NS', 'MOTHERSON.NS',
                'VOLTAS.NS', 'AUBANK.NS', 'BANDHANBNK.NS', 'IDFCFIRSTB.NS', 'PEL.NS',
                'GODREJPROP.NS', 'OBEROIRLTY.NS', 'PRESTIGE.NS', 'ABB.NS', 'SBICARD.NS',
                'INDIGO.NS', 'PETRONET.NS', 'MRF.NS', 'ALKEM.NS', 'BIOCON.NS',
                'DMART.NS', 'NAUKRI.NS', 'DIXON.NS', 'LTIM.NS', 'PERSISTENT.NS',
                'COFORGE.NS', 'MPHASIS.NS', 'LTTS.NS', 'CROMPTON.NS', 'CUMMINSIND.NS'
            ]
        }
        
        return fallback_lists.get(index, fallback_lists["^NSEI"])
    
    # Dynamically fetch list of Indian stocks using yfinance NSE indices (e.g. NIFTY 50/NIFTY 100)
    def _get_nifty_symbols(self, index="^NSEI"):
        """
        Fetch a list of Indian stock symbols from Yahoo Finance index constituents.
        Returns a list of NSE symbols with '.NS' suffix.
        
        Supported indices:
            - "^NSEI" : NIFTY 50 (50 stocks)
            - "^CRSLDX" : NIFTY 500 (500 stocks)
            - "^BSESN" : SENSEX (30 stocks)
            - "^CNX100" : NIFTY 100 (100 stocks)
            - "NIFTY_MIDCAP" : NIFTY Midcap (50 stocks)
        
        Note: yfinance doesn't provide constituents for indices reliably,
        so we use curated fallback lists for each index.
        """
        # Map of index codes to readable names for logging
        index_names = {
            "^NSEI": "NIFTY 50",
            "^CRSLDX": "NIFTY 500",
            "^BSESN": "SENSEX",
            "^CNX100": "NIFTY 100",
            "NIFTY_MIDCAP": "NIFTY Midcap"
        }
        
        index_name = index_names.get(index, index)
        print(f"📊 Fetching constituents for {index_name}...")
        
        # Try fetching from yfinance (usually doesn't work for Indian indices)
        try:
            nifty_etf = yf.Ticker(index)
            if hasattr(nifty_etf, 'constituents'):
                constituents = nifty_etf.constituents
                if constituents is not None and len(constituents) > 0:
                    print(f"✓ Successfully fetched {len(constituents)} stocks from yfinance")
                    # Use .NS suffix for NSE scripts
                    return [symbol+".NS" if not symbol.endswith('.NS') else symbol for symbol in constituents]
        except Exception as e:
            pass  # Silently fail and use fallback
        
        # Use fallback list
        fallback_stocks = self._get_fallback_stocks(index)
        print(f"✓ Using curated list of {len(fallback_stocks)} {index_name} stocks")
        return fallback_stocks
        
    def get_market_cap(self, symbol):
        """
        Get market cap in crores (Note: This is a simplified approach)
        In real implementation, you'd need actual market cap data from financial APIs
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            market_cap_usd = info.get('marketCap', 0)
            # Convert to INR crores (approximate: 1 USD = 83 INR, 1 crore = 10M)
            market_cap_crores = (market_cap_usd * 83) / 10000000
            return market_cap_crores
        except:
            return 0
    
    def get_stock_data(self, symbol, period="1y"):
        """
        Get stock data for analysis
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data
        except:
            return None
    
    def calculate_52_week_range(self, data):
        """
        Calculate 52-week high and low
        """
        week_52_high = data['High'].max()
        week_52_low = data['Low'].min()
        midpoint = (week_52_high + week_52_low) / 2
        return week_52_high, week_52_low, midpoint
    
    def check_first_half_criterion(self, current_price, week_52_high, week_52_low):
        """
        Check if current price is in first half of 52-week range
        """
        midpoint = (week_52_high + week_52_low) / 2
        return week_52_low <= current_price <= midpoint
    
    def check_monthly_candle_criterion(self, data, current_price):
        """
        Check if price lies in 75%-100% of current month candle range
        """
        # Get current month data
        current_month = data.last('30D')
        if len(current_month) == 0:
            return False
        
        monthly_high = current_month['High'].max()
        monthly_low = current_month['Low'].min()
        range_75_percent = monthly_low + 0.75 * (monthly_high - monthly_low)
        
        return range_75_percent <= current_price <= monthly_high
    
    def check_weekly_candle_criterion(self, data):
        """
        Check if weekly candle is green or has more buying than previous week
        """
        # Get last two weeks of data
        weekly_data = data.resample('W').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        if len(weekly_data) < 2:
            return False
        
        current_week = weekly_data.iloc[-1]
        previous_week = weekly_data.iloc[-2]
        
        # Check if current week is green
        is_green = current_week['Close'] > current_week['Open']
        
        # Check if current week has higher high than previous week
        higher_high = current_week['High'] > previous_week['High']
        
        return is_green or higher_high
    
    def calculate_position_size(self, current_price, stop_loss, target_price):
        """
        Calculate position size based on risk management rules
        """
        # Calculate risk per share
        risk_per_share = current_price - stop_loss
        
        if risk_per_share <= 0:
            return 0, 0, 0  # Invalid setup
        
        # Calculate reward per share
        reward_per_share = target_price - current_price
        
        # Check risk-reward ratio (should be > 1:1)
        risk_reward_ratio = reward_per_share / risk_per_share
        if risk_reward_ratio <= 1:
            return 0, 0, 0  # Risk-reward not favorable
        
        # Calculate max quantity based on risk limit (2% rule)
        max_qty_risk = int(self.max_risk_amount / risk_per_share)
        
        # Calculate max quantity based on position size limit (10% rule)
        max_qty_position = int(self.max_position_amount / current_price)
        
        # Take minimum of both constraints
        quantity = min(max_qty_risk, max_qty_position)
        
        if quantity <= 0:
            return 0, 0, 0
        
        # Calculate actual risk and potential profit
        actual_risk = quantity * risk_per_share
        potential_profit = quantity * reward_per_share
        
        return quantity, actual_risk, potential_profit
    
    def screen_stock(self, symbol):
        """
        Screen a single stock based on all criteria
        """
        # Check market cap
        market_cap = self.get_market_cap(symbol)
        if market_cap < 1000:  # Less than 1000 crores
            return None
        
        # Get stock data
        data = self.get_stock_data(symbol)
        if data is None or len(data) < 50:  # Need sufficient data
            return None
        
        current_price = data['Close'].iloc[-1]
        week_52_high, week_52_low, midpoint = self.calculate_52_week_range(data)
        
        # Check all criteria
        criterion_1 = self.check_first_half_criterion(current_price, week_52_high, week_52_low)
        criterion_2 = self.check_monthly_candle_criterion(data, current_price)
        criterion_3 = self.check_weekly_candle_criterion(data)
        
        if not (criterion_1 and criterion_2 and criterion_3):
            return None
        
        # Calculate position sizing
        stop_loss = week_52_low
        target_price = week_52_high
        quantity, risk_amount, profit_potential = self.calculate_position_size(
            current_price, stop_loss, target_price
        )
        
        if quantity <= 0:
            return None
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'quantity': quantity,
            'risk_amount': risk_amount,
            'profit_potential': profit_potential,
            'risk_reward_ratio': profit_potential / risk_amount if risk_amount > 0 else 0,
            'market_cap': market_cap,
            '52_week_high': week_52_high,
            '52_week_low': week_52_low,
            'position_value': current_price * quantity,
            'criterion_1': criterion_1,
            'criterion_2': criterion_2,
            'criterion_3': criterion_3
        }
    
    def screen_all_stocks(self):
        """
        Screen all stocks and return qualifying ones
        """
        qualified_stocks = []
        
        print("Screening stocks...")
        for i, symbol in enumerate(self.indian_stocks):
            print(f"Processing {symbol} ({i+1}/{len(self.indian_stocks)})")
            result = self.screen_stock(symbol)
            if result:
                qualified_stocks.append(result)
        
        return qualified_stocks

# ============================================================================
# MAIN SCRIPT - CONFIGURE YOUR SETTINGS HERE
# ============================================================================

# Configuration
PORTFOLIO_CAPITAL = 10000
INDEX = "^CRSLDX"  # ← Change this to select different index

# Available indices:
# "^NSEI"        - NIFTY 50 (50 large-cap stocks)
# "^CRSLDX"      - NIFTY 500 (200+ stocks - comprehensive coverage)
# "^BSESN"       - SENSEX (30 top stocks)
# "^CNX100"      - NIFTY 100 (100 large-cap stocks)
# "NIFTY_MIDCAP" - NIFTY Midcap (50 mid-cap stocks)

# Initialize strategy
print("=" * 60)
print("          INDIAN STOCK SCREENING STRATEGY")
print("=" * 60)
print(f"\n💰 Portfolio Capital: ₹{PORTFOLIO_CAPITAL:,}")
print(f"⚠️  Max Risk per Trade: 2% (₹{PORTFOLIO_CAPITAL * 0.02:,.0f})")
print(f"📊 Max Position Size: 10% (₹{PORTFOLIO_CAPITAL * 0.10:,.0f})")

# Initialize and run strategy
strategy = IndianStockStrategy(portfolio_capital=PORTFOLIO_CAPITAL, index=INDEX)

print("=" * 60)
print("Starting stock screening...")
print("=" * 60 + "\n")

qualified_stocks = strategy.screen_all_stocks()

# Display results
print("\n" + "=" * 60)
print("          SCREENING RESULTS")
print("=" * 60)
print(f"\n✓ Found {len(qualified_stocks)} qualifying stocks\n")

if qualified_stocks:
    for i, stock in enumerate(qualified_stocks, 1):
        print(f"\n{i}. {stock['symbol']}")
        print(f"   Entry Price: ₹{stock['entry_price']:.2f}")
        print(f"   Stop Loss: ₹{stock['stop_loss']:.2f}")
        print(f"   Target: ₹{stock['target_price']:.2f}")
        print(f"   Quantity: {stock['quantity']}")
        print(f"   Risk:Reward = 1:{stock['risk_reward_ratio']:.2f}")
else:
    print("No stocks meet all criteria at this time.")