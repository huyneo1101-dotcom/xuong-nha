#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cổng kiểm «Xưởng Nhà» — soi bản dựng và nguồn trước khi đẩy lên Pages.

    python3 kiem-xuong-nha.py            soi bản thật trong thư mục app
    python3 kiem-xuong-nha.py --ca       chạy bộ ca, in bảng ca đỏ
    python3 kiem-xuong-nha.py --tu-kiem  dựng từng bản hỏng, đòi đúng ca của nó đỏ

Sáu lối hỏng của app này, cả sáu đều KHÔNG phát ra tiếng:

  · `index.html` lệch `nguon/app.jsx` ⇒ người dùng mở ra vẫn thấy app chạy ngon,
    chỉ là bản của lần dựng trước; không lỗi nào, không cảnh báo nào;
  · một khoá `localStorage` dùng trong mã mà thiếu trong bảng `K` ⇒ nút «Sao lưu ra
    file» lặng lẽ bỏ sót đúng khoá đó, và người dùng chỉ biết vào lúc phục hồi, tức
    lúc dữ liệu cũ đã mất;
  · dịch mã trong trình duyệt ⇒ app vẫn chạy, chỉ chậm hẳn khi mở (quy tắc chung 29);
  · file khai trong `VON` mà thiếu trên đĩa ⇒ mất khả năng mở khi không có mạng, mà
    lúc có mạng thì mọi thứ bình thường;
  · câu ranh giới an toàn của DOME-01 biến mất khỏi mã ⇒ app vẫn đủ chức năng, chỉ
    khác là người làm không còn được nhắc rằng gọt xốp mũ bảo hiểm 25 mm còn 13 mm
    đẩy gia tốc dội lại từ ~213 g lên ~431 g. Đây là lỗi đắt nhất và câm nhất;
  · `projCost` đổi sang cộng nhầm ô số lượng (`m.q`, một chuỗi như «1 cái») thay vì
    ô giá (`m.p`) ⇒ JavaScript nối chuỗi trong im lặng, tổng tiền chợ hiện sai mà
    không lỗi nào bật lên.
