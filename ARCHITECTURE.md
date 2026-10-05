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

## Sonraki aşamalar

### 0.7
Komutları ayrı modüllere ayırmak ve JSON tabanlı ayar sistemi eklemek.

### 0.8
Program manifest sistemi ve AKM uygulama yöneticisi.

### 0.9
Masaüstü arayüzünü shell ve kullanıcı sistemiyle birleştirmek.

### 1.0
Kararlı shell, kullanıcı sistemi, uygulama altyapısı ve masaüstü ortamını tek yapıda toplamak.

> AKM-DOS şu anda gerçek bir işletim sistemi çekirdeği değildir. Python üzerinde çalışan deneysel bir shell/desktop ortamıdır.
