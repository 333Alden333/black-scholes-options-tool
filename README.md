# Black-Scholes Options Trading Confirmation Tool

A comprehensive Python-based Black-Scholes options pricing and trading confirmation system designed to help options traders make informed decisions by calculating fair values, analyzing Greeks, and providing clear buy/sell/hold recommendations.

## 🚀 Features

- **Complete Black-Scholes Implementation**: Accurate theoretical option pricing with dividend adjustments
- **All Greeks Calculations**: Delta, Gamma, Theta, Vega, and Rho for comprehensive risk analysis
- **Implied Volatility Calculation**: Newton-Raphson method for extracting IV from market prices
- **Trading Confirmation System**: Automated recommendations with confidence levels and edge analysis
- **Command Line Interface**: User-friendly CLI with interactive and batch modes
- **Multiple Output Formats**: Clean text display and JSON output for integration

## 📋 Requirements

```bash
pip install numpy scipy
```

## 🔧 Installation

1. Clone this repository:
```bash
git clone https://github.com/333Alden333/black-scholes-options-tool.git
cd black-scholes-options-tool
```

2. Install dependencies:
```bash
pip install numpy scipy
```

3. Make the CLI executable:
```bash
chmod +x options_trading_cli.py
```

## 📖 Usage

### Command Line Mode

Analyze a specific option with all parameters:

```bash
python3 options_trading_cli.py --symbol AAPL --strike 150 --expiry 2025-09-19 \
  --type call --underlying-price 155 --risk-free-rate 0.05 \
  --current-price 5.50 --volatility 0.25
```

### Interactive Mode

For step-by-step input:

```bash
python3 options_trading_cli.py --interactive
```

### JSON Output

For programmatic use:

```bash
python3 options_trading_cli.py --output-format json --symbol AAPL --strike 150 \
  --expiry 2025-09-19 --type call --underlying-price 155 --risk-free-rate 0.05 \
  --current-price 5.50 --volatility 0.25
```

## 📊 Understanding the Output

### Sample Output Explanation

```
============================================================
BLACK-SCHOLES ANALYSIS RESULTS
============================================================

THEORETICAL PRICING:
  Fair Value:          $9.57
  Implied Volatility:  25.0%

THE GREEKS:
  Delta (Δ):           0.6773
  Gamma (Γ):           0.0234
  Theta (Θ):           $-0.06/day
  Vega (ν):            $0.22/1% vol
  Rho (ρ):             $0.15/1% rate

TRADING RECOMMENDATION:
  Action:              BUY
  Confidence:          100.0%
  Edge:                74.0%
  Market Price:        $5.50
  Fair Value:          $9.57

  Analysis:
    Option undervalued by 74.0%. Fair value: $9.57 vs Market: $5.50
    Greeks - Delta: 0.677, Theta: -0.06, Vega: 0.22
============================================================
```

## 🎯 What Each Metric Means

### **Theoretical Pricing**

- **Fair Value**: The Black-Scholes calculated theoretical price of the option
- **Implied Volatility**: The volatility implied by the current market price (if provided)

### **The Greeks - Your Risk Management Tools**

#### **Delta (Δ)** - Price Sensitivity
- **Range**: -1.00 to +1.00
- **Call Options**: 0 to +1.00 (positive delta)
- **Put Options**: -1.00 to 0 (negative delta)
- **Meaning**: How much the option price changes for a $1 move in the underlying
- **Example**: Delta of 0.67 means the option gains ~$0.67 for every $1 the stock rises

#### **Gamma (Γ)** - Delta Acceleration
- **Range**: 0 to higher positive values
- **Meaning**: How much delta changes as the stock price moves
- **High Gamma**: Option delta changes rapidly (more risk/reward)
- **Low Gamma**: Delta changes slowly (more predictable)

#### **Theta (Θ)** - Time Decay
- **Usually Negative**: Options lose value as time passes
- **Meaning**: Dollar amount the option loses per day due to time decay
- **Example**: Theta of -$0.06 means the option loses 6 cents per day

#### **Vega (ν)** - Volatility Sensitivity
- **Always Positive**: Higher volatility increases option value
- **Meaning**: How much the option price changes for a 1% change in implied volatility
- **Example**: Vega of $0.22 means +1% volatility adds $0.22 to option value

