package de.daniilioffe.fundamentus;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.Date;

public class TradeSchließenActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_trade_schliessen);
        TextView tickerText = findViewById(R.id.schließenTickerText);
        TextView einstiegText = findViewById(R.id.schließenEinstiegText);
        EditText inputVerkaufspreis = findViewById(R.id.inputVerkaufspreis);
        TextView ergebnisText = findViewById(R.id.schließenErgebnisText);
        Button verkaufBestätigenButton = findViewById(R.id.buttonVerkaufBestätigen);

        Intent schließenIntent = getIntent();
        String tradeID = schließenIntent.getStringExtra("tradeID");
        if (tradeID == null || tradeID.isEmpty()) {
            Toast.makeText(TradeSchließenActivity.this, "Keine Trade-ID übergeben", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }
        String tickerAusIntent = schließenIntent.getStringExtra("ticker");
        if (tickerAusIntent == null) {
            tickerAusIntent = "";
        }
        final String tickerFürActivity;
        tickerFürActivity = tickerAusIntent;

        tickerText.setText(tickerFürActivity);

        FirebaseUser aktuellerNutzer;
        aktuellerNutzer = FirebaseAuth.getInstance().getCurrentUser();
        if (aktuellerNutzer == null) {
            Toast.makeText(TradeSchließenActivity.this, "Wer sind Sie und was wollen Sie von mir?", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }
        String userID = aktuellerNutzer.getUid();
        FirebaseFirestore datenbankVerbindung = FirebaseFirestore.getInstance();
        DocumentReference offenerTradeDokument;
        offenerTradeDokument = datenbankVerbindung.collection("users").document(userID).collection("open_trades").document(tradeID);
        offenerTradeDokument.get().addOnCompleteListener(new OnCompleteListener<DocumentSnapshot>() {
            @Override
            public void onComplete(@NonNull Task<DocumentSnapshot> tradeLaden) {
                if (tradeLaden.isSuccessful() == false) {
                    Toast.makeText(TradeSchließenActivity.this, "Trade konnte nicht geladen werden", Toast.LENGTH_SHORT).show();
                    return;
                }

                DocumentSnapshot tradeDatensatz = tradeLaden.getResult();

                if (tradeDatensatz == null || tradeDatensatz.exists() == false) {
                    Toast.makeText(TradeSchließenActivity.this, "Trade exestiert nicht", Toast.LENGTH_SHORT).show();
                    finish();
                    return;
                }

                Double kaufpreisFB = tradeDatensatz.getDouble("kaufpreis");
                Double anzahlFB = tradeDatensatz.getDouble("anzahl");
                Double kaufgebührFB = tradeDatensatz.getDouble("kaufGebühr");
                Double erwarteteVerkaufsgebührFB = tradeDatensatz.getDouble("erwarteteVerkaufsGebühr");
                Double scoreBeimEinstiegFB = tradeDatensatz.getDouble("scoreBeimEinstieg");
                String börse = tradeDatensatz.getString("broker");
                Date eröffnetAm = tradeDatensatz.getDate("erstelltAm");
                if (kaufpreisFB == null || anzahlFB == null || kaufgebührFB == null || erwarteteVerkaufsgebührFB == null) {
                    Toast.makeText(TradeSchließenActivity.this, "Daten wurden nicht vollständig übermittelt", Toast.LENGTH_SHORT).show();
                    return;
                }
                double kaufpreis = kaufpreisFB;
                double anzahl = anzahlFB;
                double kaufGebühr = kaufgebührFB;
                double verkaufsGebühr = erwarteteVerkaufsgebührFB;
                double gesamterEinsatz = kaufpreis * anzahl + kaufGebühr;
                if (börse == null) {
                    börse = "Unbekannt";
                }

                double scoreBeimEinstieg;

                if (scoreBeimEinstiegFB == null) {
                    scoreBeimEinstieg = -1.0;
                } else {
                    scoreBeimEinstieg =
                            scoreBeimEinstiegFB;
                }

                if (eröffnetAm == null) {
                    eröffnetAm = new Date();
                }

                String brokerFürAbschluss;
                brokerFürAbschluss = börse;

                double scoreFürAbschluss;
                scoreFürAbschluss = scoreBeimEinstieg;

                Date eröffnetAmFürAbschluss;
                eröffnetAmFürAbschluss = eröffnetAm;

                String tickerFürAbschluss = tickerFürActivity;
                einstiegText.setText("Einstieg: " + String.format("%.2f", kaufpreis) + " $\nAnzahl: " + String.format("%.4f", anzahl) + "\nGesamteinsatz: " + String.format("%.2f", gesamterEinsatz) + " $");

                //schließen + löschen Vorgang
                verkaufBestätigenButton.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        String verkaufspreisText;
                        verkaufspreisText = inputVerkaufspreis.getText().toString().trim().replace(",", ".");
                        if (verkaufspreisText.isEmpty()) {
                            Toast.makeText(TradeSchließenActivity.this, "Verkaufspreis eingeben(0.00)", Toast.LENGTH_SHORT).show();
                            return;
                        }
                        double verkaufspreis;
                        try {
                            verkaufspreis = Double.parseDouble(verkaufspreisText);
                        } catch (NumberFormatException fehler) {
                            Toast.makeText(TradeSchließenActivity.this, "Ungültiger Format (0.00)", Toast.LENGTH_SHORT).show();
                            return;
                        }
                        if (verkaufspreis <= 0) {
                            Toast.makeText(TradeSchließenActivity.this, "Verkaufspreis kann nicht 0 oder kleiner sein.", Toast.LENGTH_SHORT).show();
                            return;
                        }
                        double verkaufsErlös = verkaufspreis * anzahl - verkaufsGebühr;
                        double realisierterPL = verkaufsErlös - gesamterEinsatz;
                        double realisierterPLProzent = realisierterPL / gesamterEinsatz * 100;

                        ergebnisText.setText("Auszahlung nach Gebühr: " + String.format("%.2f", verkaufsErlös) + " $\nRealisierter P/L: " + String.format("%+.2f",realisierterPL) + " $ /" + String.format("%+.2f", realisierterPLProzent) + " %");

                        //beim Schließen den GeschlossenerTrade Objekt erzeugen, Daten übergeben => Später entsteht aus den Objekten Historie + Analysen
                        GeschlossenerTrade geschlossenerTrade;

                        geschlossenerTrade = new GeschlossenerTrade(tickerFürAbschluss, brokerFürAbschluss, scoreFürAbschluss, kaufpreis, anzahl, kaufGebühr, gesamterEinsatz, verkaufspreis, verkaufsGebühr, verkaufsErlös, realisierterPL, realisierterPLProzent, "CLOSED", eröffnetAmFürAbschluss, new Date());
                        DocumentReference geschlossenerTradeDatensatz;
                        geschlossenerTradeDatensatz = datenbankVerbindung.collection("users").document(userID).collection("closed_trades").document(tradeID);
                        verkaufBestätigenButton.setEnabled(false);
                        geschlossenerTradeDatensatz.set(geschlossenerTrade).addOnCompleteListener(new OnCompleteListener<Void>() {
                            @Override
                            public void onComplete(@NonNull Task<Void> tradeSpeichern) {
                                if (tradeSpeichern.isSuccessful() == false) {
                                    Toast.makeText(TradeSchließenActivity.this, "Trade konnte nicht gespeichert werden.", Toast.LENGTH_SHORT).show();
                                    Log.e("FIRESTORE", "Geschlossener Trade konnte nicht gespeichert werden", tradeSpeichern.getException());
                                    verkaufBestätigenButton.setEnabled(true);
                                    return;
                                }

                                offenerTradeDokument.delete().addOnCompleteListener(new OnCompleteListener<Void>() {
                                    @Override
                                    public void onComplete(@NonNull Task<Void> tradeLöschen) {
                                        if (tradeLöschen.isSuccessful() == false) {
                                            Log.e("FIRESTORE", "Offener Trade konnte nicht gelöscht werden", tradeLöschen.getException());
                                            Toast.makeText(TradeSchließenActivity.this, "Trade konnte nicht gelöscht werden", Toast.LENGTH_SHORT).show();
                                            verkaufBestätigenButton.setEnabled(true);
                                            return;
                                        }
                                        Intent tradesIntent;
                                        tradesIntent = new Intent(TradeSchließenActivity.this, TradesActivity.class);
                                        startActivity(tradesIntent);
                                        finish();


                                        Toast.makeText(TradeSchließenActivity.this, "Trade erfolgreich geschlossen", Toast.LENGTH_SHORT).show();
                                        finish();
                                    }
                                });

                            }
                        });
                    }
                });


            }
        });


    }

}
