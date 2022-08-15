import os
from pyspark.sql import SparkSession

if __name__=='__main__':
    spark = SparkSession \
    .builder \
    .appName("myApp") \
    .master("spark://spark-master:7077") \
    .config("spark.mongodb.input.uri", os.environ.get('MONGO_URL','mongodb://127.0.0.1:27012/crawler.contents')) \
    .config("spark.jars.packages","org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()

    df = spark.read.format("com.mongodb.spark.sql.DefaultSource").load()

    df.printSchema()

    df.show(2)

    df.write.parquet("hdfs://namenode:9000//user/root/crawler.parquet")

    spark.read.parquet("hdfs://namenode:9000//user/root/crawler.parquet")
