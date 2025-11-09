# Funkcionális Követelmények – WorkTrack (Munkahelyi Jelenlét Kezelő Rendszer)

## 1. Áttekintés
A **WorkTrack** rendszer fő célja a munkaidő kezelése.

---

## 2. Felhasználói Szerepkörök és Jogosultságok

| Szerepkör | Leírás                                             | Jogosultságok |
|------------|----------------------------------------------------|---------------|
| **Felhasználó** | Saját jelenlét kezelése                            | Be/kijelentkezés, saját adatok megtekintése |
| **Adminisztrátor** | Rendszer adminisztráció és teljes körű adatkezelés | Felhasználók kezelése, jogosultságok, rendszerbeállítások, minden felhasználó adatainak kezelése, jóváhagyások, riportok, szabályok beállítása |

---

## 3. Funkcionális Követelmények

### 3.1. Munkaidő-nyilvántartás modul
**Cél:** A dolgozók munkaidejének, munkavégzési helyének és túlóráinak pontos, digitális rögzítése és kezelése.

**Követelmények:**
1. A rendszer biztosítson lehetőséget a munkavállalók számára a napi be- és kijelentkezésre.
2. A be- és kijelentkezés rögzítse a pontos dátumot és időt (másodperc pontossággal).
3. Kijelentkezéskor a felhasználó megadhatja az aznapi munkavégzési helyét (iroda, home office, stb.).
4. Ha a felhasználó nem ad meg mást, a rendszer alapértelmezettként az "iroda" helyszínt rögzíti.
5. A rendszer a kijelentkezéskor automatikusan számolja a napi és heti munkaidőt.
6. Ha a rendszer a napi munkaidő alapján túlórát észlel, automatikusan túlóra kérelmet indít.
7. A túlóra kérelmek adminisztrátori jóváhagyást igényelnek.
8. A munkavállaló utólag kérelmezheti módosítását a munkaidő-nyilvántartban.
9. A módosítási kérelmek adminisztrátori jóváhagyást igényelnek.
10. Az adminisztrátor indoklással visszautasíthatja a módosítási és túlóra kérelmeket.

---

### 3.2. Jelentések és Riportok
**Cél:** Átlátható statisztikák biztosítása.

**Követelmények:**
1. A rendszer biztosítson napi, heti és havi riportokat munkaidőről és túlóráról.
2. A riportokat lehessen szűrni (dátum, felhasználó, munkavégzési hely stb.).
3. A riportok exportálhatók legyenek (PDF, Excel formátumban).
4. Csak a megfelelő jogosultsággal rendelkező felhasználók férhessenek hozzá a riportokhoz.
5. Kimutatás készíthető a home office és irodai napok arányáról.

---

### 3.3. Felhasználó- és Jogosultságkezelés
**Cél:** Biztonságos hozzáférés és szerepkör-alapú jogosultságok.

**Követelmények:**
1. A rendszer támogatja a felhasználói regisztrációt és belépést (felhasználónév + jelszó).  
2. Az adminisztrátor szerepkör képes legyen új felhasználók létrehozására, módosítására és törlésére.  
3. A felhasználók szerepkörökhöz rendelhetők (User, Admin).  
4. A rendszer naplózza a fontos műveleteket (audit log).
