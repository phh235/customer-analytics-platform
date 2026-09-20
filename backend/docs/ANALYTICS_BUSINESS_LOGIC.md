# Business Logic Analytics

> Tài liệu này mô tả logic nghiệp vụ đang được thực thi trong code hiện tại.
> Source of truth là backend analytics, không phải dữ liệu mẫu ở frontend.
>
> Phạm vi: RFM, trend, potential score, customer segment, repeat-purchase
> prediction, model lifecycle và priority list.

## 1. Mục tiêu nghiệp vụ

Hệ thống trả lời năm câu hỏi:

1. Khách hàng đã mua gần đây, mua bao nhiêu lần và chi bao nhiêu?
2. Khách hàng đang tăng hay giảm mức chi tiêu?
3. Khách hàng nào có tiềm năng chăm sóc hoặc bán thêm?
4. Khách hàng nào có khả năng mua lại trong một khoảng thời gian sắp tới?
5. Model nào đủ tốt để được triển khai phục vụ dự đoán?

Luồng tổng quát:

```text
Orders + interactions + reviews + order items
                    |
                    v
          Analysis window + valid statuses
                    |
          +---------+----------+
          |                    |
          v                    v
       RFM/trend          ML feature rows
          |                    |
          v                    v
 Potential score         Purchase-repeat model
          |                    |
          v                    v
      Segments       Probability per customer
          \                    /
           +--------+---------+
                    v
             Priority list
```

## 2. Khái niệm nền tảng

### 2.1. Order hợp lệ

Analytics chỉ sử dụng order có status thuộc cấu hình `VALID_ORDER_STATUSES`:

- `PAID`
- `COMPLETED`
- `DELIVERED`
- `PARTIAL_REFUNDED`

Code cũng chấp nhận dạng chữ thường tương ứng để tương thích với dataset hiện tại,
ví dụ `delivered` tương đương `DELIVERED`.

Các order có status khác không đóng góp vào RFM, behavior metrics, trend hoặc
training features.

Giá trị tiền dùng trong analytics là `orders.net_amount`, không phải
`total_amount`.

### 2.2. Múi giờ và ngày phân tích

Business timezone là `Asia/Ho_Chi_Minh`.

Một window `days` được tính theo dạng nửa kín:

```text
[from_utc, to_utc)
```

Vì vậy:

- order tại `from_utc` được tính;
- order tại `to_utc` không được tính;
- không bị đếm trùng khi nối tiếp hai khoảng thời gian.

Nếu API nhận `analysis_date = D`, `to_utc` là đầu ngày `D` theo giờ Việt Nam.
Feature window là `days` ngày ngay trước mốc đó; ngày `D` chưa hoàn tất không
được tính.

Ví dụ với `analysis_date = 2026-04-20`, `days = 365`:

```text
Feature window theo business date:
2025-04-20 -> hết ngày 2026-04-19
```

### 2.3. Khi không truyền `analysis_date`

Cách mặc định phụ thuộc loại API:

- Các API báo cáo/RFM thông thường dùng ngày hiện tại theo giờ Việt Nam.
- `GET /api/v1/analytics/segments` và
  `GET /api/v1/analytics/segments/{customer_id}` dùng `analysis_date` mới
  nhất của `analysis_runs` có trạng thái `COMPLETED` hoặc `SUCCESS`. Nếu
  database chưa có analysis run hoàn tất, API mới fallback về ngày hiện tại.
- API train model tự chọn cutoff lịch sử: ngày order hợp lệ mới nhất trừ
  `prediction_horizon_days`.

Cách này giữ kết quả phân khúc mặc định đồng nhất với snapshot Excel đã import,
trong khi query `analysis_date` tường minh vẫn cho phép chạy lại một mốc khác.

## 3. RFM và behavior metrics

### 3.1. Các chỉ số cơ bản

Các chỉ số dựa trên order tính trong feature window. Interaction và review là
chỉ số tích lũy theo toàn bộ lịch sử của customer:

| Chỉ số | Cách tính |
|---|---|
| `recency_days` | Số ngày dạng thập phân từ order hợp lệ gần nhất đến `analysis_date` |
| `frequency` | Số order hợp lệ |
| `monetary` | Tổng `net_amount` của order hợp lệ |
| `aov` | `monetary / frequency`; bằng `0` nếu không có order |
| `purchase_cycle_days` | Khoảng cách trung bình giữa các order hợp lệ |
| `interaction_score` | Tổng `interaction_value` toàn bộ lịch sử |
| `product_diversity` | Số product khác nhau đã mua trong window |
| `review_score` | Điểm review trung bình của customer |
| `channel_count` | Số kênh bán hàng khác nhau đã sử dụng |
| `trend` | So sánh spend gần đây với spend kỳ trước |

