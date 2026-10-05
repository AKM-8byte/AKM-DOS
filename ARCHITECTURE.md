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

## 0.7 Core Foundation — mevcut uygulama

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

PySide6 Desktop, BIOS, App/Process/Window/Package servisleri, recovery, bildirim/ses servisleri ve güvenli application sandbox bu commitlerde uygulanmaz.

## Sonraki aşamalar

### 0.7
Core Foundation sonrasında kalan komutları aşamalı ayırmak ve Explorer'ın ortak Core'a bağlanma yöntemini değerlendirmek. Processler arası iletişim gibi büyük kararlar ayrı değerlendirilir.

### 0.8
Program manifest sistemi ve AKM uygulama yöneticisi.

### 0.9
Masaüstü arayüzünü shell ve kullanıcı sistemiyle birleştirmek.

### 1.0
Kararlı shell, kullanıcı sistemi, uygulama altyapısı ve masaüstü ortamını tek yapıda toplamak.

> AKM-DOS şu anda gerçek bir işletim sistemi çekirdeği değildir. Python üzerinde çalışan deneysel bir shell/desktop ortamıdır.
