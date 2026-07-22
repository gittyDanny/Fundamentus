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
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import java.util.ArrayList;

public class StocksActivity extends AppCompatActivity {
    public ArrayList<String> stocks = new ArrayList<>();


    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_stocks);
        LinearLayout stockContainer = findViewById(R.id.stockContainer);

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

                        QuerySnapshot stockData;
                        stockData = task.getResult();

                        LayoutInflater newStock;
                        newStock = getLayoutInflater();
                        //Aktienzeile für jede Aktie
                        for (QueryDocumentSnapshot stockDok : stockData) {

                            String ticker;
                            ticker = stockDok.getString("ticker");


                            View stockRow;
                            stockRow = newStock.inflate(
                                    R.layout.item_stock,
                                    stockContainer,
                                    false
                            );

                            TextView tickerTextView;
                            tickerTextView = stockRow.findViewById(
                                    R.id.textStockTicker
                            );

                            tickerTextView.setText(ticker);

                            stockContainer.addView(stockRow);
                        }


                    }
                }

        );

    }
}
