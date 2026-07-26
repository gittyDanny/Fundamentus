package de.daniilioffe.fundamentus;

import java.util.Date;

public class OffenerTrade {
    public String ticker;
    public double scoreBeimEinstieg;
    public double kaufpreis;
    public double anzahl;
    public String broker;
    public double kaufGebühr;
    public double erwarteteVerkaufsGebühr;
    public String status;
    public Date erstelltAm;

    public OffenerTrade() {
        //für  Firebase und so(auslesen)
    }

    public OffenerTrade(String ticker, double scoreBeimEinstieg, double kaufpreis, double anzahl, String broker, double kaufGebühr, double erwarteteVerkaufsGebühr, String status, Date erstelltAm) {
        this.ticker = ticker;
        this.scoreBeimEinstieg = scoreBeimEinstieg;
        this.kaufpreis = kaufpreis;
        this.anzahl = anzahl;
        this.broker = broker;
        this.kaufGebühr = kaufGebühr;
        this.erwarteteVerkaufsGebühr = erwarteteVerkaufsGebühr;
        this.status = status;
        this.erstelltAm = erstelltAm;

    }



}
