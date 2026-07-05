package de.daniilioffe.fundamentus;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Verbindet die Activity mit unserer XML-Oberfläche.
        setContentView(R.layout.activity_main);
    }
}