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

        NavigationView navigationView = findViewById(R.id.navigationView);


        NavigationView.OnNavigationItemSelectedListener navigationListener = new NavigationView.OnNavigationItemSelectedListener() {
            @Override
            public boolean onNavigationItemSelected(MenuItem menuItem) {
                if (menuItem.getItemId() == R.id.menuLogout) {
                    Intent logoutIntent = new Intent(DashboardActivity.this, LoginActivity.class);
                    startActivity(logoutIntent);
                    FirebaseAuth.getInstance().signOut();
                    finish();
                    Toast.makeText(DashboardActivity.this, "Logout erfolgreich.", Toast.LENGTH_SHORT).show();
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
