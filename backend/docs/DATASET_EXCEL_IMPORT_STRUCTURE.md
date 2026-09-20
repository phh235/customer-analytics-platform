# DATASET EXCEL STRUCTURE FOR IMPORT AGENT

## 1. Mục đích

Tài liệu này mô tả cấu trúc file `dataset.xlsx` để Coding Agent sửa/hoàn thiện chức năng import Excel vào PostgreSQL.

Agent phải dùng tài liệu này như **import contract** cho dataset hiện tại.

Nguyên tắc:
- Không đoán tên sheet hoặc tên cột.
- Phải validate header trước khi import.
- Phải xử lý FK theo dependency.
- Phải chuẩn hóa dữ liệu trước khi insert.
- Không import trực tiếp các giá trị formula lỗi.
- Phân biệt rõ source/master data và derived analytical data.
- Import phải idempotent và hỗ trợ partial success.

---

# 2. Tổng quan workbook

| # | Sheet | Rows dữ liệu | Vai trò |
|---:|---|---:|---|
| 1 | `Customers` | 80 | Master data |
| 2 | `Products` | 40 | Master data |
| 3 | `Orders` | 200 | Transaction |
| 4 | `OderItems` | 509 | Transaction detail |
| 5 | `Payments` | 200 | Supporting transaction |
| 6 | `Reviews` | 141 | Supporting / analytical input |
| 7 | `Sellers` | 30 | Master/reference |
| 8 | `Geolocation` | 18 | Reference |
| 9 | `DataDictionary` | 140 | Metadata/documentation |
| 10 | `Employees` | 8 | Master/reference |
| 11 | `Interactions` | 480 | Analytical input |
| 12 | `Campaigns` | 4 | Master/reference |
| 13 | `CustomerAnalytics` | 80 | Derived analytical result |
| 14 | `ModelRuns` | 2 | Analytical execution metadata |

> Lưu ý: sheet `OderItems` bị typo. Domain/database dùng `OrderItems`, nhưng import phải nhận đúng tên sheet hiện tại `OderItems`.

---

# 3. Thứ tự import

```text
Employees
Campaigns
Sellers
Geolocation
Products
Customers
Orders
OderItems
Payments
Reviews
Interactions
CustomerAnalytics
ModelRuns
```

`DataDictionary` không import vào business tables.

---

# 4. Customers

## Headers

```text
customer_id
customer_unique_id
customer_zip_code_prefix
customer_city
customer_state
CustomerName
Region
ProvinceCity
Email
Phone
RegisteredDate
owner_id
CustomerStatus
CustomerSegment
```

## Mapping chính

| Excel | PostgreSQL |
|---|---|
| `customer_id` | `customers.source_customer_id` |
| `customer_unique_id` | `customers.customer_code` |
| `customer_zip_code_prefix` | `customers.zip_code` |
| `customer_city` | `customers.city` |
| `customer_state` | `customers.state_code` |
| `CustomerName` | `customers.name` |
| `Region` | `customers.region` |
| `ProvinceCity` | `customers.province_city` |
| `Email` | `customers.email` |
| `Phone` | `customers.phone` |
| `RegisteredDate` | `customers.registered_at` |
| `owner_id` | resolve `employees.employee_code` |
| `CustomerStatus` | `customers.status` |

Canonical identity:

```text
customers.id                 = internal UUID
customers.customer_code      = KH...
customers.source_customer_id = CUS...
```

FK:

```text
Customers.owner_id -> Employees.employee_id
```

`CustomerSegment` chỉ là snapshot/demo, không phải source of truth production.

---

# 5. Products

## Headers

```text
product_id
product_category_name
product_name_lenght
product_description_lenght
product_photos_qty
product_weight_g
product_length_cm
product_height_cm
product_width_cm
Description
ProductCategory
ListPrice
Currency
ProductStatus
```

## Mapping

