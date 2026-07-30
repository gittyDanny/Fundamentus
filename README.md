# Fundamentus Companion

<p align="center">
  <img src="app/src/main/res/drawable/fundamentus_logo.png"
       alt="Fundamentus Logo"
       width="180">
</p>

**Entwickler:** Daniil Ioffe
**Kurs:** App-Entwicklung mit Android, SoSe 2026

## Beschreibung

Fundamentus Companion ist die Android-App für den Fundamentus-Bot. Die App zeigt Aktienanalysen, Handelssignale und den aktuellen Bot-Status. Nutzer können eine Watchlist verwalten und Paper-Trades simulieren. Es werden keine echten Käufe oder Verkäufe durchgeführt.

## Fundamentus-Bot

Der Fundamentus-Bot läuft auf einem Raspberry Pi und wird regelmäßig automatisch ausgeführt. Er lädt Kurs- und Unternehmensdaten, berechnet für jede Aktie einen Score und erstellt daraus ein Signal.

**Datenquellen:** Yahoo Finance, SEC Company Facts
**Technische Bewertung:** 5-Tage-Momentum, 20-Tage-Trend, SMA20, SMA50, Volatilität, Handelsvolumen
**Fundamentale Bewertung:** Umsatzwachstum, Net Margin, Operating Margin, FCF Margin, Verbindlichkeiten, Cash-Bestand
**Gewichtung:** 60 % technische Bewertung, 40 % fundamentale Bewertung
**Signale:** BUY ab 70 Punkten, SELL bis 35 Punkte, sonst HOLD, bei fehlenden Fundamentaldaten teilweise WATCH
**Datenfluss:** Yahoo Finance und SEC -> Python-Bot -> SQLite -> Firebase Firestore -> Android-App

## Activities

### LoginActivity

E-Mail-Eingabe, Passworteingabe, Eingabeprüfung, Anmeldung über Firebase Authentication, Weiterleitung zum Dashboard.

### DashboardActivity

Bot-Status, Zeitpunkt des letzten Bot-Laufs, Anzahl der BUY-, HOLD- und SELL-Signale, Anzahl offener und geschlossener Trades, Schnellzugriffe, Navigationsmenü, Logout.

### StocksActivity

Anzeige aller Aktien, Suche nach Ticker, Name oder Sektor, Sektorfilter, Watchlistfilter, Hinzufügen und Entfernen von Aktien aus der Watchlist, Öffnen der Aktiendetails.

### AktienDetailsActivity

Ticker, Signal, Score, Begründung, letzter Kurs, SMA20, 20-Tage-Kursänderung, Übergabe von Ticker und Score an die Trade-Erstellung.

### TradeErstellenActivity

Kaufpreis, Anzahl, Broker, Kaufgebühr, erwartete Verkaufsgebühr, gesamter Kapitaleinsatz, Speicherung als offener Paper-Trade.

### TradesActivity

Offene Trades, Einstiegskurs, aktueller Fundamentus-Kurs, Score beim Einstieg, erwartete Auszahlung, Netto-Gewinn oder -Verlust in Dollar und Prozent, Löschen oder Schließen eines Trades.

### TradeSchließenActivity

Eingabe des Verkaufspreises, Berechnung des Verkaufserlöses, Berücksichtigung der Gebühren, realisierter Gewinn oder Verlust, Rendite in Prozent, Verschiebung von offenen zu geschlossenen Trades.

### TradeHistorieActivity

Abgeschlossene Trades, Kauf- und Verkaufspreise, realisierte Ergebnisse, Abschlussdatum, Gesamtgewinn oder -verlust, Anzahl der Gewinner und Verlierer, Sortierung nach Abschlussdatum.

### BotStatusActivity

Status des letzten Bot-Laufs, Start- und Endzeit, verarbeitete Aktien, gespeicherte Signale, Kursdatenfehler, Fehlermeldung, Zeitpunkt der Firebase-Synchronisation, manuelle Aktualisierung.

## Technische Daten

**Plattform:** Android
**Programmiersprache:** Java 11
**Benutzeroberfläche:** XML, LinearLayout, ScrollView, DrawerLayout, NavigationView
**Navigation:** 9 Activities, explizite Intents, Intent-Extras
**Datenübergabe:** Ticker, Score, Trade-ID
**Login:** Firebase Authentication
**Datenbank:** Firebase Cloud Firestore
**Bot:** Python, Raspberry Pi, SQLite, systemd
**App-Version:** 1.0, Version Code 1
**Android-Versionen:** Min SDK 24, Target SDK 36, Compile SDK 36 mit Minor API 1
**Projektumfang:** 11 Java-Dateien, 12 Layout-Dateien, etwa 2.200 Java-Zeilen

## Firestore-Struktur

**Aktien:** `assets/{ticker}`
**Signale:** `latest_signals/{ticker}`
**Bot-Status:** `bot_status/latest`
**Watchlist:** `users/{userId}`
**Offene Trades:** `users/{userId}/open_trades/{tradeId}`
**Geschlossene Trades:** `users/{userId}/closed_trades/{tradeId}`

## Verwendete Technologien

Java, Android Studio, XML, Firebase Authentication, Firebase Firestore, Python, SQLite, Raspberry Pi, Yahoo Finance, SEC-Unternehmensdaten, Git, GitHub.

## Hinweis

Die App dient ausschließlich zur Simulation. Die Signale stellen keine Anlageberatung dar und es werden keine echten Trades ausgeführt.
