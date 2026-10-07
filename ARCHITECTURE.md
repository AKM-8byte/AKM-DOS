# AKM-DOS Architecture

AKM-DOS 0.6 ile proje, tek bir recursive komut fonksiyonundan genişletilebilir bir shell mimarisine taşınmaya başlandı.

## 0.6 hedefleri

- Döngü tabanlı shell
- Komut yönlendirme tablosu
- Kullanıcıya özel home klasörü
- Desktop / Documents / Downloads / Settings klasörleri
- Temel dosya sistemi komutları
- Mevcut AKM uygulamalarını shell üzerinden başlatma
- Merkezi hata kaydı

## 0.7 Core Foundation — korunan temel

```text
main.py — AKMShell: mevcut döngü, komut tablosu, prompt
    │
    ├── akm/shell/commands/filesystem.py — dosya komutlarının sunumu
    │        └── FileSystem Service
    └── AKMCore
         ├── Event Service
         ├── Settings Service
         ├── FileSystem Service
         └── Platform Service → Windows Backend
```

`AKMCore` servislerin tek kurulum noktasıdır. Servisler Qt/Tkinter veya Shell'e bağımlı değildir. Gelecekteki GUI aynı API'leri kullanabilir; yeni servisler gerekli olduklarında eklenir.

`AKMShell(core=shared_core)` aynı Core'u yeniden başlatmadan kullanabilir. Birden fazla Shell istemcisi ortak servisleri paylaşırken kendi çalışma konumunu tutar; gelecekte normal Terminal ve hızlı Console aynı motoru kullanabilir.

### Başlangıç

`AKMCore(root)` Event Service'i oluşturur, JSON ayarlarını yükler ve Platform Service'i seçer. `start(username)` diskleri keşfeder, mevcut kullanıcı alanını hazırlar ve seçilen adı kaydeder. Tekrar başarılı `start()` çağrısı reddedilir; başarısız başlangıç sonrasında açıkça yeniden denenebilir.

`service_status` gerçek `ready`, `not_started`, `failed` sonuçlarını içerir. `core.started` ancak bütün başlangıç işlemleri başarılıysa yayınlanır; başarısız servisin adı `core.start_failed` içinde bulunur. BIOS/boot animasyonu ve otomatik recovery bu aşamada uygulanmaz.

### Olaylar

`subscribe(topic, listener)` idempotent bir abonelik iptal fonksiyonu döndürür; `unsubscribe(topic, listener)` aynı listener'ın o topic üzerindeki kayıtlarını kaldırır. `emit(topic, **payload)` sıralı bir listener snapshot'ını senkron çalıştırır. Listener hata verirse kalanlar çalışır ve hatalar tuple olarak çağırana döner. Listener hataları otomatik recovery veya merkezi crash yönetimi değildir.

Olaylar `Event(topic, payload)` taşır. Payload anahtarları salt okunurdur; içteki mutable değerler observer tarafından değiştirilmemelidir. İşlem sırasındaki abonelik değişiklikleri sonraki yayında geçerlidir. Bus thread-safe değildir ve processler arasında iletişim kurmaz.

Başarılı `mkdir`, `touch`, `delete` işlemleri `filesystem.changed` (`operation`, fiziksel `path`) yayınlar. Başarısız işlemler yayınlamaz. Ayarlar disk kaydı tamamlandıktan sonra `settings.changed` (`key`, `value`) yayınlar.

### Ayarlar ve single user geçişi

`SettingsService` flat string anahtarlarla JSON değerleri saklar. `get()` ve `all()` kopya döndürür. Yazma aynı dizindeki geçici dosyaya yapılır; `os.replace()` başarılı olmadan bellek/olay durumu değiştirilmez. Bozuk veri korunarak `SettingsError` raporlanır. Birden fazla process'in aynı JSON dosyasına eşzamanlı yazması desteklenmez.