#### **Rho (ρ)** - Interest Rate Sensitivity
- **Call Options**: Usually positive
- **Put Options**: Usually negative
- **Meaning**: How much the option price changes for a 1% change in interest rates
- **Usually**: Least important Greek for most traders

### **Trading Recommendation**

#### **Action Types**
- **BUY**: Option is undervalued based on your volatility estimate
- **SELL**: Option is overvalued based on your volatility estimate
- **HOLD**: Option is fairly valued (within edge threshold)
- **AVOID**: Option has unfavorable characteristics (too close to expiry, etc.)

#### **Confidence Level**
- **High (80-100%)**: Strong signal based on significant edge
- **Medium (50-79%)**: Moderate signal, proceed with caution
- **Low (0-49%)**: Weak signal, consider other factors

#### **Edge Percentage**
- **Positive Edge**: Option is undervalued (potential buy)
- **Negative Edge**: Option is overvalued (potential sell)
- **Example**: 74% edge means the option trades at a 74% discount to fair value

## 📊 Understanding and Estimating Volatility

Volatility is the **most critical input** for Black-Scholes accuracy. The tool handles volatility in three ways:

### **1. Automatic Implied Volatility (Recommended)**

When you provide a current option price, the tool automatically calculates implied volatility:

```bash
# Tool calculates IV from the $5.50 market price
python3 options_trading_cli.py --symbol AAPL --strike 150 --expiry 2025-09-19 \
  --type call --underlying-price 155 --current-price 5.50 --risk-free-rate 0.05
```

**Advantages:**
- **Most accurate**: Reflects market consensus on future volatility
- **Easiest**: No research or calculations needed
- **Forward-looking**: Already incorporates upcoming events

### **2. Manual Volatility Input**

When you have a specific volatility estimate:

```bash
python3 options_trading_cli.py --volatility 0.35 [other parameters]
```

### **3. Volatility Estimation Methods**

When you need to estimate volatility manually:

#### **Historical Volatility Calculation**

**Simple 30-day historical volatility:**

1. Get 30 days of closing prices
2. Calculate daily returns: `ln(Price_today / Price_yesterday)`
3. Calculate standard deviation of returns
4. Annualize: `Standard_Deviation × √252`

**Quick estimation by stock type:**
- **Blue chips** (AAPL, MSFT): 20-35%
- **Growth stocks** (TSLA, NVDA): 35-60%
- **Volatile stocks** (COIN, ARKK): 60-100%
- **Meme stocks** (GME, AMC): 80-150%

#### **Event-Driven Adjustments**

**Before earnings:**
```
Base historical vol: 30%
Earnings volatility premium: +10-15%
Estimated vol: 40-45%
```

**After earnings:**
```
Pre-earnings vol: 45%
Post-earnings drop: Usually -15-20%
New estimate: 25-30%
```

**Other events that increase volatility:**
- **FDA approvals** (biotech): +20-40%
- **Product launches**: +10-20%
- **Legal decisions**: +15-30%
- **Economic data**: +5-15%

#### **Market Context Adjustments**

**VIX-based adjustments:**
- **VIX > 30 (high fear)**: Add 5-10% to historical vol
- **VIX < 15 (complacency)**: Use historical vol or subtract 2-3%
- **VIX 15-25 (normal)**: Use historical vol as baseline

#### **Implied Volatility from Similar Options**

Check IV of nearby strikes/expirations:

```
AAPL Options Chain:
$145 Call (1 month): 28% IV
$150 Call (1 month): 25% IV  ← Your target option
$155 Call (1 month): 27% IV
$150 Call (2 months): 23% IV

Estimate: 24-27% range
```

#### **Volatility Smile/Skew**

Options at different strikes have different implied volatilities:

```
Strike  |  Implied Vol  |  Notes
$140    |     32%       |  Out-of-money puts (higher IV)
$145    |     29%       |  
$150    |     25%       |  At-the-money (lowest IV)
$155    |     28%       |  
$160    |     31%       |  Out-of-money calls (higher IV)
```

**Rule of thumb:** Use ATM (at-the-money) IV as baseline for nearby strikes.

### **4. Volatility Estimation Examples**

