import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, update, select, func
from sqlalchemy import text
import traceback
import psycopg2

from dotenv import load_dotenv
import os
# Load the environment variables from the .env file
load_dotenv()


DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PWD = os.getenv('DB_PWD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

db_params = {
    'dbname': DB_NAME,
    'user': DB_USER,
    'password': DB_PWD,
    'host': DB_HOST,
    'port': DB_PORT,  # default is 5432 for PostgreSQL
}

# Create a connection to the PostgreSQL database
engine = create_engine(f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}")

metadata = MetaData()

# Reflect the 'model_runs' table structure from the database
metadata.reflect(bind=engine)  # Bind the engine here

# Reflect the 'model_runs' table structure from the database
model_runs_table = Table('model_run', metadata, autoload=True, autoload_with=engine)

def get_latest_model_runs():
    with engine.connect() as connection:
        try:
            # Find the maximum runid
            max_runid_query = select([func.max(model_runs_table.c.runid)])
            max_runid = connection.execute(max_runid_query).scalar()

            # Fetch the records that match the maximum runid
            latest_runs_query = select([model_runs_table]).where(model_runs_table.c.runid == max_runid)
            latest_runs_result = connection.execute(latest_runs_query)

            # Process the records as needed
            latest_runs_data = [
                {
                    'topic': run['topic'],
                    'accuracy': run['accuracy'],
                    'test_sample': run['test_sample'],
                    'total_sample': run['total_sample']
                }
                for run in latest_runs_result
            ]

            return latest_runs_data
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

def update_prediction(df):
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
    SELECT distinct ticker, title, link, topic, published_est, market, hour_of_day FROM news_item
                     order by published_est desc
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

def read_news_price():
    # Define the SQL query
    sql_query = '''
    SELECT distinct ticker, title, link, topic, published_est, market,
       begin_price, end_price, index_begin_price, index_end_price,
       daily_return, index_return, daily_alpha, actual_action, predicted_action, confidence
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

def write_table(df, table_name):
    try:
        if not df.empty:
            df.to_sql(table_name, engine, if_exists='append', index=False)
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


def update_prediction_old(df):
    # Create MetaData object
    metadata = MetaData()

    # Reflect the table structure from the database to the MetaData object
    metadata.reflect(bind=engine)

    # Access the 'news_price' table from the reflected metadata
    news_price_table = metadata.tables['news_price']

    with engine.connect() as conn:
        for index, row in df.iterrows():
            try:
                # Using 'link' as the unique identifier for the row to be updated
                print('updating prediction for: ', row['link'])
                stmt = update(news_price_table).\
                    where(news_price_table.c.link == row['link']).\
                    values(prediction=row['prediction'], confidence=row['confidence'])
                conn.execute(stmt)
            except Exception as e:
                print(f"An error occurred while updating prediction and confidence for link: {row['link']}, error: {e}")
                continue  # Skip to the next row if an error occurs

    print("Predictions and confidence scores updated successfully.")