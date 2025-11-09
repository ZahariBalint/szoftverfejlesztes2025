# Funkcionális Követelmények – WorkTrack (Munkahelyi Jelenlét Kezelő Rendszer)

## 1. Áttekintés
A **WorkTrack** rendszer fő célja a munkaidő, jelenlét és távollétek automatizált kezelése.  
A rendszer különböző felhasználói szerepkörök számára biztosít funkciókat: munkavállalók, vezetők, HR munkatársak és adminisztrátorok számára.

---

## 2. Felhasználói Szerepkörök és Jogosultságok

| Szerepkör | Leírás | Jogosultságok |
|------------|---------|---------------|
| **Munkavállaló** | Saját jelenlét és szabadság kezelése | Be/kijelentkezés, szabadság igénylés, saját adatok megtekintése |
| **Vezető / Csoportvezető** | Csapatszintű jelenlét és szabadság kezelése | Csapattagok adatai, jóváhagyás, riportok |
| **HR** | Teljes vállalati adatok kezelése | Minden dolgozó adatainak kezelése, riportok, szabályok beállítása |
| **Adminisztrátor** | Rendszer működésének fenntartása | Felhasználók kezelése, jogosultságok, rendszerbeállítások |

---

## 3. Funkcionális Követelmények

### 3.1. Munkaidő-nyilvántartás modul
**Cél:** A dolgozók munkaidejének pontos, digitális rögzítése.

**Követelmények:**
1. A rendszer biztosítson lehetőséget a munkavállalók számára a napi be- és kijelentkezésre.  
2. A bejelentkezés rögzítse a pontos dátumot és időt (másodperc pontossággal).  
3. A rendszer automatikusan számolja a napi és heti munkaidőt.  
4. A munkavállaló utólag kérelmezheti az elfelejtett be- vagy kijelentkezés javítását.  
5. A módosítási kérelmek vezetői jóváhagyást igényelnek.  
6. A HR vagy vezető visszautasíthatja a módosítást indoklással.  

---

### 3.2. Munkavégzési hely modul
**Cél:** A munkavállalók aktuális és jövőbeli munkavégzési helyeinek nyilvántartása.

**Követelmények:**
1. A dolgozó minden napra megadhatja munkavégzési helyét (iroda, home office, ügyféllátogatás stb.).  
2. A rendszer alapértelmezettként az „iroda” helyszínt használja, ha nincs más megadva.  
3. A munkavállaló előre beállíthatja a következő napok/hetek munkavégzési helyét.  
4. A vezetők láthatják a csapattagok helyszíneit naptárnézetben.  
5. A HR részére összesített kimutatás készíthető a home office és irodai napokról.

---

### 3.3. Szabadságkezelő modul
**Cél:** A távollétek és szabadságok teljes körű kezelése.

**Követelmények:**
1. A munkavállaló szabadságot igényelhet, megadva a kezdő és záró dátumot, valamint a szabadság típusát.  
2. A rendszer ellenőrizze, hogy az igényelt napok nem haladják meg a rendelkezésre álló szabadságegyenleget.  
3. A szabadságigény automatikusan továbbításra kerül a közvetlen vezetőhöz jóváhagyásra.  
4. A jóváhagyás vagy elutasítás után a dolgozó értesítést kap.  
5. Többszintű jóváhagyási folyamat támogatható (pl. vezető → HR).  
6. A rendszer figyelmeztesse a vezetőt, ha több csapattag ugyanarra az időszakra kér szabadságot (ütközéskezelés).  
7. A dolgozó bármikor megtekintheti szabadság-egyenlegét.  
8. A HR és vezetők számára elérhető egy naptárnézet a csapat és vállalat szabadságairól.

---

### 3.4. Túlóra-kezelés modul
**Cél:** A túlórák automatikus felismerése és kezelése.

**Követelmények:**
1. A rendszer automatikusan számítsa ki a túlórát, ha a dolgozó napi munkaideje meghaladja az előírt óraszámot.  
2. A túlóra jóváhagyási folyamaton menjen keresztül (vezetői engedélyezés).  
3. A túlórák külön riportban is lekérdezhetők legyenek.  
4. A HR számára exportálható legyen a túlórák adata bérszámfejtéshez.

---

### 3.5. Jelentések és Riportok
**Cél:** Átlátható statisztikák biztosítása.

**Követelmények:**
1. A rendszer biztosítson napi, heti és havi riportokat munkaidőről, szabadságról és túlóráról.  
2. A riportokat lehessen szűrni (dátum, osztály, munkavégzési hely stb.).  
3. A riportok exportálhatók legyenek (PDF, Excel formátumban).  
4. Csak a megfelelő jogosultsággal rendelkező felhasználók férhessenek hozzá a riportokhoz.

---

### 3.6. Felhasználó- és Jogosultságkezelés
**Cél:** Biztonságos hozzáférés és szerepkör-alapú jogosultságok.

**Követelmények:**
1. A rendszer támogatja a felhasználói regisztrációt és belépést (felhasználónév + jelszó).  
2. Az adminisztrátor szerepkör képes legyen új felhasználók létrehozására, módosítására és törlésére.  
3. A felhasználók szerepkörökhöz rendelhetők (Employee, Leader, HR, Admin).  
4. A rendszer naplózza a fontos műveleteket (audit log).
