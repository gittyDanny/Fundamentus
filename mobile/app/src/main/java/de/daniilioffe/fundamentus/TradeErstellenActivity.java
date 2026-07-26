package de.daniilioffe.fundamentus;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.Date;

public class TradeErstellenActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_trade_erstellen);

        TextView tickerTextView = findViewById(R.id.tradeTickerText);
        TextView scoreTextView = findViewById(R.id.tradeScoreText);
        EditText inputKaufpreis = findViewById(R.id.inputKaufpreis);
        EditText inputAnzahl = findViewById(R.id.inputAnzahl);
        Spinner spinnerBörse = findViewById(R.id.spinnerBroker);
        TextView textKostenVorschau = findViewById(R.id.textKostenVorschau);
        Button tradeSpeichernButton = findViewById(R.id.buttonTradeSpeichern);

        Intent tradeErstellenIntent = getIntent();


        // Ticker + score empfangen + prüfen
        String ticker = tradeErstellenIntent.getStringExtra("ticker");
        double score = tradeErstellenIntent.getDoubleExtra("score", -1.0);
        if (ticker == null || ticker.isEmpty()) {
            Toast.makeText(TradeErstellenActivity.this, "kein Ticker übergeben", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }
        //anzeigen
        tickerTextView.setText(ticker);

        if (score == -1.0) {
            scoreTextView.setText("Score beim Einstieg: -");
        } else {
            scoreTextView.setText("Score beim Einstieg: " + score);
        }


        //ohboy habe ich viele dumme Menschen gesehen - das ist für Euch Ihr lieben:
        tradeSpeichernButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String kaufpreisText = inputKaufpreis.getText().toString().trim().replace(",", ".");
                String anzahlText = inputAnzahl.getText().toString().trim().replace(",", ".");
                if (kaufpreisText.isEmpty() || anzahlText.isEmpty()) {
                    Toast.makeText(TradeErstellenActivity.this, "Kaufpreis und Anzahl eingeben bittö", Toast.LENGTH_SHORT).show();
                    return;
                }
                double kaufpreis;
                double anzahl;

                try {
                    kaufpreis = Double.parseDouble(kaufpreisText);
                    anzahl = Double.parseDouble(anzahlText);

                } catch (NumberFormatException formatFehler) {
                    Toast.makeText(TradeErstellenActivity.this, "Ungültiger Zahlformat(0.00)", Toast.LENGTH_SHORT).show();
                    return;
                }
                if (kaufpreis <= 0 || anzahl <= 0) {
                    Toast.makeText(TradeErstellenActivity.this, "Preis und Anzahl müssen größer als 0 sein...", Toast.LENGTH_SHORT).show();
                    return;
                }

                //Transaktionsgebühren je Börse
                String börse = spinnerBörse.getSelectedItem().toString();

                double kaufGebühr;

                if (börse.equals("Scalable Capital")) {
                    kaufGebühr = 0.99;
                } else if (börse.equals("Bitpanda") || börse.equals("Trade Republic")) {
                    kaufGebühr = 1.00;
                } else {
                    kaufGebühr = 0.00;
                }

                //vorerst Kaufgebühr = Verkaufsgebühr, weil Transaktionskosten bla
                double erwarteteVerkaufsGebühr = kaufGebühr;

                double gesamtePosition = kaufpreis * anzahl + kaufGebühr;

                textKostenVorschau.setText("Gesamteinsatz: " + gesamtePosition + " €");

                OffenerTrade neuerTrade;

                neuerTrade = new OffenerTrade(ticker, score, kaufpreis, anzahl, börse, kaufGebühr, erwarteteVerkaufsGebühr, "OPEN", new Date());
                speichereOffenenTrade(neuerTrade);


            }
        });

    }

    private void speichereOffenenTrade(OffenerTrade neuerTrade) {
        FirebaseUser aktuellerNutzer;
        aktuellerNutzer = FirebaseAuth.getInstance().getCurrentUser();
        if (aktuellerNutzer == null) {
            Toast.makeText(TradeErstellenActivity.this, "Wer sind Sie und was machen Sie hier?", Toast.LENGTH_SHORT).show();
            return;
        }
        String userID = aktuellerNutzer.getUid();
        FirebaseFirestore datenbankVerbindung;

        datenbankVerbindung = FirebaseFirestore.getInstance();

        datenbankVerbindung.collection("users").document(userID).collection("open_trades").add(neuerTrade).addOnCompleteListener(new OnCompleteListener<DocumentReference>() {
            @Override
            public void onComplete(@NonNull Task<DocumentReference> tradeSpeichern) {
                if (tradeSpeichern.isSuccessful() == false) {
                    Toast.makeText(TradeErstellenActivity.this, "Position wurde nicht gespeichert", Toast.LENGTH_SHORT).show();
                    Log.e("FIRESTORE","Position konnte nicht gespeichert werden",tradeSpeichern.getException());
                    return;
                }
                Toast.makeText(TradeErstellenActivity.this, "Position gespeichert.", Toast.LENGTH_SHORT).show();
                finish();

            }
        });


    }
}
