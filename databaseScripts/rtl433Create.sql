-- MySQL Script generated by MySQL Workbench
-- Sat Feb 17 22:58:06 2018
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema rtl433
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `rtl433` ;

-- -----------------------------------------------------
-- Schema rtl433
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `rtl433` DEFAULT CHARACTER SET latin1 ;
USE `rtl433` ;

-- -----------------------------------------------------
-- Table `rtl433`.`sensor`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rtl433`.`sensor` ;

CREATE TABLE IF NOT EXISTS `rtl433`.`sensor` (
  `id` VARCHAR(25) NOT NULL,
  `description` VARCHAR(250) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;

CREATE UNIQUE INDEX `id_UNIQUE` ON `rtl433`.`sensor` (`id` ASC);


-- -----------------------------------------------------
-- Table `rtl433`.`sensorReading`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rtl433`.`sensorReading` ;

CREATE TABLE IF NOT EXISTS `rtl433`.`sensorReading` (
  `dateRecorded` DATETIME NOT NULL,
  `sensorId` VARCHAR(25) NOT NULL,
  `temperatureCelsius` DECIMAL(5,2) NULL DEFAULT NULL,
  `humidity` DECIMAL(5,2) NULL DEFAULT NULL,
  `batteryLow` TINYINT(1), 
  PRIMARY KEY (`dateRecorded`, `sensorId`),
  CONSTRAINT `sensorReading_sensor`
    FOREIGN KEY (`sensorId`)
    REFERENCES `rtl433`.`sensor` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;

CREATE INDEX `sensorReading_sensor_idx` ON `rtl433`.`sensorReading` (`sensorId` ASC);

USE `rtl433` ;

-- -----------------------------------------------------
-- procedure sensorReadingInsert
-- -----------------------------------------------------

USE `rtl433`;
DROP procedure IF EXISTS `rtl433`.`sensorReadingInsert`;

DELIMITER $$
USE `rtl433`$$
CREATE DEFINER=`msilvers`@`%.main.nova42.test` PROCEDURE `sensorReadingInsert`(sensorId VARCHAR(25), dateRecorded DATETIME, batteryLow TINYINT(1),
                                        temperatureCelsius DECIMAL(5,2), humidity DECIMAL(5,2))
BEGIN

	DECLARE exit handler for sqlexception
    BEGIN
		ROLLBACK;
	END;

	START TRANSACTION;
	INSERT IGNORE INTO 
		sensor (id) 
	VALUES 
		(sensorId);
    
    INSERT INTO 
		sensorReading (dateRecorded, sensorId, temperatureCelsius, humidity, batteryLow)
    VALUES
		(dateRecorded, sensorId, temperatureCelsius, humidity, batteryLow);

	COMMIT;
END$$

DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
