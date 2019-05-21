import schedule
import time
import sqlite3 as sql
import psycopg2 as pg2
from sqlalchemy import create_engine
import os
import re
import datetime
from content_filtering_model import main as run_model
import pandas as pd

POSTGRES = {
    'user': 'kylejcaron',
    'pw': 'PSQL6360',
    'db': 'content_filtering',
    'host': 'content-filtering.c5d9uvdlpyso.us-east-1.rds.amazonaws.com',
    'port': '5432',
}

sql_id = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

def drop_florida_man(row):
    text = re.sub('florida man', '', row)
    return text   
    
def pull_content_filtering_data(t):
    # Get current day for formatting files
    d = datetime.date.today()
    print("Pulling data from RDS...", t)
    conn = pg2.connect(dbname = POSTGRES['db'], host = POSTGRES['host'],
    user = POSTGRES['user'], password = POSTGRES['pw'])
    # SQL Query
    cur = conn.cursor()
    cur.execute('SELECT * FROM entries;')
    responses = pd.DataFrame(cur.fetchall())
    responses.columns = ['text', 'offensive']
    responses['offensive'] = (responses['offensive'].str.contains('Yes')*1).astype('int64')
    conn.close()
    # Export to csv
    responses.to_csv('data/pipeline_data/user_feedback{}.csv'.format(d.strftime('%y%m%d')))


def merge_data(t):
    # Get current day and yesterday for formatting files
    d = datetime.date.today()
    y = datetime.date.today() - datetime.timedelta(days=1)
    print('Merging RDS data with content_filtering dataset...', t)
    # Import data from AWS and from pre-existing dataset
    df_rds = pd.read_csv('data/pipeline_data/user_feedback{}.csv'.format(d.strftime('%y%m%d')))
    df_rds['text'] = df_rds.text.apply(drop_florida_man)
    df_offense = pd.read_csv('data/pipeline_data/offensive_content{}.csv'.format(y.strftime('%y%m%d')))
    df_train = pd.concat((df_rds,df_offense),axis=0).drop(['Unnamed: 0'],axis=1)
    # Export
    df_train.to_csv('data/pipeline_data/offensive_content{}.csv'.format(d.strftime('%y%m%d')))


def job(t):
    pull_content_filtering_data(t)
    merge_data(t)
    print('running model...')
    run_model()
    print('finished')

if __name__ == '__main__':
    schedule.every().day.at("01:00").do(job,'It is 01:00')

    while True:
        schedule.run_pending()
        time.sleep(60) # wait one minute
