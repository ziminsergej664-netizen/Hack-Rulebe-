package com.gtaloader.mobile;
import android.app.Activity; import android.os.Bundle; import android.content.*; import android.provider.Settings; import android.view.inputmethod.InputMethodManager; import android.widget.*; import android.graphics.Color; import android.view.View;
public class MainActivity extends Activity {
 static final String GAME="com.rockstar.gta3", PREF="activation", KEY="GTA3-106-LG11";
 LinearLayout body; TextView status; EditText key; Button launch,settings,picker;
 Button button(String text,Runnable action){Button b=new Button(this);b.setText(text);b.setAllCaps(false);body.addView(b);b.setOnClickListener(v->action.run());return b;}
 boolean active(){return getSharedPreferences(PREF,0).getBoolean("active",false);}
 void refresh(){boolean a=active();status.setText(a?"Активировано · GTA III 1.10.106":"Введите ключ активации");launch.setEnabled(a);settings.setEnabled(a);picker.setEnabled(a);}
 public void onCreate(Bundle b){super.onCreate(b);body=new LinearLayout(this);body.setOrientation(1);body.setPadding(32,48,32,32);body.setBackgroundColor(Color.rgb(17,21,29));ScrollView scroll=new ScrollView(this);scroll.addView(body);setContentView(scroll);
 TextView title=new TextView(this);title.setText("GTA III / LOADER");title.setTextSize(28);title.setTextColor(Color.WHITE);body.addView(title);status=new TextView(this);body.addView(status);key=new EditText(this);key.setSingleLine(true);key.setHint("Ключ");body.addView(key);
 button("Активировать",()->{if(KEY.equals(key.getText().toString().trim())){getSharedPreferences(PREF,0).edit().putBoolean("active",true).apply();key.setText("");refresh();}else Toast.makeText(this,"Неверный ключ",0).show();});
 launch=button("Запустить GTA III",()->{Intent i=getPackageManager().getLaunchIntentForPackage(GAME);if(i==null){Toast.makeText(this,"Игра не найдена",1).show();return;}try{startActivity(i);}catch(ActivityNotFoundException|SecurityException e){Toast.makeText(this,"Не удалось запустить игру",1).show();}});
 settings=button("Включить клавиатуру читов",()->startActivity(new Intent(Settings.ACTION_INPUT_METHOD_SETTINGS)));
 picker=button("Выбрать клавиатуру читов",()->((InputMethodManager)getSystemService(INPUT_METHOD_SERVICE)).showInputMethodPicker());
 TextView note=new TextView(this);note.setText("Клавиатура отправляет обычные чит-коды в активное поле ввода. Совместимость с GTA III не проверена. Это не внедрение в память и не плавающее меню.");body.addView(note);refresh();}
}