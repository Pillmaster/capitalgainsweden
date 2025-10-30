README – European Withdrawal Tax Calculator 🇸🇪

This Streamlit app simulates a long-term withdrawal strategy for investment portfolios, including the effect of capital gains tax, inflation, and annual returns.
It is especially tailored for users in Sweden, but the calculations are expressed in euros (€) or optionally in Swedish kronor (SEK) using the latest ECB exchange rate.

Key Features

Simulates portfolio evolution over a custom number of years.
Calculates taxes only on the profit portion of each withdrawal.
Automatically adjusts annual withdrawals for inflation.
Fetches the EUR/SEK exchange rate from the European Central Bank (with fallback rate if unavailable).
Option to view all results in SEK or EUR with a simple checkbox toggle.
Displays a detailed results table and interactive line chart.
Allows users to download the full simulation as a CSV file.

Inputs

Starting invested capital (€)
Current market value (€)
Average annual return (%)
Inflation rate (%)
Capital gains tax rate (%)
Net withdrawal in the first year (€)
Number of years to simulate

Output

Annual values for portfolio growth, withdrawals, and taxes
End-of-year portfolio value and remaining capital/profit
Graph showing portfolio trend and withdrawals over time
