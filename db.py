import psycopg2
import config
import utils
import machines

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


def get_one(sql, value):
    connect()
    with get_cur() as cur:
        cur.execute(sql, (value,))
        try:
            return cur.fetchone()[0]
        except:
            return None


def add_conf_image(name, token):
    connect()
    with get_cur() as cur:
        cur.execute("""
            INSERT INTO image (image_name, token)
            VALUES (%s, %s)
        """, (name, token,))
        conn.commit()


def get_conf_image(token):
    return get_one("SELECT image_name FROM image WHERE token = %s", token)


def get_conf_id(token):
    return get_one("SELECT id FROM image WHERE token = %s", token)


def get_conf_id_name(name):
    return get_one("SELECT id FROM image WHERE image_name = %s", name)


def add_user(username, password):
    connect()
    with get_cur() as cur:
        cur.execute("""
            INSERT INTO users (username, password)
            VALUES (%s, %s)
        """, (username, utils.hash_password(password),))
        conn.commit()


def get_user_pass(username, password):
    connect()
    with get_cur() as cur:
        cur.execute("""
            SELECT id FROM users WHERE username = %s AND password = %s
        """, (username, utils.hash_password(password),))
        try:
            return cur.fetchone()[0]
        except:
            return None


def get_user_byid(id):
    return get_one("SELECT id FROM users WHERE id = %s", id)


def get_user_bytoken(token):
    return get_one("SELECT user_id FROM auth_tokens WHERE token = %s", token)


def add_auth_token(user_id):
    token = utils.generate_auth_token()
    connect()
    with get_cur() as cur:
        cur.execute("""
            INSERT INTO auth_tokens (user_id, token, expires_on)
            VALUES (%s, %s, NOW() + INTERVAL '1 day')
        """, (user_id, token,))
        conn.commit()
    return token


def login(username, password):
    user_id = get_user_pass(username, password)
    if user_id is not None:
        return add_auth_token(user_id)
    else:
        return None

def get_machines():
    connect()
    with get_cur() as cur:
        cur.execute("""
            SELECT image_id, allocation_time, client_ip FROM image_allocation""")
        try:
            machinesall = machines.MachineManager()
            for row in cur.fetchall():
                token = get_one("SELECT token FROM image WHERE id = %s", row[0])
                image_name = get_one("SELECT image_name FROM image WHERE id = %s", row[0])
                machine = machines.Machine(token, image_name, start_time=row[1], ip=row[2], username="root", password="")
                machinesall.add_machine(machine)
            return machinesall
        except:
            return None

def get_image_allocation_all_id():
    connect()
    with get_cur() as cur:
        cur.execute("""
            SELECT id FROM image_allocation""")
        try:
            results = [list(row) for row in cur.fetchall()]
            return results
        except:
            return None



def get_image_allocation_all():
    connect()
    with get_cur() as cur:
        cur.execute("""
            SELECT * FROM image_allocation""")
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
    return get_one("SELECT last_access_time FROM image_allocation WHERE image_id = %s", image_id)


def get_image_allocation_time_id(id):
    get_one("SELECT last_access_time FROM image_allocation WHERE id = %s", id)


def get_image_allocation_clientip(token):
    id_image = get_conf_id(token)
    if id_image is None:
        return None

    return get_one("SELECT last_access_time FROM image_allocation WHERE id = %s", id_image)


def get_image_allocation_clientip_id(id):
    return get_one("SELECT client_ip FROM image_allocation WHERE id = %s", id)


def set_image_allocation(token, client_ip):
    id_image = get_conf_id(token)
    if id_image is None:
        return None

    connect()
    with get_cur() as cur:
        cur.execute("""
            INSERT INTO image_allocation (image_id, client_ip, last_access_time)
            VALUES (%s, %s, NOW())
        """, (id_image, client_ip,))
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


def del_image_allocation_id(id):
    return del_image_allocation("DELETE FROM image_allocation WHERE id = %s", id)


def update_image_allocation_time(id):
    connect()
    with get_cur() as cur:
        cur.execute("""
            UPDATE image_allocation SET last_access_time = NOW() WHERE id = %s 
        """, (id,))
        try:
            conn.commit()
            return True
        except:
            return None