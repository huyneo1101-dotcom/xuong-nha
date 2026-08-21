# Xưởng Nhà — góc tự làm

Web app một file cho việc **tự làm đồ (DIY)**: thư viện dự án, tick từng bước khi làm,
gom vật liệu thành danh sách đi chợ, và lưu lại ảnh thành phẩm.

Mở: <https://huyneo1101-dotcom.github.io/xuong-nha/> — hoặc nhấp đúp `index.html`.
Cài lên màn hình chính điện thoại được, mất mạng vẫn mở được.

## Năm tab

| Tab | Việc |
|---|---|
| **Dự án** | 24 dự án · 9 kỹ năng nền · 84 loại vật liệu — ba lớp tra cứu, lọc và sắp xếp |
| **Hôm nay** | thẻ Làm tiếp (vào thẳng chế độ làm), dự án dở, dự án đã xong, ba gợi ý đổi theo ngày |
| **Đi chợ** | vật liệu gom theo **nơi mua**, tick đã mua, cộng tiền, chép danh sách gửi Zalo |
| **Thành phẩm** | ảnh trước/sau, ghi chú, số sao, thời gian thật đã bỏ ra |
| **Tôi** | kho dụng cụ, số đo đầu, thống kê, sao lưu/phục hồi, giao diện sáng-tối |

## Ba thứ làm nên app này

**Chế độ làm.** Đang dính keo đầy tay thì không cuộn nổi danh sách tám bước. Bấm "Vào
chế độ làm" là mỗi lần một bước chiếm cả màn hình: chữ to, hình vẽ của đúng bước đó, ô
ghi chú, ba nút to ở đáy, đồng hồ đếm từ lúc bắt đầu.

**Kho dụng cụ.** Tick những món đã có trong nhà, app sẽ nói thẳng dự án nào còn thiếu
gì và lọc ra những dự án làm được ngay. Dụng cụ mỗi dự án suy ra từ kỹ năng nó dùng,
không khai tay hai chỗ.

**Tra ngược từ vật liệu.** Câu hỏi thật của người tự làm thường không phải "làm gì bây
giờ" mà "còn thừa khúc ống PVC này thì làm được món nào". Lớp Vật liệu trả lời đúng câu đó.

## DOME-01

Dự án đầu tiên — khung sáu nan bằng lưới 3D lắp thêm vào mũ bảo hiểm đang đội, tạo khe
rỗng 10–12 mm trên đỉnh đầu để đội cả ngày tóc vẫn còn nếp. Đây là dự án duy nhất có
thêm tab **Bản vẽ**: nhập chu vi vòng đầu và cung qua đỉnh thì dài nan, dài đai và
khoảng cách chân nan tự tính lại, chín hình vẽ đổi theo.

Ranh giới an toàn: **không gọt, không khoan một milimét nào vào lớp xốp EPS**. Gọt xốp
25 mm còn 13 mm thì gia tốc dội lại khi ngã vọt từ ~213 g lên ~431 g.

## Kỹ thuật

- Một file `index.html`, React 18 + Babel standalone nạp qua CDN jsDelivr — không có
  bước build, không cần Node. Kèm `sw.js`, `manifest.webmanifest` và hai icon để cài
  lên màn hình chính; ba file này chỉ có tác dụng khi mở qua http/https.
- Dữ liệu ở `localStorage`, khoá `diy.*` (doing · shop · gallery · body · kho · theme).
  Không máy chủ, không gửi đi đâu. **Xoá lịch sử trình duyệt là mất sạch** — trong tab
  Tôi có nút sao lưu ra file JSON và phục hồi lại.
- Ảnh thành phẩm nén còn cạnh dài 900 px, JPEG 0,72 trước khi lưu.
- Hình vẽ đều là SVG sinh trong JS (`FIG.*`, `figMatCat`), dùng biến màu CSS nên theo
  được cả hai giao diện; kết quả có nhớ đệm theo số đo.
- Liên kết sâu: `#p=<id dự án>&s=<tq|vl|bw|bv>` và `#k=<id kỹ năng>`.

## Sửa

Dữ liệu nằm ở ba khối đánh dấu trong `index.html`: `DATA:PROJECTS`, `DATA:KYNANG`,
`DATA:DUNGCU`. Thêm một dự án là thêm một phần tử vào `PROJECTS` — dụng cụ, chỉ mục vật
liệu, bộ lọc và thống kê tự ăn theo, không phải sửa giao diện.

Babel biên dịch ngay trên trình duyệt nên **một lỗi cú pháp là trắng màn hình**: mở lại
và xem Console (F12) sau mỗi lần sửa. Sửa `index.html` xong nhớ tăng số `KHO` trong
`sw.js`, không thì máy đã cài vẫn chạy bản cũ trong kho.
