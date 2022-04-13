from pyspark.sql import SparkSession

from rikai.spark.utils import get_default_jar_version


def get_session():
    rikai_jar_vers = get_default_jar_version(use_snapshot=False)

    spark = (
        SparkSession.builder.config(
            "spark.jars.packages",
            f"ai.eto:rikai_2.12:{rikai_jar_vers},org.apache.hadoop:hadoop-aws:3.2.3",
        )
        .config("com.amazonaws.services.s3.enableV4", "true")
        .config(
            "fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.InstanceProfileCredentialsProvider,"
            "com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
        )
        .appName("eto-sdk-spark")
        .master("local[*]")
        .getOrCreate()
    )
    return spark
