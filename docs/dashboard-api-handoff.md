# Dashboard tổng quan API handoff

## Mục tiêu

API cung cấp toàn bộ dữ liệu cho trang `Tổng quan`, gồm KPI, xu hướng kinh
doanh, phân khúc khách hàng, điểm tiềm năng, nhóm sản phẩm, xác suất mua từ ML,
ma trận cơ hội và danh sách khách hàng ưu tiên.

Frontend hiện dùng mock theo đúng contract bên dưới. Khi API hoàn thành, FE chỉ
thay adapter dữ liệu và không tự tính lại nghiệp vụ phân tích hoặc ML.

Response mẫu đầy đủ: [`dashboard-overview.example.json`](./dashboard-overview.example.json).

## Endpoint

```http
GET /api/v1/analytics/dashboard/overview
```

- Yêu cầu đăng nhập.
- Quyền đề xuất: `analytics:read`.
- Backend phải tự giới hạn phạm vi dữ liệu theo người dùng.
- Không fallback sang mock nếu API lỗi.

## Query parameters

| Query | Kiểu | Mặc định | Ý nghĩa |
| --- | --- | --- | --- |
| `period` | `30d \| 90d \| 6m \| 12m \| custom` | `90d` | Khoảng phân tích |
| `from` | `YYYY-MM-DD` |  | Bắt buộc khi `period=custom` |
| `to` | `YYYY-MM-DD` |  | Bắt buộc khi `period=custom` |
| `segment` | segment code hoặc `all` | `all` | Phân khúc chính của khách hàng |
| `potential` | `HIGH \| POTENTIAL \| NORMAL \| INSUFFICIENT_DATA \| all` | `all` | Mức Potential Score |
| `category` | category ID hoặc `all` | `all` | Nhóm sản phẩm |
| `employee` | employee ID hoặc `all` | `all` | Nhân viên phụ trách |

Khi `period` khác `custom`, backend bỏ qua `from` và `to` từ client, sau đó tự
xác định ngày theo timezone nghiệp vụ.

Ví dụ:

```http
GET /api/v1/analytics/dashboard/overview?period=90d&segment=all&potential=HIGH&category=phone&employee=nv-01
```

## Response contract

```ts
interface DashboardOverview {
  meta: {
    source: "live"
    generated_at: string
    analysis_date: string
    run_id: string
    config_version: string
    currency: "VND"
    timezone: string
  }

  period: {
    from: string
    to: string
    previous_from: string
    previous_to: string
  }

  filters: {
    period: "30d" | "90d" | "6m" | "12m" | "custom"
    from: string
    to: string
    segment: string | "all"
    potential: "HIGH" | "POTENTIAL" | "NORMAL" | "INSUFFICIENT_DATA" | "all"
    category: string | "all"
    employee: string | "all"
  }

  metrics: {
    customers: DashboardMetric
    orders: DashboardMetric
    revenue: DashboardMetric
    aov: DashboardMetric
  }

  trend: DashboardTrendPoint[]
  segments: DashboardSegmentItem[]
  potential: DashboardPotentialSummary
  categories: DashboardCategoryItem[]
  predictions: DashboardPredictionSummary
  opportunity_customers: DashboardOpportunityCustomer[]
  priority_customers: DashboardPriorityCustomer[]
  priority_total: number

  data_quality: {
    valid_orders: number
    excluded_orders: number
    unscored_customers: number
    interaction_source: "real" | "simulated"
  }
}

interface DashboardMetric {
  current: number
  previous: number
  change_percent: number | null
}

interface DashboardTrendPoint {
  date: string
  previous_date: string
  revenue: number
  previous_revenue: number
  orders: number
  previous_orders: number
}

interface DashboardSegmentItem {
  key:
    | "HIGH_VALUE"
    | "LOYAL"
    | "AT_RISK"
    | "POTENTIAL"
    | "NEW_CUSTOMER"
    | "NORMAL"
    | "INSUFFICIENT_DATA"
  label: string
  count: number
}

interface DashboardBucket {
  label: string
  min: number
  max: number
  count: number
}

interface DashboardPotentialSummary {
  distribution: DashboardBucket[]
  high_count: number
  eligible_count: number
  insufficient_count: number
  average_score: number | null
  thresholds: {
    high: number
    potential: number
  }
  weights: {
    recency: number
    frequency: number
    monetary: number
    interaction: number
  }
}

interface DashboardCategoryItem {
  id: string
  name: string
  revenue: number
  orders: number
  units: number
  customers: number
}

interface DashboardPredictionSummary {
  status: "available" | "not_deployed" | "insufficient_data"
  model_version: string | null
  prediction_date: string | null
  horizon_days: number | null
  feature_window: number | null
  evaluated_customers: number
  insufficient_count: number
  distribution: DashboardBucket[]
}

interface DashboardOpportunityCustomer {
  id: string
  name: string
  segment: string
  potential_score: number
  purchase_probability: number
  revenue: number
}

interface DashboardPriorityCustomer {
  id: string
  name: string
  segment: string
  potential_score: number
  purchase_probability: number | null
  revenue: number
  employee_id: string | null
}
```

## Dữ liệu cho từng thành phần UI

| Thành phần | Field sử dụng |
| --- | --- |
| KPI | `metrics.customers`, `metrics.orders`, `metrics.revenue`, `metrics.aov` |
| Xu hướng kinh doanh | `trend[]` |
| Phân bố khách hàng | `segments[]` |
| Phân bố Potential Score | `potential.distribution[]` |
| Nhóm sản phẩm nổi bật | `categories[]` |
| Phân bố xác suất mua | `predictions.distribution[]` |
| Ma trận cơ hội khách hàng | `opportunity_customers[]` |
| Khách hàng tiềm năng cao | `priority_customers[]`, `priority_total` |
| Chất lượng dữ liệu | `data_quality` và `meta` |