`interaction_score` là ngoại lệ so với order window: interaction không bị lọc theo
`analysis_date` hoặc `days`. `review_score` cũng lấy trung bình toàn bộ review của
customer.

Nếu chỉ có một order, `purchase_cycle_days` là `null` trong behavior API và được
đưa thành `0` khi làm ML feature.

Nếu không có order hợp lệ trong window:

- `frequency = 0`;
- `monetary = 0`;
- `recency_days` và các R/F/M score là `null`;
- customer không được đưa vào training rows.

### 3.2. RFM score năm mức

Recency và Monetary hiện dùng bucket ranking trong cohort order hợp lệ của
feature window. Frequency là ngoại lệ theo công thức chốt:

- raw Frequency dùng toàn bộ order hợp lệ trước `analysis_date`;
- cohort Frequency gồm toàn bộ customer, kể cả customer có `Frequency = 0`;
- `PERCENTRANK = count(Frequency nhỏ hơn giá trị hiện tại) / (N - 1)`;
- `FScore = ceil(PERCENTRANK × 4 + 1)`, giới hạn trong `1..5`.

Ví dụ với `N = 80`, nếu có `55` customer có Frequency nhỏ hơn `3`:

```text
PERCENTRANK = 55 / 79 = 0,6962
FScore = ceil(0,6962 × 4 + 1) = 4
```

Recency vẫn sort tăng dần; Monetary sort giảm dần và dùng:

```text
bucket = min(4, floor(rank * 5 / N))
score = 5 - bucket
```

Customer không có order trong feature window vẫn có thể có FScore từ cohort
lifetime, nhưng R/M score là `null` nếu feature window không có order.

### 3.3. Interaction score

`interaction_score` là raw score: tổng `interaction_value` trong toàn bộ lịch sử
customer, không giới hạn theo feature window và không cap ở `100`.

Potential Score dùng Interaction đã chuẩn hóa liên tục về thang `1..5` bằng
min-max trên cohort toàn bộ customer:

```text
InteractionNormalized =
  1 + (InteractionRaw - MinInteractionRaw)
      / (MaxInteractionRaw - MinInteractionRaw) × 4
```

Nếu `MaxInteractionRaw = MinInteractionRaw`, dùng giá trị trung tâm `3`.

Ví dụ dataset hiện tại có Interaction Raw từ `10` đến `15`. Với KH0041:

```text
InteractionRaw = 13
InteractionNormalized = 1 + (13 - 10) / (15 - 10) × 4 = 3,4
```

`rfm_score = r_score + f_score + m_score`, tối đa `15`. Interaction không cộng
trực tiếp vào `rfm_score`; Interaction raw và normalized chỉ dùng ở potential score.


### 3.4. Trend

Với feature window `days`, khoảng gần đây có độ dài:

```text
recent_days = max(30, min(days / 4, 90))
```

Hệ thống so sánh:

- `recent_spend`: chi tiêu trong khoảng gần đây;
- `previous_spend`: chi tiêu trong khoảng ngay trước khoảng gần đây.

```text
growth_ratio = (recent_spend - previous_spend) / previous_spend
```

Quy tắc:

| Điều kiện | Trend |
|---|---|
| `previous_spend <= 0` và `recent_spend > 0` | `STRONG_INCREASE` |
| `previous_spend <= 0` và `recent_spend = 0` | `STABLE` |
| `growth_ratio <= -0.5` | `STRONG_DECREASE` |
| `-0.5 < growth_ratio < -0.1` | `DECREASE` |
| `growth_ratio >= 0.5` | `STRONG_INCREASE` |
| `0.1 < growth_ratio < 0.5` | `INCREASE` |
| Còn lại | `STABLE` |

## 4. Potential score

Potential score là điểm từ `0` đến `100`, dùng để đánh giá tiềm năng chăm sóc hoặc
bán thêm, không phải xác suất mua lại của ML model.

### 4.1. Công thức mặc định

```text
Potential score =
  (R * 0.35 + F * 0.30 + M * 0.20 + Interaction * 0.15) * 20
```

Trong đó R, F và M là score nguyên từ `1` đến `5`; Interaction là
`InteractionNormalized` liên tục từ `1` đến `5`.

### 4.2. Missing data và trọng số

Với customer có order hợp lệ, cả bốn component R, F, M và Interaction đều
nhận score từ `1` đến `5`, nên luôn dùng đủ trọng số:

```text
R = 35%
F = 30%
M = 20%
Interaction = 15%
```

Customer không có order hợp lệ không tính được R/F/M và nhận
`INSUFFICIENT_DATA`. Không renormalize trọng số.

### 4.3. Level

