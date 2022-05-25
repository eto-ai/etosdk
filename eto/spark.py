from pyspark.sql import SparkSession
from rikai.spark.utils import get_default_jar_version


def get_session():
    ver = get_default_jar_version(use_snapshot=False)
    jars = f"org.apache.hadoop:hadoop-aws:3.1.2,ai.eto:rikai_2.12:{ver}"
    builder = (
        SparkSession.builder.appName("eto-sdk-spark")
            .config("spark.jars.packages", jars)
            .config("spark.executor.extraJavaOptions",
                    ("-Dcom.amazonaws.services.s3.enableV4=true "
                     "-Dio.netty.tryReflectionSetAccessible=true"))
            .config("spark.driver.extraJavaOptions",
                    ("-Dcom.amazonaws.services.s3.enableV4=true "
                     "-Dio.netty.tryReflectionSetAccessible=true"))
            .config("spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version",
                    2)
            .config("spark.hadoop.com.amazonaws.services.s3.enableV4", "true")
            .config("spark.hadoop.fs.AbstractFileSystem.s3a.impl",
                    "org.apache.hadoop.fs.s3a.S3A")
            .config("spark.hadoop.fs.s3a.impl",
                    "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .config("spark.hadoop.fs.s3a.aws.credentials.provider",
                    "com.amazonaws.auth.DefaultAWSCredentialsProviderChain")
    )
    for k, v in SESSION_CONF.items():
        builder = builder.config(k, v)
    spark = (
        builder
        .master("local[*]")
        .enableHiveSupport()
        .getOrCreate()
    )
    return spark


def stop_session():
    spark = SparkSession.getActiveSession()
    if spark:
        spark.stop()


SESSION_CONF = {}


def configure(conf_key, conf_value):
    import eto.spark
    SESSION_CONF[conf_key] = conf_value
    return eto.spark
