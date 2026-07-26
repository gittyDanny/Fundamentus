package de.daniilioffe.fundamentus;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.animation.TranslateAnimation;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;

public class AktienDetailsActivity extends AppCompatActivity {
    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_aktie_details);

        TextView tickerTextView = findViewById(R.id.detailsTickerText);
        TextView signalTextView = findViewById(R.id.detailsSignalText);
        TextView scoreTextView = findViewById(R.id.detailsScoreText);
        TextView reasonTextView = findViewById(R.id.detailsReasonText);
        TextView closeTextView = findViewById(R.id.detailsCloseText);
        TextView sma20TextView = findViewById(R.id.detailsSma20Text);
        TextView change20dTextView = findViewById(R.id.detailsChange20dText);
        Button tradeErstellenButton = findViewById(R.id.buttonPaperTradeErstellen);


        Intent detailsIntent = getIntent();
        String ticker = detailsIntent.getStringExtra("ticker");

        if (ticker == null || ticker.isEmpty()) {
            Toast.makeText(AktienDetailsActivity.this, "Kein Ticker womp womp", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }
        FirebaseFirestore datenbankVerbindung;
        datenbankVerbindung = FirebaseFirestore.getInstance();

        datenbankVerbindung.collection("latest_signals").document(ticker).get().addOnCompleteListener(
                new OnCompleteListener<DocumentSnapshot>() {
                    @Override
                    public void onComplete(@NonNull Task<DocumentSnapshot> task) {
                        if (!task.isSuccessful()) {
                            Log.e("FIRESTORE", "Signal konnte nicht geladen werden", task.getException());
                            Toast.makeText(AktienDetailsActivity.this, "Signal konnte nicht geladen werden", Toast.LENGTH_SHORT).show();
                            return;
                        }
                        DocumentSnapshot signalDatensatz = task.getResult();
                        if (!signalDatensatz.exists()) {
                            signalTextView.setText("Kein Signal vorhanden.");
                            Toast.makeText(AktienDetailsActivity.this, "für" + ticker + "wurde noch kein Signal gespeichert", Toast.LENGTH_SHORT).show();

                            return;

                        }

                        String signal = signalDatensatz.getString("signal");
                        String reason = signalDatensatz.getString("reason");
                        Double score = signalDatensatz.getDouble("score");
                        Double close = signalDatensatz.getDouble("close");
                        Double sma20 = signalDatensatz.getDouble("sma20");
                        Double change20dPct = signalDatensatz.getDouble("change20dPct");

                        if (signal == null) {
                            signal = "Unbekannt";
                        }
                        if (reason == null) {
                            reason = "Keine Begründung vorhanden";
                        }

                        signalTextView.setText("Signal: " + signal);
                        reasonTextView.setText("Begründung: " + reason);

                        if (score == null) {
                            scoreTextView.setText("Score: -");
                            tradeErstellenButton.setEnabled(false);
                        } else {
                            scoreTextView.setText("Score: " + score);
                            tradeErstellenButton.setEnabled(true);

                            tradeErstellenButton.setOnClickListener(new View.OnClickListener() {
                                @Override
                                public void onClick(View v) {

                                    Intent tradeErstellenIntent;
                                    tradeErstellenIntent = new Intent(AktienDetailsActivity.this, TradeErstellenActivity.class);

                                    tradeErstellenIntent.putExtra("ticker",ticker);
                                    tradeErstellenIntent.putExtra("score",score);
                                    startActivity(tradeErstellenIntent);


                                }
                            });


                        }
                        if (close == null) {
                            closeTextView.setText("Letzter Kurs: -");
                        } else {
                            closeTextView.setText("Letzter Kurs: " + close);
                        }
                        if (sma20 == null) {
                            sma20TextView.setText("SMA20: -");
                        } else {
                            sma20TextView.setText("SMA20: " + sma20);
                        }
                        if (change20dPct == null) {
                            change20dTextView.setText("20-Tage-Änderung: -");
                        } else {
                            change20dTextView.setText("20-Tage-Änderung: " + change20dPct + " %");
                        }





                        Toast.makeText(AktienDetailsActivity.this, "Signal erfolgreich geladen", Toast.LENGTH_SHORT).show();


                    }
                }
        );


        tickerTextView.setText(ticker);
    }
}
