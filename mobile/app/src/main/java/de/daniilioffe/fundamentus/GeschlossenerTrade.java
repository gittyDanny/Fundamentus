package de.daniilioffe.fundamentus;

import java.util.Date;

public class GeschlossenerTrade {
    public String ticker;
    public String broker;

    public double scoreBeimEinstieg;
    public double kaufpreis;
    public double anzahl;
    public double kaufGebühr;
    public double gesamterEinsatz;

    public double verkaufspreis;
    public double verkaufsGebühr;
    public double verkaufsErlös;

    public double realisierterPL;
    public double realisierterPLProzent;

    public String status;
    public Date eröffnetAm;
    public Date geschlossenAm;

    public GeschlossenerTrade() {
    }

    public GeschlossenerTrade(String ticker, String broker, double scoreBeimEinstieg, double kaufpreis, double anzahl, double kaufGebühr, double gesamterEinsatz,
                              double verkaufspreis, double verkaufsGebühr, double verkaufsErlös, double realisierterPL, double realisierterPLProzent, String status, Date eröffnetAm, Date geschlossenAm) {
        this.ticker = ticker;
        this.broker = broker;
        this.scoreBeimEinstieg = scoreBeimEinstieg;
        this.kaufpreis = kaufpreis;
        this.anzahl = anzahl;
        this.kaufGebühr = kaufGebühr;
        this.gesamterEinsatz = gesamterEinsatz;
        this.verkaufspreis = verkaufspreis;
        this.verkaufsGebühr = verkaufsGebühr;
        this.verkaufsErlös = verkaufsErlös;
        this.realisierterPL = realisierterPL;
        this.realisierterPLProzent = realisierterPLProzent;
        this.status = status;
        this.eröffnetAm = eröffnetAm;
        this.geschlossenAm = geschlossenAm;

    }
}
