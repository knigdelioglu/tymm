#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
COURSE = ROOT / "courses/TDE_11"
SCRIPTS = ROOT / "skill/tymm-material-planner/scripts"
GUIDE = COURSE / "teacher_guide/TEMA_04"
SECTIONS = GUIDE / "sections"
COMMIT_SHA = os.environ["GITHUB_SHA"]
BRANCH = os.environ["GITHUB_REF_NAME"]


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True, text=True)


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def provenance(pages: str, content_class: str = "MIXED", note: str | None = None) -> dict:
    out = {
        "source_ids": ["official_textbook_pdf", "textbook_map"],
        "source_locators": [f"basılı s.{pages} / PDF s.{_pdf_pages(pages)}"],
        "content_class": content_class,
    }
    if note:
        out["note"] = note
    return out


def _pdf_pages(pages: str) -> str:
    if "-" in pages:
        a, b = (int(x) for x in pages.split("-", 1))
        return f"{a + 1}-{b + 1}"
    return str(int(pages) + 1)


def item(
    iid: str,
    pages: str,
    label: str,
    itype: str,
    answer,
    criteria: list[str] | None = None,
    guidance: list[str] | None = None,
    misconceptions: list[str] | None = None,
    evidence: list[str] | None = None,
    support: list[str] | None = None,
    enrichment: list[str] | None = None,
    content_class: str = "MIXED",
    note: str | None = None,
) -> dict:
    return {
        "item_id": iid,
        "printed_page_range": pages,
        "label": label,
        "item_type": itype,
        "expected_answer": answer,
        "acceptance_criteria": criteria or [],
        "teacher_guidance": guidance or [],
        "common_misconceptions": misconceptions or [],
        "assessment_evidence": evidence or [],
        "differentiation": {"support": support or [], "enrichment": enrichment or []},
        "provenance": provenance(pages, content_class, note),
    }


def unit(
    uid: str,
    title: str,
    pages: str,
    purpose: str,
    items: list[dict],
    activity: str | None = None,
    outcome: str | None = None,
    status: str = "VERIFIED",
) -> dict:
    return {
        "unit_id": uid,
        "title": title,
        "printed_page_range": pages,
        "activity_refs": [activity] if activity else [],
        "outcome_refs": [outcome] if outcome else [],
        "content_status": status,
        "purpose": purpose,
        "items": items,
        "provenance": provenance(pages),
    }


def section(
    sid: str,
    title: str,
    stype: str,
    pages: str,
    outcomes: list[str],
    activities: list[str],
    plans: list[str],
    units: list[dict],
    status: str = "VERIFIED",
) -> dict:
    return {
        "schema_version": "1.1.0",
        "document_type": "TYMM_TEACHER_GUIDE_SECTION",
        "course_id": "TDE_11",
        "theme_id": "TEMA_04",
        "section_id": sid,
        "title": title,
        "section_type": stype,
        "printed_page_range": pages,
        "content_status": status,
        "outcome_refs": outcomes,
        "activity_refs": activities,
        "lesson_plan_refs": plans,
        "guide_units": units,
        "section_principles": [
            "Resmî ders kitabı PDF’sindeki görev sırasını ve öğrenciye verilen bağlamı koru.",
            "Açık uçlu soruları tek doğruya indirgeme; metne/kanıta dayalı gerekçeli alternatifleri kabul et.",
            "QR ile dışarı açılan video, rubrik veya görsel içeriğini yerel PDF’de görünmüyorsa uydurma.",
            "Pedagojik öğretmen notlarını resmî kitap yönergesi gibi sunma.",
        ],
        "provenance": provenance(pages),
    }


def plan_refs(block: str, first: int, last: int) -> list[str]:
    return [
        f"courses/TDE_11/generated/lesson_plans/TEMA_04/{block}/{block}_P{i:02d}.json"
        for i in range(first, last + 1)
    ]


# ---------- 00 Tema açılışı ----------
opening_units = [
    unit(
        "T4_GUIDE_U00_TEMA_CERCEVESI",
        "Tema Çerçevesi ve Ana Kavramlar",
        "236-237",
        "Hayat-edebiyat ilişkisi, tiyatro, küçürek hikâye, belgesel, canlandırma ve afiş üretimini ortak tema çerçevesinde görünür kılmak.",
        [
            item(
                "T4_G00_P236_TEMA_CERCEVESI", "236", "Tema kapsamı ve beklenen öğrenmeler", "REFERENCE",
                {"anlama": ["tiyatro / Ben, Mimar Sinan", "küçürek hikâye / Merdiven", "belgesel / Anadolu İnsanı-Fedakârlık"], "anlatma": ["tiyatro bölümünü yeniden kurgulayıp canlandırma", "belgesel içeriğini yansıtan özgün afiş"]},
                ["Temanın hayat-edebiyat ilişkisini ana eksen olarak ifade eder.", "Üç anlama ve iki anlatma odağını ayırt eder."],
                ["Bu çerçeveyi ezber listesi değil, tema boyunca dönülecek yol haritası olarak kullan."],
                evidence=["Öğrencinin tema sonunda bu beş odağın birbirine nasıl bağlandığını açıklayabilmesi."],
                content_class="OFFICIAL_TEXTBOOK",
            ),
            item(
                "T4_G00_P236_KAVRAMLAR", "236", "Anahtar kavramlar", "REFERENCE",
                ["dekor", "diyalog", "dramatik örgü", "gösterme tekniği", "kostüm", "küçürek hikâye", "modern Türk tiyatrosu", "monolog", "oyun", "perde", "sahne"],
                ["Kavramları tema içindeki metin ve görevlerle ilişkilendirir."],
                guidance=["Kavramları tanım ezberi yerine metin üstünde işlevleriyle ele al."],
                content_class="OFFICIAL_TEXTBOOK",
            ),
            item(
                "T4_G00_P237_YUNUS", "237", "Yunus Emre alıntısı — kendini bilme", "QUESTION",
                "İnsanın kendisini tanıması; bilgisini, sınırlarını, değerlerini ve davranışlarını sorgulaması gerçek öğrenmenin temelidir. Tema boyunca metin kişileri ve öğrencinin kendi deneyimleri arasında kurulacak bağ için bir giriş işlevi görür.",
                ["Kendini bilme fikrini öz farkındalıkla ilişkilendirir.", "Alıntıyı tema odağıyla gerekçeli biçimde bağlar."],
                content_class="MIXED",
            ),
        ],
    ),
    unit(
        "T4_GUIDE_U01_TEMAYA_BASLARKEN",
        "Temaya Başlarken — Edebiyat, Hayat ve Okur",
        "238-239",
        "Edebiyatın sosyal gelişim, kalıcılık, sanatsal dönüştürme ve okur yaşantısıyla ilişkisini tartışmaya açmak.",
        [
            item(
                "T4_G00_P238_Q1_2", "238", "Kitap, sosyal gelişim ve ‘ebedî dostluk’", "QUESTION",
                {"1": "Kitaplar farklı insanların deneyim, duygu ve düşünceleriyle karşılaşmayı sağladığı için empatiyi, iletişim dilini ve toplumsal bakış açısını geliştirebilir.", "2": "Kitap, yazarı ve ilk okuru ortadan kalksa bile yeniden okunabildiği; farklı zamanlarda okurla düşünsel/duygusal ilişki kurabildiği için kalıcı bir dost gibi görülebilir."},
                ["Sosyal gelişimi en az bir somut mekanizmayla açıklar.", "Kalıcılık ve yeniden okuma üzerinden ‘ebedî dost’ benzetmesini gerekçelendirir."],
                misconceptions=["Kitap okumanın sosyal gelişimi yalnız kelime hazinesine indirgemek."],
            ),
            item(
                "T4_G00_P239_Q3_5", "239", "Sanatsal metin, yaşantı ve tür seçimi", "QUESTION",
                {"3": ["kurmaca veya estetik düzenleme", "çok anlamlılık/çağrışım", "özgün dil ve üslup", "duygu-düşünceyi dönüştürerek aktarma"], "4": "Okurun yaşadığı bir olay, metindeki duygu, çatışma, kişi veya mekânla benzerlik kurduğunda metnin anlamını kişisel düzeyde derinleştirebilir.", "5": "Tür seçimi serbesttir; kabul için seçilen hayat kesiti ile türün imkânları arasında gerekçeli ilişki kurulmalıdır."},
                ["Sanatsal metni yalnız ‘gerçek dışı’ diye tanımlamaz.", "Kişisel deneyim-metinsel anlam bağını açıklar.", "Tür seçimini gerekçelendirir."],
                enrichment=["Aynı hayat olayının hikâye, tiyatro ve belgeselde nasıl farklı kurulacağını karşılaştırmasını iste."],
            ),
        ],
    ),
]

sec00 = section("T4_GUIDE_SEC_00_TEMA_ACILIS", "Tema Açılışı / Temaya Başlarken", "THEME_OPENING", "236-239", [], [], [], opening_units)

