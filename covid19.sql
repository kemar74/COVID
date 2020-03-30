-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le :  sam. 28 mars 2020 à 16:03
-- Version du serveur :  5.7.19-log
-- Version de PHP :  5.6.31

-- DROP DATABASE IF EXISTS `covid19`;
-- COMMIT;

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `covid19`
--
CREATE DATABASE IF NOT EXISTS `covid19` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `covid19`;

-- --------------------------------------------------------

--
-- Structure de la table `countries`
--

DROP TABLE IF EXISTS `countries`;
CREATE TABLE IF NOT EXISTS `countries` (
  `id_country` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `date_curfew` DATETIME DEFAULT NULL,
  `population`int(16) DEFAULT NULL,
  PRIMARY KEY (`id_country`),
  KEY `name_country_countries` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `daily_report`
--

DROP TABLE IF EXISTS `daily_report`;
CREATE TABLE IF NOT EXISTS `daily_report` (
  `id_state` int(11) NOT NULL,
  `id_country` int(11) NOT NULL,
  `confirmed` int(11) NOT NULL,
  `dead` int(11) NOT NULL,
  `recovered` int(11) NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id_state`,`id_country`,`date`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `states`
--

DROP TABLE IF EXISTS `states`;
CREATE TABLE IF NOT EXISTS `states` (
  `id_state` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `id_country` int(11) NOT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  PRIMARY KEY (`id_state`)
) ENGINE=MyISAM AUTO_INCREMENT=75 DEFAULT CHARSET=latin1;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
