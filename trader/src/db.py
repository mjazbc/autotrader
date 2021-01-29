from trader_config import TraderConfig, Wallet
import psycopg2
import os
import logging

_params = {
            'host' : '0.0.0.0',
            'database' : 'postgres',
            'user' : 'postgres',
            'password' : os.environ['PG_PASSWORD']
        }

def _insert(sql, *args) ->int:
    conn = None
    id = None
    try:
        conn = psycopg2.connect(**_params)
        cur = conn.cursor()
        cur.execute(sql, (*args,))

        if 'RETURNING' in sql:
            id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        logging.exception(error)
    finally:
        if conn is not None:
            conn.close()

    return id

def _select(sql, *args):
    conn = None
    data = None
    try:
        conn = psycopg2.connect(**_params)
        cur = conn.cursor()
        cur.execute(sql, (*args,))

        data = cur.fetchall()
        
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        logging.exception(error)
    finally:
        if conn is not None:
            conn.close()

    return data

def find_user(telegram_id:str) -> int:
    sql = "SELECT id FROM accounts WHERE telegram_chat_id = %s"
    data = _select(sql, telegram_id)
    if data:
        return data[0][0]
    
    return None

def insert_user(telegram_id:str) -> int:
    sql = "INSERT INTO accounts(telegram_chat_id) VALUES(%s) RETURNING id"
    return _insert(sql, telegram_id)

def insert_trader_config(config:TraderConfig, owner_id:int) -> None:

    sql = """INSERT INTO trader_config(name, active, owner_id, public) 
             VALUES(%s, %b, %d, %b)"""
    
    config_id = _insert(sql, config.name, True, owner_id, True)

    sql = """INSERT INTO trader_config_params(trader_config_id, key, value) 
             VALUES(%d, %s, %s)"""
            
    _insert(sql, config, 'min_price_change', config.min_change_price)

    return config_id

def load_active_traders():
    traders = _select('SELECT name FROM trader_config WHERE active = True')
    return (t[0] for t in traders)

def load_trader_config(name):
    wallet = load_trader_wallet(name)

    if not wallet:
        return None

    params = load_trader_config_params(name)

    return TraderConfig(name, wallet, params)

def load_trader_wallet(name):
    sql = """SELECT tw.token, tw.amount FROM trader_config tc 
            INNER JOIN trader_wallet tw ON 
                tc.id = tw.trader_config_id
            WHERE tc.name = %s"""
    
    result = _select(sql, name)
    return {row[0] : row[1] for row in result}

def load_trader_config_params(name):
    sql = """SELECT tcp.key, tcp.value FROM trader_config tc 
            INNER JOIN trader_config_params tcp ON 
                tc.id = tcp.trader_config_id
            WHERE tc.name = %s"""
    
    result = _select(sql, name)
    return {row[0] : row[1] for row in result}


if __name__ == '__main__':
    # insert_user('1525910880')
    id = find_user('1525910880')
    pass
    # connect()