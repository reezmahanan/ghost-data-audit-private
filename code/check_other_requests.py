import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

requests = list(csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8')))

for r in requests:
    cid_num = int(r['case_id'].split('_')[1])
    if cid_num in range(530, 545):
        continue
    txt = r['request_text']
    # Check if text does NOT contain common deletion words in English, French, Spanish, German, Japanese, Portuguese, Korean, Italian
    txt_l = txt.lower()
    del_words = [
        'delet', 'eras', 'clos', 'remov', 'supprim', 'elimin', 'lösch', '削除', 'borr', 'effac',
        'exclusão', 'excluir', 'cancelar', 'fermer', 'cancella', 'schließen', 'entfern', 'quitar',
        'eliminação', 'supressão', 'apagar', 'destruir', 'destroy', 'purge', 'expung', 'wipe',
        '삭제', '해지', '탈퇴', '폐쇄', 'suppression'
    ]
    if not any(w in txt_l for w in del_words):
        print(f"Check {r['case_id']}: {txt}")
