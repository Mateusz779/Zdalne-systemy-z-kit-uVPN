import psycopg2
import config
import utils

def connect():
    global cur, conn
    try:
        conn = psycopg2.connect(database=config.database,
                                host=config.host,
                                user=config.user,
                                password=config.password,
                                port=config.port)
    except Exception as ex:
        print(f"Error connecting to PostgreSQL: {e}")
        
    cur = conn.cursor()
    
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vpn (
                id SERIAL PRIMARY KEY,
                image_name VARCHAR(255) NOT NULL,
                token VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );""")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );""")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS auth_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                token VARCHAR(64) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_on TIMESTAMP NOT NULL
            );""")
        conn.commit()
    
def get_cur():
    return conn.cursor()

def get_conn():
    return conn

def add_conf_image(name, token):
    connect()
    with get_cur() as cur:
        cur.execute("""
            INSERT INTO vpn (image_name, token)
            VALUES (%s, %s)
        """,(name, token,))
        conn.commit()
        
def get_conf_image(token):
    connect()
    with get_cur() as cur:
        cur.execute("""
            SELECT image_name FROM vpn WHERE token = %s
        """,(token,))
        try:
            return cur.fetchone()[0]
        except:
            return None
    
def add_user(username, password):
    connect()
    with get_cur() as cur:
        cur.execute("""
            INSERT INTO users (username, password)
            VALUES (%s, %s)
        """,(username, utils.hash_password(password),))
        conn.commit()
        
def get_user(username, password):
    connect()
    with get_cur() as cur:
        cur.execute("""
            SELECT id FROM users WHERE username = %s AND password = %s
        """,(username, utils.hash_password(password),))
        try:
            return cur.fetchone()[0]
        except:
            return None
        
def get_user_byid(id):
    connect()
    with get_cur() as cur:
        cur.execute("""
            SELECT id FROM users WHERE id = %s
        """,(id,))
        try:
            return cur.fetchone()[0]
        except:
            return None

def get_user_bytoken(token):
    connect()
    with get_cur() as cur:
        cur.execute("""
            SELECT user_id FROM auth_tokens WHERE token = %s 
        """,(token,))
        try:
            return cur.fetchone()[0]
        except:
            return None

def add_auth_token(user_id):
    token = utils.generate_auth_token()
    connect()
    with get_cur() as cur:
        cur.execute("""
            INSERT INTO auth_tokens (user_id, token)
            VALUES (%s, %s)
        """,(user_id,token,))
        conn.commit()
    return token
    
def login(username, password):
    user_id = get_user(username, password)
    if user_id is not None:
        return add_auth_token(user_id)
    else:
        return None
    
