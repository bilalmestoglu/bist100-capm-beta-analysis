import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

market_ticker = "XU100.IS"
stock_tickers = ["THYAO.IS", "ASELS.IS", "AKBNK.IS", "KCHOL.IS"]
start_date = "2023-11-01"
end_date = "2026-11-01"

annual_rf = 0.40
monthly_rf = (1 + annual_rf) ** (1 / 12) - 1

all_tickers = [market_ticker] + stock_tickers
data = yf.download(all_tickers, start=start_date, end=end_date)["Close"]

monthly_prices = data.resample("ME").last()
monthly_returns = monthly_prices.pct_change().dropna()

excess_returns = monthly_returns.sub(monthly_rf)

results_summary = []
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
axes = axes.flatten()

X = sm.add_constant(excess_returns[market_ticker])

for idx, stock in enumerate(stock_tickers):
    y = excess_returns[stock]
    model = sm.OLS(y, X).fit()
    
    alpha = model.params["const"]
    beta = model.params[market_ticker]
    r_squared = model.rsquared
    p_value_beta = model.pvalues[market_ticker]
    
    results_summary.append({
        "Hisse": stock.replace(".IS", ""),
        "Alpha (Aylık)": round(alpha, 4),
        "Beta": round(beta, 3),
        "R-Kare": round(r_squared, 3),
        "Beta p-değeri": round(p_value_beta, 5)
    })
    
    ax = axes[idx]
    ax.scatter(excess_returns[market_ticker], y, alpha=0.7, color="#1f77b4", label="Aylık Gözlemler")
    
    x_vals = np.linspace(excess_returns[market_ticker].min(), excess_returns[market_ticker].max(), 100)
    y_vals = alpha + beta * x_vals
    ax.plot(x_vals, y_vals, color="#d62728", linewidth=2, label=f"CAPM (β = {beta:.2f})")
    
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.axvline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title(f"{stock.replace('.IS', '')} vs BIST 100 (R² = {r_squared:.2f})", fontweight="bold")
    ax.set_xlabel("Piyasa Artık Getirisi (BIST 100)")
    ax.set_ylabel("Hisse Artık Getirisi")
    ax.legend()
    ax.grid(True, alpha=0.3)

summary_df = pd.DataFrame(results_summary)
print("\n--- CAPM REGRESYON SONUÇLARI ---")
print(summary_df.to_string(index=False))

plt.tight_layout()
plt.savefig("capm_bist100_analizi.png", dpi=300)
plt.show()