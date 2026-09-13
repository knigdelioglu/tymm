#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT=Path('courses/TDE_11')

def read(path: Path) -> dict[str,Any]:
    return json.loads(path.read_text(encoding='utf-8'))

def write(path: Path, obj: dict[str,Any]) -> None:
    path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

def sentence(value: Any, fallback: str) -> str:
    s=' '.join(str(value or '').split()).strip()
    s=s.rstrip(' .;:')
    return s or fallback.rstrip(' .;:')

def lower_first(s: str) -> str:
    if not s: return s
    return s[0].lower()+s[1:]

def activity_catalog() -> dict[str,dict[str,Any]]:
    book=read(ROOT/'textbook_map.json')
    out={}
    for theme in book.get('themes',[]):
        for section in theme.get('sections',[]):
            for activity in section.get('activities',[]):
                aid=activity.get('activity_id')
                if aid:
                    out[aid]={**activity,'section_title':section.get('section_title')}
    return out

catalog=activity_catalog()
for path in sorted((ROOT/'generated/lesson_plans').rglob('*.json')):
    plan=read(path)
    domain='okuma'
    bid=str(plan.get('block_id',''))
    if 'KONUSMA' in bid: domain='konuşma'
    elif 'DINLEME' in bid: domain='dinleme/izleme'
    elif 'YAZMA' in bid: domain='yazma'

    plan['plan_summary']=re.sub(
        r'TDE\d\.\d\s+çıktısına yönelik',
        'ilgili öğrenme çıktısına yönelik',
        str(plan.get('plan_summary','')),
    )
    plan['teacher_notes']=str(plan.get('teacher_notes','')).replace('canonical öğrenme çıktılarına','tanımlı öğrenme çıktılarına')

    for lesson in plan.get('lessons',[]):
        aids=lesson.get('activity_ids') or []
        activity=catalog.get(aids[0],{}) if aids else {}
        title=sentence(activity.get('exact_title') or activity.get('activity_title') or activity.get('title'), 'Ders kitabı etkinliği')
        action=sentence(activity.get('student_action'), f'{domain} becerisine ilişkin görevi uygular')
        evidence=sentence(activity.get('expected_product_or_evidence') or activity.get('expected_student_evidence') or activity.get('expected_evidence'), 'tamamlanan görev ve gerekçeli kısa kanıt kaydı')
        no=int(lesson.get('lesson_no',1))

        if lesson.get('assessment_scope')=='THEME':
            lesson['objective']='Öğrenci, ders kitabındaki doğrulanmış tema sonu ölçme etkinliğinde dört beceri alanındaki öğrenmesini bağımsız ve gerekçeli yanıtlarla görünür kılar.'
            lesson['teacher_actions']=[
                'Tema sonu ölçme yönergesini ders kitabındaki doğrulanmış biçimiyle uygula; kaynakta bulunmayan ölçüt, puan aralığı veya rubrik açıklaması ekleme.',
                'Öğrencilerin yanıtlarını birbirinden bağımsız üretmesini sağla; gerektiğinde yalnız yönergenin anlaşılmasını destekle, cevabın içeriğini yönlendirme.',
                'Kanıt olarak tema sonu ölçme sorularına verilen gerekçeli yanıtları topla ve hangi beceri alanında güçlü/geliştirilecek kanıt bulunduğunu işaretle.',
                'Doğrulanmamış dış QR dereceli puanlama anahtarının ölçüt×düzey içeriğini puanlama ölçütü olarak kullanma.'
            ]
            lesson['student_actions']=[
                'Tema sonu ölçme sorularını bağımsız biçimde yanıtlar ve gerekli yerlerde gerekçesini yazar.',
                'Yanıtını ilgili metin, görev veya tema boyunca ürettiği somut öğrenme kanıtıyla ilişkilendirir.',
                'Bir güçlü yanıtını ve düzeltilmesi gereken bir yanıtını belirler.',
                'Düzeltme gerektiren yanıt için hangi bilgi veya stratejiye yeniden dönmesi gerektiğini kısa biçimde kaydeder.'
            ]
            lesson['assessment']='Ana ölçme kanıtı, ders kitabındaki tema sonu ölçme sorularına verilen bağımsız ve gerekçeli yanıtlardır; doğrulanmamış dış QR rubrik içeriği değerlendirme ölçütü değildir.'
            lesson['closure']='Öğrenci bir güçlü kanıtını ve geliştireceği bir yanıtını seçer; geliştirme gerekçesini tek cümleyle yazar.'
            continue

        focus='uygulama ve ilk kanıt' if no==1 else 'kanıtı geliştirme ve düzeltme'
        lesson['objective']=f'Öğrenci, “{title}” etkinliğinde {lower_first(action)}; ürettiği kanıtı gerekçelendirerek {focus} sürecini tamamlar.'
        lesson['opening']=f'“{title}” görevinin amacı ile beklenen kanıt açıklanır. Öğrenci, bu ders saatinde hangi {domain} davranışını göstereceğini ve sonunda hangi somut kanıtı bırakacağını kendi cümlesiyle ifade eder.'
        lesson['teacher_actions']=[
            f'“{title}” etkinliğinin yönergesini ders kitabındaki doğrulanmış kapsamla uygula; kaynakta bulunmayan içerik veya değerlendirme ölçütü ekleme.',
            f'Öğrencinin şu görevi yerine getirmesini sağla: {action}. Kararını veya yorumunu somut metin/performans/ürün göstergesiyle gerekçelendirmesini iste.',
            f'“{evidence}” kanıtını topla. Yalnız katılım gözlemini yeterli sayma; öğrencinin neyi nasıl gösterdiğini kaydet.',
            ('İlk denemeden sonra ortak bir güçlü örneği ve geliştirilmesi gereken bir örneği anonim biçimde karşılaştır; öğrencinin ikinci denemesinde neyi değiştireceğini netleştir.' if no>1 else 'Ders sırasında kısa kontrol noktaları kullan; öğrencinin yanlış veya eksik stratejiyi kanıt oluşmadan önce fark edip düzeltmesine fırsat ver.')
        ]
        lesson['student_actions']=[
            action+'.',
            'Kararını, yorumunu veya ürün tercihini somut kaynak göstergesiyle gerekçelendirir.',
            'Ürettiği kanıtı yönergeye göre kontrol eder; eksik veya belirsiz kısmı düzeltir.',
            ('İlk kanıtı ile düzeltilmiş kanıtı karşılaştırıp hangi değişikliğin sonucu iyileştirdiğini açıklar.' if no>1 else 'Kapanışta bir güçlü kanıtını ve bir geliştirme adımını kısa biçimde kaydeder.')
        ]
        lesson['assessment']=f'Ana ölçme kanıtı “{evidence}”dir. Geri bildirim, bu kanıtın doğruluğu, gerekçesi ve hedeflenen {domain} becerisine uygunluğu üzerinden verilir.'
        lesson['closure']=f'Öğrenci “{evidence}” kanıtına bakarak bir güçlü yönünü ve bir sonraki uygulamada yapacağı tek somut değişikliği yazar.'

    write(path,plan)
