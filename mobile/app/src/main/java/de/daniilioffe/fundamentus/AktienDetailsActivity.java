package de.daniilioffe.fundamentus;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.android.material.navigation.NavigationView;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;
//Details einer Aktie
//Details Button im Stocks Activity wird angeclickt, Aktiendetails werden aufgerufen:
//Signal,Score,Begründung für das Score, letzter Kurs, SMA20, 20 Tage Änderung
//Über ticker aus Firestore geholt
public class AktienDetailsActivity extends AppCompatActivity {
    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_aktie_details);

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
                    dashboardIntent = new Intent(AktienDetailsActivity.this, DashboardActivity.class);
                    startActivity(dashboardIntent);
                    finish();
                    return true;
                } else if (menuItem.getItemId() == R.id.menuStocks) {
                    Intent stocksIntent;
                    stocksIntent = new Intent(AktienDetailsActivity.this, StocksActivity.class);
                    startActivity(stocksIntent);
                    finish();
                    return true;
                } else if (menuItem.getItemId() == R.id.menuLogout) {
                    Intent logoutIntent;
                    logoutIntent = new Intent(AktienDetailsActivity.this, LoginActivity.class);
                    FirebaseAuth.getInstance().signOut();
                    startActivity(logoutIntent);
                    Toast.makeText(AktienDetailsActivity.this, "logout erfolgreich", Toast.LENGTH_SHORT).show();

                    finish();
                    return true;

                } else if (menuItem.getItemId() == R.id.menuTrades) {
                    Intent tradesIntent;
                    tradesIntent = new Intent(AktienDetailsActivity.this, TradesActivity.class);
                    startActivity(tradesIntent);

                    finish();
                    return true;

                } else if (menuItem.getItemId() == R.id.menuLogout) {
                    Intent tradesIntent;
                    tradesIntent = new Intent(AktienDetailsActivity.this, TradesActivity.class);
                    startActivity(tradesIntent);

                    finish();
                    return true;

                }
                return false;
            }
        });

        TextView tickerTextView = findViewById(R.id.detailsTickerText);
        TextView signalTextView = findViewById(R.id.detailsSignalText);
        TextView scoreTextView = findViewById(R.id.detailsScoreText);
        TextView reasonTextView = findViewById(R.id.detailsReasonText);
        TextView closeTextView = findViewById(R.id.detailsCloseText);
        TextView sma20TextView = findViewById(R.id.detailsSma20Text);
        TextView change20dTextView = findViewById(R.id.detailsChange20dText);
        Button tradeErstellenButton = findViewById(R.id.buttonPaperTradeErstellen);

        // ticker aus StocksActivity
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

                                    tradeErstellenIntent.putExtra("ticker", ticker);
                                    tradeErstellenIntent.putExtra("score", score);
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
