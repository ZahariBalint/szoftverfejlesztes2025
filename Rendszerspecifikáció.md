# Rendszerkövetelmények

## 1. Rendszer Áttekintése

A WorkTrack egy **webalapú kliens–szerver architektúrájú** alkalmazás, amely böngészőn keresztül érhető el.
A rendszer célja a dolgozók munkaidejének, jelenlétének és szabadságainak kezelése egy központi adatbázison keresztül.
A megvalósítás célja egy **könnyen használható, skálázható és biztonságos** rendszer.

---

## 2. Rendszerarchitektúra

### 2.1 Architektúra modell

3 tier modell

|| Leírás                                                 | Technológiák                                     |
| ---------------------------------- | ------------------------------------------------------ | ------------------------------------------------ |
| **Frontend**  | A felhasználói felület, amely a böngészőben fut        | HTML, CSS, JavaScript, Bootstrap                 |
| **Backend** | Az alkalmazás logikáját és az adatkezelést végzi       | Python (Flask / Django)                          |
| **Database**  | A felhasználói, jelenléti és szabadságadatokat tárolja | PostgreSQL (fejlesztéshez SQLite) |

A frontend és a backend között **REST API** kommunikáció zajlik JSON formátumban.

---

## 3. Használandó Technológiák

| Komponens            | Technológia                            | Indoklás                                               |
| -------------------- | -------------------------------------- | ------------------------------------------------------ |
| Backend              | **Python + Flask**                     | Gyors fejlesztés |
| Adatbázis            | **PostgreSQL**                         | Többfelhasználós környezet  |
| Fejlesztői DB        | **SQLite**                             | Könnyű helyi fejlesztéshez és teszteléshez             |
| Frontend             | **HTML5, CSS3, Bootstrap, JavaScript** | Reszponzív és egyszerű felhasználói felület            |
| Tesztelés            | **pytest / Postman**                   | Backend API-k és modulok tesztelésére                  |
| Telepítés            | **PythonAnywhere / Render / Docker**   | Ráér később eldönteni                  |

---

## 4. Biztonsági és Jogosultsági Követelmények

* HTTPS protokoll alkalmazása az adatátvitelhez
* Jelszavak biztonságos tárolása (bcrypt / SHA256 hash)
* Szerepkör alapú hozzáférés-kezelés (Employee, Leader, HR, Admin)
* Admin audit log minden módosításról
* SQL injection és XSS elleni védelem

---

## 5. Rendszerelemek és Fő Modulok

| Modul                  | Funkció                                  | Fő elemek                          |
| ---------------------- | ---------------------------------------- | ---------------------------------- |
| **Felhasználókezelés** | Regisztráció, belépés, szerepkörök       | Login, JWT token / session kezelés |
| **Munkaidő modul**     | Be és kijelentkezés, időbélyeg rögzítés | Start / Stop gomb, időszámítás     |
| **Szabadság modul**    | Igénylés, jóváhagyás, riport             | HR és vezetői workflow             |
| **Túlóra modul**       | Túlóra számítás és jóváhagyás            | Automatikus időelemzés             |
| **Riport modul**       | PDF / Excel exportálás                   | Admin felület, adatszűrés          |

---

## 6. Kivitelezés Nagyvonalakban

1. **Adatbázis tervezés:**
   Felhasználók, jelenléti adatok, szabadságkérelmek és túlórák tábláinak definiálása.
   Kapcsolatok (foreign key) létrehozása.

2. **Backend fejlesztés:**

   * REST API végpontok létrehozása (Flask Blueprint-ekkel)
   * Authentikáció és jogosultságkezelés
   * Riportgenerálás modul

3. **Frontend fejlesztés:**

   * Reszponzív webfelület HTML + Bootstrap segítségével
   * Formok a bejelentkezéshez és időrögzítéshez
   * AJAX hívások az API felé

4. **Tesztelés:**

   * Egység- és integrációs tesztek
   * Felhasználói tesztelés (mock adatokkal)

5. **Telepítés és dokumentálás:**

   * GitHub-on verziókezelés és release-elés
   * Deployment PythonAnywhere-en vagy Render-en