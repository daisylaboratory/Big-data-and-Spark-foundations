# Khai báo các thư viện cần thiết
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import StandardScaler
from pyspark.ml.clustering import KMeans

# Mở spark session
spark = SparkSession.builder.appName('Kmeans').getOrCreate()

# Đọc dữ liệu
data = spark.read.csv('home/camnh/Desktop/Trung/data/hack_data.csv',header=True,inferSchema=True)

# Kiểm tra dữ liệu
data.printSchema()
data.columns

# Xử lý dữ liệu tạo vector cho các đặc trưng
assembler = VectorAssembler(inputCols=['Session_Connection_Time',
 'Bytes Transferred',
 'Kali_Trace_Used',
 'Servers_Corrupted',
 'Pages_Corrupted',
 'WPM_Typing_Speed'], outputCol='features')

final_data = assembler.transform(data)
final_data.printSchema()

# Xử lý scale dữ liệu
scaler = StandardScaler(inputCol='features',outputCol='scaledFeat')
final_data = scaler.fit(final_data).transform(final_data)
final_data.printSchema()

# Thử với k = 2
kmeans = KMeans(featuresCol='scaledFeat', k=2)

# Xây dựng mô hình
model = kmeans.fit(final_data)
results = model.transform(final_data)

# In ra điểm center
centers = model.clusterCenters()
print(centers)

# In ra kết quả
results.printSchema()
results.show(10)
results.describe().show()
results.groupBy('prediction').count().show()
