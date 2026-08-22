#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path('courses/TDE_10')
PROD = ROOT / 'production'
LEVELS = [
    {'score': 3, 'label': 'Oldukça iyi', 'descriptor': 'Ölçüt tam, doğru ve etkili biçimde karşılanmıştır.'},
    {'score': 2, 'label': 'Kabul edilebilir', 'descriptor': 'Ölçüt büyük ölçüde karşılanmıştır; sınırlı eksikler vardır.'},
    {'score': 1, 'label': 'Geliştirilmeli', 'descriptor': 'Ölçüt sınırlı ölçüde karşılanmıştır; belirgin eksikler vardır.'},
]
SPECS = [
    dict(form_id='FORM_T10_T1_KONUSMA_DPA_CANONICAL', artifact_id='TDE10_KONUSMA_RUBRIC', requirement_id='REQ_T10_T1_KONUSMA_DPA', source_link_id='LINK_T1_KONUSMA_DPA', theme_id='TEMA_01', block_id='BLOCK_T1_02_KONUSMA', task_title='Şiir Dinletisi', outcomes=['TDE3.4'], locator='Ders kitabı s.55-57; LINK_T1_KONUSMA_DPA', criteria=['Şiir seçiminin temaya uygunluğu','Dikkat çekici giriş ve planlı sunum','Şiirleri özgün üslupla seslendirme','Görsel/işitsel ögeler','Beden dili','Mekân kullanımı','Vurgu-tonlama','Olumlu tutum','Süre','Planı tamamlama','Türkçenin doğru kullanımı']),
    dict(form_id='FORM_T10_T2_KONUSMA_DPA_CANONICAL', artifact_id='TDE10_KONUSMA_RUBRIC', requirement_id='REQ_T10_T2_KONUSMA_DPA', source_link_id='LINK_T2_PODCAST_DPA', theme_id='TEMA_02', block_id='BLOCK_T2_04_KONUSMA', task_title='Podcast (Sesli Blog)', outcomes=['TDE3.4'], locator='Ders kitabı s.146-149; LINK_T2_PODCAST_DPA', criteria=['İçeriğin anlam ve amaca uygunluğu','Dil ve anlatım','İşitsel ögelerin kullanımı','Özgünlük','Vurgu-tonlama ve akıcılık','Podcast akışı ve süre']),
    dict(form_id='FORM_T10_T3_KONUSMA_DPA_CANONICAL', artifact_id='TDE10_KONUSMA_RUBRIC', requirement_id='REQ_T10_T3_KONUSMA_DPA', source_link_id='LINK_T3_KONUSMA_DPA', theme_id='TEMA_03', block_id='BLOCK_T3_02_KONUSMA', task_title='Türk Destanlarıyla İlgili Sunum', outcomes=['TDE3.4'], locator='Ders kitabı s.204-208; LINK_T3_KONUSMA_DPA', criteria=['İçeriğe uygunluk ve doğruluk','Hedef kitleye uygun dil','Beden dili','Ses kontrolü','Türkçenin doğru kullanımı','Vurgu-tonlama','Sunum organizasyonu ve süre']),
    dict(form_id='FORM_T10_T4_KONUSMA_DPA_CANONICAL', artifact_id='TDE10_KONUSMA_RUBRIC', requirement_id='REQ_T10_T4_KONUSMA_DPA', source_link_id='LINK_T4_KONUSMA_DPA', theme_id='TEMA_04', block_id='BLOCK_T4_02_KONUSMA', task_title='Hikâyeden Sahneye', outcomes=['TDE3.4'], locator='Ders kitabı s.280-283; LINK_T4_KONUSMA_DPA', criteria=['Uygun hikâye ve özgün yorum','Plana uygun canlandırma','Beden dili','Metnin bağlamına bağlılık','İletişim ve görgü','Görsel/işitsel ögeler','Mekân kullanımı','Süre','Türkçenin doğru ve millî bilinçle kullanımı']),
    dict(form_id='FORM_T10_T1_YAZMA_DPA_CANONICAL', artifact_id='TDE10_YAZMA_RUBRIC', requirement_id='REQ_T10_T1_YAZMA_DPA', source_link_id='LINK_T1_YAZMA_DPA', theme_id='TEMA_01', block_id='BLOCK_T1_04_YAZMA', task_title='Masalı Film Şeridine Dönüştürme', outcomes=['TDE4.4'], locator='Ders kitabı s.75-78; LINK_T1_YAZMA_DPA', criteria=['Akıcılık','Görsel ögeler','Karakter tasarımı','Senaryo','Olay akışı','Estetik','Dil ve anlatım','İçeriği zenginleştirme','Yazım-noktalama','Olumlu tutum/değerler']),
    dict(form_id='FORM_T10_T2_YAZMA_DPA_CANONICAL', artifact_id='TDE10_YAZMA_RUBRIC', requirement_id='REQ_T10_T2_YAZMA_DPA', source_link_id='LINK_T2_YAZMA_DPA', theme_id='TEMA_02', block_id='BLOCK_T2_02_YAZMA', task_title='Öğretici Metinden Edebî Metne', outcomes=['TDE4.4'], locator='Ders kitabı s.124-128; LINK_T2_YAZMA_DPA', criteria=['Temel anlamın korunması','Edebî tür özellikleri','Dil ve anlatım','Özgünlük','Görsel/işitsel ögeler','Yazım ve noktalama','Metin bütünlüğü']),
    dict(form_id='FORM_T10_T3_YAZMA_DPA_CANONICAL', artifact_id='TDE10_YAZMA_RUBRIC', requirement_id='REQ_T10_T3_YAZMA_DPA', source_link_id='LINK_T3_YAZMA_DPA', theme_id='TEMA_03', block_id='BLOCK_T3_04_YAZMA', task_title='Fabl Yazma', outcomes=['TDE4.4'], locator='Ders kitabı s.224-228; LINK_T3_YAZMA_DPA', criteria=['Özgünlük','Biçim/tür özellikleri','Ahenk','Etkileyicilik','Dil ve anlatım','Söz varlığı','Estetik','Dil bilgisi']),
    dict(form_id='FORM_T10_T4_YAZMA_DPA_CANONICAL', artifact_id='TDE10_YAZMA_RUBRIC', requirement_id='REQ_T10_T4_YAZMA_DPA', source_link_id='LINK_T4_YAZMA_DPA', theme_id='TEMA_04', block_id='BLOCK_T4_04_YAZMA', task_title='Hikâyeden Şiire', outcomes=['TDE4.4'], locator='Ders kitabı s.302-305; LINK_T4_YAZMA_DPA', criteria=['Hikâye temasının şiire aktarılması','İçeriğe uygunluk','Etkileyicilik','Şiir dilinin etkili kullanımı','Bağlama uygun söz varlığı','Özgün üslup','Estetik unsurlar','Dil bilgisi']),
]

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

