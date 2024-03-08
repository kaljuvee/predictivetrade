import streamlit as st
from st_pages import Page, show_pages

title = "Predictive Trade"
st.title(title)

show_pages(
    [   
        Page("Home.py", "Home", "🏠"),
        Page("pages/01_Equities_Event_Prediction.py", "Equities Event Prediction", icon="📈", in_section=False),
        Page("pages/02_Equities_Event_Analytics.py", "Equities Event Analytics", icon="📊", in_section=False),
        Page("pages/04_Equities_Correlations.py", "Equities Correlations", icon="📉", in_section=False),
        Page("pages/05_Equities_Backtest.py", "Equities Backtest", icon="📊", in_section=False),
        Page("pages/06_Equities_Mean_Reversion.py", "Equities Mean Reversion", icon="📊", in_section=False),
        Page("pages/07_Crypto_Correlations.py", "Crypto Correlations", icon="📉", in_section=False),
        Page("pages/08_Crypto_Backtest.py", "Crypto Backtest", icon="📊", in_section=False),
        Page("pages/09_Equity_News_Benzinga.py", "Equity News Benzinga", icon="📰", in_section=False),
        Page("pages/10_Google_Trends.py", "Google Trends", icon="📉", in_section=False),
        Page("pages/20_Glossary.py", "Glossary", icon="📚", in_section=False),
    ]
)

st.markdown("""
## Tool Overview

* **Equity Event Prediction** - provides a long / short signal generated by an AI / machine learning model trained on an historical news and press release corpus, with an associated confidence score.
* **Equity Event Analytics** - model training results and distribution of event types vs market move.
* **Equity Statistical Analysis** - enables the research of correlated and co-integrated pairs, plotting the price performance, selects top correlations and provides a correlation matrix.
* **Equity Statistical Backtesting** - can simulate a back test using the clasical statistical arbitrage methodology, using the z-score parameter as the entry signal, and profit target, stop loss or Z-score as the exit signal.
* **Crypto Statistical Analysis** - analysis of crypto assets from selected exchanges.
* **Crypto Statistical Backtesting** - simulation of crypto assets from selected exchanges.

## Statistical Arbitrage Overview 

* **Selection of Pairs:** Traders look for two assets that exhibit a strong historical correlation, often within the same industry or sector. The assets should move together under normal market conditions due to similar market influences.
* **Identifying Divergence:** The strategy comes into play when the relationship between these two assets deviates from the historical norm. For instance, if one stock underperforms while the other overperforms, creating a gap that is unusual based on historical data.
* **Trading:** The trader takes a long position (buys) in the underperforming asset and a short position (sells) in the overperforming asset, betting that the underperformer will rise or the overperformer will fall, or both, thus returning to their historical correlation.
* **Profit from Convergence:** The goal is to profit when the spread between the two assets narrows, i.e., when they revert to their historical mean relationship. The trader would then close both positions to realize the gains from this convergence.

## References
* Read more about [statistical arbitrage with pairs trading and backtesting](https://medium.com/analytics-vidhya/statistical-arbitrage-with-pairs-trading-and-backtesting-ec657b25a368).
""")

