package de.daniilioffe.fundamentus;

import android.content.Intent;
import android.os.Bundle;

import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;


import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

import com.google.android.material.navigation.NavigationView;
import com.google.firebase.auth.FirebaseAuth;

// 1. XML wird geladen, 2. UI Elemente werden gefunden 3. Listener werden registriert,
// 4. Nutzer clickt 5. Listener Methode wird ausgeführt -> Activity
public class DashboardActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dashboard);
        DrawerLayout drawerLayout = findViewById(R.id.drawerLayout);
        Button buttonOpenMenu = findViewById(R.id.buttonOpenMenu);

        buttonOpenMenu.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View view) {
                drawerLayout.openDrawer(GravityCompat.START);
            }
        });
        // Ansicht holen
        NavigationView navigationView = findViewById(R.id.navigationView);
        // Listener, der auf die Menuauswahl wartet
        NavigationView.OnNavigationItemSelectedListener navigationListener = new NavigationView.OnNavigationItemSelectedListener() {
            @Override
            public boolean onNavigationItemSelected(MenuItem menuItem) {
                if (menuItem.getItemId() == R.id.menuLogout) {
                    Intent logoutIntent = new Intent(DashboardActivity.this, LoginActivity.class);
                    startActivity(logoutIntent);
                    //Auth - Instanz "beenden"
                    FirebaseAuth.getInstance().signOut();
                    finish();
                    Toast.makeText(DashboardActivity.this, "Logout erfolgreich.", Toast.LENGTH_SHORT).show();
                    return true;
                }

                if (menuItem.getItemId() == R.id.menuTrades) {
                    Intent tradesIntent = new Intent(DashboardActivity.this, TradesActivity.class);
                    startActivity(tradesIntent);
                    return true;
                }


                if (menuItem.getItemId() == R.id.menuStocks) {
                    Intent goToStocksIntent = new Intent(DashboardActivity.this, StocksActivity.class);
                    startActivity(goToStocksIntent);
                    return true;
                }
                return false;
            }


        };
        navigationView.setNavigationItemSelectedListener(navigationListener);


    }


}
