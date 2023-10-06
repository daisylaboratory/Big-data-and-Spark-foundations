# Khai báo các thư viện
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import VectorAssembler

# Mở spark session
spark = SparkSession.builder.appName("Linear Regression Model").getOrCreate()

# Đọc dữ liệu
data = spark.read.csv('home/camnh/Desktop/Trung/data/Ecommerce_Customers.csv',header = True, inferSchema = True)

# Kiểm tra dữ liệu
data.show(4)
data.printSchema()
for item in data.head(1)[0]:
    print(item)
data.columns

# Xử lý và chuẩn bị dữ liệu
assembler = VectorAssembler(inputCols =['Avg Session Length','Time on App','Time on Website','Length of Membership'],
                            outputCol='features')
output = assembler.transform(data)
output.printSchema()
output.head(1)
final_data = output.select('features','Yearly Amount Spent')

# Chia dữ liệu huấn luyện và kiểm tra
train_data,test_data = final_data.randomSplit([0.7,0.3])
train_data.describe().show()
test_data.describe().show()

# Huấn luyện mô hình
regressor = LinearRegression(labelCol='Yearly Amount Spent')
model = regressor.fit(train_data)

# Đánh giá kết quả mô hình
pred_data = model.evaluate(test_data)
pred_data.residuals.show()
pred_data.rootMeanSquaredError
pred_data.r2

# Dự đoán cho dữ liệu mới
unlabeled_data = test_data.select('features')
test_predictions = model.transform(unlabeled_data)
test_predictions.show()