# Top-Down Stealth Roguelite Game

Sebuah proyek game aksi penyusupan dari sudut pandang atas (*top-down*) yang memadukan elemen *stealth* taktis dengan mekanik *roguelite*. Game ini dikembangkan menggunakan bahasa pemrograman **Python** dan *library* **Pygame** dengan fokus utama pada penerapan konsep Pemrograman Berbasis Objek (OOP) yang mendalam.

---

## Anggota Kelompok

| Nama Anggota | NIM | Kelas |
| :--- | :--- | :--- |
| Nailah Salsabila Ramadhani Kusnadi | 25051204075 | TI 2025 A |
| Johana Putri Adelia | 25051204053 | TI 2025 A |
| Aisyah Miyuki Anastasya Syafila | 25051204172 | TI 2025 A |

---

## Fitur Utama

* **Procedural Map Generation**
  Tata letak ruangan, dinding, rintangan, dan koridor digenerasikan secara acak setiap kali permainan baru dimulai, memberikan tantangan yang unik di setiap *run*.
* **Dynamic Level & Object Placement**
Tata letak rintangan, musuh, perangkap (trap), terminal, dan item digenerasikan secara dinamis setiap kali permainan baru dimulai, memberikan tantangan yang unik di setiap run.
* **Dynamic AI State Machine**
  Musuh memiliki kecerdasan buatan dinamis yang merespons aksi pemain (melihat atau mendengar langkah kaki) dengan transisi perilaku yang halus.
* **Advanced Vision & Sound System**
   * **Field of View (FOV)**: Perhitungan geometri 2D dan Line of Sight (raycasting) untuk mendeteksi pemain.
   * **Sound Propagation**: Sistem suara yang mendeteksi langkah kaki pemain berdasarkan jarak dan status stealth.
* **Hacking & Inventory System**
  Pemain dapat mengumpulkan item (Medkit, Hack Tool, Cloak) dan meretas terminal keamanan untuk menonaktifkan kamera pengawas untuk menang.
* **Robust Game State Management**
  Sistem menu yang lengkap dan stabil, termasuk Pause Menu (ESC), Win Screen, dan Game Over Screen dengan navigasi penuh untuk Restart, kembali ke Main Menu, atau Quit Game.
* **Refined Collision & UI** 
  Player dapat menginjak perangkap (trap) untuk memicu damage, tetapi tidak dapat menembus perangkap tersebut (anti-clip).
---

## Penjelasan Implementasi OOP

Proyek ini dirancang dengan arsitektur berorientasi objek yang kuat, menerapkan beberapa *Design Pattern* standar industri:

### 1. State Machine Pattern (Kecerdasan Buatan Musuh)
Perilaku musuh diisolasi ke dalam beberapa *class state* terpisah yang diturunkan dari *abstract class* `EnemyState`. Hal ini menghindari percabangan `if-else` yang rumit di kelas utama:
* **`PatrolState`**: Musuh bergerak secara periodik di antara titik-titik rute patroli yang sudah ditentukan.
* **`ChaseState`**: Terpicu saat `VisionSystem` mendeteksi pemain. Kecepatan musuh meningkat dan langsung memburu posisi pemain.
* **`SearchState`**: Terpicu jika musuh kehilangan jejak pemain. Musuh akan menginvestigasi area sekitar titik terakhir pemain terlihat selama beberapa detik sebelum kembali ke mode patroli.
* **`InvestigateState`**: Terpicu oleh `SoundSystem` saat pemain membuat suara di dekatnya.

### 2. Factory Pattern (Manajemen Objek)
Menggunakan class `ObjectFactory` untuk mengotomatisasi pembuatan instansiasi objek di dalam map (seperti `Enemy`, `Item`, `Terminal`, dan `SecurityCamera`). *Factory* ini bertugas mengatur atribut acak objek berdasarkan tingkat kesulitan (*difficulty level*) agar permainan tetap seimbang.

### 3. Inheritance & Polymorphism (Struktur Entitas)
Semua objek bergerak di dalam game diturunkan dari satu *superclass* utama, yaitu `Entity`. 
* Class `Player` dan `Enemy` mewarisi properti dasar seperti koordinat (`x`, `y`), `rect` (untuk sistem *collision* Pygame), serta fungsi `move()`.
* Prinsip *Polymorphism* diterapkan pada method `update()` dan `draw()`, di mana setiap objek anak mendefinisikan ulang cara mereka memperbarui logika dan menampilkan visualnya masing-masing di layar.

### 4. Strategy Pattern (Sistem Deteksi)
Logika deteksi dipisahkan ke dalam class utilitas `VisionSystem` dan `SoundSystem`. Ini memungkinkan sistem deteksi untuk diuji, dimodifikasi, atau digunakan oleh entitas berbeda (seperti `SecurityCamera` dan `Enemy`) tanpa menduplikasi kode.

---

## Cara Menjalankan Project

### Prasyarat
Pastikan Anda sudah menginstal **Python (versi 3.8 atau yang lebih baru)** di komputer Anda.

### Langkah-Langkah Instalasi

1. **Clone Repositori Ini**
   ```bash
   gh repo clone miyuki-cell/stealth
   cd stealth

2. **Buat & aktifkan virtual environtmen (Direkomendasikan)**
   * Windows
     ```bash
     python -m venv venv
     venv\Scripts\activate
   * macOs/Linux
     ```bash
     python3 -m venv venv
     source venv/bin/activate

3. **Instal dependensi**
   ```bash
   `pip install pygame` 
4. **Siapkan Folder Aset (Opsional tapi Disarankan)**
   Buat folder bernama assets di direktori utama proyek, dan tambahkan file audio berikut agar fitur suara berfungsi (game tetap bisa berjalan tanpa file ini, tetapi akan silent):
* assets/lobby.mp3 (Musik menu utama)
* assets/gameover.mp3 (Suara kalah)
* assets/Blip.wav (Suara navigasi UI)
* assets/win.mp3 (Suara menang)

5. **Jalankan Game**
   Eksekusi salah satu perintah di bawah ini sesuai dengan sistem operasi Anda:
   ```bash
   # Untuk Windows / Virtual Environment aktif
   python stealth.py

   # Untuk macOS / Linux (tanpa venv)
   python3 stealth.py

**Kontrol Permainan**
**Tombol**                                                              **Fungsi**
WASD / Arrow Keys                                                      Bergerak
H                                                         Bersembunyi / Muncul (Hide/Unhide)
E                                                  Berinteraksi (Meretas Terminal / Mengambil Item)
ESC                                                        Pause / Resume (Saat bermain)
R                                                              Restart (Saat Game Over)
← / →                                             Navigasi Menu (Saat Win / Game Over / Skin Select)
ENTER / SPACE                                                  Konfirmasi Pilihan Menu
