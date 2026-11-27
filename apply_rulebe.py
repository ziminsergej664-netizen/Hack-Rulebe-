from pathlib import Path
import sys
root=Path(sys.argv[1])
def replace(p,a,b):
 p=root/p
 s=p.read_text()
 assert s.count(a)==1, str(p)
 p.write_text(s.replace(a,b,1))
p='src/core/Pad.cpp'
replace(p,'#include "General.h"','#include "General.h"\n#include "Clock.h"\n#if defined(ANDROID)\n#include <jni.h>\n#include <mutex>\n#include <deque>\n#endif')
replace(p,'void CPad::DoCheats(void)\n{',r'''
#if defined(ANDROID)
namespace {
struct RulebeAction { int id, value; };
std::mutex rulebeMutex;
std::deque<RulebeAction> rulebeQueue;
bool rulebeHealth=false, rulebeAmmo=false, rulebeWanted=false;
int rulebeAmmoCount=250;
void RulebeTick() {
    if (FrontEndMenuManager.GetIsMenuActive() || CCutsceneMgr::IsRunning() || !FindPlayerPed()) {
        std::lock_guard<std::mutex> lock(rulebeMutex); rulebeQueue.clear(); return;
    }
    auto* player=FindPlayerPed();
    std::deque<RulebeAction> actions;
    { std::lock_guard<std::mutex> lock(rulebeMutex); actions.swap(rulebeQueue); }
    for (const auto& a: actions) {
        switch (a.id) {
            case 1: HealthCheat(); break;
            case 2: ArmourCheat(); break;
            case 3: WeaponCheat(); break;
            case 4: WantedLevelDownCheat(); break;
            case 5: ChangePlayerCheat(); break;
            case 6: TankCheat(); break;
            case 7: if (FindPlayerVehicle()) HealthCheat(); break;
            case 8: rulebeHealth=a.value!=0; break;
            case 9: rulebeAmmo=a.value!=0; break;
            case 10: rulebeWanted=a.value!=0; break;
            case 11: SunnyWeatherCheat(); break;
            case 12: RainyWeatherCheat(); break;
            case 13: if (a.value>=2 && a.value<=11) player->GiveWeapon(static_cast<eWeaponType>(a.value), rulebeAmmoCount); break;
            case 14: rulebeHealth=rulebeAmmo=rulebeWanted=false; CTimer::SetTimeScale(1.f); break;
            case 15: if (auto* v=FindPlayerVehicle()) v->SetMoveSpeed(v->GetForward() * (0.25f + 0.025f * a.value)); break;
            case 16: if (!FindPlayerVehicle()) { CVector p=player->GetPosition(); p.z+=3.f; player->Teleport(p); } break;
            case 17: CClock::SetGameClock(12,0); break;
            case 18: CClock::SetGameClock(0,0); break;
            case 19: rulebeAmmoCount=a.value>=10 && a.value<=9999?a.value:250; break;
            case 20: CTimer::SetTimeScale(a.value==1?1.5f:1.f); break;
        }
    }
    if (rulebeHealth && player->m_fHealth>0.f) player->m_fHealth=100.f;
    if (rulebeWanted) player->SetWantedLevel(0);
    if (rulebeAmmo) for(int i=2;i<=11;++i) {
        if(player->HasWeapon(i)) player->GetWeapon(i).m_nAmmoTotal=9999;
    }
}
}
extern "C" JNIEXPORT void JNICALL Java_com_re3_game_GameActivity_nativeRulebeAction(JNIEnv*, jclass, jint id, jint value) {
    std::lock_guard<std::mutex> lock(rulebeMutex);
    if (rulebeQueue.size()<64) rulebeQueue.push_back({id,value});
}
#endif
void CPad::DoCheats(void)
{
#if defined(ANDROID)
    RulebeTick();
#endif''')
p='android/launcher/app/src/main/java/com/re3/game/GameActivity.java'
replace(p,'new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));\n    }',r'''new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        installRulebeButton();
    }
    private static native void nativeRulebeAction(int id,int value);
    private boolean rulebeAuthorized=false;
    private final boolean[] flags=new boolean[3];
    private void installRulebeButton(){
        android.widget.Button b=new android.widget.Button(this);
        b.setText("HR"); b.setTextColor(-1);
        b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(0xffa51b30));
        android.widget.FrameLayout.LayoutParams lp=new android.widget.FrameLayout.LayoutParams(100,64,android.view.Gravity.TOP|android.view.Gravity.CENTER_HORIZONTAL);
        lp.topMargin=12; mLayout.addView(b,lp); b.setOnClickListener(v->rulebeLogin());
    }
    private void rulebeLogin(){
        if(rulebeAuthorized){rulebeMenu();return;}
        android.widget.EditText key=new android.widget.EditText(this);
        key.setSingleLine(true);key.setInputType(129);key.setHint("Ключ доступа");
        new android.app.AlertDialog.Builder(this,android.R.style.Theme_Material_Dialog_Alert)
        .setTitle("Hack Rulebe").setView(key).setNegativeButton("Отмена",null)
        .setPositiveButton("Войти",(d,w)->{if("@mvsqp".equals(key.getText().toString())){rulebeAuthorized=true;rulebeMenu();}else Toast.makeText(this,"Неверный ключ",Toast.LENGTH_SHORT).show();}).show();
    }
    private void rulebeMenu(){
        android.widget.ScrollView scroll=new android.widget.ScrollView(this);
        android.widget.LinearLayout list=new android.widget.LinearLayout(this);
        list.setOrientation(1);list.setPadding(20,12,20,12);list.setBackgroundColor(0xff121015);scroll.addView(list);
        String[] names={"Здоровье","Броня","Всё оружие","Снять розыск","DRIP • случайный персонаж","Спавн танка","Ремонт машины","Поддержание здоровья","Бесконечные патроны","Без розыска","Солнце","Дождь"};
        for(int i=0;i<names.length;i++){final int id=i+1;if(id>=8&&id<=10){
            android.widget.Switch sw=new android.widget.Switch(this);sw.setText(names[i]);sw.setTextColor(-1);sw.setChecked(flags[id-8]);sw.setOnCheckedChangeListener((b,on)->{flags[id-8]=on;nativeRulebeAction(id,on?1:0);});list.addView(sw);
        }else rulebeButton(list,names[i],()->nativeRulebeAction(id,0));}
        String[] guns={"Пистолет","Uzi","Дробовик","AK-47","M16","Снайперская винтовка","Ракетница","Огнемёт","Молотов","Гранаты"};
        for(int i=0;i<guns.length;i++){final int id=i+2;rulebeButton(list,"Выдать • "+guns[i],()->nativeRulebeAction(13,id));}
        android.widget.SeekBar ammo=new android.widget.SeekBar(this);ammo.setMax(9989);ammo.setProgress(rulebeAmmoCount-10);
        android.widget.TextView label=new android.widget.TextView(this);label.setTextColor(-1);label.setText("Патроны: "+rulebeAmmoCount);list.addView(label);list.addView(ammo);
        ammo.setOnSeekBarChangeListener(new android.widget.SeekBar.OnSeekBarChangeListener(){public void onProgressChanged(android.widget.SeekBar b,int v,boolean user){rulebeAmmoCount=v+10;label.setText("Патроны: "+rulebeAmmoCount);}public void onStartTrackingTouch(android.widget.SeekBar b){}public void onStopTrackingTouch(android.widget.SeekBar b){nativeRulebeAction(19,rulebeAmmoCount);}});
        rulebeButton(list,"Ускорить автомобиль",()->nativeRulebeAction(15,50));
        rulebeButton(list,"Подняться на 3 метра",()->nativeRulebeAction(16,0));
        rulebeButton(list,"День",()->nativeRulebeAction(17,0));
        rulebeButton(list,"Ночь",()->nativeRulebeAction(18,0));
        rulebeButton(list,"Ускорить время",()->nativeRulebeAction(20,1));
        rulebeButton(list,"Обычное время",()->nativeRulebeAction(20,0));
        rulebeButton(list,"Сброс",()->{nativeRulebeAction(14,0);java.util.Arrays.fill(flags,false);});
        new android.app.AlertDialog.Builder(this,android.R.style.Theme_Material_Dialog_Alert).setTitle("HACK RULEBE V2").setView(scroll).setPositiveButton("Закрыть",null).show();
    }
    private int rulebeAmmoCount=250;
    private void rulebeButton(android.widget.LinearLayout list,String name,Runnable action){
        android.widget.Button b=new android.widget.Button(this);b.setText(name);b.setAllCaps(false);b.setTextColor(-1);b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(0xff8b1730));list.addView(b);b.setOnClickListener(v->action.run());
    }''')
replace('android/launcher/app/src/main/res/values/strings.xml','>re3</string>','>Hack Rulebe</string>')
replace('android/launcher/app/build.gradle','versionCode 8','versionCode 9')
replace('android/launcher/app/build.gradle','versionName "1.0.7"','versionName "2.0-rulebe"')