| Excel | PostgreSQL |
|---|---|
| `product_id` | `source_product_id`, `product_code` |
| `product_category_name` | `source_category_code` |
| `Description` | `name`, `description` |
| `ProductCategory` | `category` |
| `ListPrice` | `price`, `list_price` |
| `Currency` | `currency` |
| `ProductStatus` | `status` |
| `product_weight_g` | `weight_g` |
| `product_length_cm` | `length_cm` |
| `product_height_cm` | `height_cm` |
| `product_width_cm` | `width_cm` |
| `product_photos_qty` | `photo_count` |

Normalization:

```text
VNĐ -> VND
```

Không tự sửa tên cột typo khi đọc Excel:

```text
product_name_lenght
product_description_lenght
```

---

# 6. Orders

## Headers

```text
order_id
customer_id
order_status
order_purchase_timestamp
order_approved_at
order_delivered_carrier_date
order_delivered_customer_date
order_estimated_delivery_date
CustomerID
SalesChannel
PaymentMethod
Region
ProvinceCity
owner_id
OrderSubtotal
FreightTotal
DiscountTotal
OrderTotal
Currency
IsValidForRFM
```

## Mapping

| Excel | PostgreSQL |
|---|---|
| `order_id` | `source_order_id`, `order_code`, `order_number` |
| `customer_id` | resolve `customers.source_customer_id` |
| `order_status` | `status` |
| `order_purchase_timestamp` | `order_date` |
| `order_approved_at` | `approved_at` |
| `order_delivered_carrier_date` | `delivered_carrier_at` |
| `order_delivered_customer_date` | `delivered_customer_at` |
| `order_estimated_delivery_date` | `estimated_delivery_at` |
| `SalesChannel` | `sales_channel` / `channel` |
| `PaymentMethod` | `payment_method` |
| `Region` | `region` |
| `ProvinceCity` | `province_city` |
| `owner_id` | resolve `employees.employee_code` |
| `OrderSubtotal` | `subtotal` |
| `FreightTotal` | `freight_total` |
| `DiscountTotal` | `discount_total` |
| `OrderTotal` | `total_amount` |
| `Currency` | `currency` |
| `IsValidForRFM` | `is_valid_for_rfm` |

Dataset có hai customer reference:

```text
customer_id = CUS...
CustomerID  = KH...
```

Ưu tiên resolve:

```text
Orders.customer_id
-> Customers.customer_id
-> customers.source_customer_id
```

Current statuses:

```text
delivered
returned
canceled
processing
```

Dataset hiện có rule:

```text
delivered   -> IsValidForRFM = TRUE
returned    -> FALSE
canceled    -> FALSE
processing  -> FALSE
```

Refund không có trong Excel:

```text
refund_amount = 0
net_amount    = OrderTotal
```

---

# 7. OderItems

## Headers

```text
order_id
order_item_id
product_id
seller_id
shipping_limit_date
price
freight_value
Quantity
LineAmount
OrderDetailID
discount_value
line_subtotal
line_total
```

## Mapping

```text
order_id            -> orders.source_order_id
order_item_id       -> item_sequence
product_id          -> products.source_product_id
seller_id           -> sellers.seller_code
shipping_limit_date -> shipping_limit_at
price               -> unit_price
freight_value       -> freight_value
Quantity            -> quantity
LineAmount          -> line_amount
discount_value      -> discount_value
line_subtotal       -> line_subtotal
line_total          -> line_total
```

FK:

```text
order_id   -> Orders.order_id
product_id -> Products.product_id
seller_id  -> Sellers.seller_id
```

Idempotency key:

```text
(order_id, order_item_id)
```

---

# 8. Payments

## Headers

```text
order_id
payment_sequential
payment_type
payment_installments
payment_value
PaymentMethodVN
Currency
```

Mapping:

```text
order_id             -> order_id
payment_sequential   -> payment_sequence
payment_type         -> payment_type
payment_installments -> payment_installments
payment_value        -> payment_value
PaymentMethodVN      -> payment_method
Currency             -> currency
```

Unique key:

```text
(order_id, payment_sequential)
```

---

# 9. Reviews

## Headers

```text
review_id
order_id
review_score
review_comment_title
review_comment_message
review_creation_date
review_answer_timestamp
CustomerID
Channel
```

Mapping:

