CREATE TABLE `agromate_db`.`users`(
    `u_id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(150) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `password` VARCHAR(30) NOT NULL,
    `created_at` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status` INT NOT NULL,
    PRIMARY KEY(`u_id`)
) ENGINE = InnoDB;

CREATE TABLE `agromate_db`.`admins`(
    `a_id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(150) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `password` VARCHAR(30) NOT NULL,
    `created_at` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status` INT NOT NULL,
    PRIMARY KEY(`a_id`)
) ENGINE = InnoDB;

CREATE TABLE `agromate_db`.`conversation`(
    `c_id` INT NOT NULL AUTO_INCREMENT,
    `admin_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `created_at` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status` INT NOT NULL,
    PRIMARY KEY(`c_id`)
) ENGINE = InnoDB;

CREATE TABLE `agromate_db`.`conversation_reply`(
    `cr_id` INT NOT NULL AUTO_INCREMENT,
    `message` TEXT NOT NULL,
    `sender` VARCHAR(10) NOT NULL,
    `created_at` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `c_id` INT NOT NULL,
    PRIMARY KEY(`cr_id`)
) ENGINE = InnoDB;