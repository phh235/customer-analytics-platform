# DATA MODEL INVENTORY & SRS ALIGNMENT

## Hệ thống phân tích dữ liệu khách hàng và dự đoán tiềm năng mua hàng

**Nguồn đối chiếu**
- `dataset.xlsx`
- `Software Requirements Specification (1).docx`

**Mục đích tài liệu**
- Liệt kê toàn bộ data model hiện có trong dataset.
- Làm baseline đối chiếu với Entity/Model trong code và table trong database.
- Chỉ ra model nào thuộc dữ liệu nguồn, model nào là dữ liệu phân tích/derived.
- Chỉ ra những model SRS yêu cầu nhưng dataset hiện chưa có.
- Ghi nhận các mismatch/data-quality issue cần xử lý trước khi dùng dataset làm baseline production.

---

# 1. KẾT LUẬN NHANH

Dataset **khớp khá tốt với core data model của SRS**, đặc biệt là các nhóm:

- Customer
- Order / Transaction
- Order Detail
- Product
- Interaction

Dataset còn mở rộng thêm:

- Payment
- Review
- Seller
- Geolocation
- Employee
- Campaign
- Customer Analytics
- Model Run

Tuy nhiên dataset **chưa đủ để ánh xạ 1:1 thành database production theo SRS**, vì còn thiếu các nhóm model hệ thống như:

- User
- Role
- Permission
- Role Permission
- User Role
- Configuration / Configuration Version
- Analysis Run đầy đủ
- Behavior History
- Segment History
- Potential Score History
- Prediction History
- Product Preference History
- ML Model Version / Deployment
- Import Job / Import Error
- Audit Log

Do đó nên xem dataset hiện tại là:

> **Seed/Data Demo + Analytical Prototype Dataset**

không phải schema database production hoàn chỉnh.

---

# 2. THỐNG KÊ DATASET

| Sheet / Data Model | Số dòng dữ liệu | Số field | Phân loại |
|---|---:|---:|---|
| Customers | 80 | 14 | Core |
| Products | 40 | 14 | Core |
| Orders | 200 | 20 | Core |
| OderItems | 509 | 13 | Core |
| Payments | 200 | 7 | Supporting |
| Reviews | 141 | 9 | Supporting / Analytics |
| Sellers | 30 | 6 | Supporting |
| Geolocation | 18 | 6 | Reference |
| Employees | 8 | 8 | Authorization/Data Scope Support |
| Interactions | 480 | 10 | Core Analytics |
| Campaigns | 4 | 9 | Supporting |
| CustomerAnalytics | 80 | 16 | Derived / Analytical Result |
| ModelRuns | 2 | 8 | Derived / Execution Metadata |
| DataDictionary | 140 data rows | 15 | Metadata, không phải business entity |

> Lưu ý: Sheet đang có tên `OderItems`. Khi triển khai code/database nên chuẩn hóa thành `OrderItems`.

---

# 3. QUAN HỆ MODEL TỔNG QUÁT

```text
Employees
    │
    ├──────────────┐
    │              │
    ▼              ▼
Customers       Orders
    │              │
    │              ├──────────────► Payments
    │              │
    │              ├──────────────► Reviews
    │              │
    │              ▼
    │          OrderItems
    │              │
    │              ├──────────────► Products
    │              │
    │              └──────────────► Sellers
    │
    ├──────────────► Interactions ─────► Products
    │                    │
    │                    └──────────────► Campaigns
    │
    └──────────────► CustomerAnalytics

ModelRuns
    └──────────────► metadata của quá trình phân tích
```

---

# 4. MODEL: CUSTOMER

## Dataset source

`Customers`

## Khuyến nghị tên model/code

```text
Customer
```

## Khuyến nghị tên table

```text
customers
```

## Fields

| Dataset Field | Kiểu logic | Vai trò | Gợi ý DB field | Ghi chú |
|---|---|---|---|---|
| customer_id | String | PK hiện tại | customer_id | `CUS00001` |
| customer_unique_id | String | Business/alternate ID | external_customer_id hoặc customer_code | `KH0001` |
| customer_zip_code_prefix | String/Number | Attribute | zip_code | |
| customer_city | String | Attribute | city | |
| customer_state | String | Attribute | state_code | |
| CustomerName | String | Attribute | name | Nên chuẩn hóa naming |
| Region | String | Attribute | region | |
| ProvinceCity | String | Attribute | province_city | |
| Email | String | Attribute | email | |
| Phone | String | Attribute | phone | |
| RegisteredDate | Date/Datetime | Attribute | registered_at | |
| owner_id | String | FK | owner_id | FK -> Employee |
| CustomerStatus | String | Attribute | status | Dataset hiện toàn bộ `Active` |
| CustomerSegment | String | Derived snapshot | current_segment | Có thể không nên lưu trực tiếp tại bảng customer |

## Quan hệ

```text
Customer.owner_id -> Employee.employee_id
```

Dataset hiện có mapping 1-1 giữa:

```text
customer_id <-> customer_unique_id
```

Nhưng đang tồn tại **hai loại Customer ID**.

### Quyết định khuyến nghị

Trong database production chỉ nên có **một PK chính**.

Ví dụ:

```text
id                  UUID / BIGINT
customer_code       KH0001
source_customer_id  CUS00001
```

Không nên để service này dùng `CUS...`, service khác dùng `KH...` mà không có convention rõ ràng.

---

