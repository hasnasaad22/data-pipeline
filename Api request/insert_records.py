import psycopg2
from api_request import mock_fetch_data


def connect_to_db():
    print("Connecting to the PostgreSQL database...")
    try:
        conn = psycopg2.connect(
            host="db",
            port=5432,
            dbname="airflow_db",
            user="airflow",
            password="airflow"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        raise


def create_table(conn):
    print("Creating schema and table if not exists...")

    query = """
    CREATE SCHEMA IF NOT EXISTS dev;

    CREATE TABLE IF NOT EXISTS dev.raw_weather_data (
        id SERIAL PRIMARY KEY,
        city TEXT,
        temperature FLOAT,
        weather_descriptions TEXT,
        wind_speed FLOAT,
        time TIMESTAMP,
        inserted_at TIMESTAMP DEFAULT NOW(),
        utc_offset TEXT
    );
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        print("Table created successfully.")
    except psycopg2.Error as e:
        print(f"Failed to create table: {e}")
        conn.rollback()
        raise


def insert_records(conn, data):
    print("Inserting weather data into the database...")

    query = """
    INSERT INTO dev.raw_weather_data (
        city,
        temperature,
        weather_descriptions,
        wind_speed,
        time,
        inserted_at,
        utc_offset
    ) VALUES (%s, %s, %s, %s, %s, NOW(), %s)
    """

    try:
        cursor = conn.cursor()

        for record in data:
            cursor.execute(query, (
                record["city"],
                record["temperature"],
                record["weather_descriptions"],
                record["wind_speed"],
                record["time"],
                record["utc_offset"]
            ))

        conn.commit()
        print("Data inserted successfully.")

    except psycopg2.Error as e:
        print(f"Failed to insert records: {e}")
        conn.rollback()
        raise


def main():
    conn = connect_to_db()

    create_table(conn)

    data = mock_fetch_data()
    insert_records(conn, data)

    conn.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()