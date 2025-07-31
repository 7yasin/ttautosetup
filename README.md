# TTGM Otomatik Kurulum #

## 🛠️ Basit Kurulum Talimatları

Bu proje otomatik iso yüklemesi sonrasında kurulum için hazırlanmıştır. Aşağıda iki farklı kurulum yöntemi yer almaktadır:

---

### 🔹 1. Kolay Yöntem (Tavsiye Edilen)

Eğer bilgisayarınızda herhangi bir antivirüs aktif değilse, doğrudan aşağıdaki dosyayı indirip çalıştırabilirsiniz:

👉 [TTAutoSetup.exe indir](https://github.com/7yasin/ttautosetup/releases/download/supportassist/TTAutoSetup.exe)

> Bu dosya her şeyi sizin yerinize yapar. Kurulum sırasında çıkan güvenlik uyarılarını “Çalıştır” diyerek geçebilirsiniz.

---

### 🔹 2. Alternatif Yöntem (Antivirüs engel oluyorsa)

Bazı antivirüs programları otomatik kurulum aracını engelleyebilir. Bu durumda aşağıdaki `.zip` dosyasını indirip içindeki `kurulum.bat` dosyasını çalıştırmalısınız:

👉 [autoSetup.zip indir](https://github.com/7yasin/ttautosetup/releases/download/supportassist/autoSetup.zip)

**İçindekiler:**
- `kurulum.bat` → Python yükler ve kurulumu başlatır.
- `main.py` → Asıl kurulum dosyasıdır (otomatik çalışır).

---

📌 **Not:** Kurulum dosyaları güvenlidir. Ancak bazı antivirüsler tarafından yanlışlıkla uyarı verilebilir.







## ⚙️ Geliştiriciler ve Teknik Kullanıcılar İçin

Bu projede iki ayrı dağıtım yöntemi bulunmaktadır:

---

### 🔸 1. Tek Dosyalı Yürütülebilir (Standalone .exe)

- Dosya: [`TTAutoSetup.exe`](https://github.com/7yasin/ttautosetup/releases/download/supportassist/TTAutoSetup.exe)
- Amaç: Python kurulu olmayan sistemlerde dahi otomasyonun çalışmasını sağlamak.
- Özellik: `main.py` scripti PyInstaller ile derlenmiş; kurulum ve yapılandırma işlemlerini doğrudan başlatır.

**Not:** Çoğu antivirüs henüz bu .exe dosyasını tanımadığı için çalışmasına izin verir. Ancak bazı sistemlerde false positive uyarı verebilir.

---

### 🔸 2. Kaynak Kod ve Batch Tabanlı Kurulum (Fallback Yöntemi)

- Paket: [`autoSetup.zip`](https://github.com/7yasin/ttautosetup/releases/download/supportassist/autoSetup.zip)
- İçerik:
  - `main.py`: Python betiği
  - `kurulum.bat`: Python yükleyicisi ve script çalıştırıcısı
- Özellik: Eğer .exe engellenirse bu alternatif yol ile Windows'ta otomatik Python kurulumu yapılır ve ardından `main.py` çalıştırılır.

---

### Ek Bilgi

- `kurulum.bat`, Windows üzerinde Python olup olmadığını denetler.
- Gerekirse Microsoft Store veya doğrudan installer üzerinden Python kurar.
- Script sonrasında sistem yapılandırması için gerekli ayarları otomatik uygular.

---

**Güvenlik Notu:** Kaynak dosyalar açık olarak sağlanmaktadır. Dilerseniz `main.py` içeriğini gözden geçirip kendi sisteminizde derleme yapabilirsiniz.

