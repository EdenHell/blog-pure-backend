CREATE TABLE `essay` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(128) NOT NULL,
  `content` text NOT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

CREATE TABLE `about` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(8) NOT NULL,
  `mail` varchar(128) NOT NULL,
  `github` varchar(128) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `sex` char(8) NOT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE `comment` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `essay_id` bigint(20) unsigned NOT NULL,
  `content` varchar(128) NOT NULL,
  `name` varchar(128) NOT NULL,
  `mail` varchar(128) NOT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `essay_id` (`essay_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;