| Potential score | Level |
|---:|---|
| `>= 80` | `HIGH` |
| `60-<80` | `POTENTIAL` |
| `< 60` | `NORMAL` |
| Không đủ dữ liệu | `INSUFFICIENT_DATA` |

## 5. Customer segmentation

Segment được suy ra trực tiếp từ Potential Score:

| Potential score | Segment |
|---:|---|
| `>= 80` | `HIGH` |
| `60-<80` | `POTENTIAL` |
| `< 60` | `NORMAL` |
| Không có order hợp lệ | `INSUFFICIENT_DATA` |

Trong API hiện tại, enum `HIGH_VALUE` là tên tương thích của mức `HIGH`
trong công thức. Không còn ưu tiên riêng các rule `HIGH_VALUE`, `LOYAL`,
`AT_RISK` hoặc `NEW_CUSTOMER` trước Potential Score.

## 6. Repeat-purchase prediction

Đây là model dự đoán customer có phát sinh order hợp lệ trong prediction horizon hay
không.

### 6.1. Training window và label

Với `analysis_date = D`, các khoảng thời gian được hiểu theo business date:

```text
Feature window: [D - feature_window_days, D)
Label window:   [D, D + prediction_horizon_days)
```

Ví dụ `D = 2026-04-20` và horizon `90` ngày:

```text
Feature window: 2025-04-20 -> hết ngày 2026-04-19
Label window:   2026-04-20 -> hết ngày 2026-07-19
```

Theo implementation, label là:

```text
label = 1 nếu tồn tại ít nhất một order hợp lệ trong label window
label = 0 nếu không tồn tại order hợp lệ trong label window
```

Customer không có `recency_days` trong feature window bị loại khỏi training.
Training tối thiểu cần:

- ít nhất `4` customer có label;
- có cả label `0` và label `1`.

### 6.2. ML features

Model hiện tại sử dụng đúng 8 feature sau, theo đúng thứ tự:

```text
recency
frequency
monetary
aov
purchase_cycle
interaction_score
product_diversity
review_score
```

Các giá trị `null` khi đưa vào model được thay bằng `0`.
Trong training, `interaction_score` là raw interaction value tích lũy toàn bộ lịch sử
và được giữ ở dạng raw; chỉ khi tính RFM/Potential Score mới quy đổi sang thang 5.

### 6.3. Model type

API hỗ trợ:

- `LOGISTIC_REGRESSION`: logistic regression tự triển khai, batch gradient descent;
- `RANDOM_FOREST`: ensemble deterministic của các one-level decision tree.

Trước khi train, feature được standardize theo mean và scale của training set.
Artifact lưu các tham số chuẩn hóa cùng tham số model để dùng lại lúc prediction.

### 6.4. Metrics và approval gates

Các metrics chính:

- Accuracy
- Precision
- Recall
- F1
- ROC-AUC
- PR-AUC
- Precision@Top10
- Lift@Top10
- Overall conversion
- Baseline PR-AUC

`baseline_pr_auc` trong training hiện bằng overall conversion:

```text
baseline_pr_auc = số positive labels / tổng số training rows
```

Model chỉ được `APPROVED` khi đồng thời thỏa cả ba điều kiện:

```text
PR-AUC > baseline PR-AUC
Lift@Top10 >= 2.0
Precision@Top10 >= 2.0 * overall conversion
```

Các ngưỡng được cấu hình bởi:

- `ML_MIN_LIFT_TOP10`
- `ML_MIN_PRECISION_TOP10_MULTIPLIER`
- `ML_BASELINE_PR_AUC`

### 6.5. Lifecycle và deployment

`POST /api/v1/analytics/models/train` thực hiện:

1. Tạo training feature rows.
2. Train model.
3. Tạo artifact JSON trong `MODEL_STORAGE_DIR`.
4. Đăng ký model với trạng thái `TRAINED`.
5. Đánh giá metrics.
6. Chuyển thành `APPROVED` nếu pass toàn bộ gate.

Train không tự động deploy model.

Chỉ model `APPROVED` mới được deploy qua:

```text
POST /api/v1/analytics/models/{version}/deploy
```

Khi deploy một model, model `DEPLOYED` trước đó được chuyển về `APPROVED`.
Hệ thống chỉ phục vụ prediction từ model được deploy rõ ràng. Nếu không có model
deployed hoặc artifact không đọc được, prediction API trả lỗi `503`.

## 7. Prediction và priority list

### 7.1. Purchase probability

Với mỗi customer có order hợp lệ trong feature window, hệ thống tạo 8 feature ML,
đọc artifact của model deployed và trả:

- `purchase_probability` từ `0` đến `1`;
- model version;
- feature window days;
- prediction horizon days.

