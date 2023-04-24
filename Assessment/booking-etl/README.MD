
# Instruction to run the spark application.

### 1. Copy the bookings.csv file from local file system to HDFS file system

```
hdfs dfs -put /local-file-path /hdfs-file-path
```

### 2. Set the path variable by assigning input_path and output_path in bookingETL.py file

```
input_path = hdfs-file-path
output_path = output-file-path
```
### 3. To run the spark application follow this command.

```
spark-submit --master yarn \
--deploy-mode client \
--num-executors <number_of_executors> \
--executor-memory <executor_memory> \
--executor-cores <executor_cores> \
--driver-memory <driver_memory> \
--class <main_class> \
<application_jar_file> <input_file_path> <output_file_path>
```



--master yarn: Specifies the Spark master URL to be yarn.\
--deploy-mode client: Specifies the deploy mode. client mode means the driver program runs on the client side.\
--num-executors: The number of executors to be allocated.\
--executor-memory: The amount of memory to be allocated per executor.\
--executor-cores: The number of CPU cores to be allocated per executor.\
--driver-memory: The amount of memory to be allocated for the driver program.\
--class: The fully-qualified name of the main class of your Spark application.\
--<application_jar_file>: The path to the jar file containing your Spark application code.\
--<input_file_path>: The path to the input file.\
--<output_file_path>: The path to the output file.

