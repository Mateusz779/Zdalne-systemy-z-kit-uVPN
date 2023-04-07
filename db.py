import psycopg2
import config

def Connect():
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
            )
        """)
        conn.commit()
    
def GetCur():
    return conn.cursor()

def GetConn():
    return conn

def AddVPNImage(name, token):
    Connect()
    with GetCur() as cur:
        cur.execute("""
            INSERT INTO vpn (image_name, token)
            VALUES (%s, %s)
        """,(name, token,))
        conn.commit()
        
def GetVPNImage(token):
    Connect()
    with GetCur() as cur:
        return cur.execute("""
            SELECT image_name FROM vpn WHERE token = %s
        """,(token,)).fetchone()
        
    