#### **Conservative Approach**
```python
# Use 30-day historical + safety buffer
historical_vol = 0.28  # 28%
conservative_estimate = historical_vol * 1.15  # Add 15% buffer = 32.2%
```

#### **Aggressive Approach**
```python
# Forecast based on upcoming events
base_vol = 0.25  # 25% historical
if earnings_this_week:
    estimate = base_vol * 1.6  # 40%
elif major_news_expected:
    estimate = base_vol * 1.3  # 32.5%
else:
    estimate = base_vol  # 25%
```

#### **Real-World Example: AAPL Analysis**

```
Current AAPL price: $155
30-day historical vol: 28%
Earnings announcement: In 5 days
Recent options IV range: 25-35%
Current VIX: 18 (normal market)
Recent stock movement: Steady uptrend

Analysis:
- Base historical vol: 28%
- Earnings premium: +8% (28% × 0.3)
- Market adjustment: 0% (VIX normal)
- Final estimate: 36%

Usage:
python3 options_trading_cli.py --volatility 0.36 [other params]
```

### **5. Validation Techniques**

#### **Cross-Check Method**
```bash
# Test your estimate against current market prices
python3 options_trading_cli.py --symbol AAPL --strike 150 \
  --current-price 5.50 --volatility YOUR_ESTIMATE

# If tool's calculated IV ≈ your estimate, you're in the right range
```

#### **Sensitivity Analysis**
```bash
# Test multiple volatility scenarios
python3 options_trading_cli.py --volatility 0.25 [params]  # Conservative
python3 options_trading_cli.py --volatility 0.30 [params]  # Base case
python3 options_trading_cli.py --volatility 0.35 [params]  # Aggressive

# See how much your edge changes with different vol assumptions
```

### **6. Common Volatility Mistakes**

❌ **Don't do:**
- Use volatility from months ago
- Ignore upcoming earnings/events
- Apply the same vol to all strikes
- Forget to annualize daily volatility

✅ **Do:**
- Update volatility estimates regularly
- Account for known upcoming events
- Consider volatility smile/skew
- Use market-implied volatility when available

### **7. Volatility Trading Strategies**

#### **High IV Environment (IV > Historical)**
- **Sell options**: Collect inflated premiums
- **Iron condors**: Profit from IV crush
- **Covered calls**: Enhanced income

#### **Low IV Environment (IV < Historical)**
- **Buy options**: Cheap premium before vol expansion
- **Long straddles**: Position for volatility increase
- **Calendar spreads**: Benefit from vol differences

#### **IV Crush Plays**
- **Before earnings**: IV often 40-60%
- **After earnings**: IV drops to 20-30%
- **Strategy**: Sell options before, buy after

## 💡 How to Apply This to Your Trading

### **1. Pre-Trade Analysis**

Before entering any options position:

```bash
# Analyze the option you're considering
python3 options_trading_cli.py --symbol XYZ --strike 100 --expiry 2025-12-19 \
  --type call --underlying-price 105 --risk-free-rate 0.05 \
  --current-price 8.50 --volatility 0.30
```

**Look for:**
- **Edge > 10%**: Strong value opportunity
- **Time to expiry > 30 days**: Avoid near-expiry options unless specifically trading time decay
- **Reasonable Greeks**: Delta 0.30-0.70 for directional plays

### **2. Volatility Assessment**

The tool's effectiveness depends on your volatility estimate:

**Conservative Approach:**
- Use historical volatility (20-30 day average)
- Add 10-20% buffer for uncertainty

**Aggressive Approach:**
- Use your forecast of future volatility
- Consider upcoming events (earnings, FDA approvals, etc.)

### **3. Position Sizing with Greeks**

**Delta for Directional Exposure:**
```
Position Delta = Number of Contracts × 100 × Option Delta
```
- Want $1000 of stock exposure? Buy $1000 ÷ (Delta × 100) contracts

**Theta for Income Strategies:**
- Selling options: Look for high theta to collect time decay
- Buying options: Minimize theta drag, focus on gamma plays

**Vega for Volatility Plays:**
- High vega: Benefits from volatility increases
- Low vega: Less affected by volatility changes

### **4. Risk Management Rules**