```text
review_id               -> review_code
order_id                 -> resolve Order
review_score             -> score
review_comment_title     -> title
review_comment_message   -> message
review_creation_date     -> review_created_at
review_answer_timestamp  -> answered_at
CustomerID               -> resolve customers.customer_code
Channel                  -> channel
```

Validation:

```text
1 <= review_score <= 5
```

---

# 10. Sellers

## Headers

```text
seller_id
seller_zip_code_prefix
seller_city
seller_state
Region
SellerName
```

Mapping:

```text
seller_id              -> seller_code
seller_zip_code_prefix -> zip_code
seller_city            -> city
seller_state           -> state_code
Region                 -> region
SellerName             -> seller_name
```

---

# 11. Geolocation

## Headers

```text
geolocation_zip_code_prefix
geolocation_lat
geolocation_lng
geolocation_city
geolocation_state
Region
```

Mapping:

```text
geolocation_zip_code_prefix -> zip_code
geolocation_lat             -> latitude
geolocation_lng             -> longitude
geolocation_city            -> city
geolocation_state           -> state_code
Region                      -> region
```

---

# 12. Employees

## Headers

```text
employee_id
employee_name
department
email
phone
region_scope
status
start_date
```

Mapping:

```text
employee_id   -> employee_code
employee_name -> name
department    -> department
email         -> email
phone         -> phone
region_scope  -> region_scope
status        -> status
start_date    -> start_date
```

Employees phải import trước Customers và Orders.

---

# 13. Campaigns

## Headers

```text
campaign_id
campaign_name
campaign_type
start_date
end_date
channel
target_segment
status
budget_vnd
```

Mapping:

```text
campaign_id    -> campaign_code
campaign_name  -> name
campaign_type  -> campaign_type
start_date     -> start_date
end_date       -> end_date
channel        -> channel
target_segment -> target_segment
status         -> status
budget_vnd     -> budget_vnd
```

---

# 14. Interactions

## Headers

```text
interaction_id
customer_unique_id
product_id
interaction_type
interaction_timestamp
channel
session_id
campaign_id
interaction_value
interaction_result
```

Mapping:

```text
interaction_id        -> interaction_code
customer_unique_id    -> customers.customer_code
product_id            -> products.source_product_id
interaction_type      -> interaction_type
interaction_timestamp -> interaction_timestamp
channel               -> channel
session_id            -> session_id
campaign_id           -> campaign_id nullable
interaction_value     -> interaction_value
interaction_result    -> interaction_result
```

Special case quan trọng:

```text
campaign_id = "1583"
```

không tồn tại trong Campaigns.

Import rule:

```text
"1583" -> NULL
```

Không tạo Campaign giả.

Phase 1:

```text
is_mock_data = TRUE
```

---

# 15. CustomerAnalytics

## Headers

```text
AnalysisDate
CustomerID
OwnerID
RecencyDays
Frequency
Monetary
AOV
AvgPurchaseCycleDays
AvgReviewScore
InteractionScore
RScore
FScore
MScore
PotentialScore
Segment
ModelStatus
```

Đây là **derived analytical result**, không phải master/source transaction.

Mapping logic:

```text
Frequency
Monetary
AOV
AvgReviewScore
-> customer_behavior_history

RScore
FScore
MScore
InteractionScore
PotentialScore
-> customer_potential_score_history

Segment
-> segment_history
```

Dataset hiện có formula lỗi:

```text
RecencyDays = #NAME?
AvgPurchaseCycleDays = #NAME?
```

Agent không được insert `#NAME?`.

Phải tính lại hai giá trị này từ Orders hợp lệ.

Current Phase-1 Potential Score:

```text
Recency     35%
Frequency   30%
Monetary    20%
Interaction 15%
```

Không dùng Trend trong Phase 1.

Segment:

```text
PotentialScore >= 80        -> Tiềm năng cao
60 <= PotentialScore < 80   -> Tiềm năng
PotentialScore < 60         -> Thông thường
No valid order              -> Chưa đủ dữ liệu
```

---

# 16. ModelRuns

## Headers

```text
run_id
run_timestamp
analysis_date
model_type
model_version
status
record_count
notes
```

Mapping:

```text
run_id        -> analysis_runs.run_code
run_timestamp -> started_at / completed_at
analysis_date -> analysis_date
model_type    -> analysis_type
status        -> status
record_count  -> total_records
```

Dataset hiện có:

```text
RUN001 = RFM + Potential Score / Completed / 80 records
RUN002 = Machine Learning / Not trained / 0 records
```

Không sinh ML prediction giả từ RUN002.

---

# 17. DataDictionary

`DataDictionary` chỉ là metadata/documentation.

Không import vào core business tables.

Không dùng sheet này tự động generate:
- FK
- migration
- constraint
- enum

vì một số metadata hiện có giá trị placeholder/không đáng tin như `1583`.

Source of truth cho import:

```text
Actual sheet data
+ SRS
+ Current PostgreSQL schema
```

---

# 18. Excel date/time parsing

Nhiều ngày được lưu dạng Excel serial number, ví dụ:

```text
45421
45905.31335648148
```

Base:

```text
1899-12-30
```

Pseudo:

```text
datetime = 1899-12-30 + serial days
```

Business timezone:

```text
Asia/Ho_Chi_Minh
```

DB target:

```text
TIMESTAMPTZ
```

---

# 19. Currency normalization

```text
VNĐ -> VND
VND -> VND
```

---

# 20. Import validation

## Customer
```text
customer_id required
customer_unique_id required
owner_id phải tồn tại nếu provided
```

## Product
```text
product_id required
ProductCategory required
ListPrice >= 0
```

## Order
```text
order_id required
customer_id phải tồn tại
OrderTotal >= 0
```

## OrderItem
```text
order_id tồn tại
product_id tồn tại
seller_id tồn tại nếu provided
Quantity > 0
price >= 0
```

## Payment
```text
order_id tồn tại
payment_value >= 0
```

## Review
```text
order_id tồn tại
CustomerID tồn tại
review_score từ 1 đến 5
```

## Interaction
```text
customer tồn tại
product tồn tại
campaign nullable
"1583" -> NULL
```

---

# 21. Partial success

Không rollback toàn workbook vì vài row lỗi.

Ví dụ:

```text
1000 rows
990 valid
10 invalid
```

Kết quả:

```text
successRows = 990
failedRows  = 10
```

Error phải chứa:

```text
sheet
rowNumber
fieldName
errorCode
errorMessage
rawValue
```

---

# 22. Idempotency / duplicate keys

```text
Employees     -> employee_id
Campaigns     -> campaign_id
Sellers       -> seller_id
Products      -> product_id
Customers     -> customer_id / customer_unique_id
Orders        -> order_id
OrderItems    -> (order_id, order_item_id)
Payments      -> (order_id, payment_sequential)
Reviews       -> review_id
Interactions  -> interaction_id
ModelRuns     -> run_id
```

Import lại file không được tạo duplicate.

---

# 23. Sheet classification

## Source / Master
```text
Customers
Products
Employees
Sellers
Geolocation
Campaigns
```

## Transaction
```text
Orders
OderItems
Payments
Reviews
Interactions
```

## Derived / Analytics
```text
CustomerAnalytics
ModelRuns
```

## Documentation only
```text
DataDictionary
```

---

# 24. Agent implementation rules

Agent sửa Excel import phải tuân thủ:

