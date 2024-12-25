import logging 
from datetime import datetime

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructField

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def create_keyspace(session):
    session.execute("""CREATE KEYSPACE IF NOT EXISTS spark_streams WITH
replication = {'class': 'SimpleStrategy' ,'replication_factor':'1'}""")
    logger.info("Creating keyspace successfully")
def create_table(session):
     session.execute("""CREATE TABLE spark_stream if not EXISTS spark_streams.created_users(
    id TEXT PRIMARY KEY,
    thread_title TEXT,
    thread_date TIMESTAMP,
    latest_poster TEXT,
    latest_post_time TIMESTAMP,
    message_content TEXT,
    thread_url TEXT,
    positive_count FLOAT,
    negative_count FLOAT,
    neutral_count FLOAT,
    analyzed_at TIMESTAMP                        
                     );""")
     logger.info("Creating table successfully")

def insert_data(session, **kwargs):
    id = kwargs.get('id')
    thread_title = kwargs.get('thread_title')
    thread_date = kwargs.get('thread_date')
    latest_poster = kwargs.get('latest_poster')
    latest_post_time = kwargs.get('latest_post_time')
    message_content = kwargs.get('message_content')
    thread_url = kwargs.get('thread_url')
    positive_count = kwargs.get('positive_count')
    negative_count = kwargs.get('negative_count')
    neutral_count = kwargs.get('neutral_count')
    analyzed_at = kwargs.get('analyzed_at')

    try :
        session.execute("""INSERT INTO spark_streams.created_users (first_name, last_name, street, city, state, country, email, picture) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (id, thread_title, thread_date, latest_poster, latest_post_time, message_content, thread_url, positive_count, negative_count, neutral_count, analyzed_at))
        logger.info(f"Inserted data: {id} at {analyzed_at}")
    except Exception as e:
        logger.error(f"Error inserting data: {e}")

def connect_to_kafka(spark_conn):
    spark_df = None
    try:
        spark_df = spark_conn.read_stream\
        .format("kafka")\
        .option("kafka.bootstrap.servers", "localhost:9092")\
        .option("subscribe", "test")\
        .option("startingOffsets", "earliest")\
        .option("failOnDataLoss", "false")\
        .load()
        logger.info("Reading data from Kafka successfully")
    except Exception as e:
        logger.error(f"Error reading data from Kafka: {e}")
    return spark_df
        

def create_spark_connection():
    spark = None
    try:
        spark = SparkSession \
            .builder \
            .appName("Spark Cassandra") \
            .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.13:3.5.1","org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0") \
            .config('spark.cassandra.connection.host','localhost') \
            .getOrCreate()

        spark.sparkContext.setLogLevel("ERROR")
        logger.info("Spark session created successfully")
        return spark
    except Exception as e:
        logger.error(f"Error creating Spark connection: {e}")
    
def spark_schema(spark_conn):
    schema = StructType([
        StructField("id", StringType()),
        StructField("thread_title", StringType()),
        StructField("thread_date", TimestampType()),
        StructField("latest_poster", StringType()),
        StructField("latest_post_time", TimestampType()),
        StructField("message_content", StringType()),
        StructField("thread_url", StringType()),
        StructField("positive_count", FloatType()),
        StructField("negative_count", FloatType()),
        StructField("neutral_count", FloatType()),
        StructField("analyzed_at", TimestampType())
    ])
    sel = spark_conn.selectExpr("CAST(value AS STRING)")\
    .select(from_json("value", schema).alias("data"))\
    .select("data.*")
    return sel
    

def create_cassandra_connection():
    try:
        cluster = Cluster(['localhost'])
        cas_session = cluster.connect()
        return cas_session
    except:
        logger.error("Failed to connect to Cassandra")
        return None

try :
    spark_conn = create_spark_connection()

    if spark_conn is not None:
        df = connect_to_kafka(spark_conn)
        select_df = spark_schema(df)
        cas_session = create_cassandra_connection()
        if cas_session is not None:
            create_keyspace(cas_session)
            create_table(cas_session)
            # insert_data(cas_session)

            streaming_query = select_df.writeStream.format("org.apache.spark.sql.cassandra")\
            .option("table", "created_users")\
            .option("keyspace", "spark_streams")\
            .option("checkpointLocation", "file:///tmp")\
            .start()

            streaming_query.awaitTermination()
            logger.info("Spark and Cassandra connections closed")
            
except Exception as e:
    logger.error(f"Error in main: {e}")