# Handoff Backend: biểu đồ Xác suất mua hàng

## Mục tiêu

Frontend cần hiển thị biểu đồ phân bố xác suất mua lại trên trang Tổng quan.
Dữ liệu được lấy từ object `predictions` của endpoint:

```http
GET /api/v1/analytics/dashboard/overview
```

Các query filter hiện tại của dashboard vẫn được gửi kèm như `period`, `from`,
`to`, `segment`, `potential`, `category`, `employee`.

## Trạng thái hiện tại

UI đang nhận được:

```text
0 khách hàng có dự đoán
80 khách hàng chưa đủ dữ liệu
model_version = purchase-repeat-2026-09-19_2
```

Frontend vì thế hiển thị trạng thái:

```text
Chưa đủ dữ liệu
Chưa có khách hàng đủ dữ liệu để chạy dự đoán.
```

Việc có `model_version` chưa đủ để vẽ biểu đồ. Frontend chỉ hiển thị chart
khi `predictions.status` bằng `available` và `predictions.distribution` có dữ
liệu.

## Contract frontend đang sử dụng

```ts
type PredictionStatus = "available" | "not_deployed" | "insufficient_data"

interface DashboardPredictionBucket {
  label: string
  min: number
  max: number
  count: number
}

interface DashboardPredictions {
  status: PredictionStatus
  model_version: string | null
  prediction_date: string | null
  horizon_days: number | null
  feature_window: number | null
  evaluated_customers: number
  insufficient_count: number
  distribution: DashboardPredictionBucket[]
}
```

## Response cần có khi dự đoán khả dụng

```json
{
  "predictions": {
    "status": "available",
    "model_version": "purchase-repeat-2026-09-19_2",
    "prediction_date": "2026-09-20",
    "horizon_days": 90,
    "feature_window": 365,
    "evaluated_customers": 64,
    "insufficient_count": 16,
    "distribution": [
      {
        "label": "0–20%",
        "min": 0,
        "max": 0.2,
        "count": 8
      },
      {
        "label": "20–40%",
        "min": 0.2,
        "max": 0.4,
        "count": 14
      },
      {
        "label": "40–60%",
        "min": 0.4,
        "max": 0.6,
        "count": 18
      },
      {
        "label": "60–80%",
        "min": 0.6,
        "max": 0.8,
        "count": 16
      },
      {
        "label": "80–100%",
        "min": 0.8,
        "max": 1,
        "count": 8
      }
    ]
  }
}
```

Yêu cầu dữ liệu:

```text
sum(distribution[].count) = evaluated_customers
evaluated_customers + insufficient_count = tổng khách hàng sau khi áp filter
```

`purchase_probability` dùng thang `0–1`. Các bucket không được chồng lấn và
phải bao phủ toàn bộ khoảng `0–1`.

## Response khi chưa triển khai model

```json
{
  "predictions": {
    "status": "not_deployed",
    "model_version": null,
    "prediction_date": null,
    "horizon_days": null,
    "feature_window": null,
    "evaluated_customers": 0,
    "insufficient_count": 80,
    "distribution": []
  }
}
```

## Response khi model có nhưng khách hàng chưa đủ feature

```json
{
  "predictions": {
    "status": "insufficient_data",
    "model_version": "purchase-repeat-2026-09-19_2",
    "prediction_date": "2026-09-20",
    "horizon_days": 90,
    "feature_window": 365,
    "evaluated_customers": 0,
    "insufficient_count": 80,
    "distribution": []
  }
}
```

## Logic status đề xuất

```text
Không có model DEPLOYED
  -> status = not_deployed

Có model DEPLOYED nhưng không có prediction hợp lệ trong phạm vi filter
  -> status = insufficient_data

Có ít nhất một prediction hợp lệ
  -> status = available
  -> tạo distribution từ purchase_probability
```

## Checklist backend

- Lấy đúng model đang `DEPLOYED`.
- Đọc prediction tương ứng với model version hiện tại.
- Không loại toàn bộ khách hàng chỉ vì một feature phụ bị null nếu pipeline có
  giá trị mặc định hợp lệ.
- Áp cùng dashboard filters cho số khách được dự đoán và số khách thiếu dữ liệu.
- Trả `distribution` ngay trong dashboard overview; frontend không tự tải toàn
  bộ prediction để chia bucket.
- Đảm bảo tổng `count` trong distribution bằng `evaluated_customers`.
- Trả `status = available` khi `evaluated_customers > 0`.
- Thêm test cho đủ ba trạng thái: `available`, `not_deployed`,
  `insufficient_data`.

## Frontend mapping

```text
predictions.horizon_days
  -> mô tả “90 ngày tiếp theo”

predictions.status
  -> quyết định hiển thị chart hay empty state

predictions.distribution[].label
  -> trục X

predictions.distribution[].count
  -> chiều cao cột

predictions.evaluated_customers
  -> “x khách hàng có dự đoán”

predictions.insufficient_count
  -> “y chưa đủ dữ liệu”

predictions.model_version + prediction_date
  -> metadata cuối card
```
