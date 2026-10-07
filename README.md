# AKM-DOS

AKM-DOS, Python ile geliştirilmiş deneysel ve Windows odaklı bir komut sistemi / mini masaüstü ortamı projesidir.

Proje; terminal tabanlı komut sistemi, basit dosya gezgini ve bazı küçük masaüstü uygulamalarını tek bir yapı altında toplamayı amaçlar.

Bu çalışma kopyası **0.8 Alpha — Boot / BIOS / Desktop Foundation** aşamasındadır.
Ortak Core üzerinde geleneksel BIOS/POST, yerel Boot/Login ve Figma AKM Desktop
görünümünde PySide6 arayüzü bulunur. Shell ve eski bağımsız uygulamalar korunur.

## Özellikler

- Komut satırı tabanlı ana arayüz
- Basit hesap makinesi
- Windows Aygıt Yöneticisi'ni açabilme
- Shell üzerinden mevcut AKM Python uygulamalarını başlatabilme
- Kullanıcı dosyalarını listeleme, oluşturma, okuma ve silme
- Konsol rengini değiştirme
- Tkinter tabanlı dosya gezgini
- Basit not defteri
- Dijital saat
- PyQt5 tabanlı web tarayıcısı
- Açılış ekranı ve ses efekti
- GUI'den bağımsız `AKMCore`, Event, Settings, FileSystem ve Platform servisleri
- Atomik JSON ayar kaydı ve kullanıcı adının sonraki açılışta hatırlanması
- `AKM:/` mantıksal dosya yolları ve korunan System alanı
- Core durumuna bağlı boot, hata gösterimi ve açık yeniden deneme
- Figma AKM Desktop görünümünde görev çubuğu ve taşınabilir Terminal/System/Settings pencereleri
- İlk açılışta kalıcı tam ekran veya pencere modu seçimi
- Özgün, kaynağı belgelenmiş 3,6 saniyelik başlangıç sesi

`cmd` ve `calistir` komutları 0.6 Shell branch'inde kaldırılmıştır; 0.7 bunları yeniden eklemez. Mevcut Explorer, Browser ve Notepad başlatıcıları korunur.

## Proje Yapısı

```text
AKM-DOS/
├── main.py
├── akm/
│   ├── core.py
│   ├── gui/                 # Boot, BIOS, Desktop ve ses adaptörü
│   ├── version.py
│   ├── services/
│   │   ├── events.py
│   │   ├── settings.py
│   │   ├── filesystem.py
│   │   └── platform.py
│   ├── platform/windows.py
│   └── shell/commands/filesystem.py
├── tests/
├── ARCHITECTURE.md
├── baslangıç.py
├── aka.py
├── mvekr.py
├── assets/                  # Özgün ses ve Figma SVG'leri
├── tools/                   # Ses üretimi ve görsel önizleme
├── hatakyt.txt
├── Programs/
│   ├── calculator.py
│   ├── clock.py
│   ├── notepad.py
│   └── webbrowser.py
└── requirements.txt
```

## Gereksinimler

- Python 3.10 veya üzeri (geliştirme testleri Python 3.12 ile çalıştırıldı)
- Windows
- `pip`

Proje Windows'a özel bazı özellikler kullanır:

- `os.startfile()`
- `cls`
- `color`
- `devmgmt.msc`
- Windows DPI API'leri

Bu nedenle Linux ve macOS üzerinde doğrudan çalışması beklenmez.

## Kurulum

Depoyu klonlayın:

```bash
git clone https://github.com/AKM-8byte/AKM-DOS.git
cd AKM-DOS
```

Gerekli Python paketlerini kurun:

```bash
pip install -r requirements.txt
```

`requirements.txt` eski bağımsız uygulamaların paketlerini içerir. **Shell ve
Core yalnızca Python standart kütüphanesini kullanır.** Yeni 0.8 GUI için:

```bash
pip install -r requirements-gui.txt
```

Bu çalışma ortamında PySide6 proje içindeki `.venv` içine kurulmuştur.
Eski Tkinter/PyQt5 uygulamaları değiştirilmemiştir.

## Çalıştırma

Açılış ekranıyla başlatmak için:

```bash
python "baslangıç.py"
```

Yerel `.venv` kullanıyorsanız Windows PowerShell'de:

```powershell
.\.venv\Scripts\python.exe "baslangıç.py"
```