# ---------- 01 Okuma: Ben, Mimar Sinan ----------
read1_units = [
    unit(
        "T4_GUIDE_U02_TIYATRO_YONETIM", "Okumayı Yönetme — Tiyatroya Hazırlık ve Okuma Çemberi", "240-242",
        "Tiyatro metnine ön bilgiyi etkinleştirerek, rol temelli okuma çemberiyle amaçlı okuma hazırlığı yapmak.",
        [
            item(
                "T4_G01_P240_TIYATRO_YAZMA", "240", "Mimar Sinan bağlamından kısa tiyatro metni üretme", "PERFORMANCE_TASK",
                {"beklenen_bilesenler": ["karakter", "durum/çatışma", "diyalog veya monolog", "sahne bağlamı", "tarihî bilgiyi kurmacaya dönüştürme"]},
                ["Tiyatroya özgü en az iki unsur kullanır.", "Verilen bağlamla çelişmeyen kısa bir sahne kurar."],
                guidance=["Öğrenciden ders kitabındaki metni tahmin etmesini değil, tiyatro biçimine dair ön bilgisini görünür kılmasını bekle."],
            ),
            item(
                "T4_G01_P241_OKUMA_CEMBERI", "241", "Okuma çemberi rolleri", "PROCESS",
                ["Bağ Kurucu", "Sorgulayıcı", "Ressam", "Okuma Aydınlatıcısı", "Özetleyici", "Tahmin Edici", "Karakter Çözümleyici", "Kelime Avcısı", "Hareket İzcisi"],
                ["Öğrenci rolünün görevini yerine getirir.", "Rol çıktısını metin kanıtıyla paylaşır."],
                guidance=["Rolleri öğrenci sayısına göre birleştirebilirsin; ancak sorgulama, karakter, söz varlığı ve sahne hareketi boyutlarını koru."],
                content_class="OFFICIAL_TEXTBOOK",
            ),
            item(
                "T4_G01_P242_TAHMIN_STRATEJI", "242", "Metin öncesi tahmin ve okuma stratejisi", "PROCESS",
                "Başlık, görsel, yazar bilgisi ve tiyatro türüne ilişkin ön bilgilerden hareketle gerekçeli tahmin yapılması; okuma sırasında tahminlerin metinle kontrol edilmesi beklenir.",
                ["Tahminini en az bir ön ipucuna dayandırır.", "Okuma sonrasında tahminini doğrular veya revize eder."],
            ),
        ],
        "T4_ACT_01_OKUMA_YONETIM", "TDE2.1",
    ),
    unit(
        "T4_GUIDE_U03_TIYATRO_ANLAM", "Ben, Mimar Sinan — İçerik ve Anlam Oluşturma", "243-250",
        "Tiyatro metninin tarih, emek, estetik, toplumsal hayat ve dil boyutlarından anlam oluşturmak.",
        [
            item(
                "T4_G01_P243_246_METIN_CERCEVESI", "243-246", "Ben, Mimar Sinan — temel anlam çerçevesi", "REFERENCE",
                "Metin Mimar Sinan’ın meslekî gelişimini, bilgi-azim-çalışkanlıkla ilerleyişini, büyük mimari eserlerin oluşumunu ve bireysel ustalığın tarih/kültür/ortak üretim içindeki yerini dramatik bir anlatımla görünür kılar.",
                ["Sinan’ın kişisel emeği ile tarihî/kültürel çevreyi birlikte görür.", "Metni salt biyografi özeti olarak ele almaz; dramatik sunumu fark eder."],
                guidance=["Tarihî ayrıntılarda ders kitabında verilen sınırı aşan kesinlik iddiaları üretme; amaç metnin anlam ve tiyatro işleyişini çözmektir."],
            ),
            item(
                "T4_G01_P247_SOZ_VARLIGI", "247", "Söz varlığı — bağlamdan anlam", "VOCABULARY",
                {"çağdaş": "aynı çağda yaşayan/çağa uygun", "özge": "başka, farklı", "görkemli": "gösterişli ve etkileyici", "şevk": "istek ve coşku", "âvâze": "yüksek ses/sesleniş; bağlama göre ün-seda çağrışımı da taşıyabilir", "sadrazam": "Osmanlı Devleti’nde padişahtan sonra en yetkili devlet görevlisi"},
                ["Anlamı önce bağlamdan tahmin eder.", "Sözlük doğrulamasından sonra bağlama en uygun karşılığı seçer."],
                guidance=["Çok anlamlı kelimelerde tek sözlük karşılığını otomatik doğru sayma; cümle bağlamını esas al."],
                content_class="MIXED",
            ),
            item(
                "T4_G01_P248_TIYATRO_ISLEVI", "248", "Tiyatro sanatının işlevi", "QUESTION",
                ["insanı ve toplumu farklı durumlar içinde görünür kılma", "duygu ve düşünce farkındalığı oluşturma", "eleştirel düşünme ve empati geliştirme", "tarihî/toplumsal tecrübeyi sahnede yeniden yorumlama"],
                ["En az iki işlevi açıklar.", "İşlevi Ben, Mimar Sinan veya kendi tiyatro deneyimiyle örneklendirir."],
            ),
            item(
                "T4_G01_P249_250_HAYAT_SAHNE", "249-250", "Günlük hayat, sahne atmosferi ve toplumsal ilişkiler", "TABLE",
                {"ortakliklar": ["insan ilişkileri", "çatışma", "mekân-zaman", "sözlü/sözsüz iletişim", "değerler"], "tiyatroya_ozgu_donusturme": ["seçilmiş olay", "dramatik örgü", "sahneleme", "ışık-müzik-dekor", "yoğunlaştırılmış diyalog/monolog"]},
                ["Gündelik gerçeklikle dramatik kurgu arasındaki hem benzerliği hem farkı açıklar.", "Metindeki en az bir ifadenin sosyal hayatı nasıl yansıttığını gerekçelendirir."],
                misconceptions=["Tiyatro metnini gerçek hayatın birebir kopyası saymak."],
            ),
        ],
        "T4_ACT_02_OKUMA_ICERIK_ANLAM", "TDE2.2",
    ),
    unit(
        "T4_GUIDE_U04_TIYATRO_ANLAYALIM", "Metni Anlayalım ve Cimri ile Karşılaştırma", "251-254",
        "Metnin konusu, amacı, karakterleri, temel iletileri ve modern tiyatro türleri üzerinden çıkarım yapmak.",
        [
            item(
                "T4_G01_P251_Q1_4", "251", "Konu, amaç, yazar-metin ilişkisi ve karakter özellikleri", "QUESTION",
                {"konu": "Mimar Sinan’ın hayatı ve sanat yolculuğu ekseninde çalışma, üretme, estetik ve tarihî miras.", "amac": "Tarihî bir kişiliği dramatik biçimde tanıtırken emek, sorumluluk, estetik ve kültür bilinci üzerine düşündürmek.", "yazar_metin": "Yazar tarihî malzemeyi seçip sahne düzenine, diyalog/monologlara ve dramatik akışa dönüştürür.", "karakter": ["çalışkan", "azimli", "öğrenmeye açık", "sorumluluk sahibi", "estetik kaygı taşıyan"]},
                ["Konu ile amacı ayırır.", "Karakter çıkarımını söz/eylem kanıtına dayandırır.", "Yazarın tarihî malzemeyi dramatikleştirdiğini fark eder."],
            ),
            item(
                "T4_G01_P252_TALIHI_YENMEK", "252", "‘Bilgim, azmim ve çalışkanlığımla talihimi yenmiştim’ iletisi", "QUESTION",
                "Kişinin koşullarını tamamen kontrol edemese de bilgi edinme, kararlılık ve düzenli emekle seçeneklerini genişletebileceğini; başarının yalnız şansa bağlanmaması gerektiğini vurgular.",
                ["Bilgi, azim ve çalışkanlığı birlikte yorumlar.", "Sözü kaderi mutlak biçimde kontrol etme iddiasına dönüştürmez."],
            ),
            item(
                "T4_G01_P253_254_CIMRI_KARSILASTIRMA", "253-254", "Ben, Mimar Sinan — Cimri karşılaştırması ve tür", "TABLE",
                {"Ben_Mimar_Sinan": {"icerik": "tarihî kişilik, üretim ve kültürel miras", "donem_zihniyet": "Cumhuriyet dönemi modern Türk tiyatrosunun tarih/kültür bilinci", "uslup": "ciddi, dramatik, tarihî malzemeyi sahneleyen", "tur": "dram"}, "Cimri": {"icerik": "aile/evlilik/para ilişkileri ve cimrilik", "donem_zihniyet": "Batı/Fransız klasik komedi geleneği", "uslup": "gülünç durum ve karakter kusuru üzerinden eleştirel", "tur": "komedi"}},
                ["En az içerik, dönem/zihniyet ve üslup boyutlarını karşılaştırır.", "Cimri’yi komedi; Ben, Mimar Sinan’ı dram olarak metin özellikleriyle gerekçelendirir."],
                guidance=["Tür sınıflamasında öğrencinin metinden güçlü gerekçesi varsa kavram yanılgısı ile yorum farkını ayır."],
            ),
        ],
        "T4_ACT_02_OKUMA_ICERIK_ANLAM", "TDE2.2",
    ),
    unit(
        "T4_GUIDE_U05_TIYATRO_COZUMLEME", "Tiyatro Metnini Çözümleme", "255-261",
        "Özet, yapı, dil-üslup, dönem, değer, disiplinler arası ilişki ve çatışma boyutlarını çözümlemek.",
        [
            item(
                "T4_G01_P255_OZET_DEGERLENDIRME", "255", "Özet, amaç-dil ilişkisi, tarihî gerçeklik ve dekor", "QUESTION",
                {"ozet": "Özet; Sinan’ın gelişimini, önemli eserlerini ve çalışma/estetik anlayışını ana olay çizgisiyle, ayrıntıya boğmadan aktarmalıdır.", "amac_dil": "Bilgilendirici tarihî malzeme dramatik anlatımla birleşir; açık konuşmalar ve sahne ögeleri tarih bilincini canlı kılar.", "tarih": "Metindeki tarihî ad/yer/eser bilgileri gerçeklik duygusu oluşturur; tiyatro olduğu için seçme, yoğunlaştırma ve dramatikleştirme yapılır.", "dekor": "Tasarımlar sahnenin tarihî atmosferini, çalışma ortamını ve mimari eserleri işlevsel biçimde desteklemelidir."},
                ["Özette ana çizgiyi korur.", "Dil/üslup ile yazılma amacı arasında bağ kurar.", "Tarihî gerçeklik ile dramatik kurgu ayrımını korur.", "Dekor önerisini sahne işleviyle gerekçelendirir."],
            ),
            item(
                "T4_G01_P256_YAPI", "256", "Yapı unsurları ve ilişkileri", "TABLE",
                {"kisiler": "Mimar Sinan ve tarihî çevresindeki kişiler/sesler", "mekan": "mimarlık ve saray/şehir/eser bağlamları", "zaman": "Sinan’ın meslek hayatını kapsayan tarihî süreç", "catismalar": "başarma/engel, eskiyi aşma-yeniyi kurma, bireysel kaygı-sorumluluk gibi gerilimler", "dramatik_orgu": "seçilmiş yaşam kesitlerinin sahne akışı içinde neden-sonuç ve dönüm noktalarıyla düzenlenmesi"},
                ["Yapı unsurlarını metinden ayırt eder.", "Kişi-mekân, kişi-çatışma, mekân-zaman ve çatışma-dramatik örgü ilişkilerinden en az ikisini açıklar."],
            ),
            item(
                "T4_G01_P257_258_DIL_USLUP", "257-258", "Monolog, diyalog, cümle çeşitliliği ve üslup", "QUESTION",
                {"monolog": "karakterin iç düşüncesini, değerlendirmesini veya geçmişe bakışını doğrudan açar", "diyalog": "kişiler arası ilişkiyi, çatışmayı ve sahne hareketini canlılaştırır", "cumle_cesitliligi": "ritim, vurgu, duygu tonu ve karakter seslerini çeşitlendirir", "uslup": "tarihî/bilgilendirici içeriği dramatik ve yer yer coşkulu söyleyişle birleştirir"},
                ["Monolog ve diyaloğun işlevini ayırır.", "Cümle türlerini yalnız etiketlemekle kalmaz, üsluba katkısını açıklar."],
                guidance=["Cümle sınıflamasında kitapta verilen örnek sınıflamayı model olarak kullan; farklı cümleler için yüklemin türü/yeri, anlamı ve yapısını ayrı ayrı kontrol et."],
            ),
            item(
                "T4_G01_P259_260_DONEM_DEGER", "259-260", "Cumhuriyet tiyatrosu, tarih-kimlik ve değerler", "QUESTION",
                {"tarih_bilinci": "Cumhuriyet dönemi tiyatrosu tarihî malzemeyi güncel kültür ve kimlik bilinciyle yeniden ele alabilir; Ben, Mimar Sinan geçmişi öğretici/düşündürücü dramatik malzemeye dönüştürür.", "degerler": ["çalışkanlık", "sorumluluk", "estetik duyarlılık", "azim", "kültürel mirasa bağlılık", "toplumsal yarar"]},
                ["Metni tarih bilinci/kültür aktarımıyla ilişkilendirir.", "En az üç değeri somut söz veya eylemle eşleştirir."],
                misconceptions=["Tarihî konulu her tiyatro metnini tarih belgesi saymak."],
            ),
            item(
                "T4_G01_P260_261_DISIPLIN_CATISMA", "260-261", "Tiyatro-sosyal bilimler ve çatışmaların işlevi", "QUESTION",
                {"disiplinler": {"tarih": "olay, kişi, dönem ve eser bağlamı", "psikoloji": "kişilerin amaç, kaygı ve iç gerilimleri", "sosyoloji": "toplumsal yapı, meslek, kurum ve değer ilişkileri"}, "catismalarin_islevi": "Karakter amaçlarını görünür kılar, dramatik gerilim ve değişimi üretir, iletileri soyut açıklama yerine eylem içinde gösterir."},
                ["En az iki disiplinle metinsel bağ kurar.", "Çatışmanın dramatik örgüdeki işlevini açıklar."],
            ),
        ],
        "T4_ACT_03_OKUMA_UYGULAMA_COZUMLEME", "TDE2.3",
    ),
    unit(
        "T4_GUIDE_U06_TIYATRO_DEGERLENDIRME", "Süreç ve Beğeni Ölçütleriyle Değerlendirme", "262",
        "Metni günlük hayat, karakter, sahneleme ve kişisel beğeni ölçütleri üzerinden değerlendirmek.",
        [
            item(
                "T4_G01_P262_HAYAT_DEGERLENDIRME", "262", "Günlük insan ilişkileri ve beğeni ölçütleri", "ASSESSMENT",
                "Öğrenci; otorite-sorumluluk, usta-çırak/çalışan ilişkisi, güven, emek, hedef, kuşak ve değer aktarımı gibi metinde dayanak bulabildiği kesitleri belirleyebilir. Beğeni ölçütü olarak etkileyicilik, inandırıcılık, dil, karakter, sahneleme veya ileti gibi ölçütler kullanılabilir.",
                ["En az bir günlük hayat ilişkisini metin kanıtıyla açıklar.", "Kendi değerlendirme ölçütünü açıkça adlandırır ve gerekçelendirir."],
            ),
            item(
                "T4_G01_P262_BEN_KIMIM", "262", "‘Ben Kimim?’ karakter oyunu ve kısa senaryo", "PERFORMANCE_TASK",
                "Seçilen karakter; adı söylenmeden ayırt edici özellik, amaç, ilişki ve davranışlarıyla tanıtılmalı; güncel kısa senaryoda karakterin temel özellikleri tutarlı biçimde korunmalıdır.",
                ["Tanıtım karaktere özgü en az iki ipucu içerir.", "Senaryo karakter özelliğiyle tutarlıdır.", "Tahminler sonrası kısa öz değerlendirme yapılır."],
            ),
        ],
        "T4_ACT_04_OKUMA_DEGERLENDIRME", "TDE2.4",
    ),
]

