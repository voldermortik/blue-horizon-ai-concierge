"""
Example of using the currency conversion tool.

This example demonstrates:
1. Basic currency conversion (USD to EUR)
2. Getting current exchange rates for all supported currencies
3. Proper currency formatting with symbols
"""

from blue_horizon.tools.currency_tool import (
    CurrencyTool,
    Currency,
    CurrencyConversionError,
)


def main():
    """Demonstrate currency conversion functionality."""
    tool = CurrencyTool()

    # Example 1: Convert USD to EUR
    amount_usd = 100.00
    try:
        amount_eur = tool.convert(amount_usd, Currency.USD, Currency.EUR)
        formatted_usd = tool.format_amount(amount_usd, Currency.USD)
        formatted_eur = tool.format_amount(amount_eur, Currency.EUR)
        print("\nExample 1 - Basic conversion:")
        print(f"Converted {formatted_usd} to {formatted_eur}")
    except CurrencyConversionError as e:
        print(f"Error converting USD to EUR: {str(e)}")

    # Example 2: Get all current exchange rates
    try:
        print("\nExample 2 - Current exchange rates (base: USD):")
        rates = tool.get_exchange_rates(Currency.USD)
        for currency, rate in rates.items():
            formatted = tool.format_amount(rate, currency)
            print(f"1 USD = {formatted}")
    except CurrencyConversionError as e:
        print(f"Error getting exchange rates: {str(e)}")


if __name__ == "__main__":
    main()
