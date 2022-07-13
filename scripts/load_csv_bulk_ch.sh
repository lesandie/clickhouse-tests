CSVs=`ls *.csv`
for CSV in $CSVs; do
	clickhouse-client --host localhost --port 9000 --query="INSERT INTO test_insert.fact_sales FORMAT CSV" < ${CSV}
done