read_outcomes = ["TDE2.1", "TDE2.2", "TDE2.3", "TDE2.4"]
sec01 = section(
    "T4_SEC_01_OKUMA_TIYATRO",
    "Metin Tahlili-1 (Anlama): Okuma — Tiyatro / Ben, Mimar Sinan",
    "READING", "240-262", read_outcomes,
    ["T4_ACT_01_OKUMA_YONETIM", "T4_ACT_02_OKUMA_ICERIK_ANLAM", "T4_ACT_03_OKUMA_UYGULAMA_COZUMLEME", "T4_ACT_04_OKUMA_DEGERLENDIRME"],
    plan_refs("BLOCK_T4_01_OKUMA", 1, 4), read1_units,
)

# ---------- 02 Okuma: Merdiven ----------
read2_units = [
    unit(
        "T4_GUIDE_U07_KUCU_REK_YONETIM", "Okumayı Yönetme — Yaşam Metaforları ve Küçürek Hikâye", "263-265",
        "Yaşam-merdiven çağrışımını ve küçürek hikâyenin yoğun anlatım özelliklerini okuma öncesinde etkinleştirmek.",
        [
            item(
                "T4_G02_P263_HAYAT_YOLCULUK", "263", "Yaşam evreleri ve yol/merdiven metaforları", "QUESTION",
                "Yol, merdiven, bahar ve diken gibi imgeler; başlangıç, ilerleme, güçlük, yükselme/gerileme, yaşlanma, yenilenme ve sonluluk gibi hayat evrelerini mecazlaştırabilir. Farklı gerekçeli çağrışımlar kabul edilir.",
                ["En az iki metaforu yaşam evresiyle gerekçeli bağlar.", "Görsel/ifade ile yorum arasında açık ilişki kurar."],
            ),
            item(
                "T4_G02_P264_KUCU_REK_OZELLIK", "264", "Küçürek/minimal hikâyenin özellikleri", "REFERENCE",
                ["çok kısa ve yoğun anlatım", "az sözle geniş çağrışım", "şiirsel/yoğun dil", "boşlukları okurun tamamlaması", "seçilmiş an veya kırılma noktası"],
                ["Kısalığı tek özellik olarak görmez.", "Yoğunluk ve okur katılımını açıklar."],
                content_class="OFFICIAL_TEXTBOOK",
            ),
            item(
                "T4_G02_P264_265_OKUMA_PLANI", "264-265", "Okuma amacı, tahmin ve strateji", "PROCESS",
                "Öğrencinin başlık ve tür bilgisinden içerik tahmini yapması; kısa metinde tekrar, simge, karşıtlık ve dönüşüm noktalarını izlemeye uygun bir strateji seçmesi beklenir.",
                ["Okuma amacını açıklar.", "Tahminini başlık/tür ipucuna dayandırır.", "Stratejiyi metnin kısalığı ve yoğunluğuyla ilişkilendirir."],
            ),
        ],
        "T4_ACT_05_OKUMA_YONETIM", "TDE2.1",
    ),
    unit(
        "T4_GUIDE_U08_KUCU_REK_ANLAM", "Merdiven — Söz Varlığı, İleti ve Simgeler", "266-270",
        "Metindeki söz varlığından, tekrar ve karşıtlıklardan hareketle yaş, zaman, kariyer ve ölüm farkındalığına ilişkin anlam kurmak.",
        [
            item(
                "T4_G02_P266_267_SOZ_VARLIGI", "266-267", "Söz varlığı ve çok anlamlı kullanım", "VOCABULARY",
                {"daire": "bağlamda kurum içindeki iş bölümü/oda-birim; başka bağlamlarda geometrik şekil veya konut anlamı taşıyabilir", "yeni_yetme": "çok genç/deneyimsiz görülen kişi", "kanimca": "bence, benim görüşüme göre", "yol_vermek": "geçiş önceliği tanımak; mecazen yerini/önceliği başkasına bırakmak", "gereksinme": "ihtiyaç", "duralamak": "kısa süre durup kararsız kalmak"},
                ["Bağlamdaki anlamı belirler.", "Aynı kelimeyi başka anlamda uygun cümlede kullanabilir."],
            ),
            item(
                "T4_G02_P268_BAHTIYAR", "268", "‘Bahtiyar ol’ ve kültürel kalıp sözler", "QUESTION",
                {"anlam": "Mutlu ol, bahtın açık olsun, iyilik ve güzel bir gelecek seninle olsun anlamında iyi dilek.", "benzerler": ["Bahtın açık olsun.", "Yolun açık olsun.", "Allah gönlüne göre versin.", "Güle güle kullan/otur.", "Allah zihin açıklığı versin."]},
                ["Kalıp sözün iyi dilek işlevini açıklar.", "Benzer örnekleri bağlama uygun seçer.", "Söz varlığının gündelik kültürü yansıttığını gerekçelendirir."],
                guidance=["Bölgesel/ailevi farklı kalıp sözleri, anlam ve kullanım bağlamı uygunsa kabul et."],
            ),
            item(
                "T4_G02_P269_Q1_4", "269", "Metni Anlayalım 1-4 — kişi, öğüt ve merdiven simgesi", "QUESTION",
                {"ihtiyar": "Yaşamın sonuna yaklaşmış, deneyimin verdiği sakinlikle koşuşturmanın değersizleşebileceğini sezen/uyaran figür.", "delikanli": "Yeni kuşağı ve meslek hayatının devamlılığını çağrıştıran genç figür; anlatıcıya istemeden ayna olur.", "ogut": "Sürekli yükselme/koşuşturma uğruna hayatın kendisini kaçırmama uyarısı olarak yorumlanabilir.", "inmek_cikmak": "Meslekî yükseliş kadar yaş, zaman, kuşak değişimi ve hayat döngüsünü simgeleştirebilir."},
                ["Kişi çıkarımlarını davranış/sözle destekler.", "Merdiveni yalnız fiziksel araç olarak yorumlamaz; simgesel katmanı açıklar.", "Alternatif yorumlarda metin kanıtı arar."],
            ),
            item(
                "T4_G02_P269_270_Q5_8", "269-270", "Metni Anlayalım 5-8 — tür, ritim ve final", "QUESTION",
                {"yazilma_amaci": "Kısa bir karşılaşma üzerinden yaşamın geçiciliği, hırs, yaşlanma ve kuşak değişimi üzerine okuru düşündürmek.", "az_kisi": "Küçürek hikâyenin yoğunlaştırma ekonomisine uygundur; gereksiz yan olay/karakter yerine kırılma anına odaklanır.", "ritim": ["merdiven", "çıkmak/inmek", "yol vermek", "Bahtiyar ol oğlum" gibi tekrar ve karşıtlıklar], "final": "Anlatıcı ölüm ve genç kuşakla yüzleşince ‘yukarı’ yönündeki meslekî/yaşamsal koşuşturmasını sorgular; aşağı inmeyi kabulleniş/farkındalık olarak seçer."},
                ["Tür özelliğini metin yapısıyla ilişkilendirir.", "Ritmi tekrar/karşıtlık örnekleriyle açıklar.", "Final yorumunu ölüm, zaman veya kuşak farkındalığıyla metne dayandırır."],
                misconceptions=["‘Aşağı inme’yi yalnız fiziksel hareket olarak okumak veya tek zorunlu metafor kabul etmek."],
            ),
        ],
        "T4_ACT_06_OKUMA_ICERIK_ANLAM", "TDE2.2",
    ),
    unit(
        "T4_GUIDE_U09_KUCU_REK_COZUMLEME", "Merdiven — Karşılaştırma, Karakter, Yapı, Çatışma ve Disiplinler", "271-278",
        "Küçürek hikâyenin yoğunlaştırma tekniğini farklı metinlerle karşılaştırıp karakter-yapı-çatışma-değer-disiplin ilişkilerini çözümlemek.",
        [
            item(
                "T4_G02_P271_KUCU_REK_KARSILASTIRMA", "271", "Az sözle çok duygu ve okur katılımı", "QUESTION",
                "Uzun açıklamalar yerine seçilmiş ayrıntı, çağrışımlı söz, boşluk, beklenmedik dönüş ve simgesel öge kullanımı okurun eksik bağlantıları kendi deneyimiyle tamamlamasını sağlar. Merdiven’de tekrar eden çıkma-inme/yol verme motifleri bu yoğunluğu destekler.",
                ["En az bir anlatım tekniğini örnekle açıklar.", "Okur katılımını metindeki eksiltme/açıklıkla ilişkilendirir."],
            ),
            item(
                "T4_G02_P272_TUR_KARSILASTIRMA", "272", "Ben, Mimar Sinan — Merdiven karşılaştırması", "TABLE",
                {"tiyatro": "sahnelenmek üzere diyalog/monolog, dramatik örgü, sahne yönergeleri ve tarihî yaşam kesitleri", "kucurek_hikaye": "çok kısa düzyazı, yoğun çağrışım, sınırlı kişi/olay, simgesel ve açık uçlu anlam", "ortak": ["insan ilişkileri", "değerler", "çatışma", "hayatın seçilmiş kesitlerini dönüştürme"]},
                ["İçerik, tür, şekil, dönem, yapı, dil/üslup ve ileti ölçütlerinden çoğunu karşılaştırır.", "Hangi türün değeri daha iyi yansıttığı görüşünü gerekçelendirir; tek zorunlu cevap aranmaz."],
            ),
            item(
                "T4_G02_P273_SAIR_TAVAFI", "273", "Şair Tavafî — Merdiven karşılaştırması", "TABLE",
                {"şiirsel_dil": "Merdiven daha yoğun tekrar/simge ve kısa cümlelerle şiirsel yoğunluk kurar; Şair Tavafî daha geniş anlatı ayrıntısı taşır.", "icerik": "İkisi de insan ve gündelik yaşam kesitlerine yönelir fakat ölçek ve anlatı genişliği farklıdır.", "cagrisim": "Merdiven sözcük ve eylemleri simgesel katmana daha yoğun açar.", "anlatici": "Her iki parçada da anlatıcı perspektifi önemlidir; işlevleri metnin anlatım biçimine göre karşılaştırılmalıdır."},
                ["Dört ölçütte metin kanıtı kullanır.", "Beğeni tercihini gerekçelendirir."],
            ),
            item(
                "T4_G02_P274_275_KARAKTER_YAPI", "274-275", "Karakter çözümleme ve yapı unsurları", "TABLE",
                {"anlatici": {"baslangic": "aceleci, iş/konum odaklı", "degisim": "ölüm ve genç memurla karşılaşma sonrası kendi yerini/zamanını sorgular"}, "ihtiyar": {"islev": "deneyim, fanilik ve yavaşlama uyarısı"}, "genc_memur": {"islev": "yeni kuşak/devamlılık ve anlatıcının konum değişimini görünür kılan ayna"}, "yapi": {"mekan": "merdiven ve kurum", "zaman": "kısa bir zaman dilimi", "olay": "tekrarlanan karşılaşmalar ve ölüm haberiyle oluşan farkındalık"}},
                ["Her karakterin özellik, amaç/niyet ve işlevini ayırır.", "Yapı unsurlarını metindeki yoğunlaştırma ile ilişkilendirir."],
            ),
            item(
                "T4_G02_P275_278_HAYAT_CATISMA_DEGER", "275-278", "Güncelleme, kuşak farkı, çatışma, değer ve disiplinler", "QUESTION",
                {"guncelleme": "Asansör/dijital iş akışı gibi araçlar fiziksel olay örgüsünü değiştirebilir; fakat yükselme, kuşak değişimi, acele ve fanilik temaları başka simgelerle korunabilir.", "catismalar": ["anlatıcının kendi hırsı/zamanı ile iç çatışması", "kuşak/konum farkından doğan insan-insan gerilimi"], "degerler": ["saygı", "duyarlılık", "sorumluluk", "nezaket", "empati"], "disiplinler": {"psikoloji": "ölüm, kaygı, benlik ve farkındalık", "sosyoloji": "kurum, kuşak ve meslek rolleri", "felsefe": "varoluş, fanilik, anlam", "saglik": "yaşlılık ve ani ölüm"}},
                ["Güncel kurgu önerisinde tematik çekirdeği korur.", "İç ve kişiler arası çatışmayı ayırır.", "Değer/disiplin eşleşmesini metin ayrıntısıyla gerekçelendirir."],
            ),
        ],
        "T4_ACT_07_OKUMA_UYGULAMA_COZUMLEME", "TDE2.3",
    ),
    unit(
        "T4_GUIDE_U10_KUCU_REK_DEGERLENDIRME", "Merdiven — Yazar Poetikası ve Okur Değerlendirmesi", "279",
        "Ferit Edgü’nün küçürek hikâye anlayışının metindeki yansımalarını ve öğrencinin gerekçeli beğenisini değerlendirmek.",
        [
            item(
                "T4_G02_P279_EDGU_POETIKA", "279", "Ferit Edgü’nün küçürek hikâye anlayışının Merdiven’e yansıması", "QUESTION",
                ["ayıklama/yoğunlaştırma", "açık yapıt ve okur katılımı", "simgesel göstergeler", "kısa zaman-mekân", "varoluş/yalnızlık/kaygı çağrışımları", "diyalog ve kısa cümlelerle benliği görünür kılma"],
                ["En az üç özelliği Merdiven’den kanıtla ilişkilendirir."],
            ),
            item(
                "T4_G02_P279_BEGeni", "279", "Ölçüt geliştirerek hikâyeyi değerlendirme", "ASSESSMENT",
                "Konu/ileti, dil, üslup, çağrışım gücü, yoğunluk, final etkisi veya karakter dönüşümü gibi ölçütler seçilebilir. Beğendim/beğenmedim kararı yalnız gerekçesi ve metin kanıtı varsa değerlendirilir.",
                ["En az iki açık ölçüt belirler.", "Her ölçüt için metinden gerekçe sunar."],
            ),
            item(
                "T4_G02_P279_NE_ISIM_VAR", "279", "‘Ne işim var benim yukarda?’ beyin fırtınası", "QUESTION",
                ["kariyer hırsını sorgulama", "ölümlülük/fanilik farkındalığı", "kuşağa yer açma", "hayatın hızını ve öncelikleri yeniden değerlendirme"],
                ["Farklı yorumlara açık kalır.", "Seçtiği yorumu olay dizisiyle destekler."],
            ),
        ],
        "T4_ACT_08_OKUMA_DEGERLENDIRME", "TDE2.4",
    ),
]

