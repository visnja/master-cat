
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, PandasUDFType
# import preprocess
from pyspark.sql.types import ArrayType, StringType


SPACY_MODEL = None

def get_spacy_model():
    import spacy
    import en_core_web_lg
    global SPACY_MODEL
    if not SPACY_MODEL:
        _model = en_core_web_lg.load()
        _model.vocab.add_flag(
           lambda s: s.lower() in spacy.lang.en.stop_words.STOP_WORDS,
           spacy.attrs.IS_STOP
       )
        SPACY_MODEL = _model
    return SPACY_MODEL

def quiet_logs(sc):
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel(logger.Level.ERROR)
    logger.LogManager.getLogger("akka").setLevel(logger.Level.ERROR)

def transform(line):
    if line in ['',"\n"] or line.startswith("By") or 'MIN READ' in line or 'Our Standars:' in line or 'Reporting by' in line or 'This article is for' in line:
        return None
    line = line.replace('(Reuters)','')
    line = line.lower()
    return line

@udf(returnType=StringType())
def tokenize_and_clean(documents):
    spacy_model = get_spacy_model()
    docs = spacy_model.pipe(documents)
    tokens = [" ".join([tok.lemma_ for tok in doc if not tok.is_stop and tok.text])
              for doc in docs]
    tokens_series = " ".join(tokens)
    return tokens_series

@udf(returnType=ArrayType(elementType=StringType()))
def f(body):
    filtered = list(filter(lambda txt: txt is not None, [transform(x) for x in body]))
    return filtered





if __name__=='__main__':
    import os
    os.environ['PYSPARK_PYTHON'] = "./environment/bin/python"
    spark = SparkSession \
    .builder \
    .appName("app") \
    .master("spark://spark-master:7077") \
    .getOrCreate()


    quiet_logs(spark)
  
    df = spark.read.parquet("hdfs://namenode:9000//user/root/crawler.parquet")
    df = df.drop("contentType","visited", "date", "icon","created_at",'url','classes_body','classes_summary','classes_target','publishedAt','classes_title','source','alternateImageUrl')

    df.printSchema()

    df.createOrReplaceTempView("ParquetTable")

    sql = spark.sql("select _id, body from ParquetTable")

    print('Trying foreach')
   
    sql = sql.withColumn("body_transformed",f(col("body")))
    sql.withColumn("removed_stopwords",tokenize_and_clean(col("body_transformed"))).select("removed_stopwords").show()