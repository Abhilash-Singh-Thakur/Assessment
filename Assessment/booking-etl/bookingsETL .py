from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat, lit, udf, when
from pyspark.sql.types import IntegerType
from datetime import datetime, timedelta

'''  Extract  '''

'''
 1. Function for filtering the record where the market segment is Travel Operator.
'''
def operators_bookings(bookings_df):
    
    #transform the data by filter method
    bookings_df = bookings_df.filter(col("market_segment") == "Offline TA/TO")

    return bookings_df



'''
 *  A UDF that adds a number of days to a given date and returns the incremented date.
'''
def month_name_to_int(month_name):
    month_dict = {
        'january': 1,'february': 2,'march': 3,'april': 4,
        'may': 5,'june': 6,'july': 7,'august': 8,'september': 9,
        'october': 10,'november': 11,'december': 12
        }
    return month_dict.get(month_name.lower(), None)



"""
 *   A UDF that adds a number of days to a given date and returns the incremented date.
"""
def add_days_to_date(date, days):
    new_date = datetime.strptime(date, '%Y-%m-%d') + timedelta(days=days)
    return new_date.strftime('%Y-%m-%d')



'''  Transform  '''

'''
 2. Function for create arrival_date and departure_date.
'''
def add_arrival_and_departure_dates_columns(bookings_df):

    '''
    Logic - For arrival date we need to create arrival_month_int column of intger datatype.
    '''
    # Define a UDF from the function month_name_to_int.
    month_name_to_int_udf = udf(month_name_to_int, IntegerType())

    # Apply the UDF to arrival_date_month column and create new column arrival_month_int
    bookings_df = bookings_df.withColumn('arrival_month_int',
                                        month_name_to_int_udf('arrival_date_month'))

    # Create arrival_date column from arrival_date_year, arrival_month_int and arrival_date_day_of_month
    bookings_df = bookings_df.withColumn("arrival_date",
                                        concat(col("arrival_date_year"),lit("-"),
                                        col("arrival_month_int"), lit("-"),
                                        col("arrival_date_day_of_month")))

    # Drop column arrival_month_int
    bookings_df = bookings_df.drop("arrival_month_int")


    '''
    Logic - For departure date we need to calculate total_nights and adding it into arrival_date.
    '''
    #Create the new column total_nights by combining stays_in_weekend_nights and  stays_in_week_nights columns.
    bookings_df = bookings_df.withColumn("total_nights",
                                    col("stays_in_weekend_nights") + col("stays_in_week_nights"))
    
    # Define a UDF from the function.
    add_days_to_date_udf = udf(add_days_to_date)
    
    # Apply the UDF to arrival_date_month column and create new column departure_date.
    bookings_df = bookings_df.withColumn('departure_date', add_days_to_date_udf(col('arrival_date'), col('total_nights')))

    # Drop column total_nights
    bookings_df = bookings_df.drop("total_nights")

    # Cast arrival_date column from string to date datatype for readable format.
    bookings_df = bookings_df.withColumn("arrival_date", col("arrival_date").cast("date"))

    return bookings_df



'''
 3. Function for create column with_family_breakfast.
'''
def add_with_family_breakfast_column(bookings_df):

    # Create with_family_breakfast column with Yes if children and babies sum is greater than 0 otherwise No
    bookings_df = bookings_df.withColumn("with_family_breakfast", when((col("children") + col("babies")) > 0, "Yes").otherwise("No"))
    
    return bookings_df



'''  LOAD  '''

'''
4. Function for save file as parquet format.
'''
def save_to_parquet(bookings_df, output_path):
    # Save resulting dataset as parquet file
    bookings_df.write.format("parquet").mode("overwrite").save("/input_data")



''' Main Function '''

def main():
    # Create SparkSession
    spark = SparkSession \
            .builder \
            .master("yarn") \
            .appName("bookingsETL") \
            .getOrCreate()

    input_path = "/path/to/input/csv"
    output_path = "/path/to/output/parquet"

    bookings_df = spark.read.csv(input_path, header=True, inferSchema=True)
    # Define input and output paths
    
    # Extract bookings with tour operators as market segment designations
    tour_operators_bookings_df = operators_bookings(bookings_df)

    # Add dates columns
    bookings_df_with_dates = add_arrival_and_departure_dates_columns(tour_operators_bookings_df)

    # Add with_family_breakfast column
    bookings_df_with_family_breakfast = add_with_family_breakfast_column(bookings_df_with_dates)

    # Save resulting dataset as parquet file
    save_to_parquet(bookings_df_with_family_breakfast, output_path)

    # Stop SparkSession
    spark.stop()

''' Entry point (Execution starts here) '''

if __name__ == "__main__":
    main()


# this is the another optimized approach

from pyspark.sql.functions import col, concat, expr, to_date

def add_arrival_and_departure_dates_columns(bookings_df):
    bookings_df = bookings_df.withColumn("arrival_date", to_date(expr("concat(arrival_date_year, '-', arrival_date_month, '-', arrival_date_day_of_month)"), "yyyy-MMMM-d"))
    bookings_df = bookings_df.withColumn("total_nights", col("stays_in_weekend_nights") + col("stays_in_week_nights"))
    bookings_df = bookings_df.withColumn("departure_date", expr("date_add(arrival_date, total_nights)"))

    return bookings_df


# most optimized functions
from pyspark.sql.functions import col, concat, expr, to_date, date_format

def add_arrival_and_departure_dates_columns(bookings_df):
    bookings_df = bookings_df.withColumn("arrival_date", to_date(expr("concat(arrival_date_year, '-', arrival_date_month, '-', arrival_date_day_of_month)"), "yyyy-MMMM-d"))
    bookings_df = bookings_df.withColumn("total_nights", col("stays_in_weekend_nights") + col("stays_in_week_nights"))
    bookings_df = bookings_df.withColumn("departure_date", expr("date_add(arrival_date, total_nights)"))
    
    bookings_df = bookings_df.withColumn("arrival_date", date_format(col("arrival_date"), "yyyy-MM-dd")) # convert the date into string data type.
    bookings_df = bookings_df.withColumn("departure_date", date_format(col("departure_date"), "yyyy-MM-dd"))

    return bookings_df























