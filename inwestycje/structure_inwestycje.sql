-- phpMyAdmin SQL Dump
-- version 5.2.2deb1+deb13u1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Wrz 06, 2026 at 03:27 PM
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
-- Baza danych: `inwestycje`
--

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
-- Struktura tabeli dla tabeli `obroty_arch`
--

CREATE TABLE `obroty_arch` (
  `id_obroty_arch` int(11) NOT NULL,
  `data_arch` date NOT NULL,
  `zakup_data_arch` date NOT NULL,
  `ticker_nm` varchar(50) NOT NULL,
  `stop_loss` decimal(10,2) DEFAULT NULL
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
-- Indeksy dla tabeli `obroty_arch`
--
ALTER TABLE `obroty_arch`
  ADD PRIMARY KEY (`id_obroty_arch`),
  ADD UNIQUE KEY `unique_ticker_daily` (`data_arch`,`ticker_nm`);

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
-- AUTO_INCREMENT dla tabeli `obroty_arch`
--
ALTER TABLE `obroty_arch`
  MODIFY `id_obroty_arch` int(11) NOT NULL AUTO_INCREMENT;

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