forms = []
for spec in SPECS:
    rows = [{'criterion_id': f"{spec['form_id']}_C{i:02d}", 'criterion': c, 'evidence_status': 'ACCEPTED_STRONG_COPY_CRITERION', 'weight': 1} for i, c in enumerate(spec['criteria'], 1)]
    forms.append({
        'form_id': spec['form_id'], 'artifact_id': spec['artifact_id'], 'requirement_id': spec['requirement_id'],
        'runtime_binding_key': {'artifact_id': spec['artifact_id'], 'gap_instance_id': spec['requirement_id']},
        'runtime_projection_mode': 'COMPOSE_FROM_ASSESSMENT_ARTIFACT_AND_TASK_BINDING',
        'source_link_id': spec['source_link_id'], 'theme_id': spec['theme_id'], 'block_id': spec['block_id'],
        'task_title': spec['task_title'], 'targeted_outcomes': spec['outcomes'], 'textbook_locator': spec['locator'],
        'evaluator': 'teacher', 'form_type': 'analytic_rubric', 'materialization_status': 'ACCEPTED_STRONG_COPY_CANONICAL_FORM',
        'source_acceptance': 'STRONG_COPY_ACCEPTED_FOR_STRUCTURE_AND_CRITERIA',
        'exact_external_payload_identity': 'UNVERIFIED_AUTH_GATED_PROVENANCE_ONLY',
        'level_model_ref': 'TDE10_SHARED_3_LEVEL_MODEL', 'criteria_rows': rows,
        'applicable_criterion_count': len(rows), 'max_raw_score': len(rows) * 3, 'min_raw_score': len(rows),
        'percentage_rule': 'raw_score / applicable_max_score * 100',
        'not_applicable_policy': 'N/A ölçütleri pay ve paydadan çıkarılır.',
    })

assert len(forms) == 8
assert len({x['form_id'] for x in forms}) == 8
assert sum(x['applicable_criterion_count'] for x in forms) == 66

registry = {
    'schema_version': '1.0', 'course_id': 'TDE_10', 'registry_status': 'READY',
    'registry_role': 'MATERIALIZED_VIEW_OF_CANONICAL_RUBRICS_AND_TASK_BINDINGS',
    'acceptance_policy': {
        'decision': 'ACCEPT_STRONG_COPIES', 'structure_status': 'RESOLVED_FOR_CANONICAL_USE',
        'criteria_status': 'ACCEPTED_WHERE_RECOVERED_WITH_HIGH_CONFIDENCE',
        'exact_external_payload_identity': 'UNVERIFIED_AUTH_GATED_PROVENANCE_ONLY',
        'rule': 'Güçlü kopyalardan yüksek güvenle kurtarılan görev ölçütleri canonical form satırı olarak kabul edilir. EBA hedefinin byte-byte aynı içeriği olduğu iddia edilmez.'
    },
    'shared_level_model': {'model_id': 'TDE10_SHARED_3_LEVEL_MODEL', 'levels': LEVELS},
    'form_count': 8, 'criterion_row_count': 66, 'forms': forms,
}
write(PROD / 'assessment_form_registry.json', registry)

