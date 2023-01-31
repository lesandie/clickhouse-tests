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
ENGINE = ReplacingMergeTree()
ORDER BY (id_order, id_plat, id_warehouse)
PARTITION BY tuple()

-- Generate data into a csv for INSERT

SELECT * 
FROM generateRandom('id_order UInt16,id_plat UInt32,id_warehouse UInt64,id_product UInt16,order_type UInt16,order_status String,datetime_order DateTime,units Int16,total Float32')
LIMIT 1000 INTO OUTFILE 'file.csv' FORMAT CSVWithNames