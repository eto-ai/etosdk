from pyspark.sql import SparkSession

from rikai.spark.utils import get_default_jar_version


def get_session():
    rikai_jar_vers = get_default_jar_version(use_snapshot=False)

    spark = (
        SparkSession.builder.config(
            "spark.jars.packages", f"ai.eto:rikai_2.12:{rikai_jar_vers}"
        )
        .appName("eto-sdk-spark")
        .master("local[*]")
        .getOrCreate()
    )
    return spark
