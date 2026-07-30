package de.daniilioffe.fundamentus;

import com.google.android.gms.tasks.OnFailureListener;
import com.google.android.gms.tasks.OnSuccessListener;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;

//Quasi die MainActivity, aber ich wollte alle Activities nach Funktion nennen

public class LoginActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // DIESE ZWEI ZEILEN NICHT ÄNDERN!
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        //sorry, ich habs umbenannt


        FirebaseAuth firebaseAuth = FirebaseAuth.getInstance();
        EditText inputEmail = findViewById(R.id.inputEmail);
        EditText inputPassword = findViewById(R.id.inputPassword);
        final Button buttonLogin = findViewById(R.id.buttonLogin);

        buttonLogin.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View view) {
                String email = inputEmail.getText().toString().trim();
                String password = inputPassword.getText().toString();
                //ob leer
                if (email.isEmpty()) {
                    Toast.makeText(LoginActivity.this, "Bitte E-Mail-Adresse eingeben.", Toast.LENGTH_SHORT).show();
                    return;
                }

                if (password.isEmpty()) {
                    Toast.makeText(LoginActivity.this, "Bitte Passwort eingeben.", Toast.LENGTH_SHORT).show();
                    return;
                }
                //checken ob das die Daten mit der Nutzetabelle übereinstimmen
                firebaseAuth.signInWithEmailAndPassword(email, password).addOnSuccessListener(//wenn klappt passiert:
                        new OnSuccessListener<AuthResult>() {
                            @Override
                            public void onSuccess(AuthResult authResult) {
                                Toast.makeText(LoginActivity.this, "Login erfolgreich.", Toast.LENGTH_SHORT).show();
                                Intent loginIntent = new Intent(LoginActivity.this, DashboardActivity.class);
                                startActivity(loginIntent);
                                finish();
                            }
                        }
                ).addOnFailureListener(
                        new OnFailureListener() {
                            @Override
                            public void onFailure(Exception exception) {
                                Toast.makeText(LoginActivity.this, "Login fehlgeschlagen.", Toast.LENGTH_SHORT).show();
                            }
                        }
                );
            }
        });
    }
}