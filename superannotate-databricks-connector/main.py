from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Test Application").getOrCreate()

simpleData = (("Java", 4000, 5),
              ("Python", 4600, 10),
              ("Scala", 4100, 15),
              ("Scala", 4500, 15),
              ("PHP", 3000, 20))

columns = ["CourseName", "fee", "discount %"]

# Create DataFrame
df = spark.createDataFrame(data=simpleData, schema=columns)
df.printSchema()
df.show(truncate=False)
