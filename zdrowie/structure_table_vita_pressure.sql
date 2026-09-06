-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: core-mariadb:3306
-- Generation Time: Wrz 06, 2026 at 03:19 PM
-- Wersja serwera: 11.4.10-MariaDB
-- Wersja PHP: 8.4.24

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Baza danych: `homeassistant`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `ha_vita_pressure`
--

CREATE TABLE `ha_vita_pressure` (
  `id_ha_fit` int(11) NOT NULL,
  `Date` datetime NOT NULL,
  `atmosf.` int(11) NOT NULL,
  `P_skurczowe` int(11) DEFAULT NULL,
  `P_rozkurczowe` int(11) DEFAULT NULL,
  `Puls` int(11) DEFAULT NULL,
  `temperatura` int(2) NOT NULL,
  `wilgotnosc` int(2) NOT NULL,
  `waga` decimal(3,1) DEFAULT NULL,
  `miasto` varchar(30) DEFAULT NULL,
  `uwagi` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indeksy dla zrzutów tabel
--

--
-- Indeksy dla tabeli `ha_vita_pressure`
--
ALTER TABLE `ha_vita_pressure`
  ADD UNIQUE KEY `id_ha_fit` (`id_ha_fit`);

--
-- AUTO_INCREMENT dla zrzuconych tabel
--

--
-- AUTO_INCREMENT dla tabeli `ha_vita_pressure`
--
ALTER TABLE `ha_vita_pressure`
  MODIFY `id_ha_fit` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
