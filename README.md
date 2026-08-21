# Xưởng Nhà — góc tự làm

Web app một file cho việc **tự làm đồ (DIY)**: thư viện dự án có sẵn, tick từng bước khi
làm, gom vật liệu thành danh sách đi chợ, và lưu lại ảnh thành phẩm.

Mở: <https://huyneo1101-dotcom.github.io/xuong-nha/> — hoặc nhấp đúp `index.html`.

## Có gì

| Tab | Việc |
|---|---|
| **Dự án** | 12 dự án tự làm, lọc theo 7 nhóm, tìm theo tên |
| **Đang làm** | tick từng bước, ghi chú riêng mỗi bước, thanh tiến độ |
| **Đi chợ** | gom vật liệu của mọi dự án đang làm, tick đã mua, cộng tiền còn phải mua |
| **Thành phẩm** | ảnh + nhận xét + sao cho mỗi lần làm xong |
| **Tôi** | số đo đầu, thống kê, đổi giao diện sáng/tối, xoá dữ liệu |

Mỗi dự án có: dụng cụ cần có, vật liệu kèm giá thật ở Việt Nam, các bước, và cảnh báo
an toàn ở dự án nào cần.

## DOME-01

Dự án đầu tiên — khung sáu nan bằng lưới 3D lắp thêm vào mũ bảo hiểm đang đội, tạo khe
rỗng 10–12 mm trên đỉnh đầu để đội cả ngày tóc vẫn còn nếp. Đây là dự án duy nhất có
thêm tab **Bản vẽ**: nhập chu vi vòng đầu và cung qua đỉnh thì dài nan, dài đai và
khoảng cách chân nan tự tính lại, hình vẽ đổi theo.

Ranh giới an toàn của dự án này: **không gọt, không khoan một milimét nào vào lớp xốp
EPS**. Gọt xốp 25 mm còn 13 mm thì gia tốc dội lại khi ngã vọt từ ~213 g lên ~431 g.

## Kỹ thuật

- Một file `index.html`, React 18 + Babel standalone nạp qua CDN jsDelivr — không có
  bước build, không cần Node. Cần Internet lần mở đầu.
- Dữ liệu nằm ở `localStorage` của máy đang mở, khoá `diy.*`. Không có máy chủ, không
  gửi đi đâu. Ảnh thành phẩm được nén còn cạnh dài 900 px, JPEG chất lượng 0,72 trước
  khi lưu.
- Mọi hình vẽ là SVG sinh thẳng trong JS (`FIG.*`, `figMatCat`), dùng biến màu CSS nên
  đổi sang giao diện sáng vẫn đúng màu.
- Mở thẳng một dự án: `index.html#p=<id>&s=<tab>`, `s` là một trong `tq` `vl` `bw` `bv`.
  Ví dụ `#p=dome01&s=bv`.

## Sửa

Sửa thẳng `index.html`. Dữ liệu dự án nằm ở mảng `PROJECTS` gần đầu script Babel; thêm
một dự án là thêm một phần tử, không phải sửa giao diện. Babel biên dịch ngay trên
trình duyệt nên **một lỗi cú pháp là trắng màn hình** — mở lại và xem Console (F12) sau
mỗi lần sửa.