BIOS/POST otomatik başlar; gerçek platform/servis durumlarını gösterdikten
sonra Boot/Login ekranına geçer. FileSystem, kullanıcı oturumu açılana kadar
`NOT_STARTED` gösterilir. Kayıtlı/legacy kullanıcı varsa o profil korunur;
ilk açılışta kullanıcı adı girilir. Mevcut tek kullanıcı sistemi parola
doğrulamadığından dekoratif bir parola alanı gösterilmez.

İlk açılışta "AKM DOS'u tam ekran çalıştırmak ister misiniz?" sorusundan
"Tam Ekran" veya "Pencere Modu" seçin. Tercih `gui.display_mode` anahtarıyla
Settings Service üzerinden atomik olarak saklanır. Sonraki açılışlarda
otomatik uygulanır; `Tam Ekran` gerçek Qt fullscreen kullanır. Tercih sıfırlanınca
soru tekrar gösterilir. AKM menüsü → Settings / Display üzerinden daha sonra
mod değiştirilebilir. Yazma hatasında eski ayar ve ekran modu korunur.

`ENTER SYSTEM` kullanıcı oturumunu/FileSystem'i başlatır; özgün sesle Desktop'a
geçilir. Hata durumunda ayarlar korunur ve yeniden deneme sunulur. Ses hatası
sessiz devam etmeye izin verir.

Terminal, System ve Settings aynı masaüstü içinde ayrı pencerelerdir. Başlık
çubuğundan sürükleyin; `_` küçültür, görev çubuğundaki uygulama restore eder,
`□` maximize/restore yapar, `×` yalnızca ilgili pencereyi kapatır. Pencereye
tıklamak onu öne getirir. Terminal kapatıldıktan sonra masaüstü kısayoluyla
yeniden açılabilir; aynı Core ve Shell çalışma konumu korunur.

Terminal'e komut yazıp Enter'a basın; `yardım` mevcut GUI komutlarını,
`status` gerçek servis durumlarını gösterir. `/` + Enter AKM menüsünü açar;
menü araması uygulamaları filtreler. Çıkış komutu AKM-DOS'u kapatır.
Yeni Explorer 0.9, uygulama sistemi 0.10 kapsamındadır. Files/Notes Desktop
pencereleri eklenmedi; mevcut uygulamalar Shell'den erişilebilir.
CPU/RAM/disk ölçümleri uydurulmaz. IBM Plex Mono/Inter kurulu değilse
Consolas/Segoe UI kullanılır.

Sesin kaynak/lisans bilgisi: [assets/audio/README.md](assets/audio/README.md).

Doğrudan komut sistemini başlatmak için:

```bash
python main.py
```

Dosya gezginini doğrudan açmak için:

```bash
python aka.py
```

## Ana Komutlardan Bazıları

| Komut | Açıklama |
|---|---|
| `yardım` | Kullanılabilir komutları gösterir |
| `sürüm` | AKS sürümünü gösterir |
| `hesap` | Basit hesap makinesini açar |
| `aygıtlar` | Windows Aygıt Yöneticisi'ni açar |
| `dir` / `ls` | Klasör içeriğini listeler |
| `cd`, `pwd` | Konumu değiştirir / gösterir |
| `mkdir`, `touch` | Klasör / dosya oluşturur |
| `type` / `cat` | UTF-8 metin dosyasını okur |
| `sil` / `del` | Dosya veya boş klasör siler |
| `systeminfo` | Platform ve Python bilgilerini gösterir |
| `settings` | Ortak JSON ayarlarını gösterir |
| `settings get <anahtar>` | Bir ayarı okur |
| `settings set <anahtar> <değer>` | JSON değerini veya metni kaydeder |
| `web` | AKM Browser'ı açar |
| `aka` | AKS Dosya Gezgini'ni açar |
| `renk` | Konsol rengini değiştirir |
| `temizle` | Konsolu temizler |
| `kapat` | Programı kapatır |

## Dosya yolları ve veri koruma

| Mantıksal yol | Fiziksel karşılık |
|---|---|
| `AKM:/User` | Mevcut `Users/<kullanıcı>` |
| `AKM:/Programs` | Mevcut `Programs/` |
| `AKM:/System` | `Data/System/` — Shell/API üzerinden yazmaya kapalı |
| `AKM:/Drives` | Platform Service'in keşfettiği disklerin mantıksal listesi |
| `AKM:/Drives/C:/` | Gerçek `C:/` diski |

