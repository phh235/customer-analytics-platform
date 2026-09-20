# BỘ CÔNG THỨC PHÂN TÍCH KHÁCH HÀNG VÀ POTENTIAL SCORE

## 1. Công thức dữ liệu hành vi gốc

### 1.1. Recency

**Bài toán cần giải quyết:**  
Xác định khách hàng đã bao lâu chưa phát sinh giao dịch.

```text
Recency = AnalysisDate - Max(OrderDate hợp lệ)
```

### 1.2. Frequency

**Bài toán cần giải quyết:**  
Xác định số lần khách hàng mua hàng trong cửa sổ phân tích.

```text
Frequency = COUNT(DISTINCT OrderID hợp lệ)
```

### 1.3. Monetary

**Bài toán cần giải quyết:**  
Xác định tổng giá trị mua hàng của khách hàng.

```text
Monetary = SUM(OrderTotal của các đơn hợp lệ)
```

### 1.4. AOV

**Bài toán cần giải quyết:**  
Xác định giá trị trung bình trên mỗi đơn hàng.

```text
AOV = Monetary / Frequency
```

Nếu:

```text
Frequency = 0
```

thì:

```text
AOV = 0
```

### 1.5. Purchase Cycle

**Bài toán cần giải quyết:**  
Xác định khoảng thời gian trung bình giữa các lần mua liên tiếp.

```text
Purchase Cycle
= Trung bình số ngày giữa các lần mua liên tiếp
```

Nếu khách hàng có dưới 2 đơn hợp lệ:

```text
Purchase Cycle = NULL / Chưa đủ dữ liệu
```

---

# 2. Chuẩn hóa R/F/M theo 5 nhóm

Tất cả khách hàng có giao dịch hợp lệ được xếp hạng thành 5 nhóm.

```text
Hạng tốt nhất      → 5
Hạng tiếp theo     → 4
                    → 3
                    → 2
Hạng thấp nhất     → 1
```

## 2.1. Recency Score

Recency càng nhỏ càng tốt.

```text
20% khách có Recency thấp nhất → RScore = 5
20% tiếp theo                  → RScore = 4
20% tiếp theo                  → RScore = 3
20% tiếp theo                  → RScore = 2
20% cao nhất                   → RScore = 1
```

## 2.2. Frequency Score

Frequency càng lớn càng tốt. Raw Frequency của RFM là tổng số order hợp lệ
của customer trong toàn bộ lịch sử trước `AnalysisDate`, bao gồm cả customer
có `Frequency = 0` trong cohort.

Với `N` customer trong cohort:

```text
PERCENTRANK
= COUNT(Frequency nhỏ hơn Frequency hiện tại) / (N - 1)
```

Sau đó:

```text
FScore = ROUNDUP(PERCENTRANK × 4 + 1, 0)
FScore = MAX(1, MIN(5, FScore))
```

Ví dụ cohort có `N = 80`, và có `55` customer có Frequency nhỏ hơn `3`:

```text
PERCENTRANK = 55 / (80 - 1) = 0,6962
FScore = ROUNDUP(0,6962 × 4 + 1, 0)
       = ROUNDUP(3,7848, 0)
       = 4
```

## 2.3. Monetary Score

Monetary càng lớn càng tốt.

```text
20% Monetary cao nhất → MScore = 5
20% tiếp theo         → MScore = 4
20% tiếp theo         → MScore = 3
20% tiếp theo         → MScore = 2
20% thấp nhất         → MScore = 1
```

---

# 3. Công thức bucket

Giả sử sau khi sắp xếp có `N` khách hàng.

```text
bucket = floor(rank × 5 / N)
```

`Frequency Score` dùng công thức `PERCENTRANK` riêng tại mục 2.2 để giữ
đúng phân bố toàn bộ customer, bao gồm nhóm `Frequency = 0`.
Trong đó:

```text
rank = 0, 1, 2, ..., N-1
```

Sau đó:

```text
Score = 5 - bucket
```

Pseudo-code:

```python
bucket = min(4, floor(rank * 5 / total_customers))
score = 5 - bucket
```

Quy tắc sắp xếp:

```text
Recency   → sort tăng dần
Frequency → sort giảm dần
Monetary  → sort giảm dần
```

---

# 4. Quy đổi từ thang 1–5 sang thang 20–100

Nếu cần hiển thị theo thang 100:

```text
Normalized Score = Score × 20
```

Mapping:

```text
1 → 20
2 → 40
3 → 60
4 → 80
5 → 100
```

Ví dụ:

```text
RScore = 3
```

thì:

```text
R_Normalized = 3 × 20 = 60
```

---

# 5. Interaction Score

## 5.1. Interaction Raw Score

**Bài toán cần giải quyết:**  
Đo mức độ quan tâm của khách hàng thông qua các hành vi tương tác.

| Interaction Type | Điểm |
|---|---:|
| `email_open` | 1 |
| `product_view` | 1 |
| `search` | 1 |
| `wishlist` | 2 |
| `email_click` | 2 |
| `chat` | 3 |
| `add_to_cart` | 3 |
| `checkout_started` | 4 |