### Ma trận cơ hội khách hàng

- Trục X: `purchase_probability * 100`.
- Trục Y: `potential_score`.
- Kích thước điểm: `revenue`.
- Màu điểm: `segment`.
- Chỉ trả khách có đồng thời Potential Score và kết quả ML.
- Giới hạn tối đa 80 khách để biểu đồ dễ đọc.
- Sắp xếp đề xuất: `potential_score * purchase_probability` giảm dần, sau đó
  theo ID để kết quả ổn định.

### Danh sách ưu tiên

- Trả tối đa 10 khách hàng.
- `priority_total` là tổng số khách đạt ngưỡng, không giới hạn 10.
- Sắp xếp Potential Score giảm dần, sau đó dùng ID làm khóa phụ.
- Potential Score và xác suất mua phải giữ độc lập.

## Quy tắc nghiệp vụ

1. Chỉ tính đơn hàng hợp lệ theo cấu hình. Đơn hủy không được tính.
2. Khi join chi tiết đơn, số đơn phải dùng `COUNT(DISTINCT order_id)`.
3. `revenue` là tổng giá trị giao dịch hợp lệ trong kỳ.
4. `aov = revenue / orders`; nếu không có đơn thì AOV bằng `0`.
5. `change_percent = (current - previous) / previous * 100`. Nếu kỳ trước bằng
   `0`, trả `null`.
6. Kỳ hiện tại và kỳ trước phải có cùng số ngày.
7. Chuỗi `trend` phải có đủ mọi ngày; ngày không phát sinh đơn trả giá trị `0`.
8. Potential Score dùng thang `0–100`.
9. `purchase_probability` dùng thang `0–1`; FE tự nhân `100` khi hiển thị.
10. Không được suy xác suất mua từ Potential Score.
11. Khách thiếu dữ liệu phải mang trạng thái `INSUFFICIENT_DATA`, không đưa vào
    bucket điểm `0`.
12. `segments[]` luôn trả đủ các nhóm, kể cả nhóm có `count = 0`.
13. `categories[]` sắp theo doanh thu giảm dần.
14. Tiền trả về dạng số nguyên VND. Nếu backend dùng Decimal dạng chuỗi thì cần
    thống nhất lại adapter với FE.

## Các invariant để kiểm thử

```text
sum(trend.revenue) == metrics.revenue.current
sum(trend.orders) == metrics.orders.current
sum(segments.count) == metrics.customers.current
potential.eligible_count + potential.insufficient_count == metrics.customers.current
predictions.evaluated_customers + predictions.insufficient_count == metrics.customers.current
priority_customers.length <= 10
opportunity_customers.length <= 80
```

Tổng doanh thu theo category có thể nhỏ hơn tổng KPI nếu dữ liệu đơn hàng chưa
được ánh xạ đầy đủ vào danh mục. Nếu hệ thống đảm bảo mọi dòng hàng đều có danh
mục thì hai tổng phải bằng nhau.

## Trạng thái ML

| Status | Ý nghĩa |
| --- | --- |
| `available` | Có mô hình đã triển khai và có kết quả dự đoán phù hợp |
| `not_deployed` | Chưa có mô hình được triển khai |
| `insufficient_data` | Có luồng dự đoán nhưng không đủ dữ liệu đầu vào |

Khi status khác `available`, `distribution` có thể rỗng,
`evaluated_customers = 0`, còn `model_version` và `prediction_date` trả `null`
nếu chưa có metadata.

## Endpoint options đề xuất

```http
GET /api/v1/analytics/dashboard/options
```

Response đề xuất:

```json
{
  "segments": [{ "value": "LOYAL", "label": "Trung thành" }],
  "potential_levels": [
    { "value": "HIGH", "label": "Tiềm năng cao", "min": 80 }
  ],
  "categories": [{ "value": "category-id", "label": "Điện thoại" }],
  "employees": [{ "value": "employee-id", "label": "Nguyễn Văn A" }],
  "max_custom_range_days": 366
}
```

Options cũng phải được giới hạn theo phạm vi dữ liệu mà người dùng được phép
xem.

## HTTP errors

| Status | Xử lý mong đợi |
| --- | --- |
| `401` | FE chạy refresh token; thất bại thì về trang đăng nhập |
| `403` | Không có quyền xem dashboard |
| `422` | Filter hoặc khoảng ngày không hợp lệ; trả lỗi field cụ thể |
| `500` | Trả lỗi an toàn, không lộ exception hoặc SQL |

Không có dữ liệu phù hợp vẫn trả `200`, KPI bằng `0`, danh sách rỗng và các
bucket có `count = 0`.

## Checklist bàn giao

- [ ] Chốt semantics của filter category giữa kỳ hiện tại và kỳ trước.
- [ ] Áp dụng quyền và phạm vi dữ liệu tại backend.
- [ ] Không chạy lại mô hình ML mỗi lần người dùng đổi filter dashboard.
- [ ] Trả metadata của snapshot/model thực tế đã dùng.
- [ ] Kiểm thử preset 30 ngày, 90 ngày, 6 tháng, 12 tháng và custom.
- [ ] Kiểm thử ngày không có đơn, kỳ trước bằng 0 và tập dữ liệu rỗng.
- [ ] Kiểm thử ML chưa triển khai và khách thiếu dữ liệu.
- [ ] Đối chiếu các invariant tổng hợp trước khi nối FE.
- [ ] Giữ response tương thích với JSON mẫu.
