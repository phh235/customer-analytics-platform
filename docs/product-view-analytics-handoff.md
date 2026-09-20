# Handoff: Product View Analytics và ghi nhận lượt xem sản phẩm

## Mục tiêu

Khi khách hàng mở trang chi tiết sản phẩm, hệ thống phải ghi nhận một lượt xem.
Admin sau đó có thể xem KPI, biểu đồ theo thời gian, danh sách khách đã xem và
các sản phẩm đang tăng mức độ quan tâm.

Tài liệu này phân biệt rõ hai luồng:

1. **User Product Detail** ghi dữ liệu lượt xem.
2. **Admin Product Analytics** đọc và tổng hợp dữ liệu đã ghi.

## Trạng thái hiện tại

### Frontend user

Khi người dùng mở Product Detail, frontend hiện gọi:

```http
GET /api/v1/products/{product_id}
GET /api/v1/products?page=1&size=12
```

Request thứ hai dùng để lấy sản phẩm liên quan. Sau khi Product Detail tải thành
công và phiên đăng nhập đã sẵn sàng, frontend gọi thêm:

```http
POST /api/v1/products/{product_id}/view
```

Request tracking không chặn render và không hiển thị lỗi cho user. Frontend có
guard 2 giây theo `product_id` để tránh React remount gửi trùng ngay lập tức.

Endpoint lấy chi tiết sản phẩm trong OpenAPI hiện chỉ có mô tả:

```text
Get product by ID. Requires products:read permission.
```

Không có thông tin cho thấy endpoint này tự ghi `product_view`.

### Frontend admin

Frontend đã nối các API đọc thống kê sau:

| API                                                                    | Thành phần sử dụng               |
| ---------------------------------------------------------------------- | -------------------------------- |
| `GET /api/v1/analytics/products/{product_id}/interest`                 | KPI tổng quan                    |
| `GET /api/v1/analytics/products/{product_id}/views`                    | Tổng lượt xem                    |
| `GET /api/v1/analytics/products/{product_id}/unique-viewers`           | Số khách xem duy nhất            |
| `GET /api/v1/analytics/products/{product_id}/viewers`                  | Tần suất xem theo khách hàng     |
| `GET /api/v1/analytics/products/{product_id}/top-interested-customers` | Bảng khách quan tâm nhiều nhất   |
| `GET /api/v1/analytics/products/{product_id}/trend`                    | Biểu đồ ngày/tuần/tháng          |
| `GET /api/v1/analytics/products/trending`                              | Sản phẩm xu hướng trên Dashboard |

Các route trên đã xuất hiện trong OpenAPI và trả `401` khi gọi không có access
token, xác nhận route đang tồn tại và được bảo vệ.

## Vấn đề cần xử lý

Các API analytics hiện tại đều là API **đọc dữ liệu**. Ví dụ:

```http
GET /api/v1/analytics/products/{product_id}/views
```

API này chỉ trả tổng lượt xem đã có, không tạo lượt xem mới. Vì chưa có endpoint
ghi nhận hành vi, việc user mở Product Detail trên frontend không làm tăng
`total_views` và không tạo dữ liệu mới cho `/viewers` hoặc `/trend`.

Nếu dữ liệu analytics hiện đang có số liệu, số liệu đó đến từ dữ liệu import,
seed hoặc một nguồn backend khác; nó chưa phản ánh lượt mở Product Detail mới
từ frontend.

## Flow cần hoàn thiện

```text
User mở Product Detail
        ↓
GET /api/v1/products/{product_id}
        ↓
Hiển thị thông tin sản phẩm
        ↓
POST /api/v1/products/{product_id}/view
        ↓
Backend xác định customer từ access token
        ↓
Lưu product_view và viewed_at
        ↓
Admin mở Product Analytics
        ↓
Các API /views, /viewers, /trend... tổng hợp dữ liệu vừa ghi
```

## Endpoint ghi nhận lượt xem đề xuất

```http
POST /api/v1/products/{product_id}/view
Authorization: Bearer <access_token>
Content-Type: application/json
```

Request body tối thiểu:

```json
{}
```

Backend nên lấy `customer_id` từ access token hoặc quan hệ giữa user đang đăng
nhập và customer. Không nhận `customer_id` trực tiếp từ frontend để tránh giả
mạo lượt xem của khách khác.

Nếu cần thêm ngữ cảnh:

```json
{
  "channel": "WEB",
  "session_id": "ses_abc123"
}
```

Response đề xuất:

```json
{
  "success": true,
  "product_id": "abc-123",
  "viewed_at": "2026-09-20T16:30:00+07:00"
}
```

Status code:

| Status           | Ý nghĩa                                |
| ---------------- | -------------------------------------- |
| `201` hoặc `204` | Ghi nhận thành công                    |
| `401`            | Chưa đăng nhập hoặc token không hợp lệ |
| `403`            | Tài khoản không được phép xem sản phẩm |
| `404`            | Sản phẩm không tồn tại                 |

## Dữ liệu backend cần lưu

Một record lượt xem tối thiểu cần có:

```text
id
customer_id
product_id
interaction_type = product_view
viewed_at
channel = WEB
session_id (nullable)
```

Nếu backend dùng bảng `customer_interactions`, nên thống nhất timestamp thực tế
dùng để tổng hợp với các API analytics. Các API phải cùng lọc theo một trường
thời gian và cùng timezone nghiệp vụ.

## Quy tắc đếm

### Tổng lượt xem

```text
total_views = COUNT(product_view)
```

Mỗi lần user mở Product Detail có thể được tính là một lượt. Backend nên chốt
quy tắc chống đếm lặp do React remount, refresh hoặc retry mạng.

