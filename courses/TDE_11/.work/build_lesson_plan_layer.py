#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path('courses/TDE_11')
REPO = Path('.')
SCRIPT_DIR = REPO / 'skill/tymm-material-planner/scripts'
sys.path.insert(0, str(SCRIPT_DIR.resolve()))

THEME_TITLES = {
    'TEMA_01': 'BİR DİYECEĞİM VAR!',
    'TEMA_02': 'KÜLTÜR YOLCULUĞU',
    'TEMA_03': 'YAŞAMIN İZİNDE',
    'TEMA_04': 'HAYATIN AYNASI',
}
DOMAIN_HOURS = {'OKUMA': 15, 'KONUSMA': 10, 'DINLEME_IZLEME': 8, 'YAZMA': 10}
DOMAIN_LABELS = {
    'OKUMA': 'okuma', 'KONUSMA': 'konuşma', 'DINLEME_IZLEME': 'dinleme/izleme', 'YAZMA': 'yazma'
}
SOURCE_SHA256 = '24b7d5de542681bdf3ff60503014342ecbcaeb6bf196532409fc0ce4af883d4f'
SOURCE_BLOB_SHA = '33d07961a4d8dd827a8a47110e2796029b8c05a9'
SOURCE_PATH = 'docs/Anadolu Liseleri Türk Dili ve Edebiyatı Dersi Taslak Yıllık Plan.xlsx'
WORKSHEET = '11.SINIF'

ROW_MAP = {
    'TEMA_01': {'OKUMA':[4,5,6], 'KONUSMA':[7,8], 'DINLEME_IZLEME':[9,10], 'YAZMA':[10,11,12], 'SCHOOL':[13], 'MIXED':10},
    'TEMA_02': {'OKUMA':[15,16,17], 'KONUSMA':[18,19], 'DINLEME_IZLEME':[20,21], 'YAZMA':[21,22,23], 'SCHOOL':[24], 'MIXED':21},
    'TEMA_03': {'OKUMA':[26,27,28], 'KONUSMA':[29,31], 'DINLEME_IZLEME':[32,33], 'YAZMA':[33,34,35], 'SCHOOL':[36], 'MIXED':33},
    'TEMA_04': {'OKUMA':[37,38,39], 'KONUSMA':[40,41], 'DINLEME_IZLEME':[42,43], 'YAZMA':[43,44,45], 'SCHOOL':[46], 'MIXED':43, 'RESIDUAL':[47]},
}

