from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

import time

from configparser import ConfigParser

# Loading Kafka Cluster/Server details from configuration file(datamaking_app.conf)

conf_file_path = "/home/datamaking/workarea/code/course_download/ecom-real-time-case-study/realtime_data_processing/"
conf_file_name = conf_file_path + "datamaking_app.conf"
config_obj = ConfigParser()
print(config_obj)
print(config_obj.sections())
config_read_obj = config_obj.read(conf_file_name)
print(type(config_read_obj))
print(config_read_obj)
print(config_obj.sections())

# Kafka Cluster/Server Details
kafka_host_name = config_obj.get('kafka', 'host')
kafka_port_no = config_obj.get('kafka', 'port_no')
input_kafka_topic_name = config_obj.get('kafka', 'input_topic_name')
output_kafka_topic_name = config_obj.get('kafka', 'output_topic_name')
kafka_bootstrap_servers = kafka_host_name + ':' + kafka_port_no

# MySQL Database Server Details
mysql_host_name = config_obj.get('mysql', 'host')
mysql_port_no = config_obj.get('mysql', 'port_no')
mysql_user_name = config_obj.get('mysql', 'username')
mysql_password = config_obj.get('mysql', 'password')
mysql_database_name = config_obj.get('mysql', 'db_name')
mysql_driver = config_obj.get('mysql', 'driver')

mysql_salesbycardtype_table_name = config_obj.get('mysql', 'mysql_salesbycardtype_tbl')
mysql_salesbycountry_table_name = config_obj.get('mysql', 'mysql_salesbycountry_tbl')

mysql_jdbc_url = "jdbc:mysql://" + mysql_host_name + ":" + mysql_port_no + "/" + mysql_database_name
# https://mvnrepository.com/artifact/mysql/mysql-connector-java
# --packages mysql:mysql-connector-java:5.1.49

# spark-submit --master local[*] --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,mysql:mysql-connector-java:5.1.49 --files /home/datamaking/workarea/code/course_download/ecom-real-time-case-study/realtime_data_processing/datamaking_app.conf /home/datamaking/workarea/code/course_download/ecom-real-time-case-study/realtime_data_processing/realtime_data_processing.py

#Create the Database properties
db_properties = {}
db_properties['user'] = mysql_user_name
db_properties['password'] = mysql_password
db_properties['driver'] = mysql_driver


def save_to_mysql_table(current_df, epoc_id, mysql_table_name):
    print("Inside save_to_mysql_table function")
    print("Printing epoc_id: ")
    print(epoc_id)
    print("Printing mysql_table_name: " + mysql_table_name)

    mysql_jdbc_url = "jdbc:mysql://" + mysql_host_name + ":" + str(mysql_port_no) + "/" + mysql_database_name

    current_df = current_df.withColumn('batch_no', lit(epoc_id))

    #Save the dataframe to the table.
    current_df.write.jdbc(url = mysql_jdbc_url,
                  table = mysql_table_name,
                  mode = 'append',
                  properties = db_properties)

    print("Exit out of save_to_mysql_table function")

