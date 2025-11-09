# Vízió Dokumentum
## Munkahelyi Jelenlét Kezelő Rendszer (WorkTrack)

### 1. Bevezetés

#### 1.1 Célkitűzés
A WorkTrack egy átfogó munkahelyi jelenlét és munkaidő kezelő rendszer, amely lehetővé teszi a vállalatok számára a dolgozók munkaidejének hatékony nyomon követését, a jelenléti adatok pontos rögzítését, valamint a munkavállalók szabadságainak és munkavégzési helyeinek egyszerű kezelését. A rendszer célja, hogy automatizálja és digitalizálja a jelenleg manuális folyamatokat, csökkentse az adminisztratív terhet, és átlátható, valós idejű betekintést nyújtson mind a dolgozók, mind a vezetők számára.

#### 1.2 Hatókör
A rendszer lefedi a dolgozók napi munkaidő-nyilvántartását, a távmunka és szabadságok kezelését, a túlórák rögzítését, valamint részletes riportolási és statisztikai funkciókat biztosít a HR és vezetői szint számára.

---

### 2. Érintettek és Felhasználók

#### 2.1 Elsődleges Felhasználók
- **Munkavállalók**: Napi be- és kijelentkezés, saját munkaidő megtekintése, szabadság igénylés
- **Vezetők/Csoportvezetők**: Csapattagok jelenlétének nyomon követése, szabadságok jóváhagyása
- **HR osztály**: Teljes körű áttekintés, riportok generálása, szabályok konfigurálása
- **Rendszeradminisztrátorok**: Rendszer karbantartás, felhasználók kezelése

#### 2.2 Másodlagos Érintettek
- **Pénzügyi osztály**: Bérszámfejtéshez szükséges adatok exportálása
- **Felsővezetés**: Összesített statisztikák és trendek megtekintése

---

### 3. Termék Áttekintés

#### 3.1 Termék Perspektíva
A WorkTrack egy önálló webalapú alkalmazás lesz, amely böngészőn keresztül és mobil eszközökön is elérhető. A rendszer központi adatbázisban tárolja az összes jelenléti adatot, és REST API-n keresztül integrálható más vállalati rendszerekkel (pl. bérszámfejtő szoftver, ERP rendszerek).

#### 3.2 Termék Funkciók Összefoglalása

##### 3.2.1 Munkaidő Nyilvántartás
- **Automatikus be- és kijelentkezés**: A dolgozók egy kattintással rögzíthetik érkezésüket és távozásukat
- **Pontos időbélyegzők**: Másodperc pontosságú időrögzítés
- **Napi munkaidő számítás**: Automatikus számítás a ledolgozott órákról
- **Munkaidő módosítás**: Elfeledett be/kijelentkezés utólagos javítása (jóváhagyási workflow-val)

##### 3.2.2 Munkavégzés Helyszíne
- **Irodai jelenlét**: Alapértelmezett munkavégzési mód
- **Home office mód**: Dolgozók jelezhetik, ha otthonról dolgoznak
- **Helyszíni munka**: Külső lokációk rögzítése (pl. ügyfélnél végzett munka)
- **Hibrid munkavégzés**: Rugalmas váltás az irodai és távmunka között
- **Helyszín előre tervezés**: Lehetőség a jövőbeli munkavégzési helyszín előzetes beállítására

##### 3.2.3 Szabadság Kezelés
- **Szabadság igénylés**: Dolgozók előre tervezhetik és igényelhetik szabadságaikat
- **Jóváhagyási workflow**: Többszintű jóváhagyási folyamat vezetők számára
- **Szabadság egyenleg**: Valós idejű kimutatás a fennmaradó szabadnapokról
- **Szabadság típusok**: Különböző típusú távollét kezelése (éves szabadság, betegszabadság, fizetés nélküli szabadság, tanulmányi szabadság)
- **Ütköző igények kezelése**: Figyelmeztetés, ha több dolgozó ugyanarra az időszakra kér szabadságot
- **Szabadság naptár**: Csapatszintű áttekintés a szabadságokról

##### 3.2.4 Túlóra Kezelés
- **Automatikus túlóra számítás**: A rendszer automatikusan azonosítja és rögzíti a túló