# 5. MODEL: PRODUCT

## Dataset source

`Products`

## Code model

```text
Product
```

## Table

```text
products
```

## Fields

| Dataset Field | Vai trò | Gợi ý DB |
|---|---|---|
| product_id | PK | product_id |
| product_category_name | Source category | source_category_code |
| product_name_lenght | Source metadata | Có thể bỏ khỏi domain model |
| product_description_lenght | Source metadata | Có thể bỏ |
| product_photos_qty | Source metadata | photo_count |
| product_weight_g | Attribute | weight_g |
| product_length_cm | Attribute | length_cm |
| product_height_cm | Attribute | height_cm |
| product_width_cm | Attribute | width_cm |
| Description | Attribute | description |
| ProductCategory | Business category | category_name / category_id |
| ListPrice | Price reference | list_price |
| Currency | Currency | currency |
| ProductStatus | Status | status |

## Nhận xét

SRS cần tối thiểu:

```text
Product ID
Product Name
Product Category
```

Dataset có category và description nhưng không có field rõ ràng tên `ProductName`.

Nên xác nhận:

```text
Description có đang được dùng như Product Name hay không?
```

Nếu không, database cần bổ sung:

```text
product_name
```

---

# 6. MODEL: ORDER

## Dataset source

`Orders`

## Code model

```text
Order
```

## Table

```text
orders
```

## Fields

| Field | Vai trò |
|---|---|
| order_id | PK |
| customer_id | FK -> Customer |
| order_status | Trạng thái đơn |
| order_purchase_timestamp | Ngày đặt |
| order_approved_at | Ngày duyệt |
| order_delivered_carrier_date | Ngày giao carrier |
| order_delivered_customer_date | Ngày giao khách |
| order_estimated_delivery_date | Ngày giao dự kiến |
| CustomerID | Customer alternate ID |
| SalesChannel | Kênh bán |
| PaymentMethod | Hình thức thanh toán |
| Region | Region snapshot |
| ProvinceCity | Province snapshot |
| owner_id | Employee phụ trách |
| OrderSubtotal | Tiền hàng |
| FreightTotal | Phí vận chuyển |
| DiscountTotal | Giảm giá |
| OrderTotal | Tổng đơn |
| Currency | Tiền tệ |
| IsValidForRFM | Cờ dùng cho phân tích RFM |

## Trạng thái dataset hiện tại

```text
delivered   : 141
returned    : 23
canceled    : 18
processing  : 18
```

Cờ `IsValidForRFM` hiện tại:

```text
delivered   -> true
returned    -> false
canceled    -> false
processing  -> false
```

Tức dataset hiện đang chốt ngầm:

> Chỉ đơn `delivered` mới được tính vào RFM.

## Công thức OrderTotal trong dataset

Các bản ghi kiểm tra đều thỏa:

```text
OrderTotal =
OrderSubtotal
+ FreightTotal
- DiscountTotal
```

## Gap so với SRS

Dataset **không có**:

```text
refund_amount
net_amount
```

Vì vậy dataset chưa hỗ trợ đầy đủ rule:

```text
Net Amount = Total Amount - Refund Amount
```

Nếu production cần refund/partial refund thì database phải bổ sung.

---

# 7. MODEL: ORDER ITEM / ORDER DETAIL

## Dataset source

`OderItems`

> Tên sheet bị typo. Nên đổi `OderItems` -> `OrderItems`.

## Code model

```text
OrderItem
```

hoặc

```text
OrderDetail
```

Nên chọn **một tên duy nhất** cho toàn codebase.

## Table

```text
order_items
```

## Fields

| Field | Vai trò |
|---|---|
| order_id | FK -> Order |
| order_item_id | Sequence trong order |
| product_id | FK -> Product |
| seller_id | FK -> Seller |
| shipping_limit_date | Deadline shipping |
| price | Unit price/source price |
| freight_value | Freight của item |
| Quantity | Quantity |
| LineAmount | price × quantity |
| OrderDetailID | Unique detail ID |
| discount_value | Discount item |
| line_subtotal | Subtotal |
| line_total | Total sau freight/discount theo dataset |

## Khuyến nghị key

Production:

```text
id / order_detail_id = PK
order_id              = FK
product_id            = FK
```

Không nên dùng composite key trừ khi architecture chủ động chọn.

---

# 8. MODEL: PAYMENT

## Dataset source

`Payments`

## Code model

```text
Payment
```

## Table

```text
payments
```

## Fields

| Field | Vai trò |
|---|---|
| order_id | FK -> Order |
| payment_sequential | Sequence |
| payment_type | Payment type source |
| payment_installments | Số kỳ |
| payment_value | Giá trị thanh toán |
| PaymentMethodVN | Business display |
| Currency | Currency |

## Quan hệ

```text
Payment.order_id -> Order.order_id
```

## SRS alignment

Payment không phải core entity được SRS yêu cầu trực tiếp, nhưng hữu ích cho:

- kiểm tra giá trị giao dịch
- reporting
- mở rộng hành vi thanh toán

---

# 9. MODEL: REVIEW

## Dataset source

`Reviews`

## Code model

```text
Review
```

## Table

```text
reviews
```

## Fields

| Field | Vai trò |
|---|---|
| review_id | PK |
| order_id | FK -> Order |
| review_score | Rating |
| review_comment_title | Title |
| review_comment_message | Content |
| review_creation_date | Created date |
| review_answer_timestamp | Answered date |
| CustomerID | Customer reference |
| Channel | Review channel |

