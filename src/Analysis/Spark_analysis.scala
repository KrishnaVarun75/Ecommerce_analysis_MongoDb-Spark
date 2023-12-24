import org.apache.spark.sql._
import org.apache.spark.sql.functions._
import org.apache.spark.sql.expressions.Window
import org.apache.spark.sql.DataFrame

object Spark_analysis {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("MongoDB_Spark")
      .master("local[*]")
      .config("spark.mongodb.input.uri", "mongodb://localhost:27017/ecommerce.project")
      .config("spark.mongodb.output.uri", "mongodb://localhost:27017/ecommerce.project")
      .getOrCreate()

    val mongoDF: DataFrame = spark.read
      .format("mongo")
      .load()
      .drop("_id")

    val dataColumns = Array(
      "order_id", "customer_id", "timestamp", "customer_city", "customer_state",
      "quantity", "price_MRP", "payment", "payment_type", "payment_installments",
      "product_id", "product_category", "rating", "seller_id", "seller_city",
      "seller_state", "order_status"
    )

    val data = mongoDF.select(dataColumns.map(col): _*)
    data.show(5)
    data.count()
    val size = data.count()
    println(s"Size of data: $size")

    val data2 = mongoDF.filter(!(mongoDF.columns.map(c => col(c).isNull || trim(column(c)) === "").reduce(_ || _)))
    data2.show(5)
    val size2 = data2.count()
    println(s"Size of data: $size2")

//customerLifetimeValuePrediction(data2) //geetha
//   peakOrderHoursAnalysis(data2)     //himamsh
//  seasonalTrendsInSales(data2)     //varun
//    Seller_totalRevenue_byTime(data2)       //varun
// average_tax_by_payment_type(data2)    //himamsh
// seller_loyalty_analysis(data2)    //dinakar
//top_selling_product_category(data2)   //geetha
//   products_with_common_state(data2)    //dinakar
    spark.stop()
  }


  def customerLifetimeValuePrediction(df: DataFrame): Unit = {

    val aovPerCustomer = df.filter(col("order_status") === "delivered")
      .groupBy(col("customer_id"))
      .agg(avg(col("payment")).alias("avg_order_value"))

    val purchaseFrequency = df.filter(col("order_status") === "delivered")
      .groupBy(col("customer_id"))
      .agg(countDistinct(col("order_id")).alias("purchase_count"))

    val clvDF = aovPerCustomer.join(purchaseFrequency, "customer_id")
      .withColumn("clv", col("avg_order_value") * col("purchase_count"))
      .orderBy(col("clv").desc)

    clvDF.show()
  }


  def seasonalTrendsInSales(df: DataFrame): Unit = {

    val Season = df.filter(col("order_status") === "delivered")
      .withColumn("order_month", month(to_timestamp(col("timestamp"), "dd-MM-yyyy HH:mm")))
      .groupBy("order_month")
      .agg(sum("payment").alias("total_sales"))
      .orderBy("order_month")

    Season.show()
  }


  def peakOrderHoursAnalysis(df: DataFrame): Unit = {

    val dfWithTimestamp = df.withColumn("timestamp", to_timestamp(col("timestamp"), "dd-MM-yyyy HH:mm"))

    val ordersByHour = dfWithTimestamp
      .withColumn("order_hour", hour(col("timestamp")))
      .groupBy("order_hour")
      .agg(count("order_id").alias("order_count"))
      .orderBy(col("order_hour"))

    ordersByHour.show()
  }


  def Seller_totalRevenue_byTime(df1: DataFrame):Unit= {
    val df = df1.withColumn("timestamp", to_timestamp(col("timestamp"), "dd-MM-yyyy HH:mm"))
    val windowSpec = Window.partitionBy("seller_id").orderBy("timestamp")


    val rankedSellers = df.withColumn("total_revenue_overtime",sum("payment")
      .over(windowSpec)).where(col("seller_id")==="ccc4bbb5f32a6ab2b7066a4130f114e3")
      .select("seller_id","timestamp","payment","total_revenue_overtime")

    rankedSellers.show()

    
  }

  def average_tax_by_payment_type(df: DataFrame): Unit= {

    val dfWithTax = df.withColumn("tax", col("payment") - col("price_MRP"))

    val averageTaxByPaymentType = dfWithTax.groupBy("payment_type")
      .agg(avg("tax").alias("average_tax"))

    averageTaxByPaymentType.show()
  }

  def seller_loyalty_analysis(df: DataFrame): Unit = {

    val repeatCustomersBySeller = df.groupBy("seller_id", "customer_id")
      .agg(count("order_id").alias("order_count"))
      .filter(col("order_count") > 1)

    val totalRepeatCustomersBySeller = repeatCustomersBySeller.groupBy("seller_id")
      .agg(countDistinct("customer_id").alias("total_repeat_customers"))

    val topSellersWithRepeatCustomers = totalRepeatCustomersBySeller
      .orderBy(desc("total_repeat_customers"))
      .show(10)
  }

  def top_selling_product_category(df: DataFrame): Unit = {

    val productCategorySales = df.groupBy("product_category")
      .agg(sum("quantity").alias("total_quantity_sold"))

    val topSellingCategory = productCategorySales
      .orderBy(desc("total_quantity_sold"))
      .limit(10)

    topSellingCategory.show()
  }

  def products_with_common_state(df: DataFrame): Unit = {

    val productStateCounts = df.groupBy("product_id", "customer_state")
      .agg(count("order_id").alias("occurrences"))

    val commonStateProducts = productStateCounts.groupBy("product_id")
      .agg(collect_set("customer_state").alias("common_states"))
      .filter(size(col("common_states")) > 1).show()
  }

  }