Probability không phải label thực tế. Label chỉ biết sau khi prediction horizon kết
thúc; probability là đánh giá trước thời điểm đó.

### 7.2. Priority list

Customer được đưa vào priority list nếu thỏa ít nhất một điều kiện:

```text
potential_score >= 80
OR
purchase_probability >= 0.5
```

Priority list kết hợp:

- potential score;
- purchase probability;
- preferred product category;
- purchase cycle;
- priority reason;
- recommended next action.

## 8. Customer scope và quyền truy cập

Analytics áp dụng scope theo user hiện tại:

- `ADMIN`: xem toàn bộ customer;
- `MANAGER`: chỉ customer thuộc team của manager;
- user thông thường: chỉ customer được assign cho user;
- user không có scope hợp lệ: không trả dữ liệu customer.

Scope được áp dụng ở repository query, không chỉ lọc ở frontend.

Các thao tác model lifecycle yêu cầu quyền admin, gồm:

- đăng ký model;
- list model;
- train model;
- evaluate model;
- deploy model.

## 9. Các API chính

| API | Mục đích |
|---|---|
| `GET /api/v1/analytics/rfm` | RFM cho toàn bộ customer |
| `GET /api/v1/analytics/rfm/{customer_id}` | RFM một customer |
| `GET /api/v1/analytics/segments` | Phân nhóm customer |
| `GET /api/v1/analytics/potential-scores` | Potential score |
| `GET /api/v1/analytics/priority-list` | Danh sách ưu tiên kết hợp score và ML |
| `GET /api/v1/analytics/predictions/purchase-repeat` | Xác suất mua lại từ model deployed |
| `GET /api/v1/analytics/customer-360/{customer_id}` | Tổng hợp hồ sơ, order và analytics |
| `POST /api/v1/analytics/models/train` | Train và evaluate model |
| `GET /api/v1/analytics/models` | Danh sách model versions |
| `POST /api/v1/analytics/models/{version}/deploy` | Deploy model đã approved |
| `POST /api/v1/analytics/recalculate` | Tính lại RFM, segments, potential scores và lưu segment history |

Các API nhận `days` và một số API nhận thêm `analysis_date`. Ba API
`GET /api/v1/analytics/segments`, `GET /api/v1/analytics/predictions/purchase-repeat`
và `GET /api/v1/analytics/priority-list` hỗ trợ thêm query `search`, tìm không
phân biệt hoa thường theo tên/customer ID; predictions còn tìm theo model version,
priority còn tìm theo mức tiềm năng, danh mục, lý do và khuyến nghị.
Endpoint `/api/v1/analytics/segments` vẫn hỗ trợ `page` (mặc định `1`) và `size`
(mặc định `10`, tối đa `100`), trả về `{current, size, total, pages, records}`.

## 10. Ví dụ đối chiếu thủ công

Giả sử:

```text
analysis_date = 2026-04-20
feature_window_days = 365
prediction_horizon_days = 90
```

Customer `KH0013` có:

```text
frequency = 2
monetary = 4,613,000
AOV = 4,613,000 / 2 = 2,306,500
```

Nếu customer có order hợp lệ trong khoảng `2026-04-21` đến `2026-07-19`,
label của customer là `1`. Nếu không có order trong khoảng đó, label là `0`.

Label này dùng để đánh giá model sau training; nó không phải là probability mà
model trả cho customer.

## 11. Những điểm cần tránh khi phân tích

1. Không dùng mọi order bất kể status; phải lọc valid order statuses.
2. Không trộn `total_amount` với `net_amount`.
3. Không so sánh hai báo cáo dùng khác `analysis_date` hoặc khác `days`.
4. Không dùng ngày hiện tại làm cutoff training nếu label window chưa có dữ liệu
   tương lai.
5. Không coi `potential_score` là `purchase_probability`.
6. Không phục vụ prediction từ model chỉ ở trạng thái `TRAINED` hoặc `APPROVED`;
   model phải được deploy.
7. Không diễn giải `label = 1` là chắc chắn khách sẽ mua lại trong tương lai;
   đó là kết quả lịch sử dùng làm ground truth cho training.

## 12. Source code chính

- `backend/src/customer_analytics/app/features/analytics/infrastructure/repositories/analytics_repository_impl.py`
- `backend/src/customer_analytics/app/features/analytics/application/services/purchase_model.py`
- `backend/src/customer_analytics/app/features/analytics/application/services/model_lifecycle_service.py`
- `backend/src/customer_analytics/app/features/analytics/domain/analysis_window.py`
- `backend/src/customer_analytics/app/config.py`
- `backend/src/customer_analytics/app/features/analytics/presentation/routes/analytics_routes.py`
- `backend/src/customer_analytics/app/features/analytics/presentation/schema/analytics_schemas.py`
