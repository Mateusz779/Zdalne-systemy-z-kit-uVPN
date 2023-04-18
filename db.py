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
        print(f"Error connecting to PostgreSQL: {ex}")
        
    cur = conn.cursor()
    
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS image (
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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS image_allocation (
                id SERIAL PRIMARY KEY,
                image_id INTEGER NOT NULL REFERENCES image(id),
                allocation_time TIMESTAMP NOT NULL DEFAULT NOW(),
                last_access_time TIMESTAMP,
                client_ip INET
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
            INSERT INTO image (image_name, token)
            VALUES (%s, %s)
        """,(name, token,))
        conn.commit()
        
def get_conf(sql,value):
    connect()
    with get_cur() as cur:
        cur.execute(sql,(value,))
        try:
            return cur.fetchone()[0]
        except:
            return None

def get_conf_image(token):
    return get_conf("SELECT image_name FROM image WHERE token = %s", token)
    # connect()
    # with get_cur() as cur:
    #     cur.execute("""
    #         SELECT image_name FROM image WHERE token = %s
    #     """,(token,))
    #     try:
    #         return cur.fetchone()[0]
    #     except:
    #         return None
        
def get_conf_id(token):
    return get_conf("SELECT id FROM image WHERE token = %s", token)
    # connect()
    # with get_cur() as cur:
    #     cur.execute("""
    #         SELECT id FROM image WHERE token = %s
    #     """,(token,))
    #     try:
    #         return cur.fetchone()[0]
    #     except:
    #         return None

def get_conf_id_name(name):
    return get_conf("SELECT id FROM image WHERE image_name = %s", name)
    # connect()
    # with get_cur() as cur:
    #     cur.execute("""
    #         SELECT id FROM image WHERE image_name = %s
    #     """,(name+".squashfs",))
    #     try:
    #         return cur.fetchone()[0]
    #     except:
    #         return None
    
def add_user(username, password):
    connect()
    with get_cur() as cur:
        cur.execute("""
            INSERT INTO users (username, password)
            VALUES (%s, %s)
        """,(username, utils.hash_password(password),))
        conn.commit()
        
def get_user_pass(username, password):
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
            INSERT INTO auth_tokens (user_id, token, expires_on)
            VALUES (%s, %s, NOW() + INTERVAL '1 day')
        """,(user_id,token,))
        conn.commit()
    return token
    
def login(username, password):
    user_id = get_user_pass(username, password)
    if user_id is not None:
        return add_auth_token(user_id)
    else:
        return None
    
    
def get_image_allocation_all():
    connect()
    with get_cur() as cur:
        cur.execute("""
            SELECT id FROM image_allocation""")
        try:
            results = [list(row) for row in cur.fetchall()]
            return results
        except:
            return None


def get_image_allocation(sql, value):
    connect()
    with get_cur() as cur:
        cur.execute(sql, (value,))
        try:
            return cur.fetchone()[0]
        except:
            return None

def get_image_allocation_time(token):
    image_id = get_conf_id(token)
    if image_id is None:
        return None
    
    return get_image_allocation_time_imageid(image_id)

def get_image_allocation_time_imageid(image_id):
    get_image_allocation("SELECT last_access_time FROM image_allocation WHERE image_id = %s", image_id)
    # connect()
    # with get_cur() as cur:
    #     cur.execute("""
    #         SELECT last_access_time FROM image_allocation WHERE image_id = %s 
    #     """,(image_id,))
    #     try:
    #         return cur.fetchone()[0]
    #     except:
    #         return None
        
def get_image_allocation_time_id(id):
    get_image_allocation("SELECT last_access_time FROM image_allocation WHERE id = %s", id)
    # connect()
    # with get_cur() as cur:
    #     cur.execute("""
    #         SELECT last_access_time FROM image_allocation WHERE id = %s 
    #     """,(id,))
    #     try:
    #         return cur.fetchone()[0]
    #     except:
    #         return None
        
def get_image_allocation_clientip(token):
    id_image = get_conf_id(token)
    if id_image is None:
        return None
    
    get_image_allocation("SELECT last_access_time FROM image_allocation WHERE id = %s", id_image)
    # connect()
    # with get_cur() as cur:
    #     cur.execute("""
    #         SELECT client_ip FROM image_allocation WHERE image_id = %s 
    #     """,(id_image,))
    #     try:
    #         return cur.fetchone()[0]
    #     except:
    #         return None

def get_image_allocation_clientip_id(id):    
    connect()
    with get_cur() as cur:
        cur.execute("""
            SELECT client_ip FROM image_allocation WHERE id = %s 
        """,(id,))
        try:
            return cur.fetchone()[0]
        except:
            return None

def set_image_allocation(token, client_ip):
    id_image = get_conf_id(token)
    if id_image is None:
        return None
    
    connect()
    with get_cur() as cur:
        cur.execute("""
            INSERT INTO image_allocation (image_id, client_ip, last_access_time)
            VALUES (%s, %s, NOW())
        """,(id_image,client_ip,))
        conn.commit()
    return token

def del_image_allocation_token(token):
    id_image = get_conf_id(token)
    if id_image is None:
        return None 
    
    return del_image_allocation_id_image(id_image)

def del_image_allocation(sql, value):
    connect()
    with get_cur() as cur:
        cur.execute(sql, (value, ))
        try:
            conn.commit()
            return True
        except:
            return None

def del_image_allocation_id_image(image_id):
    return del_image_allocation("DELETE FROM image_allocation WHERE image_id = %s", image_id)
    # connect()
    # with get_cur() as cur:
    #     cur.execute("""
    #         DELETE FROM image_allocation WHERE image_id = %s 
    #     """,(id_image,))
    #     try:
    #         conn.commit()
    #         return True
    #     except:
    #         return None

def del_image_allocation_id(id): 
    return del_image_allocation("DELETE FROM image_allocation WHERE id = %s", id)   
    # connect()
    # with get_cur() as cur:
    #     cur.execute("""
    #         DELETE FROM image_allocation WHERE id = %s 
    #     """,(id,))
    #     try:
    #         conn.commit()
    #         return True
    #     except:
    #         return None
        
def update_image_allocation_time(id):    
    connect()
    with get_cur() as cur:
        cur.execute("""
            UPDATE image_allocation SET last_access_time = NOW() WHERE id = %s 
        """,(id,))
        try:
            conn.commit()
            return True
        except:
            return None