"""

import io
import json
import os
import re
import subprocess
import sys

THU_APP = os.path.dirname(os.path.abspath(__file__))

# Câu ranh giới an toàn PHẢI còn trong mã. Khai bằng mảnh chữ ngắn, không khai cả câu:
# sửa lời văn là chuyện thường, bỏ mất ranh giới mới là lỗi.
MOC_AN_TOAN = (
    ('không gọt, không khoan', 'ranh giới không đụng vào lớp xốp EPS'),
    ('213', 'số gia tốc dội lại của xốp nguyên 25 mm'),
    ('431', 'số gia tốc dội lại sau khi gọt còn 13 mm'),
    ('một cú va đập', 'lời nhắc xốp EPS chỉ hấp thụ được một lần'),
)


def _doc(duong):
    try:
        with io.open(duong, encoding='utf-8') as f:
            return f.read()
    except OSError:
        return None


def van_tay(s):
    """Cùng phép băm mà `dungapp/dung.py` ghi vào `nguon/.van-tay`."""
    import hashlib
    return hashlib.sha256((s or '').encode('utf-8')).hexdigest()


def soi(thu=THU_APP, dung_lai=True):
    """Soi app trong `thu`. Trả danh sách câu mô tả lỗi, rỗng là sạch."""
    loi = []
    index = _doc(os.path.join(thu, 'index.html'))
    jsx = _doc(os.path.join(thu, 'nguon', 'app.jsx'))
    if index is None:
        return ['không đọc được index.html']
    if jsx is None:
        return ['không đọc được nguon/app.jsx — app một file phải giữ nguồn tách riêng']

    # ── luật 1: bản dựng chưa bị sửa tay ──────────────────────────────────────
    moc = (_doc(os.path.join(thu, 'nguon', '.van-tay')) or '').strip()
    if not moc:
        loi.append('nguon/.van-tay trống — không có mốc nào để biết index.html còn '
                   'đúng bản dựng hay đã bị sửa tay')
    elif moc != van_tay(index):
        loi.append('index.html đã bị sửa tay sau lần dựng trước (vân tay lệch) — lần '
                   'dựng sau sẽ nuốt mất bản sửa đó')

    # ── luật 2: bản dựng khớp nguồn, dựng lại ra đúng bản đang có ─────────────
    if dung_lai:
        loi += _soi_dung_lai(thu)

    # ── luật 3: sao lưu phủ ĐỦ mọi khoá localStorage ──────────────────────────
    loi += _soi_khoa_sao_luu(jsx)

    # ── luật 4: không dịch mã trong trình duyệt (quy tắc chung mục 29) ────────
    if '@babel/standalone' in index or 'text/babel' in index:
        loi.append('index.html dịch mã trong trình duyệt — bản dựng phải là mã đã dịch sẵn')

    # ── luật 5: lớp chạy nền và manifest khai đúng file có thật ───────────────
    loi += _soi_vo(thu)

    # ── luật 6: ranh giới an toàn DOME-01 còn nguyên trong mã ─────────────────
    for manh, y in MOC_AN_TOAN:
        if manh not in jsx:
            loi.append('mã không còn %s («%s») — người làm mất lời cảnh báo mà app '
                       'vẫn đủ chức năng' % (y, manh))

    # ── luật 7: tổng tiền vật liệu cộng đúng trường giá ───────────────────────
    loi += _soi_tien_vat_lieu(jsx)
    return loi


def _soi_tien_vat_lieu(jsx):
    """`projCost` phải cộng trường giá `m.p`, không phải số lượng `m.q` hay ô khác.

    Đây là hàm tính tổng tiền chợ hiện trên từng dự án; đổi nhầm sang cộng ô số
    lượng (chuỗi kiểu «1 cái») là JavaScript nối chuỗi trong im lặng — tổng tiền hiện
    ra sai mà không lỗi nào bật lên.
    """
    m = re.search(r'projCost\s*=\s*p\s*=>\s*p\.mats\.reduce\(\(s,m\)=>s\+m\.(\w+),0\)', jsx)
    if not m:
        return ['không tìm thấy đúng khuôn hàm projCost — không đo được có còn cộng '
                'đúng giá không']
    if m.group(1) != 'p':
        return ['projCost đang cộng trường "%s" thay vì "p" (giá) — tổng tiền chợ '
                'của mọi dự án tính sai' % m.group(1)]
    return []


def _soi_dung_lai(thu):
    """Dựng lại từ nguồn rồi so với `index.html` đang có. Không đo được thì KÊU."""
    dung = os.path.expanduser('~/Claude/HeThong/dungapp/dung.py')
    if not os.path.exists(dung):
        dung = '/Users/Huy/Claude/HeThong/dungapp/dung.py'
    if not os.path.exists(dung):
        return ['không tìm thấy dungapp/dung.py — không đo được bản dựng có khớp nguồn không']
    try:
        p = subprocess.run([sys.executable, dung, thu, '--kiem'],
                           capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError) as e:
        return ['không chạy được phép dựng lại: %s' % e]
    ra = (p.stdout or '') + (p.returncode and (p.stderr or '') or '')
    if p.returncode != 0:
        return ['phép dựng lại thoát mã %d: %s' % (p.returncode, (p.stderr or '').strip()[:200])]
    if '≠' in ra:
        return ['index.html LỆCH bản dựng từ nguon/app.jsx — nguồn đã sửa mà chưa dựng '
                'lại, người dùng vẫn đang mở bản của lần trước']
    if '=' not in ra:
        return ['phép dựng lại không nói được khớp hay lệch: %r' % ra.strip()[:120]]
    return []


def _soi_khoa_sao_luu(jsx):
    """Mọi khoá `diy.*` dùng trong mã phải nằm trong bảng `K`.

    `goiDuLieu()` duyệt đúng `Object.values(K)`, nên một khoá dùng thẳng mà quên khai
    ở `K` sẽ bị nút «Sao lưu ra file» bỏ qua trong im lặng — người dùng chỉ biết vào
    lúc phục hồi, tức lúc dữ liệu cũ đã bị ghi đè.
    """
    m = re.search(r'const K\s*=\s*\{(.*?)\}\s*;', jsx, re.S)
    if not m:
        return ['không tìm thấy bảng khoá K — không đo được sao lưu có phủ đủ không']
    trong_bang = set(re.findall(r"'(diy\.[\w]+)'", m.group(1)))
    dung_trong_ma = set(re.findall(r"'(diy\.[\w]+)'", jsx))
    # Hỏi bảng rỗng TRƯỚC: bảng rỗng thì phép so bên dưới cũng kêu, nhưng kêu bằng câu
    # «thiếu 9 khoá» — đọc lên thành quên khai vài khoá, trong khi thứ đã xảy ra là mất
    # sạch bảng và nút sao lưu ghi ra file rỗng.
    if not trong_bang:
        return ['bảng khoá K rỗng — sao lưu ra file rỗng mà không lỗi nào phát ra']
    thieu = sorted(dung_trong_ma - trong_bang)
    if thieu:
        return ['%d khoá dùng trong mã mà KHÔNG khai ở bảng K (%s) — nút sao lưu bỏ '
                'sót đúng những khoá đó' % (len(thieu), ', '.join(thieu))]
    return []


def _soi_vo(thu):
    loi = []
    sw = _doc(os.path.join(thu, 'sw.js'))
    if sw is None:
        loi.append('không đọc được sw.js')
    else:
        m = re.search(r'VON\s*=\s*\[(.*?)\]', sw, re.S)
        if not m:
            loi.append('sw.js không khai danh sách file vỏ VON')
        else:
            vo = re.findall(r"'([^']+)'", m.group(1))
            if './index.html' not in vo:
                loi.append('vỏ không khai ./index.html — mất mạng là trắng trang')
            for f in vo:
                if f.startswith('http') or f in ('./', '/'):
                    continue
                if not os.path.exists(os.path.join(thu, f[2:] if f.startswith('./') else f)):
                    loi.append('sw.js khai file vỏ %s nhưng không có trên đĩa' % f)
        if not re.search(r"KHO\s*=\s*'[\w.-]+-v\d+'", sw):
            loi.append('tên kho của sw.js không theo khuôn «<app>-v<số>» — không tăng '
                       'số được thì máy đã cài mãi chạy bản cũ')

    man = _doc(os.path.join(thu, 'manifest.webmanifest'))
    if man is None:
        loi.append('không đọc được manifest.webmanifest')
        return loi
    try:
        d = json.loads(man)
    except ValueError as e:
        loi.append('manifest.webmanifest không phải JSON hợp lệ: %s' % e)
        return loi
    for i in d.get('icons') or []:
        src = i.get('src') or ''
        if src and not os.path.exists(os.path.join(thu, src)):
            loi.append('manifest khai icon %s nhưng file không có trên đĩa' % src)
    if not any('maskable' in (i.get('purpose') or '') for i in d.get('icons') or []):
        loi.append('manifest không khai icon maskable nào — Android tự cắt icon thường')
    dau = (d.get('start_url') or './').lstrip('./')
    if dau and not os.path.exists(os.path.join(thu, dau)):
        loi.append('manifest khai start_url %s nhưng file không có trên đĩa'
                   % d.get('start_url'))
    return loi


# ── Bộ ca ────────────────────────────────────────────────────────────────────

DEM_CA = {'tong': 0}


def _ca(so, ten, dat):
    DEM_CA['tong'] += 1
    print('  %s ca %-3d %s' % ('✓' if dat else '✗', so, ten))
    return dat


class app_hong(object):
    """Chép app thật sang thư mục tạm rồi bẻ đúng một chỗ."""

    CHEP = ('index.html', 'sw.js', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png')
    CHEP_NGUON = ('app.jsx', 'khung.html', '.van-tay')

    def __init__(self, doi):
        self.doi = doi

    def __enter__(self):
        import shutil
        import tempfile
        self.thu = tempfile.mkdtemp(prefix='_thu-xuongnha-')
        os.makedirs(os.path.join(self.thu, 'nguon'))
        for ten in self.CHEP:
            g = os.path.join(THU_APP, ten)
            if os.path.exists(g):
                shutil.copy2(g, os.path.join(self.thu, ten))
        for ten in self.CHEP_NGUON:
            g = os.path.join(THU_APP, 'nguon', ten)
            if os.path.exists(g):
                shutil.copy2(g, os.path.join(self.thu, 'nguon', ten))
        for ten, sua in self.doi.items():
            duong = os.path.join(self.thu, ten)
            if sua is None:
                if os.path.exists(duong):
                    os.unlink(duong)
                continue
            with io.open(duong, encoding='utf-8') as f:
                cu = f.read()
            with io.open(duong, 'w', encoding='utf-8') as f:
                f.write(sua(cu))
        return self.thu

    def __exit__(self, *a):
        import shutil
        shutil.rmtree(self.thu, ignore_errors=True)
        return False


def _co(loi, manh):
    return any(manh in x for x in loi)


def chay_ca():
    do = []

    # ĐỐI CHỨNG: bản thật phải sạch. Chạy KÈM phép dựng lại, tức ca này cũng là ca duy
    # nhất trả lời được câu «index.html còn khớp nguon/app.jsx không».
    that = soi(THU_APP)
    if not _ca(1, 'ĐỐI CHỨNG: bản thật phải sạch, kể cả phép dựng lại (%s)'
               % ('sạch' if not that else that[0][:60]), not that):
        do.append(1)

    # ── luật 1: vân tay ───────────────────────────────────────────────────────
    with app_hong({'index.html': lambda s: s.replace('</body>', '<!-- sửa tay --></body>', 1)}) as t:
        if not _ca(2, 'PHẢI CHẶN: index.html bị sửa tay sau lần dựng (vân tay lệch)',
                   _co(soi(t, dung_lai=False), 'bị sửa tay')):
            do.append(2)
    with app_hong({'nguon/.van-tay': lambda s: ''}) as t:
        if not _ca(3, 'PHẢI CHẶN: mốc vân tay trống — không đo được thì phải KÊU',
                   _co(soi(t, dung_lai=False), 'không có mốc nào')):
            do.append(3)

    # ── luật 2: bản dựng khớp nguồn ───────────────────────────────────────────
    with app_hong({'nguon/app.jsx': lambda s: s.replace(
            "const DIFF = {1:'Dễ',2:'Vừa',3:'Khó'};",
            "const DIFF = {1:'Dễ',2:'Vừa',3:'Rất khó'};", 1)}) as t:
        if not _ca(4, 'PHẢI CHẶN: nguồn đã sửa mà chưa dựng lại ⇒ người dùng mở bản cũ',
                   _co(soi(t), 'LỆCH bản dựng')):
            do.append(4)

    # ── luật 3: sao lưu phủ đủ khoá ───────────────────────────────────────────
    with app_hong({'nguon/app.jsx': lambda s: s.replace(
            "const DIFF = ", "const KHOA_MOI = 'diy.ghichep';\nconst DIFF = ", 1)}) as t:
        if not _ca(5, 'PHẢI CHẶN: khoá localStorage mới không khai ở bảng K ⇒ sao lưu bỏ sót',
                   _co(soi(t, dung_lai=False), 'KHÔNG khai ở bảng K')):
            do.append(5)
    with app_hong({'nguon/app.jsx': lambda s: re.sub(
            r'const K\s*=\s*\{.*?\}\s*;', 'const K = {};', s, count=1, flags=re.S)}) as t:
        if not _ca(6, 'PHẢI CHẶN: bảng khoá K rỗng ⇒ sao lưu ra file rỗng',
                   _co(soi(t, dung_lai=False), 'bảng khoá K rỗng')):
            do.append(6)

    # ── luật 4: dịch mã trong trình duyệt ─────────────────────────────────────
    with app_hong({'index.html': lambda s: s.replace(
            '<body', '<script src="https://x/@babel/standalone"></script><body', 1)}) as t:
        if not _ca(7, 'PHẢI CHẶN: bản dựng nạp Babel (quy tắc chung mục 29)',
                   _co(soi(t, dung_lai=False), 'dịch mã trong trình duyệt')):
            do.append(7)

    # ── luật 5: vỏ và manifest ────────────────────────────────────────────────
    with app_hong({'sw.js': lambda s: s.replace("'./icon-192.png',", "'./icon-chua-co.png',", 1)}) as t:
        if not _ca(8, 'PHẢI CHẶN: vỏ khai file không có trên đĩa ⇒ mất mạng là trắng trang',
                   _co(soi(t, dung_lai=False), 'file vỏ')):
            do.append(8)
    with app_hong({'sw.js': lambda s: s.replace("'./index.html',", '', 1)}) as t:
        if not _ca(9, 'PHẢI CHẶN: vỏ không khai ./index.html',
                   _co(soi(t, dung_lai=False), 'mất mạng là trắng trang')):
            do.append(9)
    with app_hong({'sw.js': lambda s: s.replace("const KHO = 'xuongnha-v4';",
                                                "const KHO = 'kho';", 1)}) as t:
        if not _ca(10, 'PHẢI CHẶN: tên kho không đánh số ⇒ máy đã cài mãi chạy bản cũ',
                   _co(soi(t, dung_lai=False), 'không theo khuôn')):
            do.append(10)
    with app_hong({'icon-512.png': None}) as t:
        if not _ca(11, 'PHẢI CHẶN: manifest khai icon mà file không có trên đĩa',
                   _co(soi(t, dung_lai=False), 'manifest khai icon')):
            do.append(11)
    with app_hong({'manifest.webmanifest': lambda s: s.replace(', "purpose": "maskable"', '', 1)}) as t:
        if not _ca(12, 'PHẢI CHẶN: manifest không còn icon maskable nào',
                   _co(soi(t, dung_lai=False), 'không khai icon maskable')):
            do.append(12)

    # ── luật 6: ranh giới an toàn ─────────────────────────────────────────────
    with app_hong({'nguon/app.jsx': lambda s: s.replace('không gọt, không khoan', 'nên cẩn thận', 1)}) as t:
        if not _ca(13, 'PHẢI CHẶN: mã mất ranh giới không đụng vào lớp xốp EPS',
                   _co(soi(t, dung_lai=False), 'ranh giới không đụng')):
            do.append(13)
    with app_hong({'nguon/app.jsx': lambda s: s.replace('431', 'nhiều', 1)}) as t:
        if not _ca(14, 'PHẢI CHẶN: mã mất số gia tốc dội lại sau khi gọt xốp',
                   _co(soi(t, dung_lai=False), 'gia tốc dội lại sau khi gọt')):
            do.append(14)

    # ── luật 7: tổng tiền vật liệu ────────────────────────────────────────────
    with app_hong({'nguon/app.jsx': lambda s: s.replace(
            'p.mats.reduce((s,m)=>s+m.p,0)', 'p.mats.reduce((s,m)=>s+m.q,0)', 1)}) as t:
        if not _ca(15, 'PHẢI CHẶN: projCost cộng nhầm số lượng (m.q) thay vì giá (m.p)',
                   _co(soi(t, dung_lai=False), 'cộng trường')):
            do.append(15)

    # ── ĐƯỜNG GẮN ─────────────────────────────────────────────────────────────
    with app_hong({'index.html': lambda s: s.replace('</body>', '<!-- sửa tay --></body>', 1)}) as t:
        p = subprocess.run([sys.executable, os.path.abspath(__file__),
                            '--thu-muc', t, '--khong-dung-lai'],
                           capture_output=True, text=True)
        if not _ca(16, 'ĐƯỜNG GẮN: chạy thẳng trên bản hỏng thì thoát khác 0',
                   p.returncode != 0):
            do.append(16)
    return do


def tu_kiem():
    for goc in (os.path.expanduser('~/Claude/HeThong'), '/Users/Huy/Claude/HeThong'):
        if os.path.isdir(goc):
            sys.path.insert(0, goc)
            break
    from khung_tu_kiem import vong_ban_hong

    sys.dont_write_bytecode = True
    print('— bản ĐÚNG —')
    DEM_CA['tong'] = 0
    do = chay_ca()
    print('  %d/%d ca đạt' % (DEM_CA['tong'] - len(do), DEM_CA['tong']))
    if do:
        print('✗ bản đúng đã đỏ ở ca %s — sửa mã trước khi xét bản hỏng' % do)
        return 1
    return vong_ban_hong(__file__, os.path.abspath(__file__), BAN_HONG,
                         lenh=lambda duong: [sys.executable, duong, '--ca'],
                         do_rong=78,
                         tieu_de='dựng bản kiem-xuong-nha.py đã gỡ dòng bảo vệ')


def main():
    if '--tu-kiem' in sys.argv:
        return tu_kiem()
    if '--ca' in sys.argv:
        return 1 if chay_ca() else 0
    thu = THU_APP
    if '--thu-muc' in sys.argv:
        thu = sys.argv[sys.argv.index('--thu-muc') + 1]
    loi = soi(thu, dung_lai='--khong-dung-lai' not in sys.argv)
    if not loi:
        print('✓ Xưởng Nhà sạch: bản dựng khớp nguồn, sao lưu phủ đủ khoá, vỏ và '
              'manifest khai đúng file có thật, ranh giới an toàn DOME-01 còn nguyên')
        return 0
    print('✗ %d lỗi:' % len(loi))
    for x in loi:
        print('  · %s' % x)
    return 1


# ── Bảng bản hỏng đặt CUỐI file, sau mã (quy ước bắt buộc) ───────────────────

BAN_HONG = (
    # ⚠ Neo BẮT BUỘC trải ≥02 dòng và viết bằng `\n` thoát: bảng này nằm CÙNG file với
    # mã nó nhắm tới, neo một dòng sẽ tự khớp thêm chính dòng khai ⇒ «2 chỗ khớp».

    ('bỏ nhánh so vân tay — index.html sửa tay không ai kêu',
     "    elif moc != van_tay(index):\n        loi.append('index.html đã bị sửa tay",
     "    elif False:\n        loi.append('index.html đã bị sửa tay",
     (2, 16)),

    ('mốc vân tay trống được coi là bình thường (fail-open ở nhánh không đo được)',
     "    if not moc:\n        loi.append('nguon/.van-tay trống",
     "    if False:\n        loi.append('nguon/.van-tay trống",
     (3,)),

    ('bỏ phép dựng lại — nguồn sửa mà chưa dựng thì không ai biết',
     "    if dung_lai:\n        loi += _soi_dung_lai(thu)",
     "    if False:\n        loi += _soi_dung_lai(thu)",
     (4,)),

    ('phép dựng lại nuốt kết quả lệch, luôn báo khớp',
     "    if '≠' in ra:\n        return ['index.html LỆCH bản dựng",
     "    if False:\n        return ['index.html LỆCH bản dựng",
     (4,)),

    ('bỏ phép so khoá dùng trong mã với bảng K',
     "    thieu = sorted(dung_trong_ma - trong_bang)\n    if thieu:",
     "    thieu = []\n    if thieu:",
     (5,)),

    ('bảng K rỗng vẫn cho qua',
     "    if not trong_bang:\n        return ['bảng khoá K rỗng",
     "    if False:\n        return ['bảng khoá K rỗng",
     (6,)),

    ('bỏ nhánh chặn dịch mã trong trình duyệt',
     "    if '@babel/standalone' in index or 'text/babel' in index:\n        loi.append('index.html dịch mã",
     "    if False:\n        loi.append('index.html dịch mã",
     (7,)),

    ('bỏ nhánh đối chiếu file vỏ với đĩa',
     "                if not os.path.exists(os.path.join(thu, f[2:] if f.startswith('./') else f)):\n"
     "                    loi.append('sw.js khai file vỏ",
     "                if False:\n"
     "                    loi.append('sw.js khai file vỏ",
     (8,)),

    ('bỏ nhánh đòi vỏ phải khai ./index.html',
     "            if './index.html' not in vo:\n                loi.append('vỏ không khai",
     "            if False:\n                loi.append('vỏ không khai",
     (9,)),

    ('bỏ nhánh soi khuôn đánh số của tên kho',
     "        if not re.search(r\"KHO\\s*=\\s*'[\\w.-]+-v\\d+'\", sw):\n            loi.append('tên kho",
     "        if False:\n            loi.append('tên kho",
     (10,)),

    ('bỏ nhánh đối chiếu icon của manifest với đĩa',
     "        if src and not os.path.exists(os.path.join(thu, src)):\n"
     "            loi.append('manifest khai icon",
     "        if False:\n"
     "            loi.append('manifest khai icon",
     (11,)),

    ('bỏ nhánh đòi có icon maskable',
     "    if not any('maskable' in (i.get('purpose') or '') for i in d.get('icons') or []):\n"
     "        loi.append('manifest không khai icon maskable",
     "    if False:\n"
     "        loi.append('manifest không khai icon maskable",
     (12,)),

    ('bỏ phép canh ranh giới an toàn DOME-01',
     "    for manh, y in MOC_AN_TOAN:\n        if manh not in jsx:",
     "    for manh, y in ():\n        if manh not in jsx:",
     (13, 14)),

    ('bảng mốc an toàn bỏ con số gia tốc sau khi gọt xốp',
     "    ('431', 'số gia tốc dội lại sau khi gọt còn 13 mm'),\n"
     "    ('một cú va đập',",
     "    ('213', 'số gia tốc dội lại sau khi gọt còn 13 mm'),\n"
     "    ('một cú va đập',",
     (14,)),

    ('main() không gọi cổng nữa, luôn thoát 0 — cổng dựng xong mà nằm không',
     "    loi = soi(thu, dung_lai='--khong-dung-lai' not in sys.argv)\n    if not loi:",
     "    loi = []\n    if not loi:",
     (16,)),
)


if __name__ == '__main__':
    sys.exit(main())
