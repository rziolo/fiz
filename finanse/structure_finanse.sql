-- phpMyAdmin SQL Dump
-- version 5.2.2deb1+deb13u1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Wrz 06, 2026 at 03:25 PM
-- Wersja serwera: 11.8.6-MariaDB-0+deb13u1 from Debian
-- Wersja PHP: 8.4.24

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Baza danych: `finanse`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `przychody`
--

CREATE TABLE `przychody` (
  `id_przychody` int(11) NOT NULL,
  `data` date NOT NULL,
  `ZUS_Iwona` decimal(10,2) NOT NULL,
  `ZUS_Robert` decimal(10,2) NOT NULL,
  `gielda` decimal(10,2) DEFAULT 0.00,
  `odsetki` decimal(10,2) DEFAULT 0.00,
  `urzad` decimal(10,2) DEFAULT 0.00,
  `inne` decimal(10,2) DEFAULT 0.00,
  `uwagi` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `ror`
--

CREATE TABLE `ror` (
  `id_ror` int(11) NOT NULL,
  `data` date NOT NULL,
  `PKO` decimal(10,2) NOT NULL,
  `mBank` decimal(10,2) NOT NULL,
  `Millenium` decimal(10,2) DEFAULT 0.00,
  `obligacje` decimal(10,2) DEFAULT 0.00,
  `fundusze` decimal(10,2) DEFAULT 0.00,
  `lokaty` decimal(10,2) DEFAULT 0.00,
  `gotowka` decimal(10,2) DEFAULT 0.00,
  `ike_ikze` decimal(10,2) DEFAULT 0.00,
  `gielda` decimal(10,2) DEFAULT 0.00,
  `EURO` decimal(10,2) DEFAULT 0.00,
  `EURO_kurs` decimal(10,2) DEFAULT 0.00,
  `USD` decimal(10,2) DEFAULT 0.00,
  `USD_kurs` decimal(10,2) DEFAULT 0.00,
  `uwagi` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `wydatki`
--

CREATE TABLE `wydatki` (
  `id_wydatki` int(11) NOT NULL,
  `data` date NOT NULL,
  `zywnosc` decimal(10,2) NOT NULL,
  `niezywnosc` decimal(10,2) NOT NULL,
  `car_cost` decimal(10,2) DEFAULT 0.00,
  `car_km` int(11) DEFAULT 0,
  `oplaty` decimal(10,2) DEFAULT 0.00,
  `inne` decimal(10,2) DEFAULT 0.00,
  `medycyna` decimal(10,2) DEFAULT 0.00,
  `uwagi` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indeksy dla zrzutów tabel
--

--
-- Indeksy dla tabeli `przychody`
--
ALTER TABLE `przychody`
  ADD PRIMARY KEY (`id_przychody`);

--
-- Indeksy dla tabeli `ror`
--
ALTER TABLE `ror`
  ADD PRIMARY KEY (`id_ror`);

--
-- Indeksy dla tabeli `wydatki`
--
ALTER TABLE `wydatki`
  ADD PRIMARY KEY (`id_wydatki`);

--
-- AUTO_INCREMENT dla zrzuconych tabel
--

--
-- AUTO_INCREMENT dla tabeli `przychody`
--
ALTER TABLE `przychody`
  MODIFY `id_przychody` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT dla tabeli `ror`
--
ALTER TABLE `ror`
  MODIFY `id_ror` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT dla tabeli `wydatki`
--
ALTER TABLE `wydatki`
  MODIFY `id_wydatki` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
