CREATE TABLE `stock_list` (
  `index` bigint DEFAULT NULL,
  `code` text,
  `tradeStatus` text,
  `code_name` text,
  KEY `ix_stock_list_index` (`index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3