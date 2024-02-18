import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, update
from sqlalchemy import text
import traceback
import psycopg2

# Database connection parameters (you'll need to fill these in)
# db_params = {
#    'dbname': 'altsignals-beta',
#    'user': 'julian',
#    'password': 'AltData2$2',
#    'host': '34.88.153.82',
#    'port': '5432',  # default is 5432 for PostgreSQL
#}
db_params = {
    'dbname': 'pddeswvh',
    'user': 'pddeswvh',
    'password': 'uRN_JtBBpy6BAHTgkAiZKKNW05LB_U_z',
    'host': 'trumpet.db.elephantsql.com',
    'port': '5432',  # default is 5432 for PostgreSQL
}
# postgres://pddeswvh:uRN_JtBBpy6BAHTgkAiZKKNW05LB_U_z@trumpet.db.elephantsql.com/pddeswvh


# Create a connection to the PostgreSQL database
engine = create_engine(f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}")


def update_prediction(df):
    # Database connection parameters
    conn_params = {
        'dbname': 'your_database_name',
        'user': 'your_username',
        'password': 'your_password',
        'host': 'your_host',
        'port': 'your_port',  # default is 5432 for PostgreSQL
    }

    # Establish a connection to the database
    conn = psycopg2.connect(**db_params)
    
    try:
        # Create a cursor object
        cur = conn.cursor()

        for index, row in df.iterrows():
            try:
                #print(f"Updating prediction and confidence for link: {row['link']}")
                
                # SQL statement to update prediction and confidence
                update_sql = """
                UPDATE news_price
                SET prediction = %s, confidence = %s
                WHERE link = %s;
                """
                # Values to substitute into the SQL statement
                values = (row['prediction'], row['confidence'], row['link'])

                # Print SQL statement for debugging purposes
                print("Executing SQL:", update_sql.strip())
                print("With values:", values)               
                # Execute the update statement
                cur.execute(update_sql, (row['prediction'], row['confidence'], row['link']))
                
                # Commit the transaction
                conn.commit()
                print(f"Row updated for link: {row['link']}")
                
            except Exception as e:
                # Rollback the transaction in case of error
                conn.rollback()
                print(f"An error occurred while updating prediction and confidence for link: {row['link']}, error: {e}")
                continue  # Skip to the next row if an error occurs

        # Close the cursor
        cur.close()
        print("Predictions and confidence scores updated successfully.")
        
    except Exception as e:
        print(f"An error occurred while connecting to the database: {e}")
    
    finally:
        # Close the connection
        conn.close()

# Replace 'your_database_name', 'your_username', 'your_password', 'your_host', and 'your_port' with your actual database connection details.

def get_engine():
    return engine

def get_news():
    sql_query = text('''
    SELECT distinct ticker, title, link, topic, published_est, market FROM news_item 
    ORDER BY published_est DESC
    LIMIT 1000
    ''')
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(sql_query, conn)
        return df
    except Exception as e:
        print(f"An error occurred while fetching news: {e}")
        # Return an empty DataFrame in case of error
        return pd.DataFrame()

def get_news_all():
    sql_query = text('''
    SELECT distinct ticker, title, link, topic, published_est, market FROM news_item
    ''')
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(sql_query, conn)
        return df
    except Exception as e:
        print(f"An error occurred while fetching news: {e}")
        # Return an empty DataFrame in case of error
        return pd.DataFrame()

def read_news_item():
    # Define the SQL query
    sql_query = '''
    select distinct
    ticker,
    title,
    summary,
    published_gmt,
    description,
    link,
    sector,
    topic,
    published_est,
    market,
    hour_of_day 
    from news_item
    '''
    # Fetch data into a pandas DataFrame using the engine
    news_df = pd.read_sql_query(sql_query, engine)
    return news_df

import pandas as pd

def read_news_price():
    # Define the SQL query
    sql_query = '''
    SELECT distinct ticker, title, link, topic, published_est, market,
       begin_price, end_price, index_begin_price, index_end_price,
       return, index_return, daily_alpha, action
    FROM news_price
    ORDER BY published_est DESC
    '''

    try:
        # Fetch data into a pandas DataFrame using the engine
        news_df = pd.read_sql_query(sql_query, engine)

        # Check if the DataFrame is empty
        if news_df.empty:
            print("The query returned no results.")
            # Depending on your logging setup, you might want to use logging.warning or logging.info instead of print
            # logging.warning("The query returned no results.")
        else:
            return news_df

    except Exception as e:
        print(f"An error occurred while fetching news price data: {e}")
        # Depending on your logging setup, you might want to use logging.error or logging.exception instead of print
        # logging.error(f"An error occurred while fetching news price data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error



def write_news_item(df):
    try:
        if not df.empty:
            df.to_sql('news_item', engine, if_exists='append', index=False)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())

def write_news_price(df):
    try:
        if not df.empty:
            df.to_sql('news_price', engine, if_exists='append', index=False)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())