sec02 = section(
    "T4_SEC_02_OKUMA_KUCU_REK", "Metin Tahlili-2 (Anlama): Okuma — Küçürek Hikâye / Merdiven", "READING", "263-279",
    read_outcomes,
    ["T4_ACT_05_OKUMA_YONETIM", "T4_ACT_06_OKUMA_ICERIK_ANLAM", "T4_ACT_07_OKUMA_UYGULAMA_COZUMLEME", "T4_ACT_08_OKUMA_DEGERLENDIRME"],
    plan_refs("BLOCK_T4_01_OKUMA", 5, 8), read2_units,
)

# ---------- 03 Konuşma ----------
speaking_units = [
    unit(
        "T4_GUIDE_U11_KONUSMA_YONETIM", "Canlandırmayı Yönetme — Rol ve Uzam", "280-281",
        "Rol yaratma, empati, uzam ve konuşma amacını canlandırma öncesinde planlamak.",
        [
            item(
                "T4_G03_P280_ROL_UZAM", "280", "Rol yaratma ve tiyatro hakkında çıkarım", "QUESTION",
                {"diyalogdan_cikarim": ["karakterler arası ilişki", "çatışma ve amaç", "dil/üslup", "duygu ve güç ilişkisi"], "rol_hazirligi": ["karakterin dönemini ve koşullarını anlama", "alt metin/amaç", "duygu ve beden kullanımı", "mekân-zaman", "kendi deneyimiyle empati"]},
                ["Rolü yalnız ezberlenecek sözler olarak görmez.", "En az iki boyutu nedenleriyle açıklar."],
            ),
            item(
                "T4_G03_P281_DIL_TIYATRO", "281", "Diyalog, doğru dil ve ‘insanı insana insanla anlatma’", "QUESTION",
                "Diyalog tiyatroda ilişkiyi ve eylemi taşır; doğru/bağlama uygun dil anlamı, karakteri ve iletişimi güçlendirir. ‘İnsanı insana insanla anlatma’ sözü, insan deneyiminin oyuncu/karakter aracılığıyla başka insanlara canlı biçimde sunulmasını vurgular.",
                ["Diyalog ile günlük iletişim arasında işlevsel bağ kurar.", "Tiyatro tanımını insan-karakter-izleyici ilişkisiyle açıklar."],
            ),
        ],
        "T4_ACT_09_KONUSMA_YONETIM", "TDE3.1",
    ),
    unit(
        "T4_GUIDE_U12_KONUSMA_ICERIK", "Canlandırma İçeriğini Planlama", "281",
        "Ben, Mimar Sinan’dan seçilen bölümü hedef kitle, amaç, rol ve iletişim engellerine göre canlandırmaya hazırlamak.",
        [
            item(
                "T4_G03_P281_PERFORMANS_PLANI", "281", "Tiyatro bölümünü yeniden kurgulama performans görevi", "PERFORMANCE_TASK",
                {"zorunlu_adimlar": ["amaç", "grup ve rol dağılımı", "canlandırılacak bölüm", "hedef kitle/süre", "yöntem-strateji", "iletişim engellerini giderme"]},
                ["Canlandırma amacı açıktır.", "Rol ve sahne bölümü belirlenmiştir.", "Yöntem hedef kitle/süreyle uyumludur.", "İletişim engelleri için önlem alınmıştır."],
                evidence=["Kitaptaki görünür kontrol listesinin tamamlanması."],
                content_class="OFFICIAL_TEXTBOOK",
            ),
        ],
        "T4_ACT_10_KONUSMA_ICERIK_ANLAM", "TDE3.2",
    ),
    unit(
        "T4_GUIDE_U13_KONUSMA_UYGULAMA", "Rolü İçselleştirme ve Canlandırma Kuralları", "282",
        "Karakter ilişkisi, jest-mimik, doğaçlama, beden, diksiyon, görsel-işitsel ögeler ve geri bildirimle canlandırmayı gerçekleştirmek.",
        [
            item(
                "T4_G03_P282_CANLANDIRMA", "282", "Canlandırma uygulama ölçütleri", "PERFORMANCE_TASK",
                ["karakter ilişkilerini çözümleme", "uygun jest ve mimik", "gerektiğinde bağlama uygun doğaçlama", "rolün söz varlığını koruma", "beden dili-diksiyon-telaffuz", "zaman ve mekânı işlevsel kullanma", "duygu/karakter tutarlılığı", "olumlu değerler ve toplumsal hassasiyet"],
                ["Rol tutarlılığını korur.", "Sözlü ve sözsüz iletişimi birlikte kullanır.", "Doğaçlama ana bağlamı bozmaz.", "Türkçeyi anlaşılır ve bağlama uygun kullanır."],
            ),
        ],
        "T4_ACT_11_KONUSMA_UYGULAMA_COZUMLEME", "TDE3.3",
    ),
    unit(
        "T4_GUIDE_U14_KONUSMA_DEGERLENDIRME", "Canlandırma Sonrası Değerlendirme", "283",
        "Görünür kitap ölçütleriyle performansı değerlendirmek, dış QR rubriğinin sınırını korumak ve yansıtma yapmak.",
        [
            item(
                "T4_G03_P283_RUBRIK", "283", "Dereceli puanlama anahtarı — görünür ölçütler ve dış QR sınırı", "ASSESSMENT",
                ["kurgulanan içeriğe uygunluk", "özgünlük", "sözü ve beden dilini etkili kullanma", "grupla uyum içinde çalışma"],
                ["PDF’de açıkça görünen ölçütleri kullanır.", "QR içindeki görünmeyen düzey tanımlarını uydurmaz."],
                guidance=["Tam ölçüt×düzey matrisi yerel PDF’ye gömülü değildir; dış kaynak elde edilene kadar bu madde REVIEW_REQUIRED kalır."],
                content_class="OFFICIAL_TEXTBOOK",
                note="QR-linked dereceli puanlama anahtarının tam matrisi yerel PDF’de görünmez.",
            ),
            item(
                "T4_G03_P283_YANSITMA", "283", "Yansıtma yazısı, rol arkadaşı geribildirimi ve konuşmacı kimliği", "ASSESSMENT",
                "Öğrenci rolde yaşadığı duygu/düşünceyi, güçlü ve geliştirilmesi gereken yönlerini, akran geribildiriminden öğrendiklerini ve bir sonraki canlandırmada değiştireceği davranışı somutlaştırmalıdır.",
                ["Öz değerlendirme somut performans kanıtına dayanır.", "Akran geribildirimini aynen kabul etmek yerine gerekçeli biçimde değerlendirir.", "Yeni hedef belirler."],
            ),
        ],
        "T4_ACT_12_KONUSMA_DEGERLENDIRME", "TDE3.4", status="REVIEW_REQUIRED",
    ),
]

