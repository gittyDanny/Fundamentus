package de.daniilioffe.fundamentus;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.android.material.navigation.NavigationView;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;
import com.google.firebase.firestore.QuerySnapshot;

//Hier ist eine Ansicht mit laufenden Trades(offenen Trades) man kan hierüber die Trades löschen oder
// zum Schliessen Ansicht(verkaufen) weitertgeleitet werden
public class TradesActivity extends AppCompatActivity {


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_trades);
        TextView positionStatusText = findViewById(R.id.tradesStatusText);
        LinearLayout positionContainer = findViewById(R.id.tradesContainer);

        DrawerLayout drawerLayout = findViewById(R.id.drawerLayout);

        Button buttonOpenMenu;
        buttonOpenMenu = findViewById(R.id.buttonOpenMenu);

        NavigationView navigationView;
        navigationView = findViewById(R.id.navigationView);

        buttonOpenMenu.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                drawerLayout.openDrawer(GravityCompat.START);

            }
        });

        navigationView.setNavigationItemSelectedListener(new NavigationView.OnNavigationItemSelectedListener() {
            @Override
            public boolean onNavigationItemSelected(@NonNull MenuItem menuItem) {
                if (menuItem.getItemId() == R.id.menuDashboard) {
                    Intent dashboardIntent;
                    dashboardIntent = new Intent(TradesActivity.this, DashboardActivity.class);
                    startActivity(dashboardIntent);
                    finish();
                    return true;
                } else if (menuItem.getItemId() == R.id.menuStocks) {
                    Intent stocksIntent;
                    stocksIntent = new Intent(TradesActivity.this, StocksActivity.class);
                    startActivity(stocksIntent);
                    finish();
                    return true;
                } else if (menuItem.getItemId() == R.id.menuLogout) {
                    Intent logoutIntent;
                    logoutIntent = new Intent(TradesActivity.this, LoginActivity.class);
                    FirebaseAuth.getInstance().signOut();
                    startActivity(logoutIntent);
                    Toast.makeText(TradesActivity.this, "logout erfolgreich", Toast.LENGTH_SHORT).show();

                    finish();
                    return true;

                }
                return false;
            }
        });

        FirebaseUser aktuellerNutzer = FirebaseAuth.getInstance().getCurrentUser();
        if (aktuellerNutzer == null) {
            Toast.makeText(TradesActivity.this, "Wer sind Sie und was machen Sie hier?", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }


        String userID = aktuellerNutzer.getUid();
        FirebaseFirestore datenbankVerbindung = FirebaseFirestore.getInstance();

        datenbankVerbindung.collection("users").document(userID).collection("open_trades").get()
                .addOnCompleteListener(new OnCompleteListener<QuerySnapshot>() {
                                           @SuppressLint({"SetTextI18n", "DefaultLocale"})
                                           @Override
                                           public void onComplete(@NonNull Task<QuerySnapshot> tradesLaden) {
                                               if (tradesLaden.isSuccessful() == false) {
                                                   Log.e("FIRESTORE", "Offene Trades konnten nicht geladen werden", tradesLaden.getException());
                                                   Toast.makeText(TradesActivity.this, "Offene Trades konnten nicht geladen werden", Toast.LENGTH_SHORT).show();
                                                   return;
                                               }

                                               QuerySnapshot offeneTrades = tradesLaden.getResult();

                                               if (offeneTrades == null || offeneTrades.isEmpty()) {
                                                   Toast.makeText(TradesActivity.this, "Keine offene Trades vorhanden.", Toast.LENGTH_SHORT).show();
                                                   positionStatusText.setText("Keine offenen Trades vorhanden");
                                                   return;
                                               }
                                               int anzahlOffenerTrades = offeneTrades.size();
                                               Toast.makeText(TradesActivity.this, anzahlOffenerTrades + " offene Trades geladen", Toast.LENGTH_SHORT).show();
                                               positionStatusText.setText("Offene Trades: " + anzahlOffenerTrades);
                                               LayoutInflater tradeInflater;
                                               tradeInflater = getLayoutInflater();

                                               for (QueryDocumentSnapshot positionDatensatz : offeneTrades) {
                                                   String ticker = positionDatensatz.getString("ticker");
                                                   String börse = positionDatensatz.getString("broker");
                                                   Double kaufpreis = positionDatensatz.getDouble("kaufpreis");
                                                   Double anzahl = positionDatensatz.getDouble("anzahl");
                                                   Double kaufGebühr = positionDatensatz.getDouble("kaufGebühr");
                                                   Double erwarteteVerkaufsGebühr = positionDatensatz.getDouble("erwarteteVerkaufsGebühr");
                                                   Double scoreBeimEinstieg = positionDatensatz.getDouble("scoreBeimEinstieg");
                                                   String tradeID = positionDatensatz.getId();
                                                   String tickerFürSchließen = ticker;

                                                   if (ticker == null) {
                                                       ticker = "";
                                                   }

                                                   if (börse == null) {
                                                       börse = "Unbekannt";
                                                   }

                                                   if (kaufpreis == null) {
                                                       kaufpreis = 0.0;
                                                   }

                                                   if (anzahl == null) {
                                                       anzahl = 0.0;
                                                   }

                                                   if (kaufGebühr == null) {
                                                       kaufGebühr = 0.0;
                                                   }

                                                   if (erwarteteVerkaufsGebühr == null) {
                                                       erwarteteVerkaufsGebühr = 0.0;
                                                   }

                                                   if (scoreBeimEinstieg == null) {
                                                       scoreBeimEinstieg = -1.0;
                                                   }

                                                   View positionKachel;
                                                   positionKachel = tradeInflater.inflate(R.layout.item_trade, positionContainer, false);


                                                   TextView tickerText = positionKachel.findViewById(R.id.tradeItemTickerText);
                                                   TextView börseText = positionKachel.findViewById(R.id.tradeItemBrokerText);
                                                   TextView einstiegText = positionKachel.findViewById(R.id.tradeItemEinstiegText);
                                                   TextView anzahlText = positionKachel.findViewById(R.id.tradeItemAnzahlText);
                                                   TextView einsatzText = positionKachel.findViewById(R.id.tradeItemEinsatzText);
                                                   TextView kursText = positionKachel.findViewById(R.id.tradeItemKursText);
                                                   TextView auszahlungText = positionKachel.findViewById((R.id.tradeItemAuszahlungText));
                                                   TextView plText = positionKachel.findViewById(R.id.tradeItemPlText);
                                                   TextView scoreText = positionKachel.findViewById(R.id.tradeItemScoreText);
                                                   Button tradeLöschenButton = positionKachel.findViewById(R.id.buttonTradeLöschen);
                                                   Button tradeSchließenButton = positionKachel.findViewById(R.id.buttonTradeSchließen);


                                                   DocumentReference positionDatensatzReference = positionDatensatz.getReference();
                                                   tradeSchließenButton.setOnClickListener(new View.OnClickListener() {
                                                       @Override
                                                       public void onClick(View v) {
                                                           Intent schließenIntent;
                                                           schließenIntent = new Intent(TradesActivity.this, TradeSchließenActivity.class);
                                                           schließenIntent.putExtra("tradeID", tradeID);
                                                           schließenIntent.putExtra("ticker", tickerFürSchließen);
                                                           startActivity(schließenIntent);
                                                       }
                                                   });
                                                   tradeLöschenButton.setOnClickListener(new View.OnClickListener() {
                                                       @Override
                                                       public void onClick(View v) {
                                                           positionDatensatzReference.delete().addOnCompleteListener(new OnCompleteListener<Void>() {
                                                               @Override
                                                               public void onComplete(@NonNull Task<Void> tradeLöschen) {
                                                                   if (tradeLöschen.isSuccessful() == false) {
                                                                       Toast.makeText(TradesActivity.this, "Trade konnte nicht gelöscht werden", Toast.LENGTH_SHORT).show();
                                                                       return;
                                                                   }
                                                                   positionContainer.removeView(positionKachel);

                                                                   Toast.makeText(TradesActivity.this, "Trade gelöscht", Toast.LENGTH_SHORT).show();
                                                                   positionStatusText.setText("Offene Trades : " + positionContainer.getChildCount());
                                                               }
                                                           });
                                                       }
                                                   });

                                                   double gesamterEinsatz = kaufpreis * anzahl + kaufGebühr;
                                                   tickerText.setText(ticker);
                                                   börseText.setText("Broker: " + börse);
                                                   einstiegText.setText("Einstieg: " + String.format("%.2f", kaufpreis) + " $");
                                                   anzahlText.setText("Anzahl: " + String.format("%.4f", anzahl));
                                                   einsatzText.setText("Gesamteinsatz: " + String.format("%.2f", gesamterEinsatz) + " $");
                                                   if (scoreBeimEinstieg == -1.0) {
                                                       scoreText.setText("Score beim Einstieg: -");

                                                   } else {
                                                       scoreText.setText("Score beim Einstieg: " + String.format("%.1f", scoreBeimEinstieg));
                                                   }
                                                   String tickerFürKurs = ticker;
                                                   double anzahlFürBerechnung = anzahl;
                                                   double gesamterEinsatzFürBerechnung = gesamterEinsatz;
                                                   double verkaufsGebührFürBerechnung = erwarteteVerkaufsGebühr;
                                                   positionContainer.addView(positionKachel);

                                                   datenbankVerbindung.collection("latest_signals").document(tickerFürKurs).get().addOnCompleteListener(new OnCompleteListener<DocumentSnapshot>() {
                                                       @Override
                                                       public void onComplete(@NonNull Task<DocumentSnapshot> kursLaden) {
                                                           if (kursLaden.isSuccessful() == false) {
                                                               kursText.setText("kein Kurs konnte geladen werden");
                                                               return;
                                                           }

                                                           DocumentSnapshot signalDatensatz = kursLaden.getResult();
                                                           if (signalDatensatz == null || signalDatensatz.exists() == false) {
                                                               kursText.setText("Kein Kurs vorhanden");
                                                               return;
                                                           }


                                                           Double letzterBotKurs = signalDatensatz.getDouble("close");
                                                           if (letzterBotKurs == null) {
                                                               kursText.setText("Kein Kurs vorhanden");
                                                               return;
                                                           }

                                                           double aktuellerBruttowert = letzterBotKurs * anzahlFürBerechnung;
                                                           double auszahlungNachGebühr = aktuellerBruttowert - verkaufsGebührFürBerechnung;
                                                           double nettoPL = auszahlungNachGebühr - gesamterEinsatzFürBerechnung;
                                                           double nettoPLProzent = nettoPL / gesamterEinsatzFürBerechnung * 100;
                                                           kursText.setText("Letzter Fundamentus-Kurs: " + String.format("%.2f", letzterBotKurs) + " $");
                                                           auszahlungText.setText("Auszahlung nach Gebühr: " + String.format("%.2f", auszahlungNachGebühr) + " $");
                                                           plText.setText("Netto-P/L: " + String.format("%+.2f", nettoPL) + " $ /" + String.format("%+.2f", nettoPLProzent) + " %");


                                                       }
                                                   });
                                               }
                                           }
                                       }
                );


    }


}
