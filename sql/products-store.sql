CREATE TABLE `Products` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `image` varchar(255),
  `title` varchar(255),
  `rate_num` float,
  `reviews` integer,
  `price` float,
  `best_seller` boolean,
  `sales` integer,
  `link` text,
  `id_store` integer
);

CREATE TABLE `Stores` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255)
);

ALTER TABLE `Products` ADD FOREIGN KEY (`id_store`) REFERENCES `Stores` (`id`);
