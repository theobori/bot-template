CREATE TABLE `guild_log_permission` (
	`guild_id` VARCHAR(30),
	`message_delete` TINYINT DEFAULT 0,
	`message_edit` TINYINT DEFAULT 0,
	`role_create` TINYINT DEFAULT 0,
	`role_delete` TINYINT DEFAULT 0,
	`role_update` TINYINT DEFAULT 0,
	PRIMARY KEY (`guild_id`),
	UNIQUE KEY (`guild_id`)
);

CREATE TABLE `guild_log_channel` (
    `guild_id` VARCHAR(30),
	`messages` VARCHAR(100) DEFAULT NULL,
	`roles` VARCHAR(100) DEFAULT NULL,
	FOREIGN KEY (`guild_id`) REFERENCES `guild_log_permission`(`guild_id`) ON DELETE CASCADE,
    UNIQUE KEY (`guild_id`)
);

CREATE TABLE `warn` (
	`guild_id` VARCHAR(30),
	`user_id` VARCHAR(30),
	`count` INT DEFAULT 1,
	FOREIGN KEY (`guild_id`) REFERENCES `guild_log_permission`(`guild_id`) ON DELETE CASCADE,
	UNIQUE KEY (`guild_id`, `user_id`)
);

CREATE TABLE `command_stat` (
    `guild_id` VARCHAR(30),
	`name` VARCHAR(30),
	`count` INT DEFAULT 1,
	FOREIGN KEY (`guild_id`) REFERENCES `guild_log_permission`(`guild_id`) ON DELETE CASCADE,
    UNIQUE KEY (`guild_id`, `name`)
);
