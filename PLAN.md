# PLAN — NeatNook (Pinterest + Static Site + Amazon Associates)

- **ID dự án**: `pinterest-org`
- **Thị trường**: Mỹ / Quốc tế (Tiếng Anh, thu USD)
- **Ngách**: Small Space, Kitchen & Desk Organization (Đồ sắp xếp phòng nhỏ, bếp thông minh, góc bàn làm việc tối giản)
- **Mô hình kiếm tiền**: Pinterest Organic Search → Static Bridge Site (Cloudflare Pages / GitHub Pages, hosting \$0) → Amazon Associates (và sau này gắn thêm Display Ads: AdSense / Mediavine Journey)
- **Ngân sách dự kiến**: ~\$10/năm (chỉ 1 tên miền `.com`)
- **Tỷ lệ phân việc**: AI làm ~85% (nghiên cứu từ khóa, viết bài, build web, tạo hàng loạt ảnh Pin, xuất lịch đăng qua Pinterest API v5) · Owner làm ~15% (mua domain, mở Pinterest Business & Claim domain, duyệt sản phẩm/link, mở Amazon Associates & Payoneer khi đủ traffic)

---

## 1. Quy tắc tuân thủ bắt buộc (Chống khóa tài khoản)

### Amazon Associates (Mỹ)
1. **Chưa đăng ký Amazon ngay ngày 1**: Chỉ đăng ký khi Pinterest đã kéo về ổn định **≥ 20–30 outbound clicks/ngày** (thường sau 30–45 ngày) để chắc chắn vượt ải **3 đơn hợp lệ trong 180 ngày**.
2. **Cấm tải ảnh từ Amazon về host trên web mình**: Giai đoạn đầu dùng ảnh lifestyle/minh họa sạch (Unsplash/Pexels hoặc ảnh tự tạo) + nút CTA `"Check Current Price on Amazon"`. Sau khi qua 3 đơn có PA-API mới kéo ảnh chính thức qua API.
3. **Cấm ghi cứng giá tiền**: Không ghi `"$19.99"` trong bài (giá Amazon thay đổi liên tục); dùng `"Under $30"` hoặc `"Check current price"`.
4. **Bắt buộc có Affiliate Disclosure**: Hiển thị rõ ở đầu mỗi bài viết và footer theo chuẩn FTC & Amazon Operating Agreement.

### Pinterest (2026)
1. **Không dùng bot trình duyệt (Selenium/Playwright) đăng bài**: Chỉ đăng qua **Pinterest API v5 chính thức** hoặc bộ hẹn lịch gốc của Pinterest.
2. **Không spam tốc độ cao**:
   - Tuần 1–4: **3–5 Pin mới/ngày**, giãn đều khung giờ.
   - Từ tháng 2: **10–15 Pin mới/ngày**, không lặp lại cùng 1 ảnh, không trỏ quá nhiều Pin về cùng 1 URL trong 24h.
3. **Đa dạng mẫu Pin**: Mỗi 1 bài viết sinh **5 mẫu Pin dọc (1000×1500px)** khác nhau về bố cục, màu nền và tiêu đề móc câu. **Không in địa chỉ web (`github.io`) lên ảnh Pin** — chỉ hiện tên thương hiệu `NEATNOOK`, chờ khi có tên miền `.com` riêng mới bật `"showDomainOnPins": true` trong `site.config.json`.

---

## 2. Cấu trúc 8 Bảng (Boards) chuẩn SEO Pinterest

| # | Tên Board (SEO) | Từ khóa trọng tâm |
|---|---|---|
| 1 | `Small Kitchen Organization Ideas` | small kitchen organization, under sink storage, pantry organizers |
| 2 | `Desk Setup & Workspace Organization` | minimalist desk setup, cable management, small home office storage |
| 3 | `Small Apartment Storage Hacks` | tiny apartment storage, renter friendly organization, closet hacks |
| 4 | `Under-Sink & Cabinet Organizers` | under sink organizer, pull out cabinet drawers, spice rack ideas |
| 5 | `Fridge & Pantry Organization` | clear fridge bins, pantry storage containers, meal prep organization |
| 6 | `Bathroom Counter & Closet Storage` | small bathroom storage, vanity organizer, over the door storage |
| 7 | `Budget Home Finds Under $30` | amazon home finds under 30, affordable organizers, budget home upgrades |
| 8 | `Renter-Friendly No-Drill Storage` | no drill shelves, adhesive bathroom caddy, damage free apartment storage |

