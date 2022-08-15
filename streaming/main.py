import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
# import preprocess
from pyspark.sql.types import ArrayType, StringType


def quiet_logs(sc):
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel(logger.Level.ERROR)
    logger.LogManager.getLogger("akka").setLevel(logger.Level.ERROR)

def transform(line):
    if line in ['',"\n"] or line.startswith("By") or 'MIN READ' in line or '(Reuters)' in line:
        return None
    return line

@udf(returnType=ArrayType(elementType=StringType()))
def f(body):
    filtered = [x for x in body if transform(x)]
    return filtered



if __name__=='__main__':
    spark = SparkSession \
    .builder \
    .appName("streaming") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

    quiet_logs(spark)
  
    
    news = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "tweets") \
    .load()

    # df = spark.read.parquet("hdfs://namenode:9000//user/root/crawler.parquet")
    # df = df.drop("contentType","visited", "date", "icon","created_at")

    # df.printSchema()

    # df.createOrReplaceTempView("ParquetTable")

    # sql = spark.sql("select _id, body from ParquetTable").show()

    # print('Trying foreach')
   
    # df.withColumn("body",f(col("body"))).show()