```text
1. Detect exact sheet names.
2. Validate required sheets.
3. Validate exact/allowed headers trước khi parse.
4. Hỗ trợ tên sheet typo `OderItems`.
5. Parse Excel serial date/time.
6. Normalize VNĐ -> VND.
7. Resolve FK bằng business/source key.
8. Không dùng raw source ID làm PostgreSQL UUID.
9. Không import `#NAME?`.
10. campaign_id = 1583 -> NULL.
11. Interaction Phase 1 -> is_mock_data = TRUE.
12. CustomerAnalytics không phải source of truth.
13. Recalculate Recency và Purchase Cycle từ Orders.
14. Không fake ML result từ RUN002.
15. Import partial success.
16. Error phải có sheet + row + field.
17. Import phải idempotent.
18. Analytics/history phải gắn AnalysisRun.
19. Potential Score tách biệt ML probability.
20. DataDictionary không import vào business schema.
```

---

# 25. Expected header contract

## Customers
```text
customer_id
customer_unique_id
customer_zip_code_prefix
customer_city
customer_state
CustomerName
Region
ProvinceCity
Email
Phone
RegisteredDate
owner_id
CustomerStatus
CustomerSegment
```

## Products
```text
product_id
product_category_name
product_name_lenght
product_description_lenght
product_photos_qty
product_weight_g
product_length_cm
product_height_cm
product_width_cm
Description
ProductCategory
ListPrice
Currency
ProductStatus
```

## Orders
```text
order_id
customer_id
order_status
order_purchase_timestamp
order_approved_at
order_delivered_carrier_date
order_delivered_customer_date
order_estimated_delivery_date
CustomerID
SalesChannel
PaymentMethod
Region
ProvinceCity
owner_id
OrderSubtotal
FreightTotal
DiscountTotal
OrderTotal
Currency
IsValidForRFM
```

## OderItems
```text
order_id
order_item_id
product_id
seller_id
shipping_limit_date
price
freight_value
Quantity
LineAmount
OrderDetailID
discount_value
line_subtotal
line_total
```

## Payments
```text
order_id
payment_sequential
payment_type
payment_installments
payment_value
PaymentMethodVN
Currency
```

## Reviews
```text
review_id
order_id
review_score
review_comment_title
review_comment_message
review_creation_date
review_answer_timestamp
CustomerID
Channel
```

## Sellers
```text
seller_id
seller_zip_code_prefix
seller_city
seller_state
Region
SellerName
```

## Geolocation
```text
geolocation_zip_code_prefix
geolocation_lat
geolocation_lng
geolocation_city
geolocation_state
Region
```

## Employees
```text
employee_id
employee_name
department
email
phone
region_scope
status
start_date
```

## Interactions
```text
interaction_id
customer_unique_id
product_id
interaction_type
interaction_timestamp
channel
session_id
campaign_id
interaction_value
interaction_result
```

## Campaigns
```text
campaign_id
campaign_name
campaign_type
start_date
end_date
channel
target_segment
status
budget_vnd
```

## CustomerAnalytics
```text
AnalysisDate
CustomerID
OwnerID
RecencyDays
Frequency
Monetary
AOV
AvgPurchaseCycleDays
AvgReviewScore
InteractionScore
RScore
FScore
MScore
PotentialScore
Segment
ModelStatus
```

## ModelRuns
```text
run_id
run_timestamp
analysis_date
model_type
model_version
status
record_count
notes
```

---

# 26. Recommended import flow

```text
Upload Excel
    ↓
Validate workbook
    ↓
Validate sheet names
    ↓
Validate headers
    ↓
Create ImportJob
    ↓
Parse rows
    ↓
Normalize values
    ↓
Import reference/master data
    ↓
Resolve foreign keys
    ↓
Import transactions
    ↓
Import interactions
    ↓
Recalculate derived fields
    ↓
Create/resolve AnalysisRun
    ↓
Write analytical history
    ↓
Write ImportErrors
    ↓
Return summary
```

Example response:

```json
{
  "status": "PARTIAL_SUCCESS",
  "totalRows": 1792,
  "successRows": 1787,
  "failedRows": 5,
  "errors": [
    {
      "sheet": "Orders",
      "rowNumber": 25,
      "fieldName": "customer_id",
      "errorCode": "CUSTOMER_NOT_FOUND",
      "rawValue": "CUS99999"
    }
  ]
}
```

---

# 27. Final instruction to Coding Agent

Không thiết kế import theo tư duy:

```text
1 Excel sheet = 1 database table
```

Flow đúng là:

```text
Excel source
    ↓
validate
    ↓
normalize
    ↓
resolve source/business keys
    ↓
map sang PostgreSQL domain model
    ↓
recalculate derived analytics
    ↓
persist history/result
```

`CustomerAnalytics` là output prototype dùng để đối chiếu logic.

`DataDictionary` là tài liệu metadata tham khảo, không phải nguồn sinh schema.