---

## 3. Lộ trình 30 ngày đầu & Tiêu chí Go / No-Go

- **Tuần 1 (Thiết lập hạ tầng)**:
  - AI dựng xong Static Site (`site/`), Pin Factory (`pin-factory/`), và 3 bài mẫu + 15 ảnh Pin đầu tiên.
  - Owner chọn & mua 1 tên miền `.com` (~10 USD/năm), mở tài khoản Pinterest Business, Claim Website, tạo 8 Board trên.
- **Tuần 2 (Phủ nội dung nền)**:
  - AI sản xuất đủ **20 bài Listicle chuẩn SEO** + **100 ảnh Pin** (5 Pin/bài).
  - Bắt đầu đăng đều **3–5 Pin/ngày** (giãn cách trong ngày).
- **Tuần 3–4 (Tăng tốc & Đo lường)**:
  - Thêm 10 bài mới (tổng 30 bài) + nâng tốc độ lên **8–10 Pin/ngày**.
  - Kiểm tra Pinterest Analytics: chọn Top 3 Board có Outbound Clicks cao nhất để AI nhân bản gấp đôi nội dung.
- **Cổng quyết định (Ngày 45–60)**:
  - **GO (Đăng ký Amazon Associates)**: Đạt ≥ 20–30 Outbound Clicks/ngày hoặc ≥ 30.000 Impressions/tháng đang tăng đều.
  - **PIVOT (Điều chỉnh ngách/thiết kế Pin)**: Nếu sau 60 ngày và > 250 Pin mà Impressions < 5.000/tháng → đổi bộ template Pin & từ khóa ngách.

---

## 4. Lộ trình xếp chồng 5 nguồn doanh thu (Revenue Stacking)

Không ôm hết cùng lúc — mở dần từng tầng khi đạt đúng mốc traffic:

1. **Tầng 1 — Affiliate cơ bản (Mốc ≥ 20–30 click/ngày, Tháng 2–3)**:
   - Mua tên miền `.com` (~\$10/năm) + bật `"showDomainOnPins": true`.
   - Đăng ký **Amazon Associates Mỹ** + **Payoneer** (rút USD về ngân hàng VN).
2. **Tầng 2 — Quảng cáo hiển thị (Display Ads)**:
   - Gắn **Google AdSense** ngay khi có `.com` + ≥ 20 bài (~2–6 USD / 1.000 lượt xem).
   - Khi đạt **≥ 10.000 phiên/tháng** → nâng cấp lên **Journey by Mediavine** (RPM ngách Home Mỹ ~15–30 USD / 1.000 lượt xem).
3. **Tầng 3 — Mạng Affiliate biên cao hơn (Tháng 3–4)**:
   - Đăng ký qua **Impact.com / Awin / CJ Affiliate** để gắn thêm **Wayfair, Target, The Container Store, Etsy** (đơn \$100–\$400, hoa hồng 5–10%).
4. **Tầng 4 — Sản phẩm số PDF \$5–\$9 (Đã mở bán sớm!)**:
   - Đã tạo và mở bán bộ **The January Apartment Reset Kit + 72 Minimalist Pantry & Fridge Labels (\$5)** trên Gumroad (`https://khoaanh4.gumroad.com/l/aqhxc`), gắn khung mua vào tất cả bài viết trên web.
   - **Quy tắc đăng Pin cho Gumroad**: Chỉ đăng **1–2 Pin/tuần** trỏ thẳng về link Gumroad (đổi góc thiết kế khác nhau mỗi lần: nhãn tủ bếp, lịch 30 ngày, bảng đo tủ); **90% Pin còn lại** vẫn trỏ về các bài viết trên web NeatNook để tránh spam và tối ưu tỷ lệ chuyển đổi tự nhiên.
5. **Tầng 5 — Gom Email & Mở rộng kênh traffic miễn phí (Tháng 4–6)**:
   - Tặng checklist miễn phí để gom danh sách email → gửi bản tin tuần tự động qua **beehiiv** (ăn thêm affiliate + beehiiv Ad Network).
   - Khai thác thêm **Google SEO** (`sitemap.xml` + FAQ sẵn có), **Flipboard**, và **Facebook Page tiếng Anh**.