Single user seçimi eski kullanıcı dosyası → kaydedilmiş `user.name` → tek 0.6 profil → kullanıcı girdisi sırasındadır. `Users/<ad>/Desktop`, `Documents`, `Downloads`, `Settings` ve eski `profile.txt` korunur. Veri göçü, kullanıcı yönetimi veya registry sistemi eklenmez. Küçük ayarlar `Data/settings.json` içindedir; SQLite henüz gerekli değildir.

### Dosya sistemi sınırı

`AKM:/` sentetik kökü System, Programs, User ve Drives mount'larını listeler. User mevcut `Users/<ad>`, Programs mevcut `Programs/`, System `Data/System/` ile eşlenir. Windows diskleri backend tarafından keşfedilir. Çalışma konumu fiziksel `Path` olarak korunur; servis bunu mantıksal mount'a çevirerek relative gezinmeyi çözer.

Shell dosya komutları yalnızca servis API'sini kullanır. User ve Programs alanlarına yazılabilir; System ve mount kökleri korunur, dış host alanları/disk köprüleri salt okunur. Yollar normalize edilir ve mevcut symlink/junction yönlendirmelerinin mount dışına yazması engellenir. Bu kontroller OS sandbox değildir; eşzamanlı bir host işleminin dosya sistemini değiştirmesine karşı güvenli sandbox garantisi verilmez.

### Platform ve teşhis

`PlatformBackend` sınırı konsol temizleme/rengi, Aygıt Yöneticisi ve disk keşfini kapsar. Windows kodları `akm/platform/windows.py` içindedir. Renk girdisi 1–2 hexadecimal karakter ile sınırlandırılır. Device Manager shell açmadan `mmc.exe devmgmt.msc` ile başlatılır.

Platform Service standart runtime bilgilerini verir ve mevcut AKM Python uygulamalarını aynı interpreter ile başlatır. Bu bir Process/App Service değildir; uygulama lifecycle veya crash takibi yapmaz. Windows dışındaki sistemlerde backend bulunmaz; bilgi API'si kullanılabilir fakat platform işlemleri açık hata verir. Linux backend uygulanmamıştır.

Core teşhisleri `Data/logs/shell.log` içinde timestamp/traceback ile eklenir. Log yazımı başarısız olursa Shell hatayı bildirir ve komut döngüsüne devam eder. Eski crash ekranı bağımsız bir prototip olarak korunmuştur.

### Henüz bağlanmayan parçalar

`aka.py` ve `Programs/*` değiştirilmemiştir. Explorer ayrı process'te ve kendi dosya API'leriyle çalışır. Ortak GUI Core kullanımı ve `filesystem.changed` ile otomatik yenileme sonraki bir entegrasyon aşamasıdır; mevcut Event Service bunu tek başına sağlamaz.

App/Process/Window/Package servisleri, otomatik recovery, genel bildirim/ses servisleri ve güvenli application sandbox uygulanmaz.

## 0.8 Boot / BIOS / Desktop — mevcut uygulama

`baslangıç.py` PySide6 giriş noktasıdır; Turtle veya `win95.mp3` çalıştırmaz.
Shell bağımsız olarak `main.py` üzerinden kullanılabilir. Ortak sürüm kaynağı
`akm/version.py` dosyasıdır.

Qt bağımsız `akm/gui/boot.py` içindeki `BootSession.prepare()` Core'u kurar ve
Shell ile aynı legacy/kayıtlı/tek profil önceliğiyle kullanıcıyı belirler.
POST aşamasında henüz kullanıcı alanı hazırlanmaz; FileSystem `not_started`
kalır. `login()` aynı Core'un `start(username)` metodunu çağırır. Parola veya
yeni kullanıcı yönetim sistemi eklenmez. `start()` tam başlangıç için korunur.
Bozuk ayarlar sıfırlanmaz; hatalar ve gerçek servis durumları sunulur.

