package de.daniilioffe.fundamentus;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.util.LogPrinter;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
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
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QuerySnapshot;

public class TradesActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_trades);

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
                    logoutIntent = new Intent(TradesActivity.this,LoginActivity.class);
                    FirebaseAuth.getInstance().signOut();
                    startActivity(logoutIntent);
                    Toast.makeText(TradesActivity.this, "logout erfolgreich", Toast.LENGTH_SHORT).show();

                    finish();
                    return true;

                }
                return false;
            }
        });

        TextView positionStatusText = findViewById(R.id.tradesStatusText);
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
                                           @Override
                                           public void onComplete(@NonNull Task<QuerySnapshot> tradesLaden) {
                                                if (tradesLaden.isSuccessful() == false){
                                                    Log.e("FIRESTORE","Offene Trades konnten nicht geladen werden",tradesLaden.getException());
                                                    Toast.makeText(TradesActivity.this,"Offene Trades konnten nicht geladen werden",Toast.LENGTH_SHORT).show();
                                                    return;
                                                }

                                                QuerySnapshot offeneTrades = tradesLaden.getResult();

                                                if(offeneTrades == null || offeneTrades.isEmpty()){
                                                    Toast.makeText(TradesActivity.this, "Keine offene Trades vorhanden.", Toast.LENGTH_SHORT).show();
                                                    return;
                                                }
                                                int anzahlOffenerTrades = offeneTrades.size();
                                                Toast.makeText(TradesActivity.this, anzahlOffenerTrades + " offene Trades geladen", Toast.LENGTH_SHORT).show();

                                           }
                                       }
                );


    }

}
