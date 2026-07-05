package de.daniilioffe.fundamentus;

import android.content.Intent;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;

public class LoginActivity extends AppCompatActivity {

    // Verbindung zu Firebase Authentication.
    private FirebaseAuth firebaseAuth;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Verbindet die Activity mit der XML-Oberfläche.
        setContentView(R.layout.activity_login);

        // Firebase Authentication vorbereiten.
        firebaseAuth = FirebaseAuth.getInstance();

        // Eingabefelder und Button aus der XML-Datei laden.
        EditText inputEmail =
                findViewById(R.id.inputEmail);

        EditText inputPassword =
                findViewById(R.id.inputPassword);

        Button buttonLogin =
                findViewById(R.id.buttonLogin);

        // Reagiert auf einen Klick auf den Login-Button.
        buttonLogin.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View view) {

                // Eingaben auslesen.
                String email =
                        inputEmail.getText().toString().trim();

                String password =
                        inputPassword.getText().toString();

                // Leere Eingabefelder verhindern.
                if (email.isEmpty() || password.isEmpty()) {

                    Toast.makeText(
                            LoginActivity.this,
                            "Bitte E-Mail-Adresse und Passwort eingeben.",
                            Toast.LENGTH_SHORT
                    ).show();

                    return;
                }

                // E-Mail und Passwort an Firebase übergeben.
                firebaseAuth
                        .signInWithEmailAndPassword(email, password)
                        .addOnCompleteListener(
                                LoginActivity.this,
                                new OnCompleteListener<AuthResult>() {

                                    @Override
                                    public void onComplete(
                                            @NonNull Task<AuthResult> task
                                    ) {

                                        if (task.isSuccessful()) {

                                            Toast.makeText(
                                                    LoginActivity.this,
                                                    "Login erfolgreich.",
                                                    Toast.LENGTH_SHORT
                                            ).show();

                                            // Dashboard öffnen.
                                            Intent intent = new Intent(
                                                    LoginActivity.this,
                                                    DashboardActivity.class
                                            );

                                            startActivity(intent);

                                            // Login-Seite schließen, damit man nicht zurückspringen kann.
                                            finish();
                                        } else {

                                            Toast.makeText(
                                                    LoginActivity.this,
                                                    "Login fehlgeschlagen.",
                                                    Toast.LENGTH_SHORT
                                            ).show();
                                        }
                                    }
                                }
                        );
            }
        });
    }
}