# AGENTS.md — AKM-DOS Agent Instructions

Bu dosya, AKM-DOS üzerinde çalışan ana yapay zekâ ajanının ve kullanabildiği alt ajanların kalıcı çalışma kurallarını tanımlar.

Bu talimatlar belirli bir sürüme bağlı değildir. Sürüm hedefleri için `ROADMAP.md`, mevcut teknik yapı ve sınırlar için `ARCHITECTURE.md` esas alınmalıdır.

## 1. Çalışmaya başlamadan önce

Her görevde önce:

1. Kullanıcının isteğini netleştir.
2. `ROADMAP.md` dosyasını oku ve aktif geliştirme aşamasını belirle.
3. `ARCHITECTURE.md` dosyasını oku ve mevcut mimariyi anla.
4. İlgili mevcut kodu ve testleri incele.
5. Değişikliğin mevcut sürüm kapsamına uygun olup olmadığını kontrol et.

README, ROADMAP ve ARCHITECTURE birbiriyle çelişirse bunu sessizce tahmin ederek çözme. Kodun gerçek durumunu incele ve önemli bir ürün/mimari kararı gerekiyorsa kullanıcıya bildir.

## 2. Ana ajanın görevi

Ana ajan bütün işi doğrudan yapmak zorunda değildir.

Görev doğal olarak bağımsız parçalara ayrılabiliyorsa uygun alt ajanlara görev ver. Ana ajan:

- görevi parçalara ayırır,
- her alt ajana açık ve sınırlı kapsam verir,
- paralel çalışabilecek işleri paralelleştirir,
- sonuçları kontrol eder,
- çakışmaları çözer,
- entegrasyonu yapar,
- test sonuçlarını doğrular,
- nihai değişikliklerin ROADMAP ve ARCHITECTURE ile uyumunu kontrol eder.

Küçük ve tek dosyalık işler için gereksiz alt ajan kullanma.

Alt ajan kullanımı amaç değil, karmaşık işleri daha güvenli ve hızlı çözmek için bir araçtır.

## 3. Alt ajanlara görev verme

Alt ajan görevi mümkün olduğunca şunları içermelidir:

- amaç,
- incelenecek dosyalar/modüller,
- değiştirmesine izin verilen alan,
- değiştirmemesi gereken alan,
- beklenen çıktı,
- çalıştırılması gereken testler,
- varsa mimari kısıtlar.

"Projeyi düzelt" gibi belirsiz görevler verme.

Aynı dosyanın aynı bölümünü birden fazla alt ajana aynı anda değiştirtme. Çakışma ihtimali varsa işleri sıraya koy.

Alt ajanların sonuçlarını kontrol etmeden doğrudan kabul etme.

## 4. Göreve göre uzmanlaşma

Sabit ajan isimleri zorunlu değildir. Göreve göre uygun uzmanlık oluşturulabilir.

Örnek uzmanlıklar:

### Architecture
- modül sınırları,
- bağımlılıklar,
- servis tasarımı,
- büyük refactor kararları.

### Core
- `AKMCore`,
- servis yaşam döngüsü,
- ortak sistem davranışları.

### FileSystem
- `AKM:/` mantıksal dosya sistemi,
- path çözümleme,
- mount sınırları,
- dosya güvenliği.

### Platform
- `akm/platform/`,
- Windows backend,
- platform bağımlılıklarının izolasyonu,
- gelecekteki Linux backend uyumluluğu.

### Shell
- komut routing,
- shell davranışları,
- shell ile servis katmanı arasındaki bağlantı.

### GUI / Desktop
- PySide6 arayüzü,
- Desktop ve pencere katmanı,
- GUI'nin servis API'lerini doğru kullanması.

### Application System
- uygulama manifestleri,
- uygulama keşfi,
- process/app lifecycle,
- birinci/üçüncü taraf uygulama ayrımı.

### Tests
- mevcut testlerin çalıştırılması,
- regression analizi,
- yeni davranışlar için testler,
- hatanın testte mi implementasyonda mı olduğunun belirlenmesi.

Bu roller örnektir. Görev için daha uygun bir uzmanlık gerekiyorsa oluşturulabilir.

## 5. Mimari kurallar

AKM-DOS modüler kalmalıdır.

Genel yön:

```text
Shell / GUI / Applications
          ↓
        Core
          ↓
       Services
          ↓
Platform abstractions
          ↓
Windows backend / future backends
```

Core ve servisler mümkün olduğunca GUI framework'lerinden bağımsız kalmalıdır.

Shell ve GUI aynı servis API'lerini kullanabilmelidir.

Windows'a özgü davranışları genel Core koduna yayma. Platforma özgü kodları uygun platform katmanında tut.

Yeni global state eklemekten kaçın.

