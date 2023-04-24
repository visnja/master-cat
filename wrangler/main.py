
from ntpath import join
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, PandasUDFType
from pyspark.sql.types import ArrayType, StringType


SPACY_MODEL = None
SPACY_MATCHER = None


def quiet_logs(sc):
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel(logger.Level.ERROR)
    logger.LogManager.getLogger("akka").setLevel(logger.Level.ERROR)


def transform(line):
    if line in ['', "\n"] or line.startswith("By") or 'MIN READ' in line or 'Our Standars:' in line or 'Reporting by' in line or 'This article is for' in line:
        return None
    line = line.replace('(Reuters)', '')
    line = line.lower()
    return line


@udf(returnType=ArrayType(elementType=StringType()))
def f(body):
    filtered = list(filter(lambda txt: txt is not None,
                    [transform(x) for x in body]))
    return filtered


if __name__ == '__main__':
    import os
   
    HDFS_NAMENODE = os.environ.get("HDFS_NAMENODE","hdfs://namenode:9000")

    spark = SparkSession \
        .builder \
        .appName("wrangler") \
        .master("spark://spark-master:7077") \
        .getOrCreate()

    quiet_logs(spark)

    df = spark.read.parquet(HDFS_NAMENODE + "/user/root/labeled.parquet")

    df.printSchema()

    df.createOrReplaceTempView("ParquetTable")

    sql = spark.sql("select * from ParquetTable")

    sql.withColumn("body_transformed", f(col("body"))
                   ).select("body_transformed").show()
    sql.show()
    sql.write.mode("overwrite").parquet(
        HDFS_NAMENODE + "/user/root/cleaned.parquet")
    spark.read.parquet(HDFS_NAMENODE + "/user/root/cleaned.parquet")
