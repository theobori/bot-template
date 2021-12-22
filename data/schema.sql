CREATE TABLE `guild_log` (
    `guild_id` VARCHAR(30),
	`messages` VARCHAR(100) DEFAULT NULL,
    `voices` VARCHAR(100) DEFAULT NULL,
	`roles` VARCHAR(100) DEFAULT NULL,
	PRIMARY KEY (`guild_id`),
    UNIQUE KEY (`guild_id`)
);

CREATE TABLE `guild_log_permission` (
	`guild_id` VARCHAR(30) REFERENCES `guild_log`(`guild_id`) ON DELETE CASCADE,
	`message_delete` TINYINT DEFAULT 0,
	`message_edit` TINYINT DEFAULT 0,
	`role_create` TINYINT DEFAULT 0,
	`role_delete` TINYINT DEFAULT 0,
	`role_update` TINYINT DEFAULT 0,
	PRIMARY KEY (`guild_id`),
	UNIQUE KEY (`guild_id`)
);

CREATE TABLE `warn` (
	`guild_id` VARCHAR(30) REFERENCES `guild_log`(`guild_id`) ON DELETE CASCADE,
	`user_id` VARCHAR(30),
	`count` INT DEFAULT 0,
	PRIMARY KEY (`guild_id`),
	UNIQUE KEY (`guild_id`, `user_id`)
);

CREATE TABLE `command_stat` (
    `guild_id` VARCHAR(30) REFERENCES `guild_log`(`guild_id`) ON DELETE CASCADE,
	`name` VARCHAR(30),
	`count` INT DEFAULT 0,
	PRIMARY KEY (`guild_id`),
    UNIQUE KEY (`guild_id`)
);