import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
# import preprocess
from pyspark.sql.types import ArrayType, StringType

NLTK = None
CONTRACTIONS = None
RE = None


def quiet_logs(sc):
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel(logger.Level.ERROR)
    logger.LogManager.getLogger("akka").setLevel(logger.Level.ERROR)


def transform(line):
    if line in ['', "\n"] or line.startswith("By") or 'MIN READ' in line or '(Reuters)' in line:
        return None
    return line


def get_packages():

    global NLTK
    global RE
    if not NLTK:
        import nltk
        NLTK = nltk
    if not RE:
        import re
        RE = re

    return NLTK, RE


@udf(returnType=StringType())
def clean(txt):
    nltk, re = get_packages()
    txt = re.sub(r'\d+ min read', '', str(txt), flags=re.IGNORECASE)
    txt = re.sub(r'by reuters staff', '', str(txt), flags=re.IGNORECASE)
    # separate sentences with '. '
    txt = re.sub(r'\.(?=[^ \W\d])', '. ', str(txt))
    # remove punctuations and characters
    txt = re.sub(r'[^\w\s]', '', txt)
    # strip
    txt = " ".join([word.strip() for word in txt.split()])
    # lowercase
    txt = txt.lower()
    # tokenize (convert from string to list)
    lst_txt = txt.split()
    # stemming (remove -ing, -ly, ...)

    ps = nltk.stem.porter.PorterStemmer()
    lst_txt = [ps.stem(word) for word in lst_txt]
    # lemmatization (convert the word into root word)

    lem = nltk.stem.wordnet.WordNetLemmatizer()
    lst_txt = [lem.lemmatize(word) for word in lst_txt]
    # back to string
    txt = " ".join(lst_txt)

    return txt


if __name__ == '__main__':

    import os
    os.environ['PYSPARK_PYTHON'] = "./environment/bin/python"

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
        .option("subscribe", "subreddit-forex") \
        .load()

    news = news.withColumn("cleaned", clean(col("value")))

    news.printSchema()
    words = news.select(
        explode(
            split(news.cleaned, " ")
        ).alias("word"),
        news.timestamp
    ).filter(~lower(col("word")).isin(stop_words))

    word_count = words.groupBy(window(words.timestamp, "1 day"), "word")\
        .count().orderBy(desc("count")).limit(10).orderBy("window")
    query = word_count \
        .writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    query.awaitTermination()
