package de.daniilioffe.fundamentus;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

public class DashboardActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Verbindet die Activity mit der Dashboard-Oberfläche.
        setContentView(R.layout.activity_dashboard);

        // DrawerLayout und Menü-Button aus der XML-Datei laden.
        DrawerLayout drawerLayout =
                findViewById(R.id.drawerLayout);

        Button buttonOpenMenu =
                findViewById(R.id.buttonOpenMenu);

        // Öffnet das seitliche Navigationsmenü.
        buttonOpenMenu.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View view) {

                drawerLayout.openDrawer(GravityCompat.START);
            }
        });
    }
}