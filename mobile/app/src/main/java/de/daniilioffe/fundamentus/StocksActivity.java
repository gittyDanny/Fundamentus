package de.daniilioffe.fundamentus;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.SwitchCompat;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FieldValue;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;
import com.google.firebase.firestore.QuerySnapshot;

import java.util.ArrayList;


public class StocksActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_stocks);
        LinearLayout aktieLayout = findViewById(R.id.stockContainer);

        EditText suchText;
        suchText = findViewById(R.id.suchTextEingabe);


        //firebase Connection anlegen
        FirebaseFirestore databaseCon = FirebaseFirestore.getInstance();
        //Tabelle assets speichert die YML Einträge aus dem Bot - die wollen wir haben
        databaseCon.collection("assets").get().addOnCompleteListener(new OnCompleteListener<QuerySnapshot>() {
                                                                         @Override
                                                                         public void onComplete(@NonNull Task<QuerySnapshot> task) {
                                                                             if (!task.isSuccessful()) {
                                                                                 Toast.makeText(StocksActivity.this, "Daten konnten nicht geladen werden", Toast.LENGTH_SHORT).show();
                                                                                 Exception fehler = task.getException();

                                                                                 Log.e("FIRESTORE", "assets konnten nicht geladen werden", fehler);
                                                                                 return;
                                                                             }

                                                                             QuerySnapshot assetsTabelle;
                                                                             assetsTabelle = task.getResult();

                                                                             //Aktienzeile für jede Aktie
                                                                             showStocks(assetsTabelle, aktieLayout, "");


                                                                             Button suchButton = findViewById(R.id.aktienSucheButton);

                                                                             suchButton.setOnClickListener(new View.OnClickListener() {
                                                                                 @Override
                                                                                 public void onClick(View gesucht) {
                                                                                     String suchTextString = suchText.getText().toString();
                                                                                     showStocks(assetsTabelle, aktieLayout, suchTextString);
                                                                                 }
                                                                             });


                                                                         }
                                                                     }

        );


    }

    private void showStocks(QuerySnapshot assetsTabelle, LinearLayout aktieLayout, String suchText) {
        aktieLayout.removeAllViews();

        String eingegebenerSuchtext = suchText.trim().toLowerCase();

        LayoutInflater neueAktie = getLayoutInflater();

        FirebaseUser aktuellerNutzer;
        aktuellerNutzer = FirebaseAuth.getInstance().getCurrentUser();

        if (aktuellerNutzer == null) {
            Toast.makeText(StocksActivity.this, "Kein Nutzer angemeldet", Toast.LENGTH_SHORT).show();
            return;
        }
        String userID = aktuellerNutzer.getUid();

        FirebaseFirestore datenbankVerbindung;
        datenbankVerbindung = FirebaseFirestore.getInstance();


        for (QueryDocumentSnapshot assetsDatensatz : assetsTabelle) {
            String ticker = assetsDatensatz.getString("ticker");
            String name = assetsDatensatz.getString("name");
            String sector = assetsDatensatz.getString("sector");

            if (ticker == null) {
                ticker = "";
            }
            if (name == null) {
                name = "";
            }
            if (sector == null) {
                sector = "";
            }

            String tickerFuerDetails = ticker;

            boolean tickerWirdGesucht = ticker.toLowerCase().contains(eingegebenerSuchtext);
            boolean nameWirdGesucht = name.toLowerCase().contains(eingegebenerSuchtext);
            boolean sectorWirdGesucht = sector.toLowerCase().contains(eingegebenerSuchtext);

            if (tickerWirdGesucht || nameWirdGesucht || sectorWirdGesucht) {
                View aktienKachel;
                aktienKachel = neueAktie.inflate(R.layout.item_aktie, aktieLayout, false);


                TextView tickerTextView;
                tickerTextView = aktienKachel.findViewById(R.id.tickerAnzeigeText);
                tickerTextView.setText(ticker);
                TextView nameTextView;
                nameTextView = aktienKachel.findViewById(R.id.nameAnzeigeText);
                nameTextView.setText(name);
                TextView sectorTextView;
                sectorTextView = aktienKachel.findViewById(R.id.sectorAnzeigeText);
                sectorTextView.setText(sector);


                String tickerFuerWatchlist = ticker;
                SwitchCompat watchlistSwitch;
                watchlistSwitch = aktienKachel.findViewById(R.id.switchWatchlist);
                DocumentReference watchlistTabelle;

                watchlistTabelle = datenbankVerbindung.collection("users").document(userID);
                watchlistSwitch.setEnabled(false);

                watchlistTabelle.get().addOnCompleteListener(new OnCompleteListener<DocumentSnapshot>() {

                    @Override
                    public void onComplete(@NonNull Task<DocumentSnapshot> task) {

                        if (!task.isSuccessful()) {

                            Toast.makeText(StocksActivity.this, "Watchlist konnte nicht geladen werden.", Toast.LENGTH_SHORT).show();

                            return;
                        }

                        DocumentSnapshot watchlistDatensatz;
                        watchlistDatensatz = task.getResult();

                        if (watchlistDatensatz == null) {
                            watchlistSwitch.setEnabled(true);
                            return;
                        }

                        ArrayList<String> watchlist = (ArrayList<String>) watchlistDatensatz.get("watchlist");

                        if (watchlist == null) {
                            watchlist = new ArrayList<>();
                        }


                        watchlistSwitch.setChecked(watchlist.contains(tickerFuerWatchlist));

                        watchlistSwitch.setEnabled(true);

                        watchlistSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {

                            @Override
                            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {

                                if (isChecked) {

                                    watchlistTabelle.update("watchlist", FieldValue.arrayUnion(tickerFuerWatchlist));
                                } else {

                                    watchlistTabelle.update("watchlist", FieldValue.arrayRemove(tickerFuerWatchlist));
                                }


                            }


                        });
                    }


                });
                Button detailsButton;

                detailsButton = aktienKachel.findViewById(R.id.buttonAktieDetails);

                detailsButton.setOnClickListener(new View.OnClickListener() {

                    @Override
                    public void onClick(View angeklickterButton) {

                        Intent detailsIntent;

                        detailsIntent = new Intent(StocksActivity.this, AktienDetailsActivity.class);

                        detailsIntent.putExtra("ticker", tickerFuerDetails);

                        startActivity(detailsIntent);
                    }
                });
                aktieLayout.addView(aktienKachel);
            }
        }
    }
}