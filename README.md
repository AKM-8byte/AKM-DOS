# AKM-DOS

AKM-DOS, Python ile geliştirilmiş deneysel ve Windows odaklı bir komut sistemi / mini masaüstü ortamı projesidir.

Proje; terminal tabanlı komut sistemi, basit dosya gezgini ve bazı küçük masaüstü uygulamalarını tek bir yapı altında toplamayı amaçlar.

## Özellikler

- Komut satırı tabanlı ana arayüz
- Basit hesap makinesi
- Windows Aygıt Yöneticisi'ni açabilme
- Sistem komutlarını çalıştırabilme
- Dosya ve program çalıştırabilme
- Konsol rengini değiştirme
- Tkinter tabanlı dosya gezgini
- Basit not defteri
- Dijital saat
- PyQt5 tabanlı web tarayıcısı
- Açılış ekranı ve ses efekti

## Proje Yapısı

```text
AKM-DOS/
├── main.py
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

- Python 3
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
| `cmd` | Sistem komutu çalıştırır |
| `calistir` | Dosya veya program çalıştırır |
| `web` | AKM Browser'ı açar |
| `aka` | AKS Dosya Gezgini'ni açar |
| `renk` | Konsol rengini değiştirir |
| `temizle` | Konsolu temizler |
| `kapat` | Programı kapatır |

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
