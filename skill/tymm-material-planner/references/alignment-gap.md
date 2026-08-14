# Alignment and gap analysis

## İçindekiler

- Program–kitap matrisi
- İki aşamalı gap analizi
- Alignment Contract
- Coverage Matrix
- Yeniden kullanım

## Program–kitap matrisi

Tema ve ünite düzeyindeki program–kitap hizalamaları, Knowledge Resolver aracılığıyla doğrudan doğrulanmış `curriculum_map.json`, `textbook_map.json` ve `textbook_forms_index.json` haritalarından (veya `themes/tema_XX/` dilimlerinden) türetilir. Bütün PDF sıfırdan yeniden modellenmez.

Knowledge Resolver (`scripts/knowledge_resolver.py`), boşluk sorguları (örn. `"Tema 2 TDE4.4 için kitapta ne eksik?"`) geldiğinde exact structured lookup ve hybrid RAG index üzerinden doğrudan `gap_analysis.json` ve `production_manifest.json` kayıtlarını çözer.

Her kayıt mümkün olduğunca şu alanları taşır:

- program item ve locator
- program ifadesi (curriculum_map'ten verbatim)
- 'need_id'
- 'resource_plan_id'
- hedeflenen süreç bileşeni
- textbook section/activity ve locator (textbook_map'ten)
- kitaptaki öğrenci eylemi ve kanıt
- mevcut ölçme aracı ve yapısal türü (textbook_forms_index'ten: 7 yapısal türden biri)
- 'primary_coverage'
- 'need_tags'
- kalan boşluk
- üretim kararı
- öğretmen notu

Temel ilişki:

program beklentisi → instructional need → kitap karşılığı → öğrenci kanıtı → kapsama → kalan boşluk

## İki aşamalı gap analizi

### A. Instructional requirement

Bu hedefin gerçekleşmesi için hangi öğrenme yaşantısı, öğrenci eylemi, kanıt, destek, geri bildirim ve kaynak işlevi gerekir?

### B. Resource gap

Gerekli olanların hangileri ders kitabında yeterli, hangileri kısmi, hangileri yok?

Değerlendirme zinciri:

learning requirement → required instructional resource → textbook coverage → remaining gap → production decision

Kapsama durumları:

- 'COVERED'
- 'PARTIALLY_COVERED'
- 'NOT_COVERED'
- 'NEEDS_ASSESSMENT_SUPPORT'
- 'NEEDS_DIFFERENTIATION'
- 'NEEDS_ENRICHMENT'

İlk üçü ana kapsama durumudur; son üçü aynı hedefe eklenebilen ihtiyaç etiketleridir.

Kitap konuyu anlatıyor fakat öğrencinin beklenen kanıtı üretmesini, süreç bileşenini uygulamasını veya geri bildirim almasını sağlamıyorsa 'COVERED' verme. 'PARTIALLY_COVERED' veya 'NOT_COVERED' kullan.

## Alignment Contract

Üretim öncesi şu zinciri sabitle:

öğrenme çıktısı → süreç bileşeni → instructional need → expected evidence → recommended resource → textbook coverage → gap → production decision

Contract içinde:

- kullanılan program ve input id
- kullanılan kitap ve textbook input id
- program/kitap sürümü, sınıf, tema ve locator'lar
- need id'ler
- resource plan id'ler
- beklenen öğrenci eylemi ve kanıtı
- kitapta mevcut karşılık
- gap ve need tag'leri
- yeni materyalin neden gerekli olduğu
- external source id'ler
- destek, zenginleştirme, erişilebilirlik ve güvenlik
- açık belirsizlikler ve öğretmen doğrulaması

Program veya kitap uyuşmazsa contract 'CONFLICTED' olur. 'VERIFIED' olmadan son materyal üretme.

## Coverage Matrix

Üretim sonrasında şu zinciri göster:

program hedefi → öğretimsel ihtiyaç → önerilen kaynak → ders kitabındaki karşılık → kalan gap → üretilen/reuse edilen materyal → öğrenci kanıtı → ölçme aracı

Her satırda mümkünse:

- program item ve locator
- need id
- resource plan id ve resource type
- textbook locator/evidence
- primary coverage ve remaining gap
- production decision
- generated material id veya reused locator
- assessment instrument
- feedback location
- differentiation/enrichment location

Yalnız kapakta veya hizalama tablosunda yazan öğeyi işlenmiş kabul etme.

## Yeniden kullanım

- Yeterli kitap etkinliğini kopyalama veya yeniden yazma.
- Uygulama desteği eksikse öğretmen rehberi üret.
- Geri bildirim veya kanıt görünür değilse gözlem/ölçme desteği üret.
- Küçük uyarlama yeterliyse 'ADAPT_TEXTBOOK_ACTIVITY' kullan.
- Kitap içeriğini kullanırken sayfa referansını koru.