speaking_outcomes = ["TDE3.1", "TDE3.2", "TDE3.3", "TDE3.4"]
sec03 = section(
    "T4_SEC_03_KONUSMA_CANLANDIRMA", "Edebiyat Atölyesi-1 (Anlatma): Konuşma — Tiyatro Metnini Yeniden Kurgulayarak Canlandırma",
    "SPEAKING", "280-283", speaking_outcomes,
    ["T4_ACT_09_KONUSMA_YONETIM", "T4_ACT_10_KONUSMA_ICERIK_ANLAM", "T4_ACT_11_KONUSMA_UYGULAMA_COZUMLEME", "T4_ACT_12_KONUSMA_DEGERLENDIRME"],
    plan_refs("BLOCK_T4_02_KONUSMA", 1, 5), speaking_units, status="REVIEW_REQUIRED",
)

# ---------- 04 Dinleme / İzleme ----------
listening_units = [
    unit(
        "T4_GUIDE_U15_DINLEME_YONETIM", "Dinleme/İzlemeyi Yönetme — Hayat, Edebiyat ve Belgesel", "284-286",
        "Edebiyat-toplum ilişkisini hatırlayıp belgeseli amaç, tahmin, strateji ve dinleme kurallarıyla izlemeye hazırlamak.",
        [
            item(
                "T4_G04_P284_HAYAT_EDEBIYAT", "284", "Hayat ve edebiyat ilişkisi", "QUESTION",
                "Edebî eser bireysel yaratım olsa da yazarın yaşadığı zaman, çevre ve toplumsal koşullarla ilişkilidir; hayatı birebir kopyalamaz, seçer ve dönüştürür. Okur da kendi deneyimleriyle bu ilişkiyi yeniden kurar.",
                ["Bireysel yaratım ile toplumsal bağın ikisini de açıklar.", "‘Ayna’ benzetmesini birebir kopya olarak yorumlamaz."],
            ),
            item(
                "T4_G04_P285_DINLEME_PLANI", "285", "Fedakârlık belgeseli — amaç, tahmin, engel, strateji", "PROCESS",
                "Başlık/görsel/jenerikten içerik tahmini yapılır; amaç belirlenir; ses/görüntü/ortam kaynaklı iletişim engelleri azaltılır; not alma, anahtar kelime veya seçici dinleme gibi amaca uygun strateji seçilir.",
                ["Tahminini görünen ön ipucuna dayandırır.", "İletişim engeli için somut önlem önerir.", "Stratejiyi amaca bağlar."],
                guidance=["Video ve jenerik QR içeriği yerel PDF’de gömülü değildir; video izlenmeden içerik sonucu üretme."],
                note="Anadolu İnsanı / Fedakârlık video ve jenerik payload’ı dış QR kaynağındadır.",
            ),
            item(
                "T4_G04_P286_NOT_ILETI", "286", "Tema kelimeleri ve belgesel iletilerini not etme", "PROCESS",
                None,
                ["Notlar gerçekten izlenen içerikten alınır.", "Ana/yardımcı ileti ayrımı için kanıt kaydedilir."],
                guidance=["Yerel PDF yalnız görevi verir; video olmadan örnek olay, kişi veya iletiyi canonical cevap gibi yazma."],
                content_class="OFFICIAL_TEXTBOOK",
                note="İçerik cevabı dış videoya bağlıdır.",
            ),
        ],
        "T4_ACT_13_DINLEME_YONETIM", "TDE1.1", status="REVIEW_REQUIRED",
    ),
    unit(
        "T4_GUIDE_U16_DINLEME_ANLAM", "Fedakârlık — Söz Varlığı, Ana Düşünce ve Güvenilirlik", "287-291",
        "Video içeriğinden söz varlığı, konu/tema, kişi çıkarımı, öznel-nesnel ifade ve açık/örtük ileti üretmek.",
        [
            item(
                "T4_G04_P287_SOZ_VARLIGI", "287", "Belgesel söz varlığı", "VOCABULARY",
                {"fedakârlık": "bir amaç/başkası için kendi çıkar veya rahatlığından vazgeçme", "hemzemin_gecit": "kara yolu ile demir yolunun aynı seviyede kesiştiği geçit", "mesai": "çalışma süresi/iş için ayrılan zaman", "aksaklık": "işleyişi bozan gecikme veya düzensizlik", "tahammül": "dayanma, katlanma"},
                ["Önce bağlam tahmini yapar.", "Sözlük doğrulamasından sonra bağlama uygun anlamı seçer."],
            ),
            item(
                "T4_G04_P287_289_VIDEO_ANLAM", "287-289", "Anadolu insanı, konu-tema-ana düşünce ve kişi çıkarımı", "QUESTION",
                None,
                ["Anadolu insanına ilişkin çıkarım videodaki davranış/olay kanıtına dayanır.", "Konu, tema ve ana düşünce birbirinden ayrılır.", "Kişinin duygu/düşüncesi davranış kanıtıyla gerekçelendirilir.", "Ön tahmin ile son tespit karşılaştırılır."],
                guidance=["Dış videoyu izlemeden kişiye, olaya veya ana düşünceye dair kesin cevap üretme."],
                note="Cevap, Anadolu İnsanı / Fedakârlık dış video içeriğine bağlıdır.",
            ),
            item(
                "T4_G04_P289_291_BELGESEL_GUVEN", "289-291", "Belgesel kurgusu, öznel-nesnel ifadeler ve ileti güvenilirliği", "ASSESSMENT",
                None,
                ["Belgesel türü değerlendirmesinde gerçeklik iddiası ile seçme/kurgu ayrımını gözetir.", "Öznel ve nesnel ifadeyi kanıtlanabilirlik ölçütüyle ayırır.", "Açık/örtük iletiyi videodan örnekle destekler.", "Güvenilirlik sorgusunda kaynak, kanıt, bağlam ve anlatım tercihlerine değinir."],
                guidance=["Balık kılçığı ve ileti tablolarını yalnız izlenen videodan doldurt."],
                note="İçerik örnekleri dış videoya bağlıdır.",
            ),
        ],
        "T4_ACT_14_DINLEME_ICERIK_ANLAM", "TDE1.2", status="REVIEW_REQUIRED",
    ),
    unit(
        "T4_GUIDE_U17_DINLEME_COZUMLEME", "Belgeseli Çözümleme — Yapı, Dil, Dönem, Ses/Görüntü ve Disiplinler", "292-296",
        "Fedakârlık belgeselini yapı ve çok modluluk açısından çözümlemek; metinler arası/disciplinler arası bağ kurmak.",
        [
            item(
                "T4_G04_P292_IKLIM", "292", "İklim değişikliği — bireysel sorumluluk", "QUESTION",
                ["enerji ve kaynak tüketimini azaltma", "israfı önleme", "düşük karbonlu ulaşımı tercih etme", "atığı azaltma/yeniden kullanım/geri dönüşüm", "su tasarrufu", "doğru bilgi ve toplumsal farkındalığa katkı"],
                ["En az üç uygulanabilir bireysel davranış verir.", "Bireysel davranışları tek başına yeterli çözüm gibi sunmaz; toplumsal/kurumsal boyutla ilişkilendirebilir."],
            ),
            item(
                "T4_G04_P293_CALISKANLIK", "293", "Fedakârlık — Çalışkanlık belgesellerini karşılaştırma", "TABLE",
                None,
                ["Her iki videonun ana düşüncesini izlenen içeriğe göre belirler.", "Dil/üslup, ileti, tür ve içerik ölçütlerinde benzerlik/farklılık verir."],
                guidance=["Çalışkanlık videosu da dış QR’dadır; video erişimi yoksa karşılaştırmayı tamamlandı sayma."],
                note="İki dış video payload’ına bağlıdır.",
            ),
            item(
                "T4_G04_P294_295_YAPI_DIL", "294-295", "Yapı unsurları, dil ve dönem/toplum ilişkisi", "TABLE",
                None,
                ["Ses, görsel, ışık, mekân ve zaman unsurlarını videodan belirler.", "Unsurlar arası en az iki ilişkiyi içerikle açıklar.", "Dil/anlatım ile ileti arasındaki bağı gerekçelendirir.", "Kişi, amaç, dönem ve toplum çıkarımını video kanıtıyla destekler."],
                guidance=["Yerel PDF yapısal soruları sağlar; somut cevapların doğrulanması video izlemeyi gerektirir."],
                note="Somut yapı ve kişi cevapları dış videoya bağlıdır.",
            ),
            item(
                "T4_G04_P295_296_SES_GORUNTU", "295-296", "Ses ve görüntünün çok modlu metne katkısı", "QUESTION",
                "Ses ve görüntü birbirini yalnız tekrar etmemeli; bağlam, atmosfer, vurgu, duygu ve bilgi katmanları üreterek anlamı genişletebilir. Bir unsur kaldırıldığında bilgi, atmosfer veya yorum katmanının ne ölçüde azaldığı karşılaştırılmalıdır.",
                ["Ses/görüntünün en az iki işlevini açıklar.", "Kitaptaki ses kuşağı metninden genel ilkeyi kullanır.", "Fedakârlık videosuna dair somut örneği ancak video izlendiyse verir."],
                guidance=["Genel cevap PDF’deki akademik parçadan çıkarılabilir; video-özel örnek dış kaynağa bağlıdır."],
            ),
            item(
                "T4_G04_P296_DEGER_DISIPLIN", "296", "Değerler ve sosyoloji-psikoloji-coğrafya ilişkisi", "QUESTION",
                None,
                ["Millî/manevî/evrensel değerleri videodan kanıtla belirler.", "Sosyoloji, psikoloji ve coğrafya için ayrı gerekçe verir."],
                guidance=["Değer veya disiplin örneğini videoyu görmeden varsayma; öğrencinin izlenen sahne/olayla bağ kurmasını iste."],
                note="İçerik cevabı dış videoya bağlıdır.",
            ),
        ],
        "T4_ACT_15_DINLEME_UYGULAMA_COZUMLEME", "TDE1.3", status="REVIEW_REQUIRED",
    ),
    unit(
        "T4_GUIDE_U18_DINLEME_DEGERLENDIRME", "Etkin Dinleyici Kimliği ve Öğrenme Günlüğü", "297",
        "Belgeseli kişisel beğeni, hayat bağlantısı ve dinleme davranışı açısından değerlendirmek.",
        [
            item(
                "T4_G04_P297_DEGERLENDIRME", "297", "Belgeselin kattığı değer ve davranışları değerlendirme", "ASSESSMENT",
                None,
                ["Beğeni/değer yargısını somut video unsuruyla gerekçelendirir.", "Kendi hayatıyla en az bir gerçekçi bağlantı kurar."],
                guidance=["Öğrenci öznel değerlendirmesini ‘doğru cevap’ kalıbına sokma; gerekçe ve kanıtı değerlendir."],
                note="Somut içerik dış videoya bağlıdır.",
            ),
            item(
                "T4_G04_P297_GUNLUK", "297", "Etkin dinleyici öğrenme günlüğü", "ASSESSMENT",
                {"alanlar": ["belgeselin kattığı değerler", "uygulanabilir davranışlar", "kendi hayatını yansıtan yaşantılar", "daha etkin izleyici için dikkat edilecek hususlar"]},
                ["Her alanı kişisel ve somut örnekle doldurur.", "Bir sonraki dinleme/izleme için davranış hedefi belirler."],
                content_class="OFFICIAL_TEXTBOOK",
            ),
        ],
        "T4_ACT_16_DINLEME_DEGERLENDIRME", "TDE1.4", status="REVIEW_REQUIRED",
    ),
]

