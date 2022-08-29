
from ntpath import join
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, PandasUDFType
# import preprocess
from pyspark.sql.types import ArrayType, StringType


SPACY_MODEL = None
SPACY_MATCHER = None

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

def get_spacy_matcher():
    from spacy.matcher import Matcher
    nlp = get_spacy_model()
    global SPACY_MATCHER
    if not SPACY_MATCHER:
        matcher = Matcher(nlp.vocab)
        matcher.add('AUD', [
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?AUD'}}],
            [{'TEXT':{'REGEX':'AUD[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'aud'}],
            [{'LOWER':'aussie'}],
            [{"LOWER":'the','OP':'?'},{"LOWER":'australian'},{'LOWER':{'REGEX':'dollar[s]?'}}]
        ])
        matcher.add('USD', [
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?USD'}}],
            [{'TEXT':{'REGEX':'USD[/?][A-Z][A-Z][A-Z]'}}],
            [{'LOWER':{'REGEX':'[-]?the'}},{"LOWER":'dollar'}],
            [{"LOWER":'us'},{'LOWER':{'REGEX':'dollar[s]?'}}],
            [{"LOWER":'u.s.'},{'LOWER':{'REGEX':'dollar[s]?'}}],
            [{"POS":'ADJ'},{'LOWER':{'REGEX':'dollar[s]?'}}],
            [{"DEP": "compound","OP": "?"},{'LOWER':{'REGEX':'dollar[s]?'}}],
            [{"LOWER":"usd"}]
        ])
        matcher.add('EUR', [
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?EUR'}}],
            [{'TEXT':{'REGEX':'EUR[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'eur'}],
            [{'LOWER':'the','OP':'?'},{'LOWER':{'REGEX':'euro[s]?[.]?'}}]
        ])
        matcher.add('GBP', [
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?GBP'}}],
            [{'TEXT':{'REGEX':'GBP[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'gbp'}],
            [{'LOWER':'the','OP':'?'},{'LOWER':'british','OP':'?'},{'LOWER':{'REGEX':'pound[s]?'}}],
            [{'LOWER':{'REGEX':'[-]?sterling[s]?'}}]
        ])
        matcher.add('CHF', [
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?CHF'}}],
            [{'TEXT':{'REGEX':'CHF[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'chf'}],
            [{'LOWER':'swissie'}],
            [{'LOWER':'swiss'},{'LOWER':{'REGEX':'franc[s]?'}}]])
        matcher.add('CAD', [
            [{'LOWER':'cad'}],
            [{'LOWER':'cdn'}],
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?CAD'}}],
            [{'TEXT':{'REGEX':'CAD[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'canadian'},{'LOWER':{'REGEX':'dollar[s]?'}}]])
        matcher.add('CNY', [
            [{'LOWER':'cny'}],
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?CNY'}}],
            [{'TEXT':{'REGEX':'CNY[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'the','OP':'?'},{'LOWER':'chinese'},{'LOWER':'yuan'},{"IS_PUNCT": True,'OP':'?'}],
            [{'LOWER':{'REGEX':'yuan[s]?'}}]
                        ])
        matcher.add('TWD', [
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?TWD'}}],
            [{'TEXT':{'REGEX':'TWD[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'twd'}],
            [{'LOWER':'taiwan'},{'LOWER':'new','OP':'?'},{'LOWER':{'REGEX':'dollar[s]?'}}]
            ])
        matcher.add('NZD', [
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?NZD'}}],
            [{'TEXT':{'REGEX':'NZD[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'nzd'}],
            [{'LOWER':'kiwi'}],
            [{'LOWER':'new'},{'LOWER':'zealand'},{'LOWER':{'REGEX':'dollar[s]?'}}]
        ])
        matcher.add('BTC', [
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?BTC'}}],
            [{'TEXT':{'REGEX':'BTC[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'btc'}],
            [{'LOWER':{'REGEX':'bitcoin[s]?'}}]
        ])
        matcher.add('JPY', [
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?JPY'}}],
            [{'TEXT':{'REGEX':'JPY[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'jpy'}],
            [{'LOWER':'japanese'},{'LOWER':{'REGEX':'yen[s]?'}}],
            [{'LOWER':'the','OP':'?'},{'LOWER':{'REGEX':'yen[s]?'}}]
        ])
        matcher.add('TRY', [
            [{'LOWER':'try'}],
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?TRY'}}],
            [{'TEXT':{'REGEX':'TRY[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'turkish'},{'LOWER':{'REGEX':'lira[s]?'}}],
            [{'LOWER':{'REGEX':"turkey's?"}},{'LOWER':{'REGEX':'lira[s]?'}}],
            
        ])
        matcher.add('ARS', [
            [{'LOWER':'ars'}],
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?ARS'}}],
            [{'TEXT':{'REGEX':'ARS[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'argentine'},{'LOWER':{'REGEX':'peso[s]?'}}],
            
        ])
        matcher.add('MXN', [
            [{'TEXT':{'REGEX':'[a-z][a-z][a-z]MXN'}}],
            [{'TEXT':{'REGEX':'MXN[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'mxn'}],
            [{'LOWER':'mexican'},{'LOWER':{'REGEX':'peso[s]?'}}],
            [{'LOWER':'mexican'},{'LOWER':{'REGEX':'currenc[y|ies]?'}}]
            
        ])

        matcher.add('RUB', [
            [{'LOWER':'rub'}],
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?RUB'}}],
            [{'TEXT':{'REGEX':'RUB[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'russian'},{'LOWER':{'REGEX':'ruble[s]?'}}],
            [{'LOWER':{'REGEX':'ruble[s]?'}}]
            
        ])
        matcher.add('OIL', [
            [{'LOWER':'crude'},{'LOWER':{'REGEX':'oil[s]?'}}],
        ])
        matcher.add('XAU', [
            [{'TEXT':{'REGEX':'[A-Z][A-Z][A-Z][/]?XAU'}}],
            [{'TEXT':{'REGEX':'XAU[/]?[A-Z][A-Z][A-Z]'}}],
            [{'LOWER':'xau'}],
            [{'LOWER':'gold'},{'LOWER':{'REGEX':'price[s]?'}}],
        ])
        matcher.add('INDEX',[
            [{'LOWER':'nasdaq100'}],
            [{'LOWER':'nasdaq'},{'ORTH':"100"}],
            [{'LOWER':'s&p500'}],
            [{'LOWER':'sp500'}],
            [{"LOWER": "sp"}, {"ORTH": "500"}],
            [{"LOWER": "s&p"}],
            [{"LOWER": "s&p"}, {"ORTH": "500"}],
            [{'LOWER':'dow'},{'LOWER':'jones'}],
            [{'LOWER':'djia'}],
            [{'LOWER':'dow'},{'LOWER':'jones'},{'LOWER':'industrial'},{'LOWER':'average'}],
            [{'LOWER':'ftse'},{"ORTH": '100','OP':'?'}],
            [{'LOWER':'financial'},{'LOWER':'times'},{'LOWER':'stock'},{'LOWER':'exchange'}],
            [{'LOWER':'footsie'}],
            [{'LOWER':'dax'}],
            [{'LOWER':'dax'},{"ORTH": '40','OP':'?'}],
            [{'LOWER':'german'},{'LOWER':'stock'},{'LOWER':'index'}],
            [{'LOWER':'nikkei'},{"ORTH": '225','OP':'?'},{'LOWER':'index','OP':'?'}],
            [{'LOWER':'nikkei'},{'LOWER':'stock'},{'LOWER':'average'}],
            [{'LOWER':'hsi'},],
            [{'LOWER':'hang'},{'LOWER':'seng'},{'LOWER':'index'}],
            [{'LOWER':'hang'},{'LOWER':'seng'}],
            [{'LOWER':'ecb'}],
            [{'LOWER':'europian'},{'LOWER':'central'},{'LOWER':'bank'}],
            [{'LOWER':'boe'}],
            [{'LOWER':'boc'}],
            [{'LOWER':'boj'}],
            [{'LOWER':'bank'},{'LOWER':'of'},{'LOWER':'england'}],
            [{'LOWER':'bank'},{'LOWER':'of'},{'LOWER':'japan'}],
            [{'LOWER':'bank'},{'LOWER':'of'},{'LOWER':'canada'}],
            [{'LOWER':{'REGEX':'fed[eral]?'}},{'LOWER':'reserve'},{'LOWER':'bank'}],
            [{'LOWER':"russia's"},{'LOWER':'central'},{'LOWER':'bank'}]
            
        ])
        matcher_2 = Matcher(nlp.vocab)
        matcher_2.add('NASDAQ100',[
            [{'LOWER':'nasdaq100'}],
            [{'LOWER':'nasdaq'},{'ORTH':"100", 'OP':'?'}]
        ]) 
        matcher_2.add('S&P500',[
            [{'LOWER':'s&p500'}],
            [{'LOWER':'sp500'}],
            [{"LOWER": "sp"}, {"ORTH": "500"}],
            [{"LOWER": "s&p"}, {"ORTH": "500"}]
        ])
        matcher_2.add('DJIA',[
            [{'LOWER':'dow'},{'LOWER':'jones'}],
            [{'LOWER':'djia'}],
            [{'LOWER':'dow'},{'LOWER':'jones'},{'LOWER':'industrial'},{'LOWER':'average'}]
            
        ])
        matcher_2.add('FTSE',[
            [{'LOWER':'ftse'},{"ORTH": '100','OP':'?'}],
            [{'LOWER':'financial'},{'LOWER':'times'},{'LOWER':'stock'},{'LOWER':'exchange'}],
            [{'LOWER':'footsie'}]
            
        ])
        matcher_2.add('DAX',[
            [{'LOWER':'dax'}],
            [{'LOWER':'dax'},{"ORTH": '40','OP':'?'}],
            [{'LOWER':'german'},{'LOWER':'stock'},{'LOWER':'index'}]
            
        ])
        matcher_2.add('N225',[
            [{'LOWER':'nikkei'},{"ORTH": '225','OP':'?'},{'LOWER':'index','OP':'?'}],
            [{'LOWER':'nikkei'},{'LOWER':'stock'},{'LOWER':'average'}]
            
        ])
        matcher_2.add('HSI',[
            [{'LOWER':'hsi'},],
            [{'LOWER':'hang'},{'LOWER':'seng'},{'LOWER':'index','OP':'?'}]
            
        ])
        SPACY_MATCHER = matcher
    
    return SPACY_MATCHER

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

@udf(returnType=ArrayType(elementType=StringType()))
def match_tokens(text):
    nlp = get_spacy_model()
    matcher = get_spacy_matcher()

    if (text and (type(text) == str or type(text) == list)):
        text = text if type(text) == str else " ".join(text)
        classes = []
        tokens = nlp(text)
        matches = matcher(tokens)
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]  # Get string representation
            classes.append(string_id)
            span = tokens[start:end]  # The matched span
        return list(set(classes))
    return list(set([]))

@udf(returnType=ArrayType(elementType=StringType()))
def join_tokens(body,title,summary):
   
    return list(set(body+title+summary))


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
    df = df.drop("contentType","visited", "icon",'classes_body','classes_summary','classes_target','classes_title','source','alternateImageUrl')

    # df.printSchema()

    df.createOrReplaceTempView("ParquetTable")

    sql = spark.sql("select * from ParquetTable")

    
   
    sql = sql.withColumn("classes",match_tokens(col("summary")))
    sql = sql.withColumn("classes_body",match_tokens(col("body")))
    sql =  sql.withColumn("classes_title",match_tokens(col("title")))
    # sql = sql.withColumn("target",join_tokens(col["classes"],col['classes_title'] , col['classes_body']))
    # sql.withColumn("removed_stopwords",tokenize_and_clean(col("body_transformed"))).select("removed_stopwords").show()
    sql.show()
    sql.write.mode("overwrite").parquet("hdfs://namenode:9000//user/root/labaled.parquet")
    spark.read.parquet("hdfs://namenode:9000//user/root/labaled.parquet")