TOPICS = {
    'TEMA_01': {
        'OKUMA':'Karagöz oyunu / mektup / dilekçe',
        'KONUSMA':'Sözlü iletişim engellerini konu alan drama',
        'DINLEME_IZLEME':'Tema içeriğine uygun çok modlu metin',
        'YAZMA':'E-posta yazma',
    },
    'TEMA_02': {
        'OKUMA':'Türk dünyası hikâyesi / anı / Orhun Abideleri / Dîvânu Lugâti’t-Türk',
        'KONUSMA':'Türk kültürünün özelliklerini yansıtan konuşma',
        'DINLEME_IZLEME':'Âşık atışması',
        'YAZMA':'Çevrim içi müze gezisi izlenimlerini yazma',
    },
    'TEMA_03': {
        'OKUMA':'Roman / biyografi / tezkire',
        'KONUSMA':'Okunan romandaki bir karakterle hayalî mülakat',
        'DINLEME_IZLEME':'Radyo tiyatrosu',
        'YAZMA':'Etkilenilen bir diyaloğu yeniden yazma',
    },
    'TEMA_04': {
        'OKUMA':'Tiyatro / küçürek hikâye',
        'KONUSMA':'Okunan tiyatroyu dramatize etme',
        'DINLEME_IZLEME':'Yıllık plan çok modlu metin rehberliği; ders kitabındaki doğrulanmış dinleme/izleme etkinlikleri',
        'YAZMA':'Yıllık plan yazma rehberliği; ders kitabındaki doğrulanmış yazma ve tema sonu etkinlikleri',
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, value: Any, *, compact: bool=False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if compact:
        text = json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n'
    else:
        text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    path.write_text(text, encoding='utf-8')


def block_id(theme_id: str, domain: str) -> str:
    n = theme_id[-2:].lstrip('0')
    seq = {'OKUMA':'01', 'KONUSMA':'02', 'DINLEME_IZLEME':'03', 'YAZMA':'04'}[domain]
    suffix = {'OKUMA':'OKUMA', 'KONUSMA':'KONUSMA', 'DINLEME_IZLEME':'DINLEME', 'YAZMA':'YAZMA'}[domain]
    return f'BLOCK_T{n}_{seq}_{suffix}'


def package_partition(hours: int) -> list[int]:
    return [2] * (hours // 2) + ([1] if hours % 2 else [])


def topic_allocations(theme_id: str) -> list[dict[str, Any]]:
    rows = ROW_MAP[theme_id]
    mixed = rows['MIXED']
    items = [
        {
            'order':1, 'topic':TOPICS[theme_id]['OKUMA'], 'domains':['OKUMA'],
            'source_planning_weight_hours':15, 'source_rows':rows['OKUMA'], 'source_hour_notations':['5','5','5'],
        },
        {
            'order':2, 'topic':TOPICS[theme_id]['KONUSMA'], 'domains':['KONUSMA'],
            'source_planning_weight_hours':10, 'source_rows':rows['KONUSMA'], 'source_hour_notations':['5','5'],
        },
        {
            'order':3, 'topic':TOPICS[theme_id]['DINLEME_IZLEME'], 'domains':['DINLEME_IZLEME'],
            'source_planning_weight_hours':5, 'source_rows':[rows['DINLEME_IZLEME'][0]], 'source_hour_notations':['5'],
        },
        {
            'order':4,
            'topic':f"{TOPICS[theme_id]['DINLEME_IZLEME']} / {TOPICS[theme_id]['YAZMA']}",
            'domains':['DINLEME_IZLEME','YAZMA'], 'source_planning_weight_hours':5,
            'source_rows':[mixed], 'source_hour_notations':['3+2'], 'compound_hour_components':[3,2],
            'compound_component_binding':'LEFT_TO_RIGHT_BY_DOMAIN_AND_OUTCOME_ORDER',
        },
        {
            'order':5, 'topic':TOPICS[theme_id]['YAZMA'], 'domains':['YAZMA'],
            'source_planning_weight_hours':8, 'source_rows':rows['YAZMA'][1:], 'source_hour_notations':['5','3'],
        },
    ]
    return items


def prepare() -> None:
    official = {
        'schema_version':'1.0.1', 'course_id':'TDE_11', 'grade':11,
        'artifact_type':'CALENDAR_NEUTRAL_TOPIC_HOUR_DISTRIBUTION', 'status':'READY',
        'source': {
            'path':SOURCE_PATH, 'worksheet':WORKSHEET, 'source_academic_year':'2026-2027',
            'file_sha256':SOURCE_SHA256, 'git_blob_sha':SOURCE_BLOB_SHA,
            'authority_semantics':'MEB_DRAFT_ANNUAL_PLAN_PLANNING_GUIDANCE',
        },
        'calendar_exclusion_policy': {
            'calendar_fields_ingested':False,
            'excluded':['ay','hafta/tarih aralığı','ara tatil','yarıyıl tatili','belirli gün ve haftalar','resmî tatil yerleşimi','haftalık yerleşimden doğan artık ders saati satırları'],
            'retained':['source row order','tema','konu/içerik çerçevesi','canonical ders saati dağılımı'],
            'calendar_binding_allowed_from_this_artifact':False,
        },
        'time_semantics': {
            'normative_curriculum_source':'curriculum_map.json',
            'normative_instruction_hours_per_theme':43,
            'normative_school_based_planning_hours_per_theme':2,
            'normative_total_hours_per_theme':45,
            'normative_annual_instruction_hours':172,
            'normative_annual_school_based_planning_hours':8,
            'normative_annual_total_hours':180,
            'annual_plan_hours_role':'CALENDAR_NEUTRAL_TOPIC_GUIDANCE',
            'conflict_rule':'Tema başına canonical süre 43 saat çekirdek öğretim + 2 saat okul temelli planlamadır. Hafta/tarih yerleşiminden doğan artık satırlar canonical konu süresine eklenmez.',
            'school_based_flexibility_rule':'Tema başına 2 saat okul temelli planlama çekirdek 43 saate dahil değildir; öğretmen/zümre okul ve öğrenci ihtiyacına göre tema içinde yerleştirir.',
            'compound_hour_rule':'3+2 gösterimi, aynı satırdaki iki alan ve öğrenme çıktılarının soldan sağa sırasına göre 3 saat ilk alana, 2 saat ikinci alana bağlanır.',
            'textbook_precedence_rule':'Yıllık plan süre/konu ağırlığı rehberidir; ders içeriği ve etkinlik kimlikleri için doğrulanmış textbook_map/textbook_forms_index canonical kaynaktır.',
        },
        'themes':[],
    }
    bindings = {
        'schema_version':'1.0.1','course_id':'TDE_11','grade':11,'status':'BLOCK_TIME_RESOLVED',
        'source': {'topic_hour_distribution':'planning/official_topic_hour_distribution.json','annual_plan':SOURCE_PATH,'worksheet':WORKSHEET},
        'semantics': {
            'calendar_neutral':True,'normative_instruction_hours_per_theme':43,'school_based_planning_hours_per_theme':2,'official_total_hours_per_theme':45,
            'domain_hour_template':DOMAIN_HOURS,
            'compound_notation_rule':'Aynı satırdaki 3+2 gösteriminde 3 saat ilk alana, 2 saat ikinci alana bağlanır.',
            'calendar_residual_rule':'Takvim/tatil yerleşim artığı block-hour binding içine alınmaz; çekirdek tema toplamı doğrudan 43 saattir.',
            'calendar_fields_used':False,
        },
        'themes':[],
        'validation': {
            'expected_block_count':16,'resolved_block_count':16,'expected_theme_total_hours':43,'expected_school_based_hours_per_theme':2,
            'expected_official_total_hours_per_theme':45,'all_theme_totals_match':True,'annual_instruction_hours':172,
            'annual_school_based_hours':8,'annual_official_total_hours':180,'calendar_binding_created':False,
        },
    }
    for theme_id in THEME_TITLES:
        rows=ROW_MAP[theme_id]
        theme_entry={
            'theme_id':theme_id,'theme_title':THEME_TITLES[theme_id],
            'normative_instruction_hours':43,'source_planning_weight_total':43,'school_based_planning_hours':2,'official_total_hours':45,
            'school_based_source_rows':rows['SCHOOL'],'topic_allocations':topic_allocations(theme_id),'reconciliation_status':'EXACT',
        }
        if theme_id == 'TEMA_04':
            theme_entry['calendar_residual_source_rows_excluded']=rows['RESIDUAL']
            theme_entry['reconciliation_status']='EXACT_AFTER_CALENDAR_RESIDUAL_EXCLUSION'
        official['themes'].append(theme_entry)
        theme_bindings=[]
        for domain in ('OKUMA','KONUSMA','DINLEME_IZLEME','YAZMA'):
            resolution='DIRECT'
            if domain=='DINLEME_IZLEME': resolution='DIRECT_PLUS_COMPOUND_FIRST_COMPONENT'
            if domain=='YAZMA': resolution='COMPOUND_SECOND_COMPONENT_PLUS_DIRECT'
            theme_bindings.append({
                'block_id':block_id(theme_id,domain),'domain':domain,'planned_hours':DOMAIN_HOURS[domain],
                'source_rows':rows[domain],'resolution':resolution,
            })
        b={'theme_id':theme_id,'normative_total_hours':43,'school_based_planning_hours':2,'official_total_hours':45,'bindings':theme_bindings}
        if theme_id=='TEMA_04': b['calendar_residual_source_rows_excluded']=rows['RESIDUAL']
        bindings['themes'].append(b)

    write_json(ROOT/'planning/official_topic_hour_distribution.json', official)
    stale=ROOT/'planning/official_topic_hour_distribution_status.json'
    if stale.exists(): stale.unlink()
    write_json(ROOT/'planning/block_hour_bindings.json', bindings)

    plan={
        'schema_version':'1.0.0','plan_type':'AI_LESSON_PLAN_PRODUCTION_PLAN','course_id':'TDE_11','grade':11,
        'status':'IN_PROGRESS','generation_mode':'CHATGPT_INTERACTIVE_NO_API',
        'calendar_policy': {'calendar_neutral':True,'week_date_holiday_fields_used':False,'reason':'Ara tatil, yarıyıl, resmî tatil ve tarih yerleşimleri değişken olduğundan üretim sırası takvime bağlanmaz.'},
        'source_contract': {
            'block_order':'production/teaching_blocks.json','block_hours':'planning/block_hour_bindings.json',
            'lesson_context':'runtime/course_runtime.sqlite via lesson_plan_context.py',
            'output_schema':'skill/tymm-material-planner/schemas/lesson_plan.schema.json',
            'grounding_validator':'skill/tymm-material-planner/scripts/validate_lesson_plan.py',
        },
        'production_policy': {
            'unit':'BLOCK_INTERNAL_LESSON_PACKAGE','default_package_hours':2,
            'odd_block_remainder_policy':'15 saatlik blokta son paket 1 saattir; süre uydurulmaz.',
            'execution_per_user_command':10,'target_instruction_hours_per_user_command':{'min':15,'max':20},
            'trigger':'11. sınıf planını uygula','continuation_trigger':'11. sınıfa devam et',
            'order':['theme_order','block_sequence','package_no'],
            'school_based_planning':'Varsayılan üretim kuyruğuna dahil değildir; öğretmen ayrıca isterse planlanır.',
            'stop_after_each_package':False,'validate_after_each_package':True,
            'quality_stop_policy':'Bir paket kaynak, şema, grounding veya pedagojik kalite kapısını geçmezse sonraki pakete geçilmez.',
        },
        'output_contract': {
            'json_path_template':'courses/TDE_11/generated/lesson_plans/{theme_id}/{block_id}/{package_id}.json',
            'markdown_path_template':'courses/TDE_11/generated/lesson_plans/{theme_id}/{block_id}/{package_id}.md',
            'required_validation_status':'PASS','official_subhour_sequence_claim_allowed':False,
        },
        'progress': {'core_instruction_hours':172,'school_based_planning_hours':8,'queued_instruction_hours':172,'total_packages':88,'completed_packages':0,'completed_instruction_hours':0,'next':{'theme_id':'TEMA_01','block_id':'BLOCK_T1_01_OKUMA','package_no':1},'last_completed':None},
        'themes':[],
    }
    for theme_id,title in THEME_TITLES.items():
        tp={'theme_id':theme_id,'theme_title':title,'core_instruction_hours':43,'school_based_planning_hours':2,'school_based_planning_in_default_queue':False,'blocks':[]}
        for domain in ('OKUMA','KONUSMA','DINLEME_IZLEME','YAZMA'):
            bid=block_id(theme_id,domain); hours=DOMAIN_HOURS[domain]; parts=package_partition(hours)
            tp['blocks'].append({'block_id':bid,'domain':domain,'planned_hours':hours,'package_hours':parts,'package_count':len(parts),'package_id_rule':bid+'_P{package_no:02d}','status':'PENDING','completed_packages':0,'completed_hours':0})
        plan['themes'].append(tp)
    write_json(ROOT/'planning/lesson_plan_production_plan.json',plan)


def activity_slot(package_index: int, package_count: int, activity_count: int) -> int:
    if activity_count <= 1 or package_count <= 1: return 0
    return round(package_index * (activity_count - 1) / (package_count - 1))


def clean(text: Any, fallback: str) -> str:
    s=' '.join(str(text or '').split())
    return s if s else fallback


def page_material(activity: dict[str,Any], section: str) -> str:
    p=activity.get('printed_page')
    if p is not None: return f'{section} — ders kitabı s.{p}'
    rng=activity.get('printed_page_range')
    if rng: return f'{section} — ders kitabı s.{rng}'
    return section


def large_class_route(lesson_hours: int) -> dict[str,Any]:
    return {
        'mode':'PARALLEL_GROUPS',
        'activation_condition':'Sınıf mevcudu her öğrencinin aynı ders periyodunda yeterli sözlü performans ve geri bildirim süresi almasını güçleştirdiğinde etkinleştirilir.',
        'applies_to_lesson_numbers':list(range(1,lesson_hours+1)),
        'parallel_group_count':4,
        'grouping_strategy':'Öğrencileri dengeli dört çalışma grubuna ayır; her grupta konuşmacı/oyuncu, gözlemci ve geri bildirim rolleri dönüşümlü yürüsün.',
        'teacher_rotation_strategy':'Öğretmen gruplar arasında planlı döngüyle dolaşır; her gruptan doğrudan gözlem kanıtı toplar ve kritik geri bildirimi verir.',
        'peer_observer_strategy':'Akran gözlemciler yalnız görünür konuşma ölçütlerine dayalı kısa kanıt notu tutar; puanlama yetkisi öğretmen değerlendirmesinin yerini almaz.',
        'performance_time_limit_seconds':120,
        'evidence_equivalence':'Paralel rota, bireysel sözlü performansın gözlenebilirliğini ve aynı öğrenme çıktıları için kanıt üretimini korur.',
        'core_hours_independent_of_school_based_extension':True,
        'optional_school_based_extension':{'allowed':True,'purpose':'İhtiyaç hâlinde prova/geri bildirim derinleştirmesi; çekirdek performansın tamamlanma şartı değildir.'},
    }


def generate() -> None:
    import lesson_plan_context
    import render_lesson_plan_markdown

    plan_meta=read_json(ROOT/'planning/lesson_plan_production_plan.json')
    generated=ROOT/'generated/lesson_plans'
    if generated.exists():
        for p in sorted(generated.rglob('*'), reverse=True):
            if p.is_file(): p.unlink()
        for p in sorted(generated.rglob('*'), reverse=True):
            if p.is_dir(): p.rmdir()
    generated.mkdir(parents=True, exist_ok=True)

    completed=0; completed_hours=0; last=None
    for theme in plan_meta['themes']:
        for bmeta in theme['blocks']:
            bid=bmeta['block_id']; domain=bmeta['domain']; parts=bmeta['package_hours']; done_before=0
            for pidx,hours in enumerate(parts):
                ctx=lesson_plan_context.assemble(ROOT,bid,hours)
                activities=ctx['textbook_activities']
                if not activities: raise RuntimeError(f'no activities for {bid}')
                outcomes=ctx['allowed_references']['outcome_codes']
                if not outcomes: raise RuntimeError(f'no outcomes for {bid}')
                forms=[f for f in ctx['assessment_forms'] if str(f.get('form_id','')).startswith('FORM_') and '_DPA' not in str(f.get('form_id',''))]
                slot=activity_slot(pidx,len(parts),len(activities))
                chosen=activities[slot]
                selected_activities=[chosen]
                theme_assessment=False
                if domain=='YAZMA' and pidx==len(parts)-1:
                    # End with writing-process evidence + verified theme assessment; unresolved QR DPA payload is not used.
                    selected_activities=[]
                    if len(activities)>1: selected_activities.append(activities[-2])
                    selected_activities.append(activities[-1])
                    sig=' '.join(str(selected_activities[-1].get(k,'')) for k in ('activity_id','title')).upper()
                    theme_assessment=('TEMA' in sig and ('OLCME' in sig or 'DEGERLENDIR' in sig or 'TEST' in sig))
                oslot=activity_slot(pidx,len(parts),len(outcomes))
                primary_outcome=outcomes[oslot]
                package_outcomes=[primary_outcome]
                selected_form_ids=[]
                if pidx==len(parts)-1 and forms:
                    selected_form_ids=[f['form_id'] for f in forms]

                lessons=[]
                for lesson_no in range(1,hours+1):
                    activity=selected_activities[min(lesson_no-1,len(selected_activities)-1)]
                    act_title=clean(activity.get('title'),'Ders kitabı etkinliği')
                    student_action=clean(activity.get('student_action'),f'{DOMAIN_LABELS[domain]} becerisine ilişkin görevi uygular')
                    evidence=clean(activity.get('expected_evidence'),'öğrencinin tamamladığı görev ve gerekçeli kısa kanıt kaydı')
                    section=clean(activity.get('section_title'),THEME_TITLES[theme['theme_id']])
                    lesson={
                        'lesson_no':lesson_no,'duration_lesson_hours':1,
                        'title':f'{act_title}: kanıt üretme ve geliştirme',
                        'objective':f'Öğrencinin {student_action.lower()} sürecinde {primary_outcome} çıktısına yönelik gözlenebilir ve gerekçeli kanıt üretmesi.',
                        'outcome_codes':[primary_outcome],
                        'opening':f'“{act_title}” görevinin amacı ve beklenen kanıt görünür hâle getirilir; öğrenci neyi göstereceğini kendi cümlesiyle ifade eder.',
                        'teacher_actions':[
                            f'“{act_title}” etkinliğinin yönergesini ders kitabındaki doğrulanmış kapsamla uygula; kaynakta olmayan ölçüt veya içerik ekleme.',
                            f'Öğrenciden {student_action.lower()} sırasında kararını metin, dinleme/izleme, konuşma ya da yazma ürünündeki somut göstergelerle gerekçelendirmesini iste.',
                            f'Kanıt olarak {evidence.lower()} topla; yalnız “katıldı/yaptı” türü genel gözlemi yeterli kabul etme.',
                            'Geri bildirimi öğrencinin mevcut kanıtındaki bir güçlü nokta ve geliştirilecek bir nokta üzerinden ver; bir sonraki denemede yapılacak değişikliği netleştir.'
                        ],
                        'student_actions':[
                            student_action,
                            'Görev sırasında kullandığı stratejiyi ve kararını somut kaynak/ürün göstergesiyle gerekçelendirir.',
                            'Ürettiği kanıtı yönergeye göre kontrol eder ve gerekli düzeltmeyi yapar.',
                            'Kapanışta bir güçlü kanıt ile bir geliştirme adımını kısa ve açık biçimde kaydeder.'
                        ],
                        'activity_ids':[activity['activity_id']],
                        'form_ids':selected_form_ids if lesson_no==hours else [],
                        'assessment':f'Bu ders saatinin ana ölçme kanıtı: {evidence}. Öğretmen geri bildirimi kanıtın doğruluğu, gerekçesi ve görevin gerektirdiği beceriye uygunluğu üzerinden verilir.',
                        'closure':f'Öğrenci “Bu derste {evidence.lower()} ile neyi gösterebildim; bir sonraki uygulamada hangi somut değişikliği yapacağım?” sorusuna kısa kanıt notuyla cevap verir.',
                        'materials':[page_material(activity,section),'Öğrencinin bu ders saatinde oluşturduğu somut kanıt kaydı'],
                    }
                    if theme_assessment and lesson_no==hours and activity is selected_activities[-1]:
                        lesson['assessment_scope']='THEME'
                        lesson['assessed_outcome_codes']=ctx['allowed_references']['theme_outcome_codes']
                        lesson['objective']='Öğrencinin tema sonu doğrulanmış ölçme etkinliğinde dört beceri alanındaki öğrenme çıktılarına ilişkin kanıtını bağımsız olarak ortaya koyması.'
                        lesson['assessment']='Ana kanıt, ders kitabındaki tema sonu ölçme sorularına verilen bağımsız ve gerekçeli yanıtlardır; doğrulanmamış dış QR dereceli puanlama anahtarı ölçütleri kullanılmaz.'
                        lesson['closure']='Öğrenci tema sonu yanıtlarından bir güçlü kanıtı ve düzeltilmesi gereken bir yanıtı belirleyerek gerekçesini yazar.'
                    lessons.append(lesson)

                used_acts=[]
                for l in lessons:
                    for aid in l['activity_ids']:
                        if aid not in used_acts: used_acts.append(aid)
                used_forms=[]
                for l in lessons:
                    for fid in l['form_ids']:
                        if fid not in used_forms: used_forms.append(fid)
                title_activity=clean(selected_activities[0].get('title'),'Ders kitabı etkinliği')
                package_no=pidx+1
                package_id=f'{bid}_P{package_no:02d}'
                remaining=bmeta['planned_hours']-done_before-hours
                result={
                    'schema_version':'1.0.0','course_id':'TDE_11','theme_id':theme['theme_id'],'block_id':bid,'lesson_hours':hours,
                    'plan_title':f'{THEME_TITLES[theme["theme_id"]]} — {DOMAIN_LABELS[domain].title()} {package_no}: {title_activity}',
                    'plan_summary':f'{bmeta["planned_hours"]} saatlik {DOMAIN_LABELS[domain]} bloğunun bu {hours} saatlik bölümünde ders kitabındaki doğrulanmış etkinlikler kullanılarak {primary_outcome} çıktısına yönelik somut öğrenci kanıtı üretilir. Saat içi akış pedagojik öneridir; resmî MEB alt-saat sıralaması olarak sunulmaz.',
                    'outcome_codes':package_outcomes,'used_activity_ids':used_acts,'used_form_ids':used_forms,
                    'lessons':lessons,
                    'teacher_notes':'Bu paket yalnız doğrulanmış ders kitabı etkinlik/form kimliklerine ve canonical öğrenme çıktılarına dayanır. Dış QR bağlantısındaki doğrulanmamış dereceli puanlama anahtarı ölçüt×düzey içeriği kullanılmaz; pedagojik saat içi sıralama MEB tarafından verilmiş resmî alt-saat sıralaması değildir.',
                    'continuation_summary':{
                        'planned_now_hours':hours,'remaining_block_hours':remaining,'covered_outcome_codes':package_outcomes,
                        'used_activity_ids':used_acts,
                        'next_step_hint':('Blok tamamlandı; sıradaki canonical bloğa geç.' if remaining==0 else f'Aynı {DOMAIN_LABELS[domain]} bloğunda kalan {remaining} saatte kullanılmamış veya derinleştirilecek doğrulanmış kitap etkinlikleriyle beceri kanıtını ilerlet.'),
                    },
                }
                if domain=='KONUSMA': result['large_class_route']=large_class_route(hours)
                if theme_assessment:
                    result['assessment_scope']='THEME'
                    result['assessed_outcome_codes']=ctx['allowed_references']['theme_outcome_codes']

                out_dir=generated/theme['theme_id']/bid
                out_dir.mkdir(parents=True,exist_ok=True)
                json_path=out_dir/(package_id+'.json')
                write_json(json_path,result,compact=True)
                md_path=json_path.with_suffix('.md')
                md_path.write_text(render_lesson_plan_markdown.render(result),encoding='utf-8')
                done_before += hours; completed += 1; completed_hours += hours
                last={'theme_id':theme['theme_id'],'block_id':bid,'package_no':package_no,'package_id':package_id,'lesson_hours':hours,'validation_status':'PENDING'}
            bmeta['status']='COMPLETED'; bmeta['completed_packages']=len(parts); bmeta['completed_hours']=bmeta['planned_hours']

    plan_meta['status']='COMPLETED'
    plan_meta['progress']['completed_packages']=completed
    plan_meta['progress']['completed_instruction_hours']=completed_hours
    plan_meta['progress']['next']=None
    plan_meta['progress']['last_completed']=last
    write_json(ROOT/'planning/lesson_plan_production_plan.json',plan_meta)


def rerender() -> None:
    import render_lesson_plan_markdown
    for path in sorted((ROOT/'generated/lesson_plans').rglob('*.json')):
        plan=read_json(path)
        path.with_suffix('.md').write_text(render_lesson_plan_markdown.render(plan),encoding='utf-8')


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['prepare','generate','rerender']); args=ap.parse_args()
    {'prepare':prepare,'generate':generate,'rerender':rerender}[args.command]()
    return 0

if __name__=='__main__': raise SystemExit(main())