if __name__ == "__main__":
    print("Welcome to DataMaking !!!")
    print("Real-Time Data Processing Application Started ...")
    print(time.strftime("%Y-%m-%d %H:%M:%S"))

    spark = SparkSession \
        .builder \
        .appName("Real-Time Data Processing with Kafka Source and Message Format as JSON") \
        .master("local[*]") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    # Construct a streaming DataFrame that reads from test-topic
    orders_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", input_kafka_topic_name) \
        .option("startingOffsets", "latest") \
        .load()

    print("Printing Schema of orders_df: ")
    orders_df.printSchema()
    # key, value, topic, partition, offset, timestamp

    orders_df1 = orders_df.selectExpr("CAST(value AS STRING)", "timestamp")

    # Define a schema for the orders data
    # order_id,order_product_name,order_card_type,order_amount,order_datetime,order_country_name,order_city_name,order_ecommerce_website_name
    orders_schema = StructType() \
        .add("order_id", StringType()) \
        .add("order_product_name", StringType()) \
        .add("order_card_type", StringType()) \
        .add("order_amount", StringType()) \
        .add("order_datetime", StringType()) \
        .add("order_country_name", StringType()) \
        .add("order_city_name", StringType()) \
        .add("order_ecommerce_website_name", StringType())

    # {'order_id': 1, 'order_product_name': 'Laptop', 'order_card_type': 'MasterCard',
    # 'order_amount': 38.48, 'order_datetime': '2020-10-21 10:59:10', 'order_country_name': 'Italy',
    # 'order_city_name': 'Rome', 'order_ecommerce_website_name': 'www.flipkart.com'}
    orders_df2 = orders_df1\
        .select(from_json(col("value"), orders_schema)\
        .alias("orders"), "timestamp")

    orders_df2.printSchema()

    # orders -> ['order_id': 1, 'order_product_name': 'Laptop', ....]

    orders_df3 = orders_df2.select("orders.*", "timestamp")

    print("Printing schema of orders_df3 before creating date & hour column from order_datetime ")
    orders_df3.printSchema()

    orders_df3 = orders_df3.withColumn("partition_date", to_date("order_datetime"))
    orders_df3 = orders_df3.withColumn("partition_hour", hour(to_timestamp("order_datetime", 'yyyy-MM-dd HH:mm:ss')))

    print("Printing schema of orders_df3 after creating date & hour column from order_datetime ")
    orders_df3.printSchema()

    orders_agg_write_stream_pre = orders_df3 \
        .writeStream \
        .trigger(processingTime='10 seconds') \
        .outputMode("update") \
        .option("truncate", "false")\
        .format("console") \
        .start()

    orders_agg_write_stream_pre_hdfs = orders_df3.writeStream \
        .trigger(processingTime='10 seconds') \
        .format("parquet") \
        .option("path", "/tmp/data/ecom_data/raw") \
        .option("checkpointLocation", "orders-agg-write-stream-pre-checkpoint") \
        .partitionBy("partition_date", "partition_hour") \
        .start()

    # Simple aggregate - find total_sales(sum of order_amount) by order_card_type
    orders_df4 = orders_df3.groupBy("order_card_type") \
        .agg({'order_amount': 'sum'}) \
        .select("order_card_type", col("sum(order_amount)") \
        .alias("total_sales"))

    print("Printing Schema of orders_df4: ")
    orders_df4.printSchema()

    orders_df4 = orders_df4.withColumnRenamed("order_card_type","card_type")

    orders_df4.printSchema()

    orders_df4 \
    .writeStream \
    .trigger(processingTime='10 seconds') \
    .outputMode("update") \
    .foreachBatch(lambda current_df, epoc_id: save_to_mysql_table(current_df, epoc_id, mysql_salesbycardtype_table_name)) \
    .start()

    # Simple aggregate - find total_sales(sum of order_amount) by order_country_name
    orders_df5 = orders_df3.groupBy("order_country_name") \
        .agg({'order_amount': 'sum'}) \
        .select("order_country_name", col("sum(order_amount)") \
        .alias("total_sales"))

    print("Printing Schema of orders_df5: ")
    orders_df5.printSchema()

    orders_df5 = orders_df5.withColumnRenamed("order_country_name","country")

    orders_df5.printSchema()

    orders_df5 \
    .writeStream \
    .trigger(processingTime='10 seconds') \
    .outputMode("update") \
    .foreachBatch(lambda current_df, epoc_id: save_to_mysql_table(current_df, epoc_id, mysql_salesbycountry_table_name)) \
    .start()

    # Write final result into console for debugging purpose
    orders_agg_write_stream = orders_df4 \
        .writeStream \
        .trigger(processingTime='10 seconds') \
        .outputMode("update") \
        .option("truncate", "false")\
        .format("console") \
        .start()

    '''
    kafka_orders_df4 = orders_df4.selectExpr("card_type as key",
                                                 """to_json(named_struct(
                                                 'card_type', card_type,
                                                 'total_sales', total_sales)) as value""")

    # kafka_orders_df4 [key, value]
    kafka_writer_query = kafka_orders_df4 \
        .writeStream \
        .trigger(processingTime='10 seconds') \
        .queryName("Kafka Writer") \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("topic", output_kafka_topic_name) \
        .outputMode("update") \
        .option("checkpointLocation", "kafka-check-point-dir") \
        .start()
    '''

    orders_agg_write_stream.awaitTermination()

    print("Real-Time Data Processing Application Completed.")