## SRS alignment

Review không phải core requirement ban đầu nhưng dataset đang dùng:

```text
AvgReviewScore
```

trong `CustomerAnalytics`.

Nếu Review không thuộc scope production thì:

- Không nên để scoring engine phụ thuộc vào nó.
- Có thể giữ như feature mở rộng.

---

# 10. MODEL: SELLER

## Dataset source

`Sellers`

## Code model

```text
Seller
```

## Table

```text
sellers
```

## Fields

- seller_id
- seller_zip_code_prefix
- seller_city
- seller_state
- Region
- SellerName

## SRS alignment

Không phải model bắt buộc theo SRS.

Có thể giữ nếu source system cần phân tích supplier/seller.

Nếu sản phẩm chỉ tập trung Customer Analytics thì đây có thể là:

```text
source/reference model
```

chứ không phải domain chính.

---

# 11. MODEL: GEOLOCATION

## Dataset source

`Geolocation`

## Code model

```text
Geolocation
```

hoặc reference table:

```text
LocationReference
```

## Fields

- geolocation_zip_code_prefix
- geolocation_lat
- geolocation_lng
- geolocation_city
- geolocation_state
- Region

## Nhận xét

Không bắt buộc theo SRS nhưng hữu ích để:

- map region
- geographic dashboard
- data enrichment

---

# 12. MODEL: EMPLOYEE

## Dataset source

`Employees`

## Code model

```text
Employee
```

## Table

```text
employees
```

## Fields

| Field | Vai trò |
|---|---|
| employee_id | PK |
| employee_name | Name |
| department | Department |
| email | Email |
| phone | Phone |
| region_scope | Phạm vi vùng |
| status | Status |
| start_date | Start date |

## Quan hệ

Được dataset sử dụng bởi:

```text
Customers.owner_id
Orders.owner_id
CustomerAnalytics.OwnerID
```

## SRS alignment

Khớp với yêu cầu:

- nhân viên phụ trách
- scope dữ liệu
- Sales / CSKH / Analyst

Nhưng `Employee` **không thay thế cho User/Auth model**.

Production vẫn cần:

```text
User
Role
Permission
```

---

# 13. MODEL: INTERACTION

## Dataset source

`Interactions`

## Code model

```text
CustomerInteraction
```

## Table

```text
customer_interactions
```

## Fields

| Field | Vai trò |
|---|---|
| interaction_id | PK |
| customer_unique_id | FK -> Customer |
| product_id | FK -> Product |
| interaction_type | Loại tương tác |
| interaction_timestamp | Thời điểm |
| channel | Channel |
| session_id | Session |
| campaign_id | FK -> Campaign, nullable |
| interaction_value | Giá trị dùng prototype scoring |
| interaction_result | Result |

## Dataset hiện tại

480 interaction.

Mỗi loại có 60 record:

```text
search
checkout_started
chat
add_to_cart
email_open
product_view
wishlist
email_click
```

## SRS alignment

Khớp rất sát Phase 1 của SRS:

- Interaction là dữ liệu mô phỏng.
- Dùng demo/test Interaction Score.
- Không nên coi là production interaction data.

## DATA QUALITY ISSUE QUAN TRỌNG

Dataset có:

```text
320 interaction có campaign_id = "1583"
```

Trong khi Campaign hiện chỉ có:

```text
CAM001
CAM002
CAM003
CAM004
```

=> 320 record interaction đang **vi phạm FK campaign** nếu coi `1583` là giá trị thật.

SRS cho phép `Campaign ID` để trống.

### Khuyến nghị

Chuyển:

```text
"1583" -> NULL
```

nếu giá trị này thực chất đại diện cho blank/missing.

Không nên import `"1583"` thành campaign thật.

---

# 14. MODEL: CAMPAIGN

## Dataset source

`Campaigns`

## Code model

```text
Campaign
```

## Table

```text
campaigns
```

## Fields

- campaign_id
- campaign_name
- campaign_type
- start_date
- end_date
- channel
- target_segment
- status
- budget_vnd

## SRS alignment

Không bắt buộc trong MVP core nhưng hỗ trợ Interaction.

Có thể giữ Phase 1 như reference data.

---

# 15. MODEL: CUSTOMER ANALYTICS

## Dataset source

`CustomerAnalytics`

## Bản chất

Đây **không phải master data**.

Nó là:

```text
derived analytical snapshot
```

## Fields

| Field | Ý nghĩa |
|---|---|
| AnalysisDate | Ngày phân tích |
| CustomerID | Customer |
| OwnerID | Employee |
| RecencyDays | Recency |
| Frequency | Frequency |
| Monetary | Monetary |
| AOV | Average Order Value |
| AvgPurchaseCycleDays | Chu kỳ mua |
| AvgReviewScore | Rating trung bình |
| InteractionScore | Điểm interaction thô |
| RScore | Normalized Recency score |
| FScore | Normalized Frequency score |
| MScore | Normalized Monetary score |
| PotentialScore | Rule-based Potential Score |
| Segment | Segment |
| ModelStatus | Trạng thái prototype |

## Potential Score dataset hiện dùng

Dataset đang áp dụng:

```text
Recency     35%
Frequency   30%
Monetary    20%
Interaction 15%
```

Không dùng Trend trong Phase 1.

Điều này khớp với SRS hiện tại.

## Segment threshold dataset