Công thức:

```text
Interaction Raw Score
= SUM(interaction_value)
```

Ví dụ KH0041:

```text
search            = 1
checkout_started  = 4
chat              = 3
add_to_cart       = 3
email_open        = 1
product_view      = 1
```

Kết quả:

```text
Interaction Raw Score
= 1 + 4 + 3 + 3 + 1 + 1
= 13
```

## 5.2. Chuẩn hóa Interaction Score

Không dùng trực tiếp `Interaction Raw Score` để tính Potential Score. Interaction
được chuẩn hóa liên tục về thang `1..5` bằng min-max trên cohort toàn bộ customer:

```text
InteractionNormalized
= 1 + (InteractionRaw - MinInteractionRaw)
    / (MaxInteractionRaw - MinInteractionRaw) × 4
```

Nếu `MaxInteractionRaw = MinInteractionRaw`, dùng giá trị trung tâm `3`.

Ví dụ dataset hiện tại:

```text
MinInteractionRaw = 10
MaxInteractionRaw = 15
InteractionRaw(KH0041) = 13
```

```text
InteractionNormalized
= 1 + (13 - 10) / (15 - 10) × 4
= 3,4
```

Giá trị `3,4` được dùng trực tiếp trong Potential Score; cột hiển thị
`InteractionScore` vẫn là raw score `13`.

---

# 6. Potential Score

## 6.1. Cách A – Tính trực tiếp từ thang 1–5

**Công thức khuyến nghị:**

```text
Potential Score
=
(
  RScore × 35
+ FScore × 30
+ MScore × 20
+ InteractionNormalized × 15
) / 5
```

Trọng số:

```text
Recency     = 35%
Frequency   = 30%
Monetary    = 20%
Interaction = 15%
```

Ví dụ:

```text
R = 3
F = 5
M = 5
I = 4
```

Tính:

```text
Potential Score
=
(3×35 + 5×30 + 5×20 + 4×15) / 5
```

```text
= (105 + 150 + 100 + 60) / 5
= 415 / 5
= 83
```

Kết quả:

```text
Potential Score = 83
```

## 6.2. Cách B – Quy đổi sang thang 100 trước

```text
R_Normalized = RScore × 20
F_Normalized = FScore × 20
M_Normalized = MScore × 20
I_Normalized = InteractionNormalized × 20
```

Sau đó:

```text
Potential Score
=
R_Normalized × 0,35
+ F_Normalized × 0,30
+ M_Normalized × 0,20
+ I_Normalized × 0,15
```

Ví dụ:

```text
R = 60
F = 100
M = 100
I = 80
```

Tính:

```text
Potential Score
=
60×0,35
+100×0,30
+100×0,20
+80×0,15
```

```text
= 21 + 30 + 20 + 12
= 83
```

Hai cách cho cùng một kết quả.

---

# 7. Phân loại khách hàng

```text
Potential Score >= 80
→ HIGH
→ Tiềm năng cao
```

```text
60 <= Potential Score < 80
→ POTENTIAL
→ Tiềm năng
```

```text
Potential Score < 60
→ NORMAL
→ Thông thường
```

Nếu:

```text
Frequency = 0
```

thì:

```text
INSUFFICIENT_DATA
→ Chưa đủ dữ liệu
```

---

# 8. Luồng công thức tổng thể

```text
Orders
  ↓
Recency / Frequency / Monetary
  ↓
Rank toàn bộ khách hàng
  ↓
RScore / FScore / MScore ∈ [1..5]

Interactions
  ↓
SUM(interaction_value)
  ↓
Min-max normalize toàn cohort
  ↓
InteractionNormalized ∈ [1..5]

              ↓

Potential Score
=
(R×35 + F×30 + M×20 + InteractionNormalized×15) / 5
```

---

# 9. Công thức chốt đề xuất cho đồ án

```text
Recency
= AnalysisDate - Max(OrderDate hợp lệ)
```

```text
Frequency
= COUNT(DISTINCT OrderID hợp lệ)
```

```text
Monetary
= SUM(OrderTotal của các đơn hợp lệ)
```

```text
AOV
= Monetary / Frequency
```

```text
Purchase Cycle
= AVG(khoảng cách giữa các lần mua liên tiếp)
```

```text
Interaction Raw
= SUM(interaction_value)
```

```text
RScore, FScore, MScore
:= xếp hạng theo công thức tương ứng
:= 1..5

```text
InteractionNormalized
:= 1 + (InteractionRaw - MinInteractionRaw)
   / (MaxInteractionRaw - MinInteractionRaw) × 4
```

```text
Potential Score
=
(RScore × 35
+ FScore × 30
+ MScore × 20
+ InteractionNormalized × 15) / 5
```

Cách này giúp toàn bộ R/F/M/Interaction sử dụng cùng một logic:

```text
Giá trị gốc
→ Xếp hạng
→ Điểm 1–5
→ Trọng số
→ Potential Score
```

Nhờ đó hệ thống dễ giải thích, dễ code, dễ kiểm thử và dễ bảo vệ trong đồ án.