listening_outcomes = ["TDE1.1", "TDE1.2", "TDE1.3", "TDE1.4"]
sec04 = section(
    "T4_SEC_04_DINLEME_BELGESEL", "Metin Tahlili-3 (Anlama): Dinleme / İzleme — Anadolu İnsanı / Fedakârlık",
    "LISTENING_VIEWING", "284-297", listening_outcomes,
    ["T4_ACT_13_DINLEME_YONETIM", "T4_ACT_14_DINLEME_ICERIK_ANLAM", "T4_ACT_15_DINLEME_UYGULAMA_COZUMLEME", "T4_ACT_16_DINLEME_DEGERLENDIRME"],
    plan_refs("BLOCK_T4_03_DINLEME", 1, 4), listening_units, status="REVIEW_REQUIRED",
)

# ---------- 05 Yazma: afiş ----------
writing_units = [
    unit(
        "T4_GUIDE_U19_YAZMA_YONETIM", "Afiş Tasarımını Yönetme — Ölçüt ve Amaç", "298-299",
        "Afişin iletişim işlevini, tasarım ölçütlerini, hedefi ve yazma stratejisini belirlemek.",
        [
            item(
                "T4_G05_P298_AFIS_OLCUT", "298", "Afiş tasarımında temel ölçütler", "REFERENCE",
                {"mesaj": "açık ve hızlı anlaşılır ana ileti", "mesaj_imge": "görsel ile sözel iletinin birbirini desteklemesi", "sozel_hiyerarsi": "başlık/alt başlık/slogan önem sırası", "fark_edilirlik": "yaratıcı ve dikkat çekici düzen", "uygulama": ["az sayıda güçlü imge", "kısa sözel içerik", "okunaklı yazı", "güçlü kontrast", "görsel-söz arasında işlevsel ilişki"]},
                ["Dört ana kriteri ayırt eder.", "Tasarım kararını iletişim işleviyle ilişkilendirir."],
                content_class="OFFICIAL_TEXTBOOK",
            ),
            item(
                "T4_G05_P299_AFIS_HAZIRLIK", "299", "Afişin dikkat çekme ve etkileme gücü", "QUESTION",
                {"dikkat": ["görsel odak", "kontrast", "başlık/slogan", "yerleşim"], "etki": "Kısa sürede dikkat çekip bir iletiyi hatırlanabilir kılabilir; etki hedef kitle, bağlam, doğruluk ve tasarım bütünlüğüne bağlıdır.", "eklenebilecek_unsurlar": ["başlık", "slogan", "görsel/illüstrasyon/fotoğraf", "gerekli kısa bilgi", "kaynak/telif bilgisi gerektiğinde"]},
                ["Dikkat ile iletiyi ayırır.", "Etkileme gücünü mutlaklaştırmaz; hedef kitle/bağlamla ilişkilendirir."],
            ),
            item(
                "T4_G05_P299_PERFORMANS", "299", "Afiş hazırlama performans görevi — amaç ve strateji", "PERFORMANCE_TASK",
                "Amaç, Fedakârlık belgeselinin seçilmiş bir iletisini hedef kitleye özgün ve anlaşılır bir afişle aktarmaktır. Öğrenci afiş özelliklerini belirler, uygun yazma/tasarım stratejisi seçer ve sınıf dışı hazırlığını planlar.",
                ["Afişin amacı ve hedef kitlesi bellidir.", "Belgeselden aktarılacak ileti belirlenmiştir.", "Strateji ile afiş özellikleri uyumludur."],
                guidance=["Belgesel içeriğini doğrulamak için dış videonun gerçekten izlenmiş olması gerekir."],
            ),
        ],
        "T4_ACT_17_YAZMA_YONETIM", "TDE4.1", status="REVIEW_REQUIRED",
    ),
    unit(
        "T4_GUIDE_U20_YAZMA_ICERIK", "Afiş İçeriğini Oluşturma", "300",
        "Renk, yazı, görsel ve seçilen belgesel iletisini tek bir iletişim sistemi içinde planlamak.",
        [
            item(
                "T4_G05_P300_TASARIM_KARAR", "300", "Renk, yazı, görsel ve ileti seçimi", "PERFORMANCE_TASK",
                {"beklenen": ["öne çıkarılacak tek/ana ileti", "iletiyi destekleyen az sayıda görsel", "okunaklı tipografi", "hedef kitleye uygun renk/kontrast", "mesaj-imge bütünlüğü"]},
                ["Seçilen her görsel/renk/yazı kararını iletiyle gerekçelendirir.", "Afişi bilgi kalabalığına dönüştürmez."],
                guidance=["‘Afiş Hazırlama Basamakları’ videosu dış QR’dadır; PDF’deki görünür tasarım ölçütleri tek başına uygulanabilir."],
                note="QR-linked afiş hazırlama videosu yerel PDF’ye gömülü değildir.",
            ),
        ],
        "T4_ACT_18_YAZMA_ICERIK_ANLAM", "TDE4.2", status="REVIEW_REQUIRED",
    ),
    unit(
        "T4_GUIDE_U21_YAZMA_UYGULAMA", "Afişi Oluşturma ve Kural Uygulama", "301",
        "Taslağı geri bildirimle geliştirip Türkçe, tutarlılık, özgünlük, hedef kitle ve toplumsal hassasiyet kurallarıyla afişi tamamlamak.",
        [
            item(
                "T4_G05_P301_AFIS_UYGULAMA", "301", "Afiş oluşturma kuralları", "PERFORMANCE_TASK",
                ["plana bağlılık", "iletinin dikkat çekici ifadesi", "Türkçenin dil yapısı/yazım/noktalama", "özgün duygu ve düşünce", "ifade-ileti tutarlılığı", "hedef kitleye uygun söz varlığı/üslup", "toplumsal hassasiyet", "millî-manevî/kültürel unsurlarda özen"],
                ["İleti açık ve tasarımla tutarlıdır.", "Dil hataları anlamı bozmaz.", "Görsel-söz ilişkisi açıklayıcı/destekleyicidir.", "Geri bildirim sonrası en az bir bilinçli revizyon yapılır."],
            ),
            item(
                "T4_G05_P301_TELIF_ON_HAZIRLIK", "301", "Görsel ve bilgi kaynağı seçimi", "TEACHER_NOTE",
                "Kullanılan görsel/alinti için kaynak ve kullanım hakkı kontrolü, tasarımın dürüstlük ve hakkaniyet ilkelerine uygunluğu daha üretim aşamasında izlenmelidir.",
                ["Kaynağı belirsiz içeriği otomatik kullanmaz.", "Alıntı ile kendi üretimini ayırt eder."],
                guidance=["Telif değerlendirmesini yalnız son sayfada kontrol edilen bir formalite olmaktan çıkar; kaynak seçimi aşamasında hatırlat."],
                content_class="PEDAGOGICAL_ENRICHMENT",
            ),
        ],
        "T4_ACT_19_YAZMA_UYGULAMA_COZUMLEME", "TDE4.3",
    ),
    unit(
        "T4_GUIDE_U22_YAZMA_DEGERLENDIRME", "Afiş ve Yazma Sürecini Değerlendirme", "302",
        "Ürünü içerik/dil/telif yönünden değerlendirmek; dış QR rubriğinin sınırını koruyup tema sonu öğrenme günlüğüyle hedef belirlemek.",
        [
            item(
                "T4_G05_P302_AFIS_OZDEGER", "302", "Afiş öz değerlendirmesi ve paylaşım", "ASSESSMENT",
                {"boyutlar": ["süreçteki duygu-düşünce-davranış değişimi", "içerik", "dil ve anlatım", "görsel/alinti telif-hakkaniyet-dürüstlük", "uygun resmî paylaşım ortamı"]},
                ["En az bir güçlü ve bir geliştirilecek yön belirler.", "Telif ve kaynak kullanımını açıkça kontrol eder."],
            ),
            item(
                "T4_G05_P302_RUBRIK", "302", "Dereceli puanlama anahtarı — görünür ölçütler ve QR sınırı", "ASSESSMENT",
                ["konuya uygunluk", "yaratıcılık", "özgünlük", "etkileyicilik", "görsel/işitsel ögelerin seçimi"],
                ["PDF’de görünen ölçütleri kullanır.", "QR içindeki görünmeyen düzey tanımlarını uydurmaz."],
                guidance=["Tam ölçüt×düzey matrisi dış QR kaynağındadır; yerel PDF’den çıkarılamaz."],
                note="QR-linked rubrik matrisi yerel PDF’de görünmez.",
            ),
            item(
                "T4_G05_P302_TEMA_GUNLUK", "302", "Tema sonu öğrenme günlüğü", "ASSESSMENT",
                {"alanlar": ["tema öncesi bildiklerim", "tema sonunda öğrendiklerim", "hayatın duygu-düşünce-davranışa yansıması", "kelime/anlatım/dil farkındalığı", "konuşmacı ve yazar kimliğine etkisi"]},
                ["Önce-sonra değişimini somutlaştırır.", "Gelecekteki konuşma/yazma için en az bir hedef çıkarır."],
                content_class="OFFICIAL_TEXTBOOK",
            ),
        ],
        "T4_ACT_20_YAZMA_DEGERLENDIRME", "TDE4.4", status="REVIEW_REQUIRED",
    ),
]

writing_outcomes = ["TDE4.1", "TDE4.2", "TDE4.3", "TDE4.4"]
sec05 = section(
    "T4_SEC_05_YAZMA_AFIS", "Edebiyat Atölyesi-2 (Anlatma): Yazma — Özgün Afiş Hazırlama",
    "WRITING", "298-302", writing_outcomes,
    ["T4_ACT_17_YAZMA_YONETIM", "T4_ACT_18_YAZMA_ICERIK_ANLAM", "T4_ACT_19_YAZMA_UYGULAMA_COZUMLEME", "T4_ACT_20_YAZMA_DEGERLENDIRME"],
    plan_refs("BLOCK_T4_04_YAZMA", 1, 4), writing_units, status="REVIEW_REQUIRED",
)