Đề xuất cho MVP:

```text
Cùng customer + product + session trong vòng 2–5 giây
    → chỉ ghi một lượt
```

### Người xem duy nhất

```text
unique_viewers = COUNT(DISTINCT customer_id)
```

### Số lần xem theo khách

```text
GROUP BY customer_id, product_id
views = COUNT(*)
```

### Trend

Nhóm các record theo `viewed_at` và `group_by`:

```text
day   → ngày
week  → tuần
month → tháng
```

Khoảng thời gian dùng `from_date` và `to_date`, tính cả hai đầu mốc. Những mốc
không có lượt xem nên trả `views = 0` để biểu đồ không bị đứt quãng.

## Contract frontend đang sử dụng

### Interest

```http
GET /api/v1/analytics/products/{product_id}/interest
    ?from_date=2026-09-01
    &to_date=2026-09-30
```

```json
{
  "product_id": "abc-123",
  "product_code": "SP001",
  "product_name": "Tai nghe Bluetooth",
  "total_views": 128,
  "unique_viewers": 45,
  "from_date": "2026-09-01",
  "to_date": "2026-09-30"
}
```

### View trend

```http
GET /api/v1/analytics/products/{product_id}/trend
    ?from_date=2026-09-01
    &to_date=2026-09-30
    &group_by=day
```

```json
{
  "product_id": "abc-123",
  "product_code": "SP001",
  "product_name": "Tai nghe Bluetooth",
  "group_by": "day",
  "from_date": "2026-09-01",
  "to_date": "2026-09-30",
  "points": [
    {
      "period_start": "2026-09-01",
      "views": 12
    }
  ]
}
```

Frontend hiện chỉ vẽ một đường `views` vì response trend chưa trả số khách duy
nhất theo từng mốc.

### Viewers và top interested customers

Hai endpoint đang dùng cùng dạng response:

```json
{
  "product_id": "abc-123",
  "product_code": "SP001",
  "product_name": "Tai nghe Bluetooth",
  "from_date": "2026-09-01",
  "to_date": "2026-09-30",
  "records": [
    {
      "customer_id": "cus-001",
      "customer_code": "KH0001",
      "customer_name": "Nguyễn Văn A",
      "views": 12,
      "last_view_at": "2026-09-18T21:15:00+07:00"
    }
  ]
}
```

### Trending products

```http
GET /api/v1/analytics/products/trending?period_days=7&limit=10
```

Frontend hỗ trợ `period_days = 7` và `period_days = 30`.

## Frontend ghi nhận lượt xem

Frontend gọi API view sau khi `GET /products/{product_id}` trả thành công:

```ts
void recordProductView(product.id).catch(() => undefined);
```

Việc ghi nhận không được chặn render Product Detail. Nếu request tracking lỗi,
user vẫn xem được sản phẩm; lỗi có thể được ghi vào observability nhưng không
hiển thị toast gây gián đoạn trải nghiệm.

Frontend cũng cần chống gọi lặp trong cùng một mount/session. Backend vẫn phải
có chống trùng vì client-side guard không đủ tin cậy.

## Không nên làm

- Không gọi `/interest` hoặc `/views` từ Product Detail chỉ để “tạo” lượt xem;
  đây là API đọc và không thay đổi dữ liệu.
- Không để frontend gửi `customer_id` tùy ý.
- Không ghi dữ liệu bằng một request `GET` nếu có thể tránh, vì prefetch, cache
  và retry có thể làm tăng số lượt sai.
- Không lấy số liệu mock để cộng vào analytics thật.
- Không làm Product Detail thất bại chỉ vì request tracking thất bại.

## Checklist backend

- [ ] Thêm endpoint ghi nhận lượt xem sản phẩm.
- [ ] Xác định `customer_id` từ người dùng đăng nhập.
- [ ] Kiểm tra sản phẩm tồn tại và user có quyền xem.
- [ ] Lưu timestamp theo timezone/UTC thống nhất.
- [ ] Chốt quy tắc chống lượt xem trùng.
- [ ] Đảm bảo `/views` tăng sau khi ghi event.
- [ ] Đảm bảo `/unique-viewers` chỉ tăng ở lượt đầu của customer mới.
- [ ] Đảm bảo `/viewers` cập nhật `views` và `last_view_at`.
- [ ] Đảm bảo `/trend` cập nhật đúng bucket ngày/tuần/tháng.
- [ ] Đảm bảo `/trending` dùng cùng nguồn `product_view`.
- [ ] Thêm test cho ghi nhận thành công, sản phẩm không tồn tại, token không hợp
      lệ và chống trùng.

## Checklist nghiệm thu end-to-end

1. Ghi lại `total_views` hiện tại của một sản phẩm.
2. Đăng nhập bằng tài khoản customer.
3. Mở Product Detail của sản phẩm đó.
4. Xác nhận Network có request ghi nhận lượt xem và response thành công.
5. Mở Product Analytics bằng admin.
6. Xác nhận `total_views` tăng đúng theo quy tắc chống trùng.
7. Xác nhận customer xuất hiện trong `/viewers` và
   `/top-interested-customers`.
8. Xác nhận `/trend` tăng tại bucket ngày hiện tại.
9. Đổi `group_by` sang tuần và tháng, đối chiếu tổng số lượt.
10. Xác nhận mở Product Detail không bị lỗi khi tracking tạm thời thất bại.

## Các file frontend liên quan

```text
frontend/src/pages/client/product-detail.tsx
frontend/src/api/product-analytics.ts
frontend/src/hooks/use-product-analytics.ts
frontend/src/pages/admin/product-analytics.tsx
frontend/src/features/dashboard/trending-products.tsx
```
