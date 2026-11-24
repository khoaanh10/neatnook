# STATE — NeatNook (`pinterest-org`)

Cập nhật: 2026-11-25

## Trạng thái hiện tại
- **Giai đoạn**: C. Đang chạy & Đã mở bán sản phẩm số \$5!
- **Chi phí đã chi**: **0 USD**
- **Doanh thu**: 0 USD
- **Website live (HTTPS trọn đời)**: https://khoaanh10.github.io/neatnook/ (giao diện tạp chí `Newsreader`, 10 bài viết có 3 ảnh thật/bài + khung bán PDF \$5)
- **Sản phẩm số live trên Gumroad (\$5)**: https://khoaanh4.gumroad.com/l/aqhxc (*The January Apartment Reset Kit + 72 Minimalist Pantry & Fridge Labels*, đã nối TPBank Payout & Publish!)
- **Repo GitHub**: https://github.com/khoaanh10/neatnook
- **Pinterest Business**: `NeatNook` (`https://www.pinterest.com/neatnookguide/`) — Đã Claim Website + Avatar + Bio SEO + 8/8 Board công khai
- **Pinterest Developers App**: `NeatNook Pin Publisher` (`App ID: 1644049`, https://developers.pinterest.com/apps/1644049/) — Đang chờ duyệt `Trial access`
- **Kho nội dung**: **10 bài viết** · **50 ảnh Pin dọc 1000×1500px** (ảnh AI + 20 ảnh chụp thật Unsplash, đã ẩn `github.io` trên ảnh)
- **Pin đã đăng & hẹn lịch (9 Pin phủ đều 8 Board)**:
  - **25/11 (Đã đăng live — 3 Pin)**: Kitchen Under-Sink · Minimalist Desk Cables · No-Drill Bathroom
  - **26/11 (Đã hẹn lịch — 3 Pin)**: 09:00 Fridge & Pantry · 14:00 Kitchen Countertop · 20:00 Tiny Entryway
  - **27/11 (Đã hẹn lịch — 3 Pin)**: 09:00 Bathroom Vanity · 14:00 Home Finds Under $30 · 20:00 Calm Desk Reset
- **Báo cáo Email hàng ngày**: Đã cài cron 08:00 sáng trên VPS `107.175.51.106` gửi về `khoaanh15111997@gmail.com` (chờ gắn `PINTEREST_READ_TOKEN`)

## Việc kế tiếp
- [ ] Gắn `PINTEREST_READ_TOKEN` từ App `1644049` vào `/opt/neatnook/.env` trên VPS để bật báo cáo email tự động mỗi sáng
- [ ] Tối 27/11: Hẹn lịch tiếp 9 Pin cho 28–30/11 (kho còn sẵn 41 Pin mới đẹp)
- [ ] Khi Pinterest duyệt `Trial access` → bấm nâng lên `Standard access` để bật cron tự đăng 24/7 trên VPS
- [ ] Khi đạt ≥ 20–30 click/ngày → mua `.com` (~\$10/năm) + mở Amazon Associates US + AdSense