`akm/gui/app.py` akışı BIOS → Login → Desktop şeklindedir. Kurulum ve login
işleri ayrı zamanlarda tek `BootWorker` içinde çalışır; GUI worker tamamlanana
kadar Core/Event Service'e erişmez. Aralarda ve Desktop'ta Core'un tek sahibi
GUI thread'idir. Event Service thread-safe hale getirilmemiştir. Başlangıç
sürerken pencere kapatma ertelenir; thread zorla sonlandırılmaz.

`akm/gui/screens.py`, Figma `dwDgZF6gxfy0oeygvC4xlm` dosyasındaki BIOS (`2:2`)
ve Boot/Login (`2:10`) görünümünü Qt widget'larıyla uygular. 1280×800 referans
sayfaları oran korunarak ölçeklenir; login siluetleri `assets/redesign/` içindeki
orijinal SVG'lerdir. BIOS sahte bellek/aygıt testleri yayınlamaz. Başarılı login
sonrasında özgün ses başlatılır; yaklaşık dört saniye içinde veya login
düğmesine tekrar basarak Desktop açılır. Hata durumunda Desktop açılmaz.
`akm/gui/sound.py` boot'a ait `QSoundEffect` adaptörüdür; ses hatası sessiz devam
etmeye izin verir ve uyarı gösterir. Asset/kaynak `assets/audio/` ve
`tools/generate_startup_sound.py` içindedir.

`akm/gui/desktop.py`, AKM Desktop (`2:34`) görünümünü native QWidget workspace,
kısayollar ve görev çubuğuyla kurar. `windows.py` içindeki Core'dan bağımsız
`WindowManager`/`BaseWindow`, sürükleme, masaüstü sınırları, öne alma, kapatma,
küçültme, restore ve maximize/restore davranışını ortaklaştırır. Pencereler
workspace'in çocuk widget'larıdır; görev çubuğu pencere sınırının dışındadır.
Her uygulama için tek pencere yeniden kullanılır; kapatma pencereyi kaldırır,
kısayol tekrar oluşturur. Küçültme içerik ve konumu korur. Bu bir Core
Window/Process/App Service veya uygulama manifest sistemi değildir.

`terminal.py` mevcut `AKMShell(core=shared_core)` örneğini kullanır; etkileşimsiz
Shell handler'larını yeniden yazmadan çağırır. Shell çalışma konumu pencere
kapatılıp açıldığında korunur. `status` GUI adaptöründe gerçek Core durumlarını
gösterir. Dosya işlemleri mevcut FileSystem Service sınırlarına tabidir.
System ve Settings de ortak pencere bileşenini kullanır. Yeni Explorer/Notes
uygulaması eklenmez; eski uygulamalar Shell üzerinden erişilebilir.
Backend CPU/RAM/disk ölçümü sağlamadığından bu değerler üretilmez.

`display.py` Settings Service'in `gui.display_mode` değerini (`fullscreen` /
`window`) kullanır. İlk seçim Settings yazımı başarılı olduktan sonra Qt'nin
`showFullScreen()` / `showNormal()` metoduyla uygulanır. Yok/geçersiz ayar ilk
seçim sorusunu tekrar gerektirir; geçerli ayar sonraki POST'ta otomatik uygulanır.
`settings_view.py` aynı politikayla ayarın sonradan değiştirilmesini sağlar.
Core ve Settings Service'in veri formatı veya erişim sınırları değiştirilmez.

IBM Plex Mono/Inter bulunmazsa Consolas/Segoe UI kullanılır. Eski Horizon
SVG'leri korunmuştur; yeni görünümde kullanılmaz.

## Gelecek geliştirme aşamaları

Bu belge AKM-DOS'un mevcut teknik mimarisini ve mimari sınırlarını açıklar.

Gelecek sürümlerin hedefleri, geliştirme sırası ve sürüm kapsamları için tek kaynak `ROADMAP.md` dosyasıdır. Mimari kararlar uygulanıp sistemin mevcut yapısını değiştirdiğinde bu belge güncellenir.

> AKM-DOS şu anda gerçek bir işletim sistemi çekirdeği değildir. Python üzerinde çalışan deneysel bir shell/desktop ortamıdır.
