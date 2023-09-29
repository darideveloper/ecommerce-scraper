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
  `id_store` integer,
  `id_request` integer
);

CREATE TABLE `Stores` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `use_proxies` bool
);

CREATE TABLE `ApiKeys` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `api_key` varchar(255),
  `is_active` bool
);

CREATE TABLE `Requests` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `status` integer,
  `todo_datetime` datetime,
  `working_datetime` datetime,
  `done_datetime` datetime,
  `api_key` integer
);

CREATE TABLE `Status` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255)
);

CREATE TABLE `Cookies` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `id_store` integer,
  `username` varchar(255),
  `cookies` json,
  `status` integer
);

ALTER TABLE `Products` ADD FOREIGN KEY (`id_store`) REFERENCES `Stores` (`id`);

ALTER TABLE `Products` ADD FOREIGN KEY (`id_request`) REFERENCES `Requests` (`id`);

ALTER TABLE `Requests` ADD FOREIGN KEY (`status`) REFERENCES `Status` (`id`);

ALTER TABLE `Requests` ADD FOREIGN KEY (`api_key`) REFERENCES `ApiKeys` (`id`);

ALTER TABLE `Cookies` ADD FOREIGN KEY (`id_store`) REFERENCES `Stores` (`id`);

ALTER TABLE `Cookies` ADD FOREIGN KEY (`status`) REFERENCES `Status` (`id`);
