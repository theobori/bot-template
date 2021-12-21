CREATE TABLE `command_stat` (
    `guild_id` VARCHAR(30),
	`name` VARCHAR(30),
	`count` INT DEFAULT 0,
    UNIQUE KEY `guild_id` (`guild_id`)
);

CREATE TABLE `guild_log` (
    `guild_id` VARCHAR(30),
	`join_left` VARCHAR(100) DEFAULT NULL,
	`messages` TEXT DEFAULT NULL,
    `voices` VARCHAR(100) DEFAULT NULL,
    UNIQUE KEY `guild_id` (`guild_id`)
);

CREATE TABLE `warn` (
	`guild_id` VARCHAR(30),
	`user_id` VARCHAR(30),
	`count` INT DEFAULT 0,
	UNIQUE KEY `guild_id` (`guild_id`, `user_id`)
);