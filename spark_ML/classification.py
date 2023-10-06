# Khai báo các thư viện
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, OneHotEncoder
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier, GBTClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# Mở SparkSession
spark = SparkSession.builder.appName('Classification Model').getOrCreate()

# Đọc dữ liệu
df = spark.read.csv('home/camnh/Desktop/Trung/data/titanic_train.csv', header=True, inferSchema=True)

# Kiểm tra dữ liệu
df.show(4)
df.printSchema()

print('Number of rows: \t', df.count())
print('Number of columns: \t', len(df.columns))

# Phân tích dữ liệu
df.groupBy('Survived').mean('Fare', 'Age').show()
df.groupBy('Survived').pivot('Sex').count().show()
df.groupBy('Survived').pivot('Pclass').count().show()

for col in df.columns:
    print(col, '\t\t', df.filter(df[col].isNull()).count())

# Xử lý dữ liệu
df = df.fillna({'Embarked': 'S'})
df = df.withColumn('FamilySize', df['Parch'] + df['SibSp']).\
            drop('Parch', 'SibSp')
df = df.drop('PassengerID', 'Age', 'Cabin', 'Name', 'Ticket')

for col in df.columns:
    print(col, '\t\t', df.filter(df[col].isNull()).count())

# Chuẩn bị dữ liệu để huấn luyện mô hình
stringIndex = StringIndexer(inputCols=['Sex', 'Embarked'],
                       outputCols=['SexNum', 'EmbNum'])

stringIndex_model = stringIndex.fit(df)

df = stringIndex_model.transform(df).drop('Sex', 'Embarked')
df.show(4)

vec_asmbl = VectorAssembler(inputCols=df.columns[1:],
                           outputCol='features')

df = vec_asmbl.transform(df).select('features', 'Survived')
df.show(4, truncate=False)

# Chia dữ liệu huấn luyện và kiểm tra
train_df, test_df = df.randomSplit([0.7, 0.3])
train_df.show(4, truncate=False)

# Huấn luyện mô hình
ridge = LogisticRegression(labelCol='Survived',
                        maxIter=100,
                        elasticNetParam=0, # Ridge regression is choosen
                        regParam=0.3)

model = ridge.fit(train_df)

lasso = LogisticRegression(labelCol='Survived',
                           maxIter=100,
                           elasticNetParam=1, # Lasso
                           regParam=0.0003)

model = lasso.fit(train_df)

# Dự đoán kết quả
pred = model.evaluate(test_df)

# Đánh giá mô hình
pred.accuracy


# Mô hình Random Forest
evaluator = MulticlassClassificationEvaluator(labelCol='Survived',
                                          metricName='accuracy')
rf = RandomForestClassifier(labelCol='Survived',
                           numTrees=100, maxDepth=3)

model = rf.fit(train_df)
pred = model.transform(test_df)
evaluator.evaluate(pred)

# Mô hình GBT
gb = GBTClassifier(labelCol='Survived', maxIter=100, maxDepth=4)

model = gb.fit(train_df)
pred = model.transform(test_df)
evaluator.evaluate(pred)