```text
Potential Score >= 80
    -> Tiềm năng cao

60 <= Potential Score < 80
    -> Tiềm năng

Potential Score < 60
    -> Thông thường

Không có valid order
    -> Chưa đủ dữ liệu
```

Dataset có:

```text
Tiềm năng cao     11
Tiềm năng         26
Thông thường      21
Chưa đủ dữ liệu   22
```

22 khách không có valid order và đúng bằng 22 record `Chưa đủ dữ liệu`.

## DATA QUALITY / FORMULA ISSUE

Trong file hiện tại:

```text
RecencyDays
AvgPurchaseCycleDays
```

đều đang evaluate thành:

```text
#NAME?
```

cho 80 khách hàng.

Nguyên nhân quan sát được trong workbook:

- Formula sử dụng `FILTER(...)`.
- Workbook chứa wrapper `__xludf.DUMMYFUNCTION(...)`.
- Engine hiện tại không evaluate được công thức đó.

### Hệ quả

Không nên import trực tiếp các ô:

```text
RecencyDays = #NAME?
AvgPurchaseCycleDays = #NAME?
```

vào database.

### Khuyến nghị

Backend/Data service phải **tự tính lại** từ Order data.

Dataset analytics chỉ dùng để:

- đối chiếu logic
- test expected output
- demo

không được xem là nguồn sự thật cho derived fields.

## Review formula issue

Có dấu hiệu formula `AvgReviewScore` ở dòng đầu sử dụng Customer của dòng kế tiếp.

Cần kiểm tra và regenerate analytics thay vì tin hoàn toàn formula hiện tại.

---

# 16. MODEL: MODEL RUN

## Dataset source

`ModelRuns`

## Code model khuyến nghị

```text
AnalysisRun
```

và nếu triển khai ML đầy đủ:

```text
MLModelRun
```

Nên cân nhắc tách hai khái niệm.

## Fields hiện tại

- run_id
- run_timestamp
- analysis_date
- model_type
- model_version
- status
- record_count
- notes

## Dataset hiện có

### RUN001

```text
RFM + Potential Score
RULE-V1
Completed
80 records
```

### RUN002

```text
Machine Learning
N/A
Not trained
0 records
```

Dataset tự ghi chú:

> Dataset 200 đơn chưa đủ nghiệm thu ML thực tế.

## Gap so với SRS

SRS yêu cầu mỗi lần chạy cần truy vết:

- thời điểm
- người thực hiện/system task
- kỳ dữ liệu
- configuration/version
- model version nếu có

ModelRuns hiện **thiếu**:

```text
created_by / executed_by
data_from
data_to
configuration_version
started_at
completed_at
error_message
success_count
failed_count
```

---

# 17. DATA DICTIONARY

Sheet:

```text
DataDictionary
```

Không nên map thành business entity.

Có thể sử dụng như:

```text
documentation / import schema metadata
```

## Vấn đề cần lưu ý

DataDictionary có một số metadata chưa đáng tin để sinh schema tự động, ví dụ:

- `Customers.customer_unique_id` được mô tả FK về chính Customers.
- `Orders.customer_id` có metadata key chưa hợp lý.
- Nhiều ô metadata chứa giá trị `1583`.

### Khuyến nghị

Không generate migration/database schema tự động từ DataDictionary hiện tại.

Nên dùng tài liệu này để tham khảo, rồi đối chiếu lại với:

1. dữ liệu thật trong sheet;
2. SRS;
3. ERD;
4. schema code/database.

---

# 18. ĐỐI CHIẾU CORE DATASET VỚI SRS

| SRS Requirement | Dataset | Đánh giá |
|---|---|---|
| Customer | Customers | ✅ Khớp |
| Order / Transaction | Orders | ✅ Khớp |
| Order Detail | OderItems | ✅ Khớp, typo tên |
| Product | Products | ⚠️ Gần khớp, cần Product Name rõ ràng |
| Interaction | Interactions | ✅ Khớp Phase 1, nhưng campaign_id có lỗi |
| Employee/owner scope | Employees + owner_id | ✅ Có dữ liệu hỗ trợ |
| RFM | CustomerAnalytics + Orders | ✅ Có prototype |
| AOV | CustomerAnalytics | ✅ Có |
| Purchase Cycle | CustomerAnalytics | ⚠️ Formula hiện #NAME? |
| Trend | Không có trong CustomerAnalytics | ⚠️ SRS có behavior trend nhưng Phase 1 không dùng vào score |
| Segmentation | CustomerAnalytics.Segment | ✅ Khớp threshold SRS hiện tại |
| Potential Score | CustomerAnalytics | ✅ Khớp weight 35/30/20/15 |
| Product Preference | Chưa có result model riêng | ❌ Thiếu |
| ML Probability | Chưa có | ❌ Chưa train |
| Prediction Horizon | Chưa có result | ❌ Thiếu |
| Model Version | ModelRuns | ⚠️ Có một phần |
| Analysis history | ModelRuns + snapshot | ⚠️ Chưa đủ |
| Dashboard data | Có thể derive | ✅ Có data nền |
| User / Role / Permission | Không có | ❌ Thiếu |
| Configurable thresholds | Không có config model | ❌ Thiếu |
| Audit | Không có | ❌ Thiếu |
| Import error history | Không có | ❌ Thiếu |

---

# 19. CÁC MODEL CÓ TRONG DATASET NHƯNG KHÔNG PHẢI CORE SRS