Örnekler:

```text
dir AKM:/
cd AKM:/User/Documents
mkdir "My Games"
touch "My Games/readme.txt"
settings set theme classic
settings get theme
```

İlk FileSystem sürümünde yazma/silme işlemleri User ve Programs alanlarıyla sınırlıdır. Bu alanların dışındaki gerçek yollar ve disk köprüleri salt okunur; System alanı ve mount kökleri korunur. Bu, 0.6'nın sınırsız gerçek-yol yazma davranışına göre bilinçli bir değişikliktir. Kontrollü gerçek-disk yazma izinleri henüz uygulanmamıştır.

Kullanıcı adı sırasıyla eski `Kullanıcı/kullanıcı_ad.txt`, `Data/settings.json` içindeki `user.name`, ardından tek mevcut 0.6 `profile.txt` üzerinden alınır. Birden fazla eski profil varsa otomatik seçim yapılmaz; isim sorulur, klasörler korunur. Dosyalar taşınmaz veya silinmez; yeni bir multi-user sistemi oluşturulmaz.

Ayarlar `Data/settings.json`, yeni Shell hata kayıtları zaman/traceback ile `Data/logs/shell.log` içinde saklanır. Bozuk JSON otomatik sıfırlanmaz; açık bir başlangıç hatası gösterilir. Eski `hatakyt.txt` ve onu okuyan `mvekr.py` korunmuştur. `Data/`, `Users/` ve `Kullanıcı/` kişisel çalışma verileri Git'e dahil edilmez.

`settings set theme classic` yalnızca ayar kaydeder; henüz GUI teması değiştirmez. `user.name` aktif oturumda Shell üzerinden değiştirilemez.

## Testler

```bash
python -m unittest discover -s tests -v
```

GUI testleri için aynı komutu PySide6 kurulu interpreter ile çalıştırın:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/render_gui_preview.py
```

PySide6 yoksa yalnızca Qt entegrasyon testleri atlanır; Core/Shell ve boot
modeli testleri çalışır. Görsel önizlemeler geçici kullanıcı verileriyle,
ses çalmadan `artifacts/0.8-redesign/` altında üretilir.

Testler geçici klasörlerde çalışır; gerçek kullanıcı dosyaları değiştirilmez.
Qt testleri BIOS/login akışını, ekran ayarı kalıcılığını, pencere sürükleme,
kapatma, küçültme, restore ve öne alma davranışlarını doğrular.
Uygulama başlatma, konsol rengi ve Aygıt Yöneticisi çağrıları mock ile doğrulanır.
Windows path redirection kontrolleri symlink ya da junction kullanır;
ortam her ikisini de engellerse ilgili testler açıkça atlanır.

## Core Foundation sınırları

Event Service senkron ve aynı process içindedir; hatalı bir listener diğer listener'ları veya tamamlanmış dosya işlemini durdurmaz. Eski Explorer ayrı process olarak çalışır ve henüz Core'a bağlanmamıştır. Bu nedenle Shell değişikliklerinin Explorer'da otomatik yenilenmesi henüz yoktur.

FileSystem erişim sınırı güvenli bir Python sandbox değildir. Eski GUI uygulamaları doğrudan host API'lerini kullanmaya devam eder. Process/App/Window/Package servisleri, recovery ve Linux backend sonraki aşamalardır. Yeni Desktop yalnızca ortak servisleri kullanır.

## Kullanılan Teknolojiler

- Python
- Tkinter
- PyQt5
- PyQtWebEngine
- PyAutoGUI
- PySide6 (0.8 GUI)

## Proje Durumu

Proje deneysel / geliştirme aşamasındadır. Kod tabanında eski prototiplerden kalan bölümler ve geliştirmeye açık alanlar bulunabilir.

## Geliştirme Fikirleri

- Komut sistemini modüler hale getirmek
- Komut geçmişi eklemek
- Kullanıcı ayarlarını JSON veya SQLite ile saklamak
- Dosya gezginini geliştirmek
- Hata yönetimini iyileştirmek
- Linux desteği için platform bağımsız bir yapı oluşturmak

## Lisans

AKM-DOS, **GNU General Public License v3.0 or later (GPL-3.0-or-later)** altında lisanslanmıştır.

Copyright (C) 2026 Ahmet Kayra

Ayrıntılar için `LICENSE` dosyasına bakın.