Bir özellik için mevcut servis uygunsa yeni paralel sistem oluşturma.

## 6. Dosya sistemi kuralları

AKM-DOS'un mantıksal dosya sistemi modeli korunmalıdır:

```text
AKM:/
├── System/
├── Programs/
├── User/
└── Drives/
```

Shell, Explorer ve gelecekteki uygulamalar mümkün olduğunca FileSystem Service üzerinden çalışmalıdır.

Gerçek host yollarına doğrudan erişimi yeni kodlara yayma.

System ve diğer korunan alanların güvenlik sınırlarını kullanıcı açıkça istemeden zayıflatma.

Dosya silme, taşıma veya overwrite gibi veri kaybı oluşturabilecek değişikliklerde özellikle dikkatli ol.

## 7. Sürüm ve ROADMAP disiplini

Aktif sürümün kapsamı `ROADMAP.md` tarafından belirlenir.

Sonraki sürüme ait büyük bir özelliği "ileride lazım olacak" gerekçesiyle mevcut sürüme ekleme.

Gelecek özellikler için yalnızca mevcut mimariyi gereksiz yere kilitlemeyecek temiz extension point'ler bırak.

Bir sürüm tamamlandığında `AGENTS.md` sıfırdan yazılmaz. Bu dosya kalıcıdır.

Sürüm hedefleri değişirse `ROADMAP.md` güncellenir.

Mimari gerçekten değişirse `ARCHITECTURE.md` güncellenir.

Kalıcı ajan çalışma kuralları değişirse `AGENTS.md` güncellenir.

## 8. Kod değiştirme politikası

Değişiklik yapmadan önce mevcut implementasyonu oku.

Mümkün olan en küçük güvenli değişikliği tercih et.

Görevle ilgisiz kodu refactor etme.

Kullanıcı istemeden büyük framework, dependency veya teknoloji değişikliği yapma.

Sırf kodu "daha modern" yapmak için çalışan sistemi yeniden yazma.

Backward compatibility önemliyse mevcut davranışı koru veya değişikliği açıkça belirt.

Kod okunabilir, test edilebilir ve proje ölçeğine uygun kalmalıdır.

Erken optimizasyon yapma.

## 9. Test politikası

Önemli değişikliklerden sonra ilgili testleri çalıştır.

Önce hedeflenen testleri, ardından mümkünse tüm test paketini çalıştır.

Yeni davranış ekleniyorsa uygun test eklemeyi değerlendir.

Test başarısız olduğunda testi yalnızca yeşile döndürmek için değiştirme.

Önce şunu belirle:

- implementasyon mu yanlış,
- test mi yanlış,
- beklenen davranış bilinçli olarak mı değişti?

Test çalıştırılamıyorsa bunu açıkça belirt ve çalıştırılmış gibi davranma.

## 10. Dokümantasyon

Kod davranışı veya mimari değiştiğinde ilgili dokümantasyonun güncel kalıp kalmadığını kontrol et.

- Kullanıcı/geliştirici kullanım bilgisi → `README.md`
- Sürüm planı → `ROADMAP.md`
- Mevcut teknik mimari → `ARCHITECTURE.md`
- Ajan çalışma kuralları → `AGENTS.md`

Aynı bilgiyi gereksiz yere dört dosyada tekrar etme.

## 11. Kullanıcıya danışılması gereken durumlar

Şunlarda önemli bir karar vermeden önce kullanıcıya danış:

- büyük mimari yön değişikliği,
- yeni framework veya büyük dependency,
- geriye dönük uyumluluğu bozacak değişiklik,
- veri formatı veya dosya sistemi modeli değişikliği,
- güvenlik sınırlarının gevşetilmesi,
- ROADMAP kapsamının değiştirilmesi,
- kullanıcı tarafından görülen önemli davranış değişikliği.

Küçük implementasyon ayrıntılarında gereksiz onay isteme.

## 12. Tamamlama kontrolü

Bir görevi tamamlamadan önce ana ajan şunları kontrol etmelidir:

- İstenen görev gerçekten tamamlandı mı?
- Değişiklik aktif ROADMAP aşamasına uygun mu?
- Mimari sınırlar korundu mu?
- Alt ajan çıktıları gözden geçirildi mi?
- İlgili testler çalıştırıldı mı?
- Regression riski var mı?
- Dokümantasyon güncellemesi gerekiyor mu?
- Gereksiz dosya veya dependency eklendi mi?

Sonuç raporunda yapılan değişiklikleri, test durumunu ve varsa kalan riskleri kısa ve açık şekilde belirt.

## Temel ilke

AKM-DOS küçük, anlaşılabilir, modüler ve geliştirilebilir kalmalıdır.

Yeni özellik eklemekten önce sağlam bir temel tercih edilir.
