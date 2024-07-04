# Code for ETL operations on Country-GDP data
from io import StringIO
import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
import pandas as pd # type: ignore
import sqlite3
from datetime import datetime



def log_progress(message):
   

    with open('./logs/code_log.txt', 'a') as f:
        f.write(f'{datetime.now()}: {message}\n')


def extract(url, table_attribs):


    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    table = soup.find('span', string=table_attribs).find_next('table')
    df = pd.read_html(StringIO(str(table)))[0]

    log_progress('Data extraction complete. Initiating Transformation process')

    return df


def transform(df, csv_path):

    exchange_rate = pd.read_csv('.\input\exchange_rate.csv', index_col=0).to_dict()['Rate']

    df['MC_GBP_Billion'] = round(df['Market cap (US$ billion)'] * exchange_rate['GBP'], 2)
    df['MC_EUR_Billion'] = round(df['Market cap (US$ billion)'] * exchange_rate['EUR'], 2)
    df['MC_INR_Billion'] = round(df['Market cap (US$ billion)'] * exchange_rate['INR'], 2)

    print(df['MC_EUR_Billion'][4])

    log_progress('Data transformation complete. Initiating Loading process')

    return df


def load_to_csv(df, output_path):
    """ This function saves the final data frame as a CSV file in
    the provided path. Function returns nothing."""

    df.to_csv("D:\Newfolder\Explorartory_Data_Analysis\datascience-projects\etl-with-python")

    log_progress('Data saved to CSV file')


def load_to_db(df, sql_connection, table_name):
    """ This function saves the final data frame to a database
    table with the provided name. Function returns nothing."""

    df.to_sql('Largest_banks', 'banks_db', if_exists='replace', index=False)

    log_progress('Data loaded to Database as a table, Executing queries')


def run_query(query_statement, sql_connection):
    """ This function runs the query on the database table and
    prints the output on the terminal. Function returns nothing. """

    cursor = sql_connection.cursor()
    cursor.execute(query_statement)
    result = cursor.fetchall()
    # for row in result:
    #     ic(row)

    log_progress('Process Complete')

    return result


if __name__ == '__main__':
    url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'
    output_csv_path = './output/Largest_banks_data.csv'
    database_name = './output/Banks.db'
    table_name = 'Largest_banks'
    #
    log_progress('Preliminaries complete. Initiating ETL process')
    #

    df = print(extract(url, 'By market capitalization'))

    transform(df, './input/exchange_rate.csv')

    load_to_csv(df, output_csv_path)

    with sqlite3.connect('Banks.db') as conn:
        load_to_db(df, conn, table_name)

        print(run_query('SELECT * FROM Largest_banks', conn))

        print(run_query('SELECT AVG(MC_GBP_Billion) FROM Largest_banks', conn))

        print(run_query('SELECT "Bank name" FROM Largest_banks LIMIT 5', conn))
