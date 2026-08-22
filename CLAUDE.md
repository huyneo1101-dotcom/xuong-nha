# ⛔ ĐỌC TRƯỚC KHI SỬA APP — `index.html` LÀ BẢN DỰNG, KHÔNG PHẢI NGUỒN

| File | Vai trò |
|---|---|
| `nguon/app.jsx` | **mã app — ĐÂY là chỗ sửa** |
| `nguon/khung.html` | phần HTML bao quanh |
| `index.html` | **bản dựng, sinh tự động — CẤM sửa tay** |
| `README.md` | mô tả đầy đủ cho người dùng + phần "Kỹ thuật"/"Sửa" — đọc trước khi sửa |

Sửa xong `nguon/app.jsx` thì dựng lại, nếu không thì bản chạy vẫn là mã cũ:

```bash
python3 /Users/Huy/Claude/HeThong/dungapp/dung.py /Users/Huy/Claude/App/XuongNha
```

Dựng lại xong nhớ tăng số `KHO` trong `sw.js` — không thì máy đã cài PWA vẫn chạy bản cũ
trong kho cache, và không lỗi nào phát ra để báo.

## App là gì

**Xưởng Nhà** — web app một file cho việc tự làm đồ (DIY): thư viện dự án, tick từng bước
khi làm (Chế độ làm), gom vật liệu thành danh sách đi chợ theo nơi mua, kho dụng cụ tự lọc
ra dự án làm được ngay, và lưu ảnh thành phẩm. Năm tab: Dự án · Hôm nay · Đi chợ · Thành
phẩm · Tôi. Chi tiết đầy đủ từng tab, dự án DOME-01 và ranh giới an toàn (EPS mũ bảo hiểm):
xem `README.md`.

## Vài điểm hay vấp

- **Đã bỏ dịch mã trong trình duyệt** (22/08/2026) — không còn `@babel/standalone`, JSX
  dịch sẵn trên máy lúc dựng. Lỗi cú pháp bị bắt ngay lúc `dung.py` chạy, không còn ra
  trắng màn hình trên máy người dùng.
- Dữ liệu ở `localStorage`, khoá `diy.*` — không máy chủ, không đồng bộ. Xoá lịch sử trình
  duyệt là mất sạch; tab Tôi có nút sao lưu/phục hồi ra file JSON.
- Ba khối dữ liệu đánh dấu trong `nguon/app.jsx`: `DATA:PROJECTS`, `DATA:KYNANG`,
  `DATA:DUNGCU`. Thêm dự án mới chỉ cần thêm một phần tử vào `PROJECTS` — dụng cụ, chỉ mục
  vật liệu, bộ lọc và thống kê tự ăn theo.
- Hình vẽ SVG sinh trong JS (`FIG.*`, `figMatCat`), dùng biến màu CSS nên theo được cả hai
  giao diện sáng/tối.
