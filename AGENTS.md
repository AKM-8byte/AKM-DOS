# AGENTS.md — AKM-DOS Single-Agent Instructions

Bu dosya AKM-DOS üzerinde çalışan tek yapay zekâ ajanının kalıcı çalışma kurallarını tanımlar.

Sürüm hedefleri için `ROADMAP.md`, mevcut teknik yapı ve sınırlar için `ARCHITECTURE.md` esas alınır.

## Çalışma modeli
- AKM-DOS için yalnızca tek ajan kullan.
- Alt ajan/sub-agent oluşturma, simüle etme veya görev devretme.
- Proje görevlerini paralel yürütme; bağımlılık sırasına göre tek tek tamamla.
- Architecture, implementation, testing, research, documentation ve review ayrı ajanlar değil, aynı ajanın gerektiğinde geçtiği çalışma aşamalarıdır.
- Bir aşama doğrulanmadan bağımlı sonraki aşamaya geçme.
- Küçük görevlerde gereksiz analiz ve dokümantasyon üretme.

## Çalışmaya başlamadan önce
1. Kullanıcının isteğini belirle.
2. Yalnızca görev için gerekliyse `ROADMAP.md` ve `ARCHITECTURE.md` içindeki ilgili bölümleri oku.
3. Önce ilgili kodu ve testleri incele; tüm repoyu gereksiz yere tarama.
4. Değişikliğin aktif sürüm kapsamına uygunluğunu kontrol et.
5. En küçük güvenli değişikliği uygula.

README, ROADMAP ve ARCHITECTURE çelişirse kodun gerçek durumunu esas al ve önemli ürün/mimari kararı gerekiyorsa kullanıcıya bildir.

## Mimari kurallar
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

- Core ve servisler GUI framework'lerinden mümkün olduğunca bağımsız kalmalıdır.
- Shell ve GUI aynı servis API'lerini kullanabilmelidir.
- Windows'a özgü davranışları platform katmanında tut.
- Yeni global state eklemekten kaçın.
- Mevcut servis uygunsa ikinci bir sistem oluşturma.

## Dosya sistemi
Mantıksal model korunmalıdır:

```text
AKM:/
├── System/
├── Programs/
├── User/
└── Drives/
```

Shell, Explorer ve gelecekteki uygulamalar mümkün olduğunca FileSystem Service üzerinden çalışmalıdır. Yeni kodlarda doğrudan host path erişimini yayma. Korunan alanların sınırlarını kullanıcı açıkça istemeden zayıflatma. Veri kaybı riski taşıyan silme/overwrite işlemlerinde özellikle dikkatli ol.

## Sürüm disiplini
- Aktif sürüm kapsamını `ROADMAP.md` belirler.
- Sonraki sürümün büyük özelliklerini erken ekleme.
- Yol haritası değişirse ROADMAP, mevcut teknik mimari değişirse ARCHITECTURE güncellenir.
- Uygulama kodundaki sürüm değeri ile belgelerin sürümünü uyumlu tut.

## Kod değiştirme
- Değişiklikten önce ilgili implementasyonu oku.
- En küçük güvenli değişikliği tercih et.
- Görevle ilgisiz refactor yapma.
- Kullanıcı istemeden büyük dependency/framework değişikliği yapma.
- Sırf modernleştirmek için çalışan sistemi yeniden yazma.
- Kod okunabilir ve test edilebilir kalsın.

## Test ve doğrulama
- Önemli değişikliklerden sonra önce ilgili testleri çalıştır.
- Gerekliyse ardından daha geniş test paketine geç.
- Çalıştırılmamış testi geçmiş gibi raporlama.
- Başarısızlıkta önce implementasyon, test ve beklenen davranış arasındaki farkı belirle.
- Son kontrolde diff'i ve test kanıtını aynı ajan gözden geçirir.

## Dokümantasyon
Yalnızca gerçekten etkilenen belgeyi güncelle:
- kullanım bilgisi → `README.md`
- sürüm planı → `ROADMAP.md`
- mevcut mimari → `ARCHITECTURE.md`
- kalıcı çalışma kuralları → `AGENTS.md`

Aynı bilgiyi gereksiz yere birden fazla dosyada tekrarlama.

## Token ve bağlam verimliliği
- Her görevde tüm repo veya tüm dokümantasyonu yeniden okuma.
- Önce dosya adı/sembol/arama ile ilgili alanı bul, sonra gerekli bölümü oku.
- Kullanıcının istemediği uzun durum raporları, alternatifler ve tekrarlar üretme.
- Basit görevlerde uzun plan yazma; doğrudan uygula ve doğrula.
- Daha önce doğrulanmış proje bilgisini değişmediyse tekrar araştırma.
- Testlerde önce hedefli testi çalıştır; yalnızca ihtiyaç varsa tam suite çalıştır.
- Büyük dosyalarda mümkünse ilgili fonksiyon/bölümle çalış.
- Görev dışı fikirleri uygulama veya kapsamı kendiliğinden genişletme.
- Sonuç raporunu yapılan değişiklik + test + kalan risk şeklinde kısa tut.

## Kullanıcıya danış
Yalnızca önemli karar gerektiğinde sor:
- büyük mimari yön değişikliği,
- yeni framework/büyük dependency,
- geriye dönük uyumluluğu bozma,
- veri formatı veya dosya sistemi modeli değişikliği,
- güvenlik sınırlarını gevşetme,
- ROADMAP kapsamını değiştirme,
- önemli kullanıcı davranışı değişikliği.

Rutin implementasyon ayrıntılarında gereksiz onay isteme.

## Tamamlama
Görev ancak istenen davranış uygulandığında, ilgili kontroller yapıldığında ve bilinen riskler açıklandığında tamamlanmış sayılır. Gerçekleştirilmemiş çalışma, test veya inceleme uydurulmaz.

Temel ilke: AKM-DOS küçük, anlaşılabilir, modüler ve geliştirilebilir kalmalıdır; sağlam temel yeni özellikten önce gelir.
