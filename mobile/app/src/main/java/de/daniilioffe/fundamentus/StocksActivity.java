package de.daniilioffe.fundamentus;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.SwitchCompat;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.android.material.navigation.NavigationView;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FieldValue;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;
import com.google.firebase.firestore.QuerySnapshot;

import java.util.ArrayList;

//Übersicht an Aktien, die wir im Fundamentus analysieren
public class StocksActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_stocks);
        LinearLayout aktieLayout = findViewById(R.id.stockContainer);

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
                if (menuItem.getItemId() == R.id.menuDashboard){
                    Intent dashboardIntent;
                    dashboardIntent = new Intent(StocksActivity.this, DashboardActivity.class);
                    startActivity(dashboardIntent);
                    finish();
                    return true;
                } else if (menuItem.getItemId() == R.id.menuTrades) {
                    Intent tradesIntent;
                    tradesIntent = new Intent(StocksActivity.this, TradesActivity.class);
                    startActivity(tradesIntent);
                    finish();
                    return true;
                } else if (menuItem.getItemId() == R.id.menuLogout) {
                    Intent logoutIntent;
                    logoutIntent = new Intent(StocksActivity.this,LoginActivity.class);
                    FirebaseAuth.getInstance().signOut();
                    startActivity(logoutIntent);
                    Toast.makeText(StocksActivity.this, "logout erfolgreich", Toast.LENGTH_SHORT).show();

                    finish();
                    return true;

                }
                return false;
            }
        });

        EditText suchText;
        suchText = findViewById(R.id.suchTextEingabe);

        Spinner sectorFilter;
        sectorFilter = findViewById(R.id.spinnerSectorFilter);

        Spinner watchlistFilter;
        watchlistFilter = findViewById(R.id.spinnerWatchlistFilter);


        //firebase Connection anlegen
        FirebaseFirestore databaseCon = FirebaseFirestore.getInstance();
        //Tabelle assets speichert die YML Einträge aus dem Bot
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

                FirebaseUser aktuellerNutzer;
                aktuellerNutzer = FirebaseAuth.getInstance().getCurrentUser();

                if (aktuellerNutzer == null) {
                    Toast.makeText(StocksActivity.this, "Kein Nutzer angemeldet", Toast.LENGTH_SHORT).show();
                    return;
                }

                String userID = aktuellerNutzer.getUid();

                DocumentReference nutzerTabelle;
                nutzerTabelle = databaseCon.collection("users").document(userID);

                nutzerTabelle.get().addOnCompleteListener(new OnCompleteListener<DocumentSnapshot>() {
                    @Override
                    public void onComplete(@NonNull Task<DocumentSnapshot> watchlistAbholen) {
                        if (watchlistAbholen.isSuccessful() == false) {
                            Toast.makeText(StocksActivity.this, "Watchliste konnte nicht geladen werden", Toast.LENGTH_SHORT).show();
                            return;
                        }
                        DocumentSnapshot nutzerDatensatz;
                        nutzerDatensatz = watchlistAbholen.getResult();

                        ArrayList<String> abgeholteWatchlist;

                        if (nutzerDatensatz == null || nutzerDatensatz.get("watchlist") == null) {
                            abgeholteWatchlist = new ArrayList<>();
                        } else {
                            abgeholteWatchlist = (ArrayList<String>) nutzerDatensatz.get("watchlist");
                        }
                        showStocks(assetsTabelle, aktieLayout, "", "Alle Sektoren", "Alle Aktien", abgeholteWatchlist);
                        Button suchButton = findViewById(R.id.aktienSucheButton);

                        suchButton.setOnClickListener(new View.OnClickListener() {
                            @Override
                            public void onClick(View gesucht) {
                                String suchTextString = suchText.getText().toString();
                                String ausgewählterSector = sectorFilter.getSelectedItem().toString();
                                String obWatchlistFilter = watchlistFilter.getSelectedItem().toString();
                                showStocks(assetsTabelle, aktieLayout, suchTextString, ausgewählterSector, obWatchlistFilter, abgeholteWatchlist);
                            }
                        });
                    }
                });

            }
        });


    }

    private void showStocks(QuerySnapshot assetsTabelle, LinearLayout aktieLayout, String suchText, String sectorFilter, String watchlistFilter, ArrayList<String> watchlist) {
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

            boolean istWatchlisted;
            boolean watchlistPasst;
            istWatchlisted = watchlist.contains(ticker);
            if ((watchlistFilter.equals("Alle Aktien"))) {
                watchlistPasst = true;
            } else {
                watchlistPasst = istWatchlisted;
            }
            boolean tickerWirdGesucht = ticker.toLowerCase().contains(eingegebenerSuchtext);
            boolean nameWirdGesucht = name.toLowerCase().contains(eingegebenerSuchtext);
            boolean sectorWirdGesucht = sector.toLowerCase().contains(eingegebenerSuchtext);
            boolean sectorPasst;

            if (sectorFilter.equals("Alle Sektoren")) {
                sectorPasst = true;
            } else {
                sectorPasst = sector.equals(sectorFilter);
            }

            if ((tickerWirdGesucht || nameWirdGesucht || sectorWirdGesucht) && sectorPasst && watchlistPasst) {
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
                watchlistSwitch.setChecked(istWatchlisted);
                watchlistSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
                                                               @Override
                                                               public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
                                                                   if (isChecked){
                                                                       watchlistTabelle.update("watchlist", FieldValue.arrayUnion(tickerFuerWatchlist));
                                                                       if (watchlist.contains(tickerFuerWatchlist) == false){
                                                                           watchlist.add(tickerFuerWatchlist);
                                                                       }
                                                                   }else{
                                                                       watchlistTabelle.update("watchlist",FieldValue.arrayRemove(tickerFuerWatchlist));
                                                                       watchlist.remove(tickerFuerWatchlist);
                                                                   }

                                                               }
                                                           }
                );

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