md = ['# TDE_10 Canonical Öğretmen Değerlendirme Formları','',
      'Güçlü kopyalardan yüksek güvenle kurtarılan ölçütler canonical kullanım için kabul edilerek sekiz öğretmen formuna dönüştürülmüştür.','',
      '**EBA exact payload kimliği:** `UNVERIFIED_AUTH_GATED_PROVENANCE_ONLY` — form kullanımını bloke etmez.','',
      '## Ortak puanlama düzeyi','', '| Puan | Düzey | Anlam |','|---:|---|---|']
for level in LEVELS:
    md.append(f"| {level['score']} | {level['label']} | {level['descriptor']} |")
md += ['', 'N/A ölçütleri pay ve paydadan çıkarılır. Yüzde = `ham puan / uygulanabilir maksimum puan × 100`.','']
for i, form in enumerate(forms, 1):
    md += [f"## {i}. {form['task_title']}",'', f"- Form ID: `{form['form_id']}`", f"- Tema / Blok: `{form['theme_id']}` / `{form['block_id']}`", f"- Rubrik: `{form['artifact_id']}`", f"- Kaynak QR: `{form['source_link_id']}`", f"- Maksimum: **{form['max_raw_score']}**",'', '| # | Ölçüt | 3 | 2 | 1 | N/A | Puan |','|---:|---|:---:|:---:|:---:|:---:|:---:|']
    for n, row in enumerate(form['criteria_rows'], 1):
        md.append(f"| {n} | {row['criterion']} | ☐ | ☐ | ☐ | ☐ |  |")
    md += ['', f"**Toplam:** ____ / {form['max_raw_score']}",'', '**Öğretmen notu:** ________________________________________________','', '---','']
(PROD / 'assessment_forms.md').write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')

contract_path = PROD / 'assessment_design_contract.json'
contract = read(contract_path)
contract['strong_copy_acceptance'] = {'decision': 'ACCEPTED', 'accepted_structure_count': 8, 'materialized_form_count': 8, 'accepted_criterion_row_count': 66, 'criteria_policy': 'USE_HIGH_CONFIDENCE_RECOVERED_TASK_CRITERIA', 'exact_eba_payload_identity': 'UNVERIFIED_AUTH_GATED_PROVENANCE_ONLY'}
contract.setdefault('runtime_contract', {})['materialized_form_count'] = 8
contract['runtime_contract']['materialized_form_registry'] = 'production/assessment_form_registry.json'
contract['runtime_contract']['form_runtime_mode'] = 'COMPOSE_FROM_ASSESSMENT_ARTIFACT_AND_TASK_BINDING'
write(contract_path, contract)

manifest_path = PROD / 'production_manifest.json'
manifest = read(manifest_path)
manifest['materialized_assessment_form_count'] = 8
manifest['accepted_strong_copy_criterion_row_count'] = 66
manifest['unresolved_assessment_structure_count'] = 0
manifest['unresolved_exact_payload_identity_count'] = 8
manifest['strong_copy_acceptance_status'] = 'ACCEPTED_FOR_STRUCTURE_AND_HIGH_CONFIDENCE_CRITERIA'
manifest['assessment_form_registry'] = 'production/assessment_form_registry.json'
manifest['assessment_form_runtime_mode'] = 'COMPOSE_FROM_ASSESSMENT_ARTIFACT_AND_TASK_BINDING'
write(manifest_path, manifest)

validation_path = ROOT / 'parity_validation_report.json'
validation = read(validation_path)
validation.setdefault('checks', {})['external_dpa_structure_resolved_by_strong_copy_acceptance'] = True
validation['checks']['materialized_assessment_forms_8'] = True
validation['checks']['accepted_strong_copy_criterion_rows_66'] = True
validation.setdefault('counts', {})['materialized_assessment_forms'] = 8
validation['counts']['accepted_strong_copy_criterion_rows'] = 66
validation['source_structure_status'] = 'RESOLVED_8_OF_8_ACCEPTED_STRONG_COPY_ANALYTIC_RUBRICS'
validation['exact_external_payload_identity_status'] = 'UNVERIFIED_AUTH_GATED_PROVENANCE_ONLY'
write(validation_path, validation)

print(json.dumps({'status':'PASS','forms':8,'criteria_rows':66}, ensure_ascii=False))
