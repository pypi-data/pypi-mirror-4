DROP TABLE IF EXISTS `Withdraw`;
CREATE TABLE `Withdraw` (
  `id` bigint(20)  unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20)  unsigned NOT NULL,
  `op_time` bigint(20)  unsigned NOT NULL,
  `package_id` bigint(20)  unsigned NOT NULL,
  `pay_amt` bigint(20)  unsigned NOT NULL,
  `bank_no` bigint(19) unsigned NOT NULL,
  `bank_type` smallint(4) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  `desc` varchar(128),
  `phone` bigint(11) unsigned,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`package_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
