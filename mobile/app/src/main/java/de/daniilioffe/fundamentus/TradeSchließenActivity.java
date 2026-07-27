package de.daniilioffe.fundamentus;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.Firebase;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.FirebaseFirestore;

import org.w3c.dom.Document;

public class TradeSchließenActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_trade_schliessen);
        TextView tickerText = findViewById(R.id.schließenTickerText);
        TextView einstiegText = findViewById(R.id.schließenEinstiegText);
        EditText inputVerkaufspreis = findViewById(R.id.inputVerkaufspreis);
        TextView ergebnisText = findViewById(R.id.schließenErgebnisText);
        Button verkaufBestätigenButton = findViewById(R.id.buttonVerkaufBestätigen);

        Intent schließenIntent = getIntent();
        String tradeID = schließenIntent.getStringExtra("tradeID");
        if (tradeID == null || tradeID.isEmpty()){
            Toast.makeText(TradeSchließenActivity.this,"Keine Trade-ID übergeben",Toast.LENGTH_SHORT).show();
            finish();
            return;
        }
        String ticker = schließenIntent.getStringExtra("ticker");
        if (ticker == null){
            ticker = "";
        }
        tickerText.setText(ticker);

        FirebaseUser aktuellerNutzer;
        aktuellerNutzer = FirebaseAuth.getInstance().getCurrentUser();
        if(aktuellerNutzer == null){
            Toast.makeText(TradeSchließenActivity.this, "Wer sind Sie und was wollen Sie von mir?", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }
        String userID = aktuellerNutzer.getUid();
        FirebaseFirestore datenbankVerbindung = FirebaseFirestore.getInstance();
        DocumentReference offenerTradeDokument;
        offenerTradeDokument = datenbankVerbindung.collection("users").document(userID).collection("open_trades").document(tradeID);





        Double kaufpreis;
        Double anzahl;
        Double getKaufgebühr;
        Double erwarteteVerkaufsgebühr;
        Double scoreBeimEinstieg;
        String börse;
        Double verkaufspreis;
        Double gesamterEinsatz;
        double verkaufsErlös = verkaufspreis * anzahl - erwarteteVerkaufsgebühr;
        double realisierterPL = verkaufsErlös - gesamterEinsatz;
        double getRealisierterPLProzent = realisierterPL / gesamterEinsatz * 100;
    }

}