Các model dưới đây có thể giữ hoặc bỏ tùy scope implementation:

```text
Payment
Review
Seller
Geolocation
Campaign
```

Không nên vì dataset có mà mặc định toàn bộ đều phải trở thành module production.

Quy tắc:

> Dataset phục vụ SRS, không phải SRS chạy theo tất cả sheet của dataset.

---

# 20. CÁC MODEL SRS CẦN NHƯNG DATASET CHƯA CÓ

Đây là phần quan trọng khi đối chiếu với code/database.

## 20.1 Authentication & Authorization

```text
User
Role
Permission
UserRole
RolePermission
```

Có thể thêm:

```text
UserDataScope
```

---

## 20.2 Configuration

```text
ConfigurationVersion
ScoringConfiguration
ScoringThreshold
SegmentationRule
ValidOrderStatusConfig
AnalysisPeriodConfig
```

Mỗi kết quả phân tích cần biết configuration version nào đã được sử dụng.

---

## 20.3 Analysis Execution

```text
AnalysisRun
```

Đề xuất field:

```text
id
analysis_type
status
data_from
data_to
analysis_date
started_at
completed_at
executed_by
configuration_version_id
model_version_id
total_records
success_records
failed_records
error_message
```

---

## 20.4 Behavior Result History

```text
CustomerBehaviorHistory
```

Fields tối thiểu:

```text
id
analysis_run_id
customer_id
recency_days
frequency
monetary
aov
avg_purchase_cycle_days
trend
created_at
```

---

## 20.5 Potential Score History

```text
CustomerPotentialScoreHistory
```

```text
id
analysis_run_id
customer_id
r_score
f_score
m_score
interaction_score
potential_score
potential_level
configuration_version_id
created_at
```

---

## 20.6 Segment History

```text
CustomerSegmentHistory
```

```text
id
analysis_run_id
customer_id
segment_code
reason
configuration_version_id
created_at
```

---

## 20.7 Product Preference Result

```text
CustomerProductPreference
```

```text
id
analysis_run_id
customer_id
product_category_id
rank
score
purchase_frequency
quantity
monetary
purchase_share
last_purchase_at
```

---

## 20.8 ML Model Version

```text
MLModelVersion
```

```text
id
model_version
status
trained_at
dataset_version
feature_window
prediction_horizon
precision
recall
f1
roc_auc
pr_auc
notes
```

---

## 20.9 Prediction History

```text
CustomerPredictionHistory
```

```text
id
customer_id
analysis_run_id
prediction_date
prediction_horizon
probability
model_version_id
feature_from
feature_to
created_at
```

---

## 20.10 Import

```text
ImportJob
ImportError
```

Để đáp ứng requirement:

- lỗi theo dòng;
- field;
- nguyên nhân;
- partial success;
- audit import.

---

## 20.11 Audit

```text
AuditLog
```

```text
id
actor_id
action
entity_type
entity_id
before_data
after_data
ip_address
created_at
```

---

# 21. ĐỀ XUẤT DATABASE MODEL TỔNG THỂ

## Nhóm A - Master / Transaction

```text
Customer
Product
Order
OrderItem
Payment
Review
Employee
CustomerInteraction
Campaign
Seller
Geolocation
```

## Nhóm B - Security

```text
User
Role
Permission
UserRole
RolePermission
CustomerAssignment / UserDataScope
```

## Nhóm C - Configuration

```text
ConfigurationVersion
ScoringRule
ScoringThreshold
SegmentationRule
SystemConfig
```

## Nhóm D - Analytics

```text
AnalysisRun
CustomerBehaviorHistory
CustomerPotentialScoreHistory
CustomerSegmentHistory
CustomerProductPreference
```

## Nhóm E - Machine Learning

```text
MLModelVersion
MLModelEvaluation
CustomerPredictionHistory
```

## Nhóm F - Operational

```text
ImportJob
ImportError
AuditLog
```

---

# 22. CÁC VẤN ĐỀ CẦN SỬA TRƯỚC KHI ĐƯA DATASET VÀO CODE

## P0 - Nên xử lý ngay

### 1. Interaction campaign_id

```text
320 rows = "1583"
```

Không match Campaign.

Nếu đây là missing value:

```text
1583 -> NULL
```

### 2. CustomerAnalytics formula errors

```text
RecencyDays = #NAME?
AvgPurchaseCycleDays = #NAME?
```

Không được import derived result lỗi vào DB.

### 3. Chuẩn hóa Customer ID

Hiện có cả:

```text
customer_id        = CUS...
customer_unique_id = KH...
```

Phải xác định ID canonical cho API/database.

### 4. Rename typo

```text
OderItems -> OrderItems
```

---

## P1 - Chốt trước production

### 5. Refund/Net Amount

Dataset chưa có refund.

Phải quyết định có bổ sung:

```text
refund_amount
net_amount
```

hay không.

### 6. Product Name

Cần field:

```text
product_name
```

rõ ràng nếu `Description` không phải tên.

### 7. Valid Order

Dataset hiện:

```text
delivered = valid
returned/canceled/processing = invalid
```

Cần Business Owner xác nhận đây có phải production rule hay chỉ demo rule.

---

# 23. CHECKLIST ĐỐI CHIẾU VỚI CODE

Khi review source code/database, kiểm tra:

- [ ] Có entity `Customer`.
- [ ] Chỉ có một canonical customer identity dùng xuyên API.
- [ ] `Order.customer` là FK hợp lệ.
- [ ] `OrderItem.order` và `OrderItem.product` là FK.
- [ ] `OrderItem` không bị viết nhầm thành `OderItem`.
- [ ] Valid order status không hardcode rải rác.
- [ ] RFM được tính từ transaction thật, không lấy `CustomerAnalytics` làm source of truth.
- [ ] Potential Score dùng 35/30/20/15 cho Phase 1.
- [ ] Trend không bị đưa vào Potential Score Phase 1.
- [ ] Customer không có valid order trả `INSUFFICIENT_DATA`.
- [ ] Interaction mock được đánh dấu demo/non-production.
- [ ] Campaign ID nullable.
- [ ] Analysis result có history, không overwrite.
- [ ] Có `analysis_run_id`.
- [ ] Có `configuration_version`.
- [ ] ML probability tách khỏi Potential Score.
- [ ] Chưa có ML model thì không tự sinh probability.
- [ ] Có User/Role/Permission riêng, không dùng Employee thay auth.
- [ ] Data scope được kiểm tra ở query/API layer.
- [ ] Import có row-level error.
- [ ] Có Audit Log cho thao tác quan trọng.

---

# 24. KẾT LUẬN

Dataset hiện tại **phù hợp để bắt đầu code core data ingestion + RFM + Potential Score prototype**, vì các model quan trọng nhất đã có:

```text
Customer
Order
OrderItem
Product
Interaction
Employee
```

và dataset Potential Score đang khớp SRS Phase 1:

```text
Recency     35%
Frequency   30%
Monetary    20%
Interaction 15%
```

Tuy nhiên, để database/code thực sự đáp ứng toàn bộ SRS, cần bổ sung các model:

```text
Security
Configuration
Analysis History
Product Preference
ML Version
Prediction History
Import History
Audit
```

Đặc biệt không nên thiết kế database bằng cách tạo **một table cho mỗi Excel sheet một cách máy móc**.

Excel là nguồn/demo dataset.

Database phải được thiết kế theo:

```text
Business Domain
+
SRS
+
Traceability
+
Data Integrity
```

và sau đó mới xây mapping/import từ dataset vào domain model.

---

# 25. AGENT CODE CHECK — EXPECTED MODELS ONLY

> Phần này chỉ dùng để Coding Agent đối chiếu nhanh với source code và database.
>
> Mục tiêu:
> - Kiểm tra model/entity nào đã có.
> - Kiểm tra field chính.
> - Kiểm tra quan hệ.
> - Không dùng phần này để thay thế business rules ở các section phía trên.

## 25.1 Core Data Models

### Customer

```text
Customer
- id
- customerCode
- sourceCustomerId
- name
- email
- phone
- zipCode
- city
- stateCode
- region
- provinceCity
- registeredAt
- ownerId
- status
- isDeleted
- createdAt
- updatedAt
```

Relations:

```text
Customer.ownerId -> Employee.id
Customer 1 -> N Order
Customer 1 -> N CustomerInteraction
Customer 1 -> N CustomerBehaviorHistory
Customer 1 -> N CustomerPotentialScoreHistory
Customer 1 -> N CustomerSegmentHistory
Customer 1 -> N CustomerProductPreference
Customer 1 -> N CustomerPredictionHistory
```

---

### Product

```text
Product
- id
- productCode
- productName
- description
- categoryId
- categoryName
- listPrice
- currency
- weightG
- lengthCm
- heightCm
- widthCm
- photoCount
- status
- isDeleted
- createdAt
- updatedAt
```

Relations:

```text
Product 1 -> N OrderItem
Product 1 -> N CustomerInteraction
Product 1 -> N CustomerProductPreference
```

---

### Order

```text
Order
- id
- orderCode
- customerId
- ownerId
- status
- salesChannel
- paymentMethod
- region
- provinceCity
- purchasedAt
- approvedAt
- deliveredCarrierAt
- deliveredCustomerAt
- estimatedDeliveryAt
- subtotal
- freightTotal
- discountTotal
- orderTotal
- refundAmount
- netAmount
- currency
- isValidForRfm
- createdAt
- updatedAt
```

Relations:

```text
Order.customerId -> Customer.id
Order.ownerId -> Employee.id
Order 1 -> N OrderItem
Order 1 -> N Payment
Order 1 -> N Review
```

---

### OrderItem

```text
OrderItem
- id
- orderId
- productId
- sellerId
- itemSequence
- quantity
- unitPrice
- freightValue
- discountValue
- lineSubtotal
- lineAmount
- lineTotal
- shippingLimitAt
- createdAt
```

Relations:

```text
OrderItem.orderId -> Order.id
OrderItem.productId -> Product.id
OrderItem.sellerId -> Seller.id
```

---

## 25.2 Supporting Data Models

### Payment

```text
Payment
- id
- orderId
- paymentSequence
- paymentType
- paymentMethod
- installments
- paymentValue
- currency
- createdAt
```

Relation:

```text
Payment.orderId -> Order.id
```

---

### Review

```text
Review
- id
- reviewCode
- orderId
- customerId
- score
- title
- message
- channel
- createdAt
- answeredAt
```

Relations:

```text
Review.orderId -> Order.id
Review.customerId -> Customer.id
```

---

### Seller

```text
Seller
- id
- sellerCode
- sellerName
- zipCode
- city
- stateCode
- region
```

---

### Geolocation

