import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
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

    import nltk

    nltk.download('stopwords')
    from nltk.corpus import stopwords
    stop_words = stopwords.words("english")

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

    words = news.select(
        explode(
            split(news.value, " ")
        ).alias("word"),
        news.timestamp
    ).filter(~lower(col("word")).isin(stop_words))

    word_count = words.groupBy(window(words.timestamp,"1 day"), "word")\
        .count().orderBy(desc("count")).limit(10).orderBy("window")
    query = word_count \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()

    query.awaitTermination()