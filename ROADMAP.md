# AKM-DOS Roadmap

Bu belge AKM-DOS'un planlanan geliştirme yönünü tanımlar. Sürüm kapsamları bilinçli olarak ayrıdır; sonraki sürüm özellikleri mevcut sürüme erken taşınmamalıdır.

## 0.7 Alpha — Core Foundation (mevcut aşama)

Amaç: Shell ve gelecekteki GUI'nin paylaşabileceği modüler, test edilebilir çekirdeği tamamlamak.

- AKMCore ve servis yaşam döngüsü
- Event Service
- Settings Service
- FileSystem Service
- Platform Service ve Windows backend
- `AKM:/` mantıksal dosya sistemi
- Shell komutlarının servis katmanına taşınması
- Unit test kapsamının geliştirilmesi
- Eski özelliklerin yeni mimariyle uyumluluğunun doğrulanması
- Explorer'ın ortak Core/FileSystem yapısına bağlanma yönteminin değerlendirilmesi

0.7 kapsamında PySide6 Desktop, BIOS arayüzü veya yeni uygulama sistemi geliştirilmez.

## 0.8 Alpha — Boot / BIOS / Desktop Foundation

Amaç: Yeni çekirdek üzerinde ilk grafiksel AKM ortamının temelini kurmak.

- Windows 95 esintili fakat özgün AKM açılış deneyimi
- AKM-DOS'a özgü, üçüncü taraf ses kullanmayan kısa startup sound tasarımı
  - Retro BIOS başlangıcı ile sıcak 90'lar synth karakterinin birleşimi
  - Yaklaşık 3–4 saniyelik özgün ses kimliği
  - Proje içinde kaynağı ve sahipliği belgelenmiş bir asset olarak saklanması
  - Legacy `win95.mp3` bağımlılığının kaldırılması/değiştirilmesi
- BIOS benzeri sistem bilgi ekranı
- Boot akışının Core başlangıç durumuyla bağlanması
- PySide6 tabanlı Desktop temelinin oluşturulması
- Core servislerinin GUI tarafından kullanılması
- Başlangıç ve servis hatalarının kullanıcıya anlaşılır biçimde gösterilmesi

GUI, dosya sistemi veya platform işlemlerini doğrudan gerçekleştirmek yerine servis katmanını kullanmalıdır.

## 0.9 Alpha — Window Manager & Explorer

Amaç: Masaüstünü kullanılabilir bir çalışma ortamına dönüştürmek.

- Temel pencere yönetimi
- Masaüstü
- Görev çubuğu
- Yeni Explorer
- Explorer'ın FileSystem Service üzerinden çalışması
- Shell ve Explorer'ın aynı mantıksal `AKM:/` modelini kullanması
- Dosya sistemi değişikliklerinin arayüze yansıtılması

## 0.10 Alpha — Application System

Amaç: AKM-DOS için kontrollü ve genişletilebilir uygulama modelini oluşturmak.

- Uygulama manifest sistemi
- `.akmapp` uygulama modeli
- Uygulama kayıt/keşif mekanizması
- Process/App Service temeli
- Birinci taraf ve üçüncü taraf uygulama ayrımı
- Üçüncü taraf geliştiricilerin AKM uygulamaları oluşturabilmesi
- Uygulama yaşam döngüsü ve hata takibinin temelleri

Üçüncü taraf uygulamalar sistem tarafından açıkça üçüncü taraf olarak tanınmalıdır.

## 1.0 — Integrated Environment

Amaç: Shell, kullanıcı alanı, uygulama altyapısı ve grafiksel masaüstünü tek kararlı yapıda toplamak.

1.0 hedefleri 0.7–0.10 aşamalarının gerçek kullanım ve test sonuçlarına göre kesinleştirilecektir.

## Dosya Sistemi Yönü

AKM-DOS gerçek host dosya sistemini doğrudan kendi kökü olarak kullanmaz. Mantıksal yapı:

```text
AKM:/
├── System/
├── Programs/
├── User/
└── Drives/
    └── C:/  -> gerçek Windows diski
```

Shell, Explorer ve gelecekteki uygulamalar mümkün olduğunca FileSystem Service üzerinden aynı modeli kullanmalıdır.

## Platform Yönü

Proje şu anda Windows-first geliştirilir.

Platforma özgü davranışlar `akm/platform/` katmanında tutulmalıdır. Core ve servis mimarisi gereksiz Windows bağımlılıkları almamalıdır; böylece ileride Linux backend geliştirilmesi mümkün kalır.

## Teknoloji Yönü

- Ana dil: Python
- Yeni grafiksel masaüstü: PySide6
- Core ve servisler GUI framework'lerinden bağımsız kalır
- Mevcut Tkinter/PyQt5 prototipleri aşamalı olarak değerlendirilir; sırf modernleştirmek için toplu yeniden yazım yapılmaz

## Geliştirme İlkesi

Her sürüm kendi kapsamını tamamlamadan sonraki sürümün büyük özelliklerine geçilmemelidir.

Öncelik:

1. Doğruluk ve veri güvenliği
2. Test edilebilirlik
3. Modüler mimari
4. Mevcut davranışın korunması
5. Basitlik
6. Yeni özellikler

AKM-DOS şu aşamada gerçek bir işletim sistemi çekirdeği değildir. Python üzerinde çalışan, kendi servis ve kullanıcı ortamını geliştiren deneysel bir shell/desktop projesidir.