#### **Entry Rules**
- **Minimum Edge**: Don't trade unless edge > 15%
- **Time Decay**: Avoid options with < 30 days to expiry (unless scalping)
- **Liquidity**: Ensure tight bid-ask spreads

#### **Exit Rules**
- **Profit Taking**: Close at 50% of maximum profit potential
- **Stop Loss**: Close if edge turns negative by > 20%
- **Time Stop**: Close 2 weeks before expiry regardless of P&L

#### **Position Limits**
- **Single Position**: Never risk more than 2% of portfolio
- **Sector Exposure**: Limit to 10% of portfolio in any sector
- **Time Diversification**: Spread expiries across multiple months

### **5. Example Trading Scenarios**

#### **Scenario 1: Earnings Play**
```
Stock: $150, Earnings in 2 weeks
Call Strike: $155, Expiry: 30 days
Your Vol Estimate: 45% (high due to earnings)
Tool Shows: Edge +25%, Action: BUY
```
**Strategy**: Buy calls before earnings, sell immediately after

#### **Scenario 2: Income Generation**
```
Stock: $100, Sideways market expected
Put Strike: $95, Expiry: 45 days  
Tool Shows: Edge -15%, Action: SELL
```
**Strategy**: Sell cash-secured puts to collect premium

#### **Scenario 3: Value Hunt**
```
Multiple strikes analyzed
Found: $110 calls with +30% edge
High gamma, decent time value
```
**Strategy**: Buy undervalued calls, hold for mean reversion

### **6. Advanced Techniques**

#### **Volatility Skew Analysis**
Run the tool on multiple strikes to find:
- **Cheap strikes**: High positive edge
- **Expensive strikes**: High negative edge
- **Arbitrage opportunities**: Spread trades

#### **Time Decay Optimization**
```bash
# Compare different expiries
python3 options_trading_cli.py --expiry 2025-08-15 [other params]
python3 options_trading_cli.py --expiry 2025-09-19 [other params]
python3 options_trading_cli.py --expiry 2025-10-17 [other params]
```

#### **Delta Hedging**
Use delta to create market-neutral positions:
- Buy undervalued options
- Hedge with underlying stock (Delta × 100 shares per contract)

## ⚠️ Important Disclaimers

### **Model Limitations**
- **Assumes constant volatility**: Real markets have volatility clustering
- **European exercise**: American options have early exercise premiums
- **No transaction costs**: Include commissions and bid-ask spreads in your analysis
- **Perfect liquidity assumed**: May not reflect real market conditions

### **Risk Warnings**
- **Options can expire worthless**: Never risk more than you can afford to lose
- **Volatility estimates are subjective**: Your edge depends on accurate vol forecasts
- **Past performance ≠ future results**: Backtest strategies before live trading
- **Market gaps**: Black-Scholes doesn't account for overnight gaps or market crashes

### **Best Practices**
1. **Paper trade first**: Test strategies with virtual money
2. **Start small**: Begin with 1-2 contracts maximum
3. **Keep records**: Track actual vs. predicted performance
4. **Continuous learning**: Study realized vs. implied volatility patterns
5. **Professional advice**: Consult financial advisors for large positions

## 🛠️ Customization

### **Adjusting Edge Thresholds**

Modify the default 10% edge threshold:

```bash
python3 options_trading_cli.py --edge-threshold 0.20 [other params]
```

### **Integration with Trading Systems**

Use JSON output for automated trading systems:

```python
import subprocess
import json

result = subprocess.run([
    'python3', 'options_trading_cli.py', 
    '--output-format', 'json',
    '--symbol', 'AAPL', 
    # ... other parameters
], capture_output=True, text=True)

analysis = json.loads(result.stdout)
if analysis['trading_signal']['action'] == 'BUY':
    # Execute buy logic
    pass
```

## 📈 Performance Tracking

Create a simple tracking spreadsheet with these columns:
- Date
- Symbol
- Strike/Expiry
- Predicted Edge
- Actual P&L
- Days Held
- Realized Vol vs. Estimate

This helps calibrate your volatility estimates over time.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is for educational purposes. Please ensure compliance with your local financial regulations.

---

**Remember**: This tool provides analysis based on the Black-Scholes model. Always combine with fundamental analysis, technical analysis, and proper risk management. Options trading involves substantial risk and is not suitable for all investors.