# ---------- 06 Tema ölçme ----------
all_outcomes = listening_outcomes + read_outcomes + speaking_outcomes + writing_outcomes
assessment_units = [
    unit(
        "T4_GUIDE_U23_TEMA_OLCME_1_5", "4. Tema Ölçme — 1-5. Sorular", "303-305",
        "Modern Türk tiyatrosu, küçürek hikâye ve afiş/duygu aktarımını ölçmek.",
        [
            item(
                "T4_G06_P303_Q1", "303", "Soru 1 — Doğu/Batı sentezi ve modern Türk tiyatrosu", "QUESTION",
                "Parçada; Batı tiyatrosunun modern yazarlık/sahneleme teknikleri ile Meddah, Karagöz ve Ortaoyunu gibi geleneksel biçimlerin bir araya gelmesi; tipleme, söz oyunları, anlatıcı, şarkı/dans ve göstermeci sahneleme gibi Doğulu/geleneksel ögelerin modern yapı içinde kullanılması örneklenebilir.",
                ["I. metindeki genel yargıyla tiyatro parçası/II. metin arasında bağ kurar.", "En az iki geleneksel ve bir modern özellik belirtir."],
            ),
            item(
                "T4_G06_P304_Q2_3", "304", "Sorular 2-3 — metinler arası ilişki ve küçürek hikâye", "ASSESSMENT",
                {"2": "A", "3": "E"},
                ["Soru 2’de II. metnin I. metindeki durumun somut sonucu/örneklenişi olduğunu fark eder.", "Soru 3’te metnin televizyonu ‘en önemli sebeplerden biri’ diye kesinleştirmediğini ayırt eder."],
                guidance=["Q2 için seçeneklerin PDF yerleşiminde iki sütunlu çıkarım sırası metin çıkarımında karışabilir; cevap anahtarı I-II metin anlam ilişkisine göre A olarak kurulmuştur."],
            ),
            item(
                "T4_G06_P304_305_Q4_5", "304-305", "Sorular 4-5 — duygu ve afiş görseli", "QUESTION",
                {"4": "Sevgi, umut, güven, merhamet, dayanışma gibi metindeki erdem/kardeşlik/çocukluk atmosferiyle gerekçelendirilebilen duygular kabul edilir.", "5": None},
                ["Q4’te duygu seçimini metindeki en az bir ayrıntıyla gerekçelendirir.", "Q5’te seçilen görsel ile metnin iletisi arasında açık ilişki kurar."],
                guidance=["Q5 görsel seçenekleri metin çıkarımında güvenilir biçimde temsil edilmediği için tek görsel anahtarı üretme; öğrencinin seçimini gerekçe üzerinden değerlendir."],
                note="Q5 görsel seçeneklerinin kendisi PDF görsel katmanına bağlıdır; metin çıkarımından tek doğru görsel üretilmez.",
            ),
        ],
    ),
    unit(
        "T4_GUIDE_U24_TEMA_OLCME_6_14", "4. Tema Ölçme — 6-14. Sorular", "305-307",
        "Tiyatro sahne unsurları, belgesel-teknoloji-toplumsal bellek ve dış Aidiyet videosu üzerinden temayı değerlendirmek.",
        [
            item(
                "T4_G06_P305_306_Q6_7", "305-306", "Sorular 6-7 — kostüm ve sözsüz iletişim", "QUESTION",
                {"6": "Kostüm; karakterin yaş, toplumsal konum, dönem, ekonomik durum ve kişilik özellikleriyle tutarlı olmalı; sahne dekoruyla işlevsel bütünlük kurmalıdır.", "7": "Bakış, beden yönelimi, hareket, mesafe ve tekrar eden davranışlar konuşma olmadan gerilim, duygu ve ilişkiyi gösterebilir."},
                ["Kostüm önerisini karakter/sahne kanıtıyla gerekçelendirir.", "Sözsüz iletişimin en az iki işlevini açıklar."],
            ),
            item(
                "T4_G06_P306_Q8", "306", "Soru 8 — tiyatro terimleri", "ASSESSMENT",
                "B",
                ["Verilen kesitlerde dekor, jest/hareket ve çatışma iması görülebilir; açık diyalog ve monolog örneği kesin olarak çıkarılamadığı için II ve III seçilir."],
            ),
            item(
                "T4_G06_P306_307_Q9_11", "306-307", "Sorular 9-11 — belgesel, teknoloji ve toplumsal bellek", "ASSESSMENT",
                {"9": "A", "10": "B", "11": "B"},
                ["Q9’da metinde sayılan teknolojik dönüşümlerle desteklenmeyen seçeneği ayırır.", "Q10’da toplumsal belleği arşivin koruma işleviyle ilişkilendirir.", "Q11’de tablo oranlarının izleme mecralarının teknolojiyle değiştiğini gösterdiğini okur."],
            ),
            item(
                "T4_G06_P307_Q12", "307", "Soru 12 — teknolojik gelişmeler belgeselin etkisini güçlendirdi mi?", "QUESTION",
                "Her iki yönde de gerekçeli cevap kabul edilebilir. Güçlendirdi görüşü; erişim, dağıtım, ses/görüntü kalitesi ve kurgu imkânlarına; zayıflattı/karma görüşü ise dikkat dağınıklığı, platform kalabalığı, manipülasyon veya güvenilirlik sorunlarına dayandırılabilir.",
                ["En az iki gerekçe sunar.", "Gerekçeler teknoloji-belgesel ilişkisiyle doğrudan bağlantılıdır."],
            ),
            item(
                "T4_G06_P307_Q13_14", "307", "Sorular 13-14 — Anadolu İnsanı / Aidiyet", "ASSESSMENT",
                None,
                ["Q13’te belirgin özellikleri Aidiyet videosundaki davranış/olay kanıtına dayandırır.", "Q14’te aidiyetin yer, ilişki, hatıra, kültür, emek, güven veya toplumsal bağ gibi boyutlarını videodan örnekle açıklar."],
                guidance=["Aidiyet videosu dış QR içeriğidir. Yerel PDF yalnız soruları verir; videoyu görmeden canonical kişi/olay cevabı üretme."],
                note="Anadolu İnsanı / Aidiyet video payload’ı yerel PDF’ye gömülü değildir.",
            ),
        ],
    ),
]

sec06 = section(
    "T4_SEC_06_TEMA_SONU", "4. Tema Ölçme ve Değerlendirme Soruları", "THEME_ASSESSMENT", "303-307",
    all_outcomes, ["T4_ACT_21_TEMA_OLCME"], plan_refs("BLOCK_T4_04_YAZMA", 5, 5), assessment_units, status="REVIEW_REQUIRED",
)

# Write sections.
section_files = [
    ("00_tema_acilisi.json", sec00),
    ("01_okuma_tiyatro.json", sec01),
    ("02_okuma_kucurek.json", sec02),
    ("03_konusma_canlandirma.json", sec03),
    ("04_dinleme_fedakarlik.json", sec04),
    ("05_yazma_afis.json", sec05),
    ("06_tema_olcme.json", sec06),
]
for name, payload in section_files:
    dump(SECTIONS / name, payload)

# Manifest.
section_meta = [
    (sec00, None, None, "00_tema_acilisi.json"),
    (sec01, "BLOCK_T4_01_OKUMA", 15, "01_okuma_tiyatro.json"),
    (sec02, "BLOCK_T4_01_OKUMA", 15, "02_okuma_kucurek.json"),
    (sec03, "BLOCK_T4_02_KONUSMA", 10, "03_konusma_canlandirma.json"),
    (sec04, "BLOCK_T4_03_DINLEME", 8, "04_dinleme_fedakarlik.json"),
    (sec05, "BLOCK_T4_04_YAZMA", 10, "05_yazma_afis.json"),
    (sec06, "BLOCK_T4_04_YAZMA", 10, "06_tema_olcme.json"),
]
manifest = {
    "schema_version": "1.1.0",
    "document_type": "TYMM_TEACHER_GUIDE_MANIFEST",
    "course_id": "TDE_11",
    "grade": 11,
    "theme_id": "TEMA_04",
    "title": "4. TEMA: HAYATIN AYNASI — Öğretmen Rehberi",
    "status": "REVIEW_REQUIRED",
    "authority_policy": [
        {"rank": 1, "source_role": "NORMATIVE_PROGRAM", "rule": "Öğrenme çıktıları ve normatif gerekliliklerde öğretim programı belirleyicidir."},
        {"rank": 2, "source_role": "OFFICIAL_TEXTBOOK_PDF", "rule": "Kitaptaki soru, yönerge, metin bağlamı, tablo/form, sayfa akışı ve öğrenci görevinin birincil kaynağı resmî ders kitabı PDF’sidir."},
        {"rank": 3, "source_role": "OFFICIAL_TEXTBOOK_MAP", "rule": "PDF’nin sayfa, bölüm, etkinlik ve form kimliklerini indeksleyen türetilmiş yardımcı kaynaktır; PDF’nin yerine geçmez."},
        {"rank": 4, "source_role": "PROGRAM_TEXTBOOK_ALIGNMENT", "rule": "Program-kitap çapraz eşleştirmesini doğrular; PDF veya programı geçersiz kılamaz."},
        {"rank": 5, "source_role": "IMPLEMENTATION_PLANS", "rule": "Ders içi uygulama önerisidir; üst kaynaklarla çatışırsa resmî program/PDF eşleşmesi korunur."},
    ],
    "source_manifest": [
        {"source_id": "curriculum_normative", "role": "NORMATIVE_PROGRAM", "path": "courses/TDE_11/curriculum_normative_text.json", "authority_rank": 1, "usage": "Öğrenme çıktıları ve normatif tema gereklilikleri."},
        {"source_id": "curriculum_map", "role": "PROGRAM_INDEX", "path": "courses/TDE_11/curriculum_map.json", "authority_rank": 1, "usage": "Tema ve öğrenme çıktısı kimliklerini çözümler."},
        {"source_id": "official_textbook_pdf", "role": "OFFICIAL_TEXTBOOK_PDF", "path": "courses/TDE_11/source_docs/turk-dili-ve-edebiyati-11sinif-ders-kitabi_compressed.pdf", "authority_rank": 2, "usage": "Tema 4 basılı s.236-307 soru, yönerge, metin bağlamı ve sayfa yapısının canonical kaynağı."},
        {"source_id": "textbook_map", "role": "OFFICIAL_TEXTBOOK_MAP", "path": "courses/TDE_11/textbook_map.json", "authority_rank": 3, "usage": "PDF’den türetilmiş sayfa, bölüm, etkinlik ve form konumlandırma indeksi."},
        {"source_id": "theme_alignment", "role": "PROGRAM_TEXTBOOK_ALIGNMENT", "path": "courses/TDE_11/themes/tema_04/alignment.json", "authority_rank": 4, "usage": "Tema 4 program-kitap eşleşmesi."},
        {"source_id": "lesson_plan_set", "role": "IMPLEMENTATION_PLANS", "path": "courses/TDE_11/generated/lesson_plans/TEMA_04", "authority_rank": 5, "usage": "Sınıf içi uygulama, süre ve kanıt toplama önerileri."},
    ],
    "theme_overview": {"printed_page_range": "236-307", "core_instruction_hours": 43, "anlama_hours": 23, "anlatma_hours": 20, "outcome_count": 16, "legacy_guide_coverage": "YOK", "target_guide_coverage": "236-307", "target_section_count": 7},
    "content_storage": {"entrypoint_policy": "MANIFEST_PLUS_SECTION_FILES", "section_directory": "courses/TDE_11/teacher_guide/TEMA_04/sections", "section_schema_path": "skill/tymm-material-planner/schemas/teacher_guide_section.schema.json", "render_order_source": "sections_array_order"},
    "production_plan": [
        {"phase": 1, "name": "Kaynak ve yapı doğrulama", "status": "VERIFIED", "deliverables": ["Resmî PDF Tema 4 s.236-307 doğrudan çıkarıldı", "textbook_map/alignment etkinlik→çıktı eşleşmeleri doğrulandı", "43 saat/16 çıktı kapsamı donduruldu"]},
        {"phase": 2, "name": "PDF-temelli öğretmen rehberi üretimi", "status": "VERIFIED", "deliverables": ["Tema açılışı", "Ben, Mimar Sinan okuması", "Merdiven küçürek hikâyesi", "tiyatro canlandırma", "Anadolu İnsanı / Fedakârlık dinleme-izleme", "özgün afiş", "14 soruluk tema sonu ölçme"]},
        {"phase": 3, "name": "Çapraz-kaynak doğrulama", "status": "VERIFIED", "deliverables": ["7 activity→outcome plan kayması onarımı", "JSON schema/page nesting", "16 çıktı/43 saat", "QR/rubrik/media sınırları"]},
        {"phase": 4, "name": "Deterministik yayın", "status": "PLANNED", "deliverables": ["Manifest+section JSON→Markdown", "JSON→EPUB/HTML", "İsteğe bağlı PDF"]},
    ],
    "sections": [
        {"section_id": s["section_id"], "title": s["title"], "section_type": s["section_type"], "printed_page_range": s["printed_page_range"], "block_id": bid, "block_hours": hrs, "outcome_refs": s["outcome_refs"], "activity_refs": s["activity_refs"], "lesson_plan_refs": s["lesson_plan_refs"], "content_status": s["content_status"], "content_ref": f"courses/TDE_11/teacher_guide/TEMA_04/sections/{fname}"}
        for s, bid, hrs, fname in section_meta
    ],
    "known_issues": [
        {"issue_id": "T4_ISSUE_READING_PLAN_SEQUENCE_OUTCOME_MISMATCH", "severity": "ERROR", "status": "RESOLVED", "description": "Tema 4 okuma generated lesson-plan setinde P02-P07 paketleri resmî etkinlik→çıktı sırasından kaymıştı; bu değişiklikte canonical T4_ACT_02–T4_ACT_07 eşleşmesine göre onarıldı.", "source_refs": ["courses/TDE_11/source_docs/turk-dili-ve-edebiyati-11sinif-ders-kitabi_compressed.pdf", "courses/TDE_11/textbook_map.json"] + plan_refs("BLOCK_T4_01_OKUMA", 2, 7), "resolution_rule": "Ders kitabı PDF/textbook_map etkinlik→çıktı eşleşmesi korunur; plan JSON ve deterministik Markdown birlikte yeniden üretilir."},
        {"issue_id": "T4_ISSUE_LP_YAZMA_P04_OUTCOME_MISMATCH", "severity": "ERROR", "status": "RESOLVED", "description": "Tema 4 yazma P04 paketi TDE4.3 ile etiketlenmişti; resmî T4_ACT_20_YAZMA_DEGERLENDIRME→TDE4.4 eşleşmesine göre onarıldı.", "source_refs": ["courses/TDE_11/textbook_map.json", "courses/TDE_11/generated/lesson_plans/TEMA_04/BLOCK_T4_04_YAZMA/BLOCK_T4_04_YAZMA_P04.json"], "resolution_rule": "Plan ve Markdown TDE4.4 ile hizalanır ve full validation seal yenilenir."},
        {"issue_id": "T4_ISSUE_TDE3_4_EXTERNAL_RUBRIC", "severity": "WARNING", "status": "OPEN", "description": "Konuşma/canlandırma bölümünde PDF görünür ölçütleri verir; QR-linked Dereceli Puanlama Anahtarı’nın tam ölçüt×düzey matrisi yerel PDF’ye gömülü değildir.", "source_refs": ["courses/TDE_11/source_docs/turk-dili-ve-edebiyati-11sinif-ders-kitabi_compressed.pdf", "courses/TDE_11/teacher_guide/TEMA_04/sections/03_konusma_canlandirma.json"], "resolution_rule": "Dış resmî rubrik payload’ı elde edilene kadar görünür PDF ölçütlerini kullan; eksik matris hücrelerini uydurma."},
        {"issue_id": "T4_ISSUE_TDE4_4_EXTERNAL_RUBRIC", "severity": "WARNING", "status": "OPEN", "description": "Afiş yazma bölümündeki Dereceli Puanlama Anahtarı QR ile dış kaynağa bağlıdır; PDF yalnız genel ölçütleri görünür kılar.", "source_refs": ["courses/TDE_11/source_docs/turk-dili-ve-edebiyati-11sinif-ders-kitabi_compressed.pdf", "courses/TDE_11/teacher_guide/TEMA_04/sections/05_yazma_afis.json"], "resolution_rule": "Tam rubrik elde edilene kadar yalnız PDF’de görünen ölçütleri canonical kabul et."},
        {"issue_id": "T4_ISSUE_EXTERNAL_MULTIMODAL_MEDIA", "severity": "WARNING", "status": "OPEN", "description": "Anadolu İnsanı / Fedakârlık, Çalışkanlık, Aidiyet ve Afiş Hazırlama Basamakları gibi QR-linked medya payload’ları yerel PDF’ye gömülü değildir.", "source_refs": ["courses/TDE_11/source_docs/turk-dili-ve-edebiyati-11sinif-ders-kitabi_compressed.pdf", "courses/TDE_11/teacher_guide/TEMA_04/sections/04_dinleme_fedakarlik.json", "courses/TDE_11/teacher_guide/TEMA_04/sections/05_yazma_afis.json", "courses/TDE_11/teacher_guide/TEMA_04/sections/06_tema_olcme.json"], "resolution_rule": "Video-özel kişi, olay, ana düşünce ve sahne cevaplarını medya doğrulanmadan doldurma; görev/kabul ölçütü düzeyinde REVIEW_REQUIRED tut."},
    ],
    "validation_contract": {"required_checks": ["manifest schema", "section schema", "page nesting", "source/provenance references", "activity→outcome alignment", "lesson-plan alignment", "16 outcome coverage", "43 core hours", "external QR/media boundary"], "current_status": "PASS_WITH_WARNINGS"},
}
dump(GUIDE / "teacher_guide.json", manifest)

