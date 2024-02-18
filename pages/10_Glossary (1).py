import streamlit as st


st.markdown("""
# Pairs Trading Overview
Pairs trading, also known as statistical arbitrage in a more sophisticated form, is a trading strategy that involves matching a long position with a short position in two stocks that have a historical or expected strong correlation. The core idea is to exploit the anomalies or deviations from the expected relationship between the two, under the assumption that this relationship will return to its historical norm, allowing the trader to profit from the convergence.

## How Pairs Trading Works:

* **Selection of Pairs:** Traders look for two assets that exhibit a strong historical correlation, often within the same industry or sector. The assets should move together under normal market conditions due to similar market influences.

* **Identifying Divergence:** The strategy comes into play when the relationship between these two assets deviates from the historical norm. For instance, if one stock underperforms while the other overperforms, creating a gap that is unusual based on historical data.

* **Trading:** The trader takes a long position (buys) in the underperforming asset and a short position (sells) in the overperforming asset, betting that the underperformer will rise or the overperformer will fall, or both, thus returning to their historical correlation.

* **Profit from Convergence:** The goal is to profit when the spread between the two assets narrows, i.e., when they revert to their historical mean relationship. The trader would then close both positions to realize the gains from this convergence.

## Why Pairs Trading Works:
* **Market Efficiency:** Pairs trading exploits market inefficiencies temporarily present between the pair of assets. The assumption is that the market will correct these inefficiencies, allowing for arbitrage opportunities.

* **Hedging Market Risk:** By taking opposite positions in closely related assets, the strategy aims to be market-neutral, reducing exposure to broader market movements. This means that the profit is generated from the relative performance of the two assets, rather than from the direction of the market as a whole.

* **Statistical Basis:** The strategy is grounded in statistical measures and historical data, which can provide a systematic approach to identifying and exploiting temporary mispricings between assets.

* **Leveraging Quantitative Models:** Advanced forms of statistical arbitrage use complex quantitative models to identify pairs and determine the optimal points for entry and exit, increasing the potential for profit.

## Limitations and Risks:
* **Model Risk:** The effectiveness depends heavily on the model's ability to accurately identify pairs and predict their convergence. Any flaws in the model can lead to losses.

* **Market Conditions:** Extreme market volatility or unforeseen events can disrupt historical correlations, leading to potential losses.

* **Execution Risk:** The strategy requires precise execution of trades. Delays or slippage can erode potential profits.

* **Costs:** Transaction costs and borrowing costs for short positions can reduce net profits.

# Z-Score in Statistical Analysis

The z-score is a fundamental statistical measure that quantifies how far a specific value deviates from the mean of its group, expressed in terms of standard deviations. 

Think of it like this: imagine a class of students taking a test. Their scores will form a distribution, with some scoring higher than others. Z-score tells you where a particular student's score stands within that distribution, compared to the average score and how much it deviates from it.

## Formula and Calculation

Calculating a z-score is straightforward. Here's the formula:

z = (x - mu) / sigma
where:

* `x` is the value you want to assess (the student's score in our example)
* `mu`  represents the mean of the group (average class score)
* `sigma` signifies the standard deviation of the group (how spread out the scores are)

## Applications

**1. Statistical Arbitrage:**

Z-scores play a crucial role in statistical arbitrage, particularly in pairs trading. This strategy involves identifying two correlated assets and exploiting temporary deviations in their relative price relationship.

Here's how z-score helps:

* **Calculate the Spread:** First, the spread between the two assets is calculated. This could be a simple price difference, a ratio, or a more complex function intended to represent the relative value between the two.
* **Calculating the Mean and Standard Deviation:** Analyze past data to compute the average spread (μ) and how much it typically fluctuates (σ).
* **Determining the Z-Score:** Convert the current spread into a z-score using the formula. This tells you how much the current price relationship deviates from its historical norm.

**2. Trading Decisions:**
Traders often use z-score thresholds to identify potential trading opportunities.

* **Entry Pointsf** - for example, a z-score of +2 or -2 might signal a significant deviation from the historical spread, suggesting an imbalance waiting to correct.
* **Exit Points** -  z-score thresholds can be used to identify exit points when the spread returns closer to its historical mean, indicating that the arbitrage opportunity may be diminishing.
* **Risk Management** -  Z-scores can also help in risk management by indicating the magnitude of divergence and helping traders set stop-loss levels based on historical volatility.

**3. Benefits and Considerations:**
* **Standardization** -  Z-scores provide a standardized way to assess deviations, allowing for comparison across different time frames or asset pairs.
* **Quantitative Measure** - they offer a quantitative measure of how unusual or extreme the current situation is relative to historical patterns.
* **Dynamic Adjustment** - Z-scores can dynamically adjust to changes in the mean and volatility of the spread, providing a responsive measure for trading decisions.
""")
