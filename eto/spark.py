from pyspark.sql import SparkSession


def get_session():
    spark = (
        SparkSession.builder.appName("eto-sdk-spark").master("local[1]").getOrCreate()
    )
    return spark
