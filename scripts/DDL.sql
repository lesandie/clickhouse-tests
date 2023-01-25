CREATE TABLE default.insert_test
(
    `id_order` UInt16,
    `id_plat` UInt32,
    `id_warehouse` UInt64,
    `id_product` UInt16,
    `order_type` UInt16,
    `order_status` String,
    `datetime_order` DateTime,
    `units` Int16,
    `total` Float32
)
ENGINE = Log

-- Generate data into a csv for INSERT

SELECT * 
FROM generateRandom('id_order Int16,id_plat Int32,id_warehouse Int64,id_product Int16,order_type Int16,order_status String,datetime_order DateTime,units Int16,total Float32')
LIMIT 10 INTO OUTFILE 'file.csv' FORMAT CSVWithNames