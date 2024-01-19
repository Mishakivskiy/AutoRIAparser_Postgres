import psycopg2


def create_table_if_not_exists(cursor):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS cars (
        id SERIAL PRIMARY KEY,
        url VARCHAR(255),
        title VARCHAR(255),
        price_usd INTEGER,
        odometer INTEGER,
        username VARCHAR(255),
        phone_number VARCHAR(15),
        image_url VARCHAR(255),
        images_count INTEGER,
        car_number VARCHAR(20),
        car_vin VARCHAR(20),
        datetime_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)


def insert_data_into_postgres(data):
    db_params = {
        'dbname': 'your_database_name',
        'user': 'your_username',
        'password': 'your_password',
        'host': 'localhost',
        'port': '5432',
    }

    url = data.get('url', '')
    title = data.get('title', '')
    price_usd = data.get('price_usd', 0)
    odometer = data.get('odometer', 0)
    username = data.get('username', '')
    phone_number = data.get('phone_number', '')
    image_url = data.get('image_url', '')
    images_count = data.get('images_count', 0)
    car_number = data.get('car_number', '')
    car_vin = data.get('car_vin', '')

    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()

    try:
        create_table_if_not_exists(cursor)

        insert_query = """
        INSERT INTO cars (url, title, price_usd, odometer, username, phone_number, 
                                     image_url, images_count, car_number, car_vin)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        params = (url, title, price_usd, odometer, username, phone_number,
                  image_url, images_count, car_number, car_vin)

        cursor.execute(insert_query, params)

        connection.commit()

    except Exception as e:
        print(f"Помилка при вставці даних: {e}")

    finally:
        cursor.close()
        connection.close()