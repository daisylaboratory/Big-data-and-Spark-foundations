# Khai báo thư viện
from pyspark.sql import SparkSession
from pyspark.ml  import Pipeline
from pyspark.sql import SQLContext
from pyspark.sql.functions import mean,col,split, col, regexp_extract, when, lit
from pyspark.ml.feature import StringIndexer, VectorAssembler, IndexToString
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import QuantileDiscretizer

# Tạo SparkSession
spark = SparkSession.builder.appName('recommender_system').getOrCreate()

# Đọc dữ liệu
df  = spark.read.csv("home/camnh/Desktop/Trung/data/movie_ratings_df.csv", inferSchema=True, header=True)

# Kiểm tra dữ liệu
df.limit(3).toPandas()
df.printSchema()

# Xử lý dữ liệu chuẩn bị huấn luyện mô hình
stringIndexer = StringIndexer(inputCol='title', outputCol='title_new')
# Applying stringindexer object on dataframe movie title column
model = stringIndexer.fit(df)
# creating new dataframe with transformed values
indexed = model.transform(df)
# validate the numerical title values
indexed.limit(5).toPandas()

# split the data into training and test datatset
train, test = indexed.randomSplit([0.75,0.25])
from pyspark.ml.recommendation import ALS

#Training the recommender model using train datatset
rec=ALS( maxIter=10
        ,regParam=0.01
        ,userCol='userId'
        ,itemCol='title_new'
        ,ratingCol='rating'
        ,nonnegative=True
        ,coldStartStrategy="drop")

#fit the model on train set
rec_model=rec.fit(train)

#making predictions on test set
predicted_ratings=rec_model.transform(test)
predicted_ratings.limit(5).toPandas()

# Importing Regression Evaluator to measure RMSE
from pyspark.ml.evaluation import RegressionEvaluator
# create Regressor evaluator object for measuring accuracy
evaluator=RegressionEvaluator(metricName='rmse',predictionCol='prediction',labelCol='rating')
# apply the RE on predictions dataframe to calculate RMSE
rmse=evaluator.evaluate(predicted_ratings)
# print RMSE error
print(rmse)

# Đề xuất các bộ phim
# First we need to create dataset of all distinct movies
unique_movies=indexed.select('title_new').distinct()

#create function to recommend top 'n' movies to any particular user
def top_movies(user_id,n):
    """
    This function returns the top 'n' movies that user has not seen yet but might like

    """
    #assigning alias name 'a' to unique movies df
    a = unique_movies.alias('a')

    #creating another dataframe which contains already watched movie by active user
    watched_movies=indexed.filter(indexed['userId'] == user_id).select('title_new')

    #assigning alias name 'b' to watched movies df
    b=watched_movies.alias('b')

    #joining both tables on left join
    total_movies = a.join(b, a.title_new == b.title_new,how='left')

    #selecting movies which active user is yet to rate or watch
    remaining_movies=total_movies.where(col("b.title_new").isNull()).select(a.title_new).distinct()


    #adding new column of user_Id of active useer to remaining movies df
    remaining_movies=remaining_movies.withColumn("userId",lit(int(user_id)))


    #making recommendations using ALS recommender model and selecting only top 'n' movies
    recommendations=rec_model.transform(remaining_movies).orderBy('prediction',ascending=False).limit(n)


    #adding columns of movie titles in recommendations
    movie_title = IndexToString(inputCol="title_new", outputCol="title",labels=model.labels)
    final_recommendations=movie_title.transform(recommendations)

    #return the recommendations to active user
    return final_recommendations.show(n,False)

# Test: recommend 5 movies for user of id=60
top_movies(60,5)
