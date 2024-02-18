import streamlit as st


st.markdown("""
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

* **Calculate the Spread:** Find the difference between the prices of the two assets (think of it as the score for their price relationship).
* **Mean and Standard Deviation:** Analyze past data to compute the average spread (μ) and how much it typically fluctuates (σ).
* **Z-Score:** Convert the current spread into a z-score using the formula. This tells you how much the current price relationship deviates from its historical norm.

**2. Trading Decisions:**

Traders often use z-score thresholds to identify potential trading opportunities.

* **Entry Points:** For example, a z-score of +2 or -2 might signal a significant deviation from the historical spread, suggesting an imbalance waiting to correct.
* **Trading Strategy:** In such scenarios, traders might buy the undervalued asset and sell the overvalued one, expecting the spread to revert to its mean over time.
""")