```text
Geolocation
- id
- zipCode
- latitude
- longitude
- city
- stateCode
- region
```

---

### Employee

```text
Employee
- id
- employeeCode
- name
- department
- email
- phone
- regionScope
- status
- startDate
```

---

### Campaign

```text
Campaign
- id
- campaignCode
- name
- type
- startDate
- endDate
- channel
- targetSegment
- status
- budget
```

---

### CustomerInteraction

```text
CustomerInteraction
- id
- interactionCode
- customerId
- productId
- campaignId
- type
- occurredAt
- channel
- sessionId
- interactionValue
- interactionResult
- isMockData
```

Relations:

```text
CustomerInteraction.customerId -> Customer.id
CustomerInteraction.productId -> Product.id
CustomerInteraction.campaignId -> Campaign.id (nullable)
```

Important:

```text
campaignId phải nullable.
Phase 1 interaction là mock/demo data.
```

---

## 25.3 Security Models

### User

```text
User
- id
- username
- passwordHash
- employeeId
- status
- lastLoginAt
- createdAt
- updatedAt
```

Relation:

```text
User.employeeId -> Employee.id (nullable)
```

---

### Role

```text
Role
- id
- code
- name
- description
```

---

### Permission

```text
Permission
- id
- code
- name
- description
```

---

### UserRole

```text
UserRole
- userId
- roleId
```

Relations:

```text
UserRole.userId -> User.id
UserRole.roleId -> Role.id
```

---

### RolePermission

```text
RolePermission
- roleId
- permissionId
```

Relations:

```text
RolePermission.roleId -> Role.id
RolePermission.permissionId -> Permission.id
```

---

### CustomerAssignment

```text
CustomerAssignment
- id
- customerId
- userId
- assignedAt
- assignedBy
- active
```

Relations:

```text
CustomerAssignment.customerId -> Customer.id
CustomerAssignment.userId -> User.id
```

---

## 25.4 Configuration Models

### ConfigurationVersion

```text
ConfigurationVersion
- id
- version
- status
- description
- effectiveFrom
- effectiveTo
- createdBy
- createdAt
```

---

### ScoringRule

```text
ScoringRule
- id
- configurationVersionId
- component
- weight
- enabled
```

Expected components for Phase 1:

```text
RECENCY
FREQUENCY
MONETARY
INTERACTION
```

Expected default weights:

```text
RECENCY     = 35
FREQUENCY   = 30
MONETARY    = 20
INTERACTION = 15
```

---

### ScoringThreshold

```text
ScoringThreshold
- id
- configurationVersionId
- component
- minValue
- maxValue
- score
- priority
```

---

### SegmentationRule

```text
SegmentationRule
- id
- configurationVersionId
- segmentCode
- minPotentialScore
- maxPotentialScore
- priority
- enabled
```

Phase 1 expected:

```text
TIEM_NANG_CAO : score >= 80
TIEM_NANG     : 60 <= score < 80
THONG_THUONG  : score < 60
CHUA_DU_DU_LIEU : no valid order
```

---

### ValidOrderStatusConfig

```text
ValidOrderStatusConfig
- id
- configurationVersionId
- orderStatus
- isValidForAnalytics
```

---

## 25.5 Analysis Models

### AnalysisRun

```text
AnalysisRun
- id
- runCode
- analysisType
- status
- analysisDate
- dataFrom
- dataTo
- startedAt
- completedAt
- executedBy
- configurationVersionId
- modelVersionId
- totalRecords
- successRecords
- failedRecords
- errorMessage
- createdAt
```

Expected status:

```text
PENDING
PROCESSING
COMPLETED
FAILED
```

---

### CustomerBehaviorHistory

```text
CustomerBehaviorHistory
- id
- analysisRunId
- customerId
- recencyDays
- frequency
- monetary
- aov
- avgPurchaseCycleDays
- trend
- avgReviewScore
- createdAt
```

Relations:

```text
CustomerBehaviorHistory.analysisRunId -> AnalysisRun.id
CustomerBehaviorHistory.customerId -> Customer.id
```

---

### CustomerPotentialScoreHistory

```text
CustomerPotentialScoreHistory
- id
- analysisRunId
- customerId
- rScore
- fScore
- mScore
- interactionScore
- potentialScore
- potentialLevel
- configurationVersionId
- createdAt
```

Phase 1 formula:

```text
PotentialScore =
RScore * 0.35
+ FScore * 0.30
+ MScore * 0.20
+ InteractionScore * 0.15
```

Trend MUST NOT be included in Phase 1 Potential Score.

---

### CustomerSegmentHistory

```text
CustomerSegmentHistory
- id
- analysisRunId
- customerId
- segmentCode
- segmentName
- reason
- configurationVersionId
- createdAt
```

---

### CustomerProductPreference

```text
CustomerProductPreference
- id
- analysisRunId
- customerId
- productCategoryId
- productCategoryName
- rank
- score
- purchaseFrequency
- quantity
- monetary
- purchaseShare
- lastPurchaseAt
- createdAt
```

---

## 25.6 Machine Learning Models

### MLModelVersion

```text
MLModelVersion
- id
- modelCode
- modelVersion
- modelType
- status
- datasetVersion
- trainedAt
- featureWindowDays
- predictionHorizonDays
- precision
- recall
- f1Score
- rocAuc
- prAuc
- notes
- createdAt
```

Expected status:

```text
DRAFT
TRAINING
EVALUATING
APPROVED
DEPLOYED
RETIRED
FAILED
```

Only:

```text
DEPLOYED
```

may be used for inference.

---

### MLModelEvaluation

```text
MLModelEvaluation
- id
- modelVersionId
- evaluationDatasetVersion
- precision
- recall
- f1Score
- rocAuc
- prAuc
- precisionAtK
- recallAtK
- liftAtK
- evaluatedAt
```

---

### CustomerPredictionHistory

```text
CustomerPredictionHistory
- id
- analysisRunId
- customerId
- modelVersionId
- predictionDate
- predictionHorizonDays
- probability
- featureFrom
- featureTo
- createdAt
```

Important:

```text
PotentialScore != probability
```

---

## 25.7 Operational Models

### ImportJob

```text
ImportJob
- id
- fileName
- importType
- status
- totalRows
- successRows
- failedRows
- executedBy
- startedAt
- completedAt
- createdAt
```

---

### ImportError

```text
ImportError
- id
- importJobId
- rowNumber
- fieldName
- errorCode
- errorMessage
- rawValue
```

Relation:

```text
ImportError.importJobId -> ImportJob.id
```

---

### AuditLog

```text
AuditLog
- id
- actorId
- action
- entityType
- entityId
- beforeData
- afterData
- ipAddress
- createdAt
```

---

# 26. AGENT MODEL CHECKLIST

Coding Agent phải đối chiếu code/database với danh sách sau.

## Required Core Models

```text
[ ] Customer
[ ] Product
[ ] Order
[ ] OrderItem
[ ] CustomerInteraction
[ ] Employee
```

## Supporting Models

```text
[ ] Payment
[ ] Review
[ ] Seller
[ ] Geolocation
[ ] Campaign
```

Các model Supporting chỉ bắt buộc nếu source/dataset tương ứng đang được import và sử dụng.

## Required Security Models

```text
[ ] User
[ ] Role
[ ] Permission
[ ] UserRole
[ ] RolePermission
[ ] CustomerAssignment
```

## Required Configuration Models

```text
[ ] ConfigurationVersion
[ ] ScoringRule
[ ] ScoringThreshold
[ ] SegmentationRule
[ ] ValidOrderStatusConfig
```

## Required Analytics Models

```text
[ ] AnalysisRun
[ ] CustomerBehaviorHistory
[ ] CustomerPotentialScoreHistory
[ ] CustomerSegmentHistory
[ ] CustomerProductPreference
```

## Required ML Models

```text
[ ] MLModelVersion
[ ] MLModelEvaluation
[ ] CustomerPredictionHistory
```

Chỉ bắt buộc triển khai đầy đủ khi ML nằm trong phase hiện tại.

## Required Operational Models

```text
[ ] ImportJob
[ ] ImportError
[ ] AuditLog
```

---

# 27. AGENT VALIDATION RULES FOR MODELS

Coding Agent phải báo mismatch nếu gặp một trong các trường hợp:

```text
1. Thiếu model bắt buộc.
2. Có model nhưng thiếu PK.
3. FK không map đúng relation.
4. Customer dùng nhiều ID nhưng không có canonical identity.
5. OrderItem không liên kết Order và Product.
6. Interaction campaignId không nullable.
7. Employee bị dùng thay User/Auth.
8. Analysis result overwrite bản cũ thay vì lưu history.
9. Potential Score và ML Probability dùng chung field/model.
10. Analysis result không có analysisRunId.
11. Analysis result không truy được configurationVersion.
12. ML prediction không truy được modelVersion.
13. Valid Order Status bị hardcode ở nhiều nơi.
14. Phase 1 Potential Score có Trend.
15. Phase 1 Potential Score khác weight 35/30/20/15 mà không có config/version giải thích.
16. CustomerAnalytics từ Excel được dùng làm source of truth thay vì derived result.
17. Derived field lỗi từ Excel (#NAME?) được import trực tiếp vào DB.
18. Sheet/model typo `OderItems` lan vào tên domain/code.
```

---

# 28. MODEL NAMING CONVENTION KHUYẾN NGHỊ

Code model:

```text
Customer
Product
Order
OrderItem
Payment
Review
Seller
Geolocation
Employee
Campaign
CustomerInteraction

User
Role
Permission
UserRole
RolePermission
CustomerAssignment

ConfigurationVersion
ScoringRule
ScoringThreshold
SegmentationRule
ValidOrderStatusConfig

AnalysisRun
CustomerBehaviorHistory
CustomerPotentialScoreHistory
CustomerSegmentHistory
CustomerProductPreference

MLModelVersion
MLModelEvaluation
CustomerPredictionHistory

ImportJob
ImportError
AuditLog
```

Database table:

```text
customers
products
orders
order_items
payments
reviews
sellers
geolocations
employees
campaigns
customer_interactions

users
roles
permissions
user_roles
role_permissions
customer_assignments

configuration_versions
scoring_rules
scoring_thresholds
segmentation_rules
valid_order_status_configs

analysis_runs
customer_behavior_history
customer_potential_score_history
customer_segment_history
customer_product_preferences

ml_model_versions
ml_model_evaluations
customer_prediction_history

import_jobs
import_errors
audit_logs
```

> Agent không được tạo table riêng cho `CustomerAnalytics` của Excel nếu hệ thống đã có các bảng history/analytics ở trên. `CustomerAnalytics` là output prototype để đối chiếu, không phải canonical domain model.

