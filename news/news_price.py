import pandas as pd
from util.db_util import engine
from util import db_util, date_util, price_util

def main():
    news_df = db_util.get_news_all()
    # Ensure all string operations are called on the string accessor `.str`
    #news_df['topic'] = news_df['topic'].str.lower().str.replace(" ", "_").str.replace("/", "_").str.replace("&", "").str.replace("'", "")
    #pred_df = news_prediction.predict_news(news_df)
    #pred_df.to_csv('predictions.csv')
    # Group the DataFrame by 'ticker'
    #pred_df = pd.read_csv('predictions.csv')
    grouped = news_df.groupby('ticker')

    # Iterate through each group and write to the database
    for ticker, group_df in grouped:
        print('Creating returns for: ', ticker)
        processed_group_df = price_util.create_returns(group_df)  # Process only the current group
        #processed_group_df.to_csv(ticker + '.csv')
        print('Writing to db for: ', ticker)
        db_util.write_news_price(processed_group_df)  # Write only the current processed group

if __name__ == "__main__":
    main()