# Repair the same generator sequence drift previously verified/repaired in Themes 1-3.
sys.path.insert(0, str(SCRIPTS))
import render_lesson_plan_markdown  # noqa: E402

repairs = {
    "generated/lesson_plans/TEMA_04/BLOCK_T4_01_OKUMA/BLOCK_T4_01_OKUMA_P02.json": "TDE2.2",
    "generated/lesson_plans/TEMA_04/BLOCK_T4_01_OKUMA/BLOCK_T4_01_OKUMA_P03.json": "TDE2.3",
    "generated/lesson_plans/TEMA_04/BLOCK_T4_01_OKUMA/BLOCK_T4_01_OKUMA_P04.json": "TDE2.4",
    "generated/lesson_plans/TEMA_04/BLOCK_T4_01_OKUMA/BLOCK_T4_01_OKUMA_P05.json": "TDE2.1",
    "generated/lesson_plans/TEMA_04/BLOCK_T4_01_OKUMA/BLOCK_T4_01_OKUMA_P06.json": "TDE2.2",
    "generated/lesson_plans/TEMA_04/BLOCK_T4_01_OKUMA/BLOCK_T4_01_OKUMA_P07.json": "TDE2.3",
    "generated/lesson_plans/TEMA_04/BLOCK_T4_04_YAZMA/BLOCK_T4_04_YAZMA_P04.json": "TDE4.4",
}
for rel, outcome in repairs.items():
    path = COURSE / rel
    plan = json.loads(path.read_text(encoding="utf-8"))
    plan["outcome_codes"] = [outcome]
    if "assessed_outcome_codes" in plan:
        plan["assessed_outcome_codes"] = [outcome]
    for lesson in plan.get("lessons", []):
        lesson["outcome_codes"] = [outcome]
        if "assessed_outcome_codes" in lesson:
            lesson["assessed_outcome_codes"] = [outcome]
    continuation = plan.get("continuation_summary")
    if isinstance(continuation, dict):
        continuation["covered_outcome_codes"] = [outcome]
    dump(path, plan)
    path.with_suffix(".md").write_text(render_lesson_plan_markdown.render(plan), encoding="utf-8")

# Deterministic parity/timeline.
run(sys.executable, str(SCRIPTS / "validate_lesson_plan_markdown.py"), "--knowledge-root", str(COURSE), "--report", "/tmp/tde11-markdown-parity.json")
run(sys.executable, str(SCRIPTS / "resolve_course_timeline_hours.py"), "--knowledge-root", str(COURSE))

# Seal-safe sequence: provisional runtime without stale plan payload -> full validation -> reseal -> normal runtime.
import build_runtime_course_package as runtime  # noqa: E402
runtime.project_runtime_lesson_plan_payload = lambda root: {"status": "PROVISIONAL_SKIP"}
result = runtime.build(COURSE)
if result.get("status") != "PASS":
    raise SystemExit(f"provisional runtime failed: {result}")
print("PROVISIONAL_RUNTIME_PASS")

run(sys.executable, str(SCRIPTS / "validate_all_lesson_plans.py"), "--knowledge-root", str(COURSE), "--commit-sha", COMMIT_SHA, "--report", "/tmp/tde11-lesson-plan-validation.json")
report = json.loads(Path("/tmp/tde11-lesson-plan-validation.json").read_text(encoding="utf-8"))
assert report["status"] == "PASS", report
assert report["summary"]["packages"] == 88, report["summary"]
assert report["summary"]["markdown_packages"] == 88, report["summary"]
assert report["summary"]["lesson_hours"] == 172, report["summary"]
assert report["summary"]["failure_records"] == 0, report["summary"]
assert report["summary"]["warning_records"] == 0, report["summary"]

run(sys.executable, str(SCRIPTS / "finalize_lesson_plan_production.py"), "--knowledge-root", str(COURSE), "--validation-report", "/tmp/tde11-lesson-plan-validation.json", "--expected-head", COMMIT_SHA)
run(sys.executable, str(SCRIPTS / "build_runtime_course_package.py"), "build", "--knowledge-root", str(COURSE))

reports_dir = Path("/tmp/tde11-teacher-guides")
reports_dir.mkdir(exist_ok=True)
for theme in ("TEMA_01", "TEMA_02", "TEMA_03", "TEMA_04"):
    out = reports_dir / f"{theme}.json"
    run(sys.executable, str(SCRIPTS / "validate_teacher_guide.py"), "--manifest", f"courses/TDE_11/teacher_guide/{theme}/teacher_guide.json", "--report", str(out))
    guide_report = json.loads(out.read_text(encoding="utf-8"))
    assert guide_report["status"] == "PASS_WITH_WARNINGS", (theme, guide_report["status"])
    assert not guide_report["failures"], (theme, guide_report["failures"])

t4 = json.loads((reports_dir / "TEMA_04.json").read_text(encoding="utf-8"))
assert t4["sections_checked"] == 7, t4
assert len(t4["outcomes_covered"]) == 16, t4
assert t4["core_instruction_hours"] == 43, t4
messages = "\n".join(w["message"] for w in t4["warnings"])
for resolved in ("T4_ISSUE_READING_PLAN_SEQUENCE_OUTCOME_MISMATCH", "T4_ISSUE_LP_YAZMA_P04_OUTCOME_MISMATCH"):
    assert resolved not in messages, (resolved, messages)
for required in ("T4_ISSUE_TDE3_4_EXTERNAL_RUBRIC", "T4_ISSUE_TDE4_4_EXTERNAL_RUBRIC", "T4_ISSUE_EXTERNAL_MULTIMODAL_MEDIA"):
    assert required in messages, (required, messages)
print("THEME4_GUIDE_SUMMARY", json.dumps({k: t4[k] for k in ("status", "sections_checked", "unique_unit_ids", "unique_item_ids", "core_instruction_hours")}, ensure_ascii=False))

for validator in ("validate_package_topology.py", "validate_grounded_references.py", "validate_classroom_adaptations.py", "validate_closure_time_budgets.py"):
    run(sys.executable, str(SCRIPTS / validator), "--knowledge-root", str(COURSE))

# Runtime is derived; source alignment commit should not include runtime build artifacts.
run("git", "checkout", "--", "courses/TDE_11/runtime")

# Remove this temporary generator before committing. Workflow file is removed later through the repository connector.
Path(__file__).unlink()

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "-A", "--", ".tde11-theme4-finalize.py", "courses/TDE_11/teacher_guide/TEMA_04", "courses/TDE_11/generated/lesson_plans/TEMA_04/BLOCK_T4_01_OKUMA", "courses/TDE_11/generated/lesson_plans/TEMA_04/BLOCK_T4_04_YAZMA/BLOCK_T4_04_YAZMA_P04.json", "courses/TDE_11/generated/lesson_plans/TEMA_04/BLOCK_T4_04_YAZMA/BLOCK_T4_04_YAZMA_P04.md", "courses/TDE_11/planning/lesson_plan_production_plan.json", "courses/TDE_11/planning/lesson_plan_validation_seal.json", "courses/TDE_11/planning/course_timeline.json")
run("git", "diff", "--cached", "--stat")
if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
    raise SystemExit("No final changes to commit")
run("git", "commit", "-m", "feat(TDE11): complete Theme 4 teacher guide and repair plan alignment")
run("git", "push", "origin", f"HEAD:{BRANCH}")
