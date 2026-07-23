package de.daniilioffe.fundamentus;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;
import com.google.firebase.firestore.QuerySnapshot;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;



public class StocksActivity extends AppCompatActivity {



    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_stocks);
        LinearLayout aktieLayout = findViewById(R.id.stockContainer);

        EditText suchText;
        suchText = findViewById(R.id.suchTextEingabe);


        //firebase Connection anlegen
        FirebaseFirestore databaseCon = FirebaseFirestore.getInstance();
        //Tabelle assets speichert die YML Einträge aus dem Bot - die wollen wir haben
        databaseCon.collection("assets").get().addOnCompleteListener(
                new OnCompleteListener<QuerySnapshot>() {
                    @Override
                    public void onComplete(@NonNull Task<QuerySnapshot> task) {
                        if (task.isSuccessful() == false){
                            Toast.makeText(StocksActivity.this,"Daten konnten nicht geladen werden",Toast.LENGTH_SHORT).show();
                            Exception fehler = task.getException();

                            Log.e(
                                    "FIRESTORE",
                                    "assets konnten nicht geladen werden",
                                    fehler
                            );
                            return;
                        }

                        QuerySnapshot assetsTabelle;
                        assetsTabelle = task.getResult();

                        //Aktienzeile für jede Aktie
                        showStocks(assetsTabelle,aktieLayout,"");


                        Button suchButton = findViewById(R.id.aktienSucheButton);

                        suchButton.setOnClickListener(new View.OnClickListener() {
                            @Override
                            public void onClick(View gesucht) {
                                String suchTextString = suchText.getText().toString();
                                showStocks(assetsTabelle,aktieLayout,suchTextString);
                            }
                        });


                    }
                }

        );





    }
    private void showStocks(QuerySnapshot assetsTabelle, LinearLayout aktieLayout, String suchText){
        aktieLayout.removeAllViews();

        String eingegebenerSuchtext = suchText.trim().toLowerCase();

        LayoutInflater neueAktie = getLayoutInflater();

        for(QueryDocumentSnapshot assetsDatensatz : assetsTabelle){
            String ticker = assetsDatensatz.getString("ticker");
            String name  = assetsDatensatz.getString("name");
            String sector = assetsDatensatz.getString("sector");

            if (ticker == null){
                ticker = "";
            }
            if (name == null){
                name = "";
            }
            if (sector == null){
                sector = "";
            }

            boolean tickerWirdGesucht = ticker.toLowerCase().contains(eingegebenerSuchtext);
            boolean nameWirdGesucht = name.toLowerCase().contains(eingegebenerSuchtext);
            boolean sectorWirdGesucht = sector.toLowerCase().contains(eingegebenerSuchtext);

            if(tickerWirdGesucht == true || nameWirdGesucht == true || sectorWirdGesucht == true){
                View aktienKachel;
                aktienKachel =  neueAktie.inflate(R.layout.item_aktie,aktieLayout,false);

                TextView tickerTextView;
                tickerTextView = aktienKachel.findViewById(R.id.tickerAnzeigeText);
                tickerTextView.setText(ticker);
                TextView nameTextView;
                nameTextView = aktienKachel.findViewById(R.id.nameAnzeigeText);
                nameTextView.setText(name);
                TextView sectorTextView;
                sectorTextView = aktienKachel.findViewById(R.id.sectorAnzeigeText);
                sectorTextView.setText(sector);

                aktieLayout.addView(aktienKachel);
            }

        }


    }

}
