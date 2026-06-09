-- phpMyAdmin SQL Dump
-- version 5.2.2deb1+deb13u1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Cze 09, 2026 at 12:15 PM
-- Wersja serwera: 11.8.6-MariaDB-0+deb13u1 from Debian
-- Wersja PHP: 8.4.21

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
CREATE DATABASE IF NOT EXISTS `finanse` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `finanse`;

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
--
-- Baza danych: `inwestycje`
--
CREATE DATABASE IF NOT EXISTS `inwestycje` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `inwestycje`;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `dane`
--

CREATE TABLE `dane` (
  `id_dane` int(11) NOT NULL,
  `data` date NOT NULL,
  `ticker` varchar(50) NOT NULL,
  `ISIN` varchar(15) NOT NULL,
  `waluta` varchar(3) NOT NULL,
  `open` decimal(10,3) NOT NULL,
  `max` decimal(10,3) NOT NULL,
  `min` decimal(10,3) NOT NULL,
  `close` decimal(10,3) NOT NULL,
  `zmiana` decimal(10,3) NOT NULL,
  `volume` int(20) NOT NULL,
  `number_transactions` int(20) NOT NULL,
  `turnover` decimal(20,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `dane_dzienne`
--

CREATE TABLE `dane_dzienne` (
  `id_dane_dzienne` int(11) NOT NULL,
  `data` date NOT NULL,
  `wartosc` decimal(10,2) NOT NULL,
  `wklad` decimal(10,2) NOT NULL,
  `H_ilosc` int(5) NOT NULL,
  `H_vol` int(20) NOT NULL,
  `L_ilosc` int(5) NOT NULL,
  `L_vol` int(20) NOT NULL,
  `turnover` int(20) NOT NULL,
  `HL` int(5) NOT NULL,
  `NL` int(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `obroty`
--

CREATE TABLE `obroty` (
  `id_obroty` int(11) NOT NULL,
  `ticker_nm` varchar(50) NOT NULL,
  `zakup_data` date NOT NULL,
  `zakup_cena` decimal(12,2) NOT NULL,
  `zakup_ilosc` int(10) NOT NULL,
  `sprzedaz_data` date DEFAULT NULL,
  `sprzedaz_cena` decimal(12,2) DEFAULT NULL,
  `kurs_biezacy` decimal(10,2) DEFAULT NULL,
  `stop_loss` decimal(10,2) DEFAULT NULL,
  `platforma` varchar(20) NOT NULL,
  `uwagi` varchar(50) DEFAULT NULL,
  `Data_ordered` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `platforma`
--

CREATE TABLE `platforma` (
  `id_platforma` int(11) NOT NULL,
  `platforma_name` varchar(20) NOT NULL,
  `url` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `ticker`
--

CREATE TABLE `ticker` (
  `id_ticker` int(11) NOT NULL,
  `ticker_name` varchar(30) NOT NULL,
  `market` varchar(50) DEFAULT NULL,
  `rating` varchar(4) DEFAULT NULL,
  `altman` decimal(3,1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indeksy dla zrzutów tabel
--

--
-- Indeksy dla tabeli `dane`
--
ALTER TABLE `dane`
  ADD PRIMARY KEY (`id_dane`),
  ADD KEY `idx_ticker_data` (`ticker`,`data`);

--
-- Indeksy dla tabeli `dane_dzienne`
--
ALTER TABLE `dane_dzienne`
  ADD PRIMARY KEY (`id_dane_dzienne`),
  ADD UNIQUE KEY `data` (`data`);

--
-- Indeksy dla tabeli `obroty`
--
ALTER TABLE `obroty`
  ADD PRIMARY KEY (`id_obroty`),
  ADD KEY `idx_ticker_sprzedaz` (`ticker_nm`,`sprzedaz_data`);

--
-- Indeksy dla tabeli `platforma`
--
ALTER TABLE `platforma`
  ADD PRIMARY KEY (`id_platforma`),
  ADD UNIQUE KEY `platforma_name` (`platforma_name`);

--
-- Indeksy dla tabeli `ticker`
--
ALTER TABLE `ticker`
  ADD PRIMARY KEY (`id_ticker`),
  ADD UNIQUE KEY `data` (`ticker_name`);

--
-- AUTO_INCREMENT dla zrzuconych tabel
--

--
-- AUTO_INCREMENT dla tabeli `dane`
--
ALTER TABLE `dane`
  MODIFY `id_dane` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT dla tabeli `dane_dzienne`
--
ALTER TABLE `dane_dzienne`
  MODIFY `id_dane_dzienne` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT dla tabeli `obroty`
--
ALTER TABLE `obroty`
  MODIFY `id_obroty` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT dla tabeli `platforma`
--
ALTER TABLE `platforma`
  MODIFY `id_platforma` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT dla tabeli `ticker`
--
ALTER TABLE `ticker`
  MODIFY `id_ticker` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
