# AKM-DOS

AKM-DOS, Python ile geliştirilmiş deneysel ve Windows odaklı bir komut sistemi / mini masaüstü ortamı projesidir.

Proje; terminal tabanlı komut sistemi, basit dosya gezgini ve bazı küçük masaüstü uygulamalarını tek bir yapı altında toplamayı amaçlar.

Bu development branch'i **0.7 Alpha — Core Foundation** aşamasıdır. 0.6 Shell döngüsü ve komutları korunarak ortak servislere taşınmıştır. Yeni Desktop, BIOS veya App Store içermez.

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

`cmd` ve `calistir` komutları 0.6 Shell branch'inde kaldırılmıştır; 0.7 bunları yeniden eklemez. Mevcut Explorer, Browser ve Notepad başlatıcıları korunur.

## Proje Yapısı

```text
AKM-DOS/
├── main.py
├── akm/
│   ├── core.py
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
├── win95.mp3
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

Bu paketler eski GUI/açılış uygulamaları içindir. **0.7 Shell, Core ve unit testleri yalnızca Python standart kütüphanesini kullanır**; GUI paketleri ve internet olmadan çalışabilir. PySide6 Desktop geliştirmesi sonraki aşamadır; mevcut Tkinter/PyQt5 uygulamaları değiştirilmemiştir.

## Çalıştırma

Açılış ekranıyla başlatmak için:

```bash
python "baslangıç.py"
```

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

## 0.7 dosya yolları ve veri koruma

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

Testler geçici klasörlerde çalışır. Uygulama başlatma, konsol rengi ve Aygıt Yöneticisi çağrıları mock ile doğrulanır; GUI veya gerçek host dosyaları değiştirilmez. Windows path redirection kontrolleri symlink ya da junction kullanır; ortam her ikisini de engellerse ilgili testler açıkça atlanır.

## Core Foundation sınırları

Event Service senkron ve aynı process içindedir; hatalı bir listener diğer listener'ları veya tamamlanmış dosya işlemini durdurmaz. Eski Explorer ayrı process olarak çalışır ve henüz Core'a bağlanmamıştır. Bu nedenle Shell değişikliklerinin Explorer'da otomatik yenilenmesi henüz yoktur.

FileSystem erişim sınırı güvenli bir Python sandbox değildir. Eski GUI uygulamaları doğrudan host API'lerini kullanmaya devam eder. Process/App/Window/Package servisleri, recovery, Linux backend ve PySide6 Desktop sonraki aşamalardır.

## Kullanılan Teknolojiler

- Python
- Tkinter
- PyQt5
- PyQtWebEngine
- PyAutoGUI
- Playsound

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

Bu depoda şu anda ayrı bir lisans dosyası bulunmamaktadır.
