
from ntpath import join
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, PandasUDFType
from pyspark.sql.types import ArrayType, StringType
import pyspark.pandas as ps
import pandas as pd
import numpy as np


def quiet_logs(sc):
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel(logger.Level.ERROR)
    logger.LogManager.getLogger("akka").setLevel(logger.Level.ERROR)


@udf(returnType=StringType())
def f(target):
    return ",".join(target)


if __name__ == '__main__':

    spark = SparkSession \
        .builder \
        .appName("exporter") \
        .config("spark.sql.warehouse.dir", "/hive/warehouse/dir") \
        .master("spark://spark-master:7077") \
        .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
        .enableHiveSupport() \
        .getOrCreate()

    quiet_logs(spark)

    df = spark.read.parquet("hdfs://namenode:9000/user/root/labeled.parquet")
    df = spark.createDataFrame(pd.concat([df.toPandas(), df.select(df["target"]).toPandas(
    )['target'].fillna("").map(lambda x: ",".join(x)).str.get_dummies(sep=",")], axis=1))
    # pdf = ps.DataFrame(test)
    # pdf = ps.DataFrame(df.select(df["target"]).withColumn("classes",f(col("target"))))
    # target = ps.get_dummies(data=pdf, columns=["classes"], prefix=None)
    # target.to_spark().printSchema()

    df.printSchema()
    df.write.mode("overwrite").option(
        "path", "hdfs://namenode:9000/user/root/labeled").saveAsTable("labeled")

    df = spark.read.parquet("hdfs://namenode:9000/user/root/crawler.parquet")
    df.write.mode("overwrite").option(
        "path", "hdfs://namenode:9000/user/root/crawler").saveAsTable("crawler")

    # df = spark.read.parquet("hdfs://namenode:9000/user/root/cleaned.parquet")
    # df.write.mode(SaveMode.Overwrite).option("path", "hdfs://namenode:9000/user/root/cleaned").saveAsTable("cleaned")
