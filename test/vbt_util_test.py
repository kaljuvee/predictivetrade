from util import vbt_util

# Assuming vbt_util.py is located in the util directory and contains a function named get_equities_data

def get_data(asset1, asset2, input_frequency, lookback_days):
    asset1_data, asset2_data = vbt_util.get_equities_data(asset1, asset2, input_frequency, lookback_days)
    return asset1_data, asset2_data

def main():
    asset1 = 'TSLA'
    asset2 = 'MSFT'
    input_frequency = '1m'
    lookback_days = 2

    # Import the vbt_util module here to avoid import errors when the script is not run as a module
    print()
    asset1_data, asset2_data = get_data(asset1, asset2, input_frequency, lookback_days)
    print(type(asset1_data))
    # Call the get_equities_data function from the vbt_util module
    
    # Assuming you want to print the data for now; you might want to replace this with your actual use case
    print(f"Data for {asset1}:\n{asset1_data}\n")
    print(f"Data for {asset2}:\n{asset2_data}\n")

# This condition ensures that the main function is executed only when the script is run directly, not when imported
if __name__ == "__main__":
    main()
