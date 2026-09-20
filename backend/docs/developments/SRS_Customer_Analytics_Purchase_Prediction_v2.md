# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## Hệ thống phân tích dữ liệu khách hàng và dự đoán tiềm năng mua hàng

**Phiên bản:** 2.0  
**Mục đích:** Tài liệu đặc tả yêu cầu phần mềm dùng làm baseline cho BA, Backend, Frontend, Data/ML, QA và AI Coding Agent triển khai hệ thống.  
**Lưu ý:** Các ngưỡng, công thức và cấu hình được đánh dấu **[DEFAULT ĐỀ XUẤT]** là giá trị mặc định phục vụ MVP và có thể thay đổi thông qua cấu hình hệ thống sau này.

---

# 1. GIỚI THIỆU

## 1.1 Mục đích tài liệu

Tài liệu Software Requirements Specification (SRS) xác định các yêu cầu phần mềm của **Hệ thống phân tích dữ liệu khách hàng và dự đoán tiềm năng mua hàng**.

Tài liệu là cơ sở thống nhất giữa:

- Phân tích nghiệp vụ
- Thiết kế hệ thống
- Phát triển Backend
- Phát triển Frontend
- Phát triển Data/ML
- Kiểm thử
- Nghiệm thu

Requirement phải đủ rõ để có thể thiết kế, triển khai và xác minh bằng test case.

## 1.2 Phạm vi hệ thống

Hệ thống hỗ trợ:

- Quản lý dữ liệu khách hàng
- Quản lý giao dịch/đơn hàng
- Quản lý sản phẩm
- Import dữ liệu từ Excel
- Kiểm tra và chuẩn hóa dữ liệu
- Phân tích hành vi mua hàng
- Tính các chỉ số RFM, AOV, chu kỳ mua và xu hướng mua
- Phân khúc khách hàng
- Tính Potential Score theo rule
- Dự đoán Probability of Purchase khi có mô hình ML
- Phân tích sở thích nhóm sản phẩm
- Dashboard và báo cáo
- Danh sách khách hàng mục tiêu
- Quản lý người dùng, vai trò, quyền và phạm vi dữ liệu
- Lưu lịch sử phân tích, score, segment và prediction
- Audit các thao tác quan trọng

Hệ thống không được đồng nhất:

- **Potential Score**
- **Probability of Purchase**

## 1.3 Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| RFM | Recency - Frequency - Monetary |
| Recency | Số ngày kể từ lần mua gần nhất đến ngày phân tích |
| Frequency | Số đơn hàng hợp lệ duy nhất trong kỳ |
| Monetary | Tổng giá trị giao dịch hợp lệ trong kỳ |
| AOV | Average Order Value |
| Potential Score | Điểm tiềm năng theo rule, thang 0-100 |
| Probability of Purchase | Xác suất mua do mô hình ML sinh ra |
| Feature Window | Khoảng lịch sử dùng để tạo feature |
| Prediction Horizon | Khoảng tương lai cần dự đoán |
| Model Version | Phiên bản mô hình ML |
| Analysis Run | Một lần chạy phân tích |
| Configuration Version | Phiên bản cấu hình rule/threshold/weight |
| Valid Order | Đơn hàng đủ điều kiện được tính vào phân tích |

---

# 2. MÔ TẢ TỔNG QUAN HỆ THỐNG

## 2.1 Mục tiêu

Hỗ trợ doanh nghiệp:

- Hiểu hành vi khách hàng
- Xác định khách hàng giá trị cao
- Xác định khách hàng có tiềm năng mua
- Xác định khách hàng có nguy cơ giảm mua
- Hiểu nhóm sản phẩm khách hàng quan tâm
- Tạo danh sách khách hàng mục tiêu
- Hỗ trợ Sales và CSKH ưu tiên đúng khách hàng

## 2.2 Nhóm người dùng

- ADMIN
- MANAGER
- ANALYST
- SALES
- CSKH

## 2.3 Thành phần logic

```text
Data Source
    ↓
Data Validation
    ↓
Customer / Order / Product Storage
    ↓
Behavior Analytics
    ↓
Segmentation
    ↓
Potential Scoring
    ↓
Product Preference
    ↓
ML Prediction
    ↓
Dashboard / Target List / Report
```

## 2.4 Ràng buộc

### CON-01
Dữ liệu phục vụ phân tích phải qua kiểm tra chất lượng.

### CON-02
Người dùng chỉ được truy cập chức năng và dữ liệu trong phạm vi được cấp.

### CON-03
Kết quả phải truy vết được theo:

- dữ liệu đầu vào
- thời điểm chạy
- người chạy
- Analysis Run
- Configuration Version
- Model Version nếu có

### CON-04
Các tham số nghiệp vụ phải cấu hình được mà không sửa source code.

## 2.5 Giả định

- Customer ID phải nhất quán.
- Order phải liên kết được Customer.
- Order Detail phải liên kết được Product.
- Interaction chỉ được sử dụng khi có nguồn dữ liệu thực tế.
- Chất lượng ML phụ thuộc chất lượng dữ liệu lịch sử.

---

# 3. MODULE HỆ THỐNG

| Mã | Module | Mô tả |
|---|---|---|
| MOD-01 | Quản lý dữ liệu | Customer, Order, Order Detail, Product, Import |
| MOD-02 | Behavior Analytics | RFM, AOV, Purchase Cycle, Trend |
| MOD-03 | Segmentation | Phân khúc khách hàng |
| MOD-04 | Potential & Prediction | Potential Score và ML Prediction |
| MOD-05 | Product Preference | Xếp hạng nhóm sản phẩm |
| MOD-06 | Dashboard & Report | KPI, chart, target list |
| MOD-07 | System Administration | User, Role, Permission, Config |
| MOD-08 | Analysis Run & History | Quản lý các lần chạy và lịch sử |
| MOD-09 | ML Model Management | Training metadata, version, deployment status |

---

# 4. YÊU CẦU DỮ LIỆU

## 4.1 Customer

Trường tối thiểu:

- customer_id
- customer_name
- phone
- email
- region
- assigned_user_id
- created_at
- updated_at
- is_deleted

`customer_id` là business key duy nhất.

## 4.2 Order

Trường tối thiểu:

- order_id
- customer_id
- order_date
- status
- total_amount
- refund_amount
- net_amount
- created_at

## 4.3 Order Detail

- order_detail_id
- order_id
- product_id
- quantity
- unit_price
- line_amount

## 4.4 Product

- product_id
- product_name
- category_id
- category_name
- is_active

## 4.5 Interaction

Chỉ sử dụng khi có nguồn dữ liệu thực tế.

Ví dụ:

- email opened
- click
- website interaction
- campaign response
- call result

Không được tạo dữ liệu interaction giả.

---

# 5. QUY TẮC DỮ LIỆU VÀ CHẤT LƯỢNG

## 5.1 Valid Order

Danh sách trạng thái hợp lệ phải configurable.

**[DEFAULT ĐỀ XUẤT]**

Valid:

- PAID
- COMPLETED

Invalid:

- CANCELLED
- FAILED
- REFUNDED

`PARTIAL_REFUNDED` xử lý theo `net_amount`.

## 5.2 Monetary

```text
Net Amount = Total Amount - Refund Amount
Monetary = SUM(Net Amount của Valid Order)
```

Không sử dụng subtotal nếu business không cấu hình khác.

## 5.3 Frequency

```text
Frequency = COUNT(DISTINCT Order ID)
```

Không được tính theo Order Detail.

## 5.4 Import Validation

Kiểm tra:

- Required field
- Data type
- Date format
- Duplicate business key
- Referential integrity
- Invalid order status
- Invalid product mapping

Record lỗi không được coi là dữ liệu hợp lệ.

---

# 6. IMPORT EXCEL

## 6.1 File hỗ trợ

MVP:

- `.xlsx`

## 6.2 Import Mode

**[DEFAULT ĐỀ XUẤT]**

- UPSERT by business key

Business key:

| Entity | Business Key |
|---|---|
| Customer | customer_id |
| Order | order_id |
| Product | product_id |

## 6.3 Import Transaction

MVP dùng **Partial Success**.

Ví dụ:

```text
Total: 1000
Success: 990
Failed: 10
```

990 record hợp lệ được lưu.

10 record lỗi bị từ chối.

## 6.4 Import Result

Response phải có:

```json
{
  "totalRows": 1000,
  "successRows": 990,
  "failedRows": 10,
  "errors": [
    {
      "row": 25,
      "field": "customer_id",
      "code": "IMP_002",
      "message": "customer_id is required"
    }
  ]
}
```

---

# 7. ANALYSIS PERIOD

Timezone hệ thống:

```text
Asia/Ho_Chi_Minh
```

Ngày chạy:

```text
analysisDate
```

Các kỳ mặc định:

- 30 ngày
- 90 ngày
- 6 tháng
- 12 tháng
- Custom

Ví dụ:

```text
30 ngày = [analysisDate - 29 ngày, analysisDate]
```

---

# 8. BEHAVIOR ANALYTICS

## 8.1 Recency

```text
Recency = Analysis Date - Last Valid Purchase Date
```

Nếu chưa có giao dịch:

```text
status = NO_PURCHASE_DATA
```

## 8.2 Frequency

```text
Frequency = COUNT(DISTINCT valid_order_id)
```

## 8.3 Monetary

```text
Monetary = SUM(net_amount)
```

## 8.4 AOV

```text
AOV = Monetary / Frequency
```

Nếu Frequency = 0:

```text
AOV = 0
```

## 8.5 Purchase Cycle

Tính trên các ngày mua hợp lệ liên tiếp.

**[DEFAULT ĐỀ XUẤT]**

```text
Purchase Cycle dùng DISTINCT purchase date.
```

Ví dụ:

```text
01/01
11/01
31/01

Intervals:
10
20

Average Purchase Cycle = 15 days
```

Nếu có dưới 2 purchase date:

```text
status = INSUFFICIENT_DATA
```

## 8.6 Purchase Trend

```text
growthRate =
(currentValue - previousValue)
/ previousValue
* 100
```

So sánh kỳ hiện tại với kỳ trước cùng độ dài.

### Default Threshold

**[DEFAULT ĐỀ XUẤT]**

| Growth Rate | Trend |
|---|---|
| >= 30% | STRONG_INCREASE |
| 10% đến < 30% | INCREASE |
| > -10% đến < 10% | STABLE |
| > -30% đến <= -10% | DECREASE |
| <= -30% | STRONG_DECREASE |

Special case:

```text
previous = 0, current > 0 -> NEW_GROWTH
previous = 0, current = 0 -> NO_ACTIVITY
```

---

# 9. POTENTIAL SCORE

## 9.1 Nguyên tắc

Potential Score:

- Thang 0-100
- Là rule-based score
- Không phải probability
- Phải lưu component score
- Phải lưu weight
- Phải lưu config version

## 9.2 Default Weight

| Component | Weight |
|---|---:|
| Recency | 30% |
| Frequency | 25% |
| Monetary | 20% |
| Interaction | 15% |
| Trend | 10% |

Tổng = 100%.

## 9.3 Normalization

### Recency Score

**[DEFAULT ĐỀ XUẤT]**

| Recency | Score |
|---|---:|
| 0-7 ngày | 100 |
| 8-30 | 80 |
| 31-60 | 60 |
| 61-90 | 40 |
| >90 | 20 |
| No Purchase | 0 |

### Frequency Score

**[DEFAULT ĐỀ XUẤT]**

| Orders | Score |
|---|---:|
| >=10 | 100 |
| 7-9 | 80 |
| 4-6 | 60 |
| 2-3 | 40 |
| 1 | 20 |
| 0 | 0 |

### Monetary Score

Phải configurable theo business.

**[DEFAULT ĐỀ XUẤT]**

Dùng threshold cấu hình thay vì hardcode theo source code.

### Interaction Score

Chỉ tính khi có interaction data.

### Trend Score

**[DEFAULT ĐỀ XUẤT]**

| Trend | Score |
|---|---:|
| STRONG_INCREASE | 100 |
| INCREASE | 80 |
| STABLE | 60 |
| DECREASE | 30 |
| STRONG_DECREASE | 10 |
| NEW_GROWTH | 90 |
| NO_ACTIVITY | 0 |

## 9.4 Công thức

```text
Potential Score =
Σ(componentScore × effectiveWeight)
```

## 9.5 Missing Component

Nếu một component không có dữ liệu:

```text
availableWeight = tổng weight component có dữ liệu

effectiveWeight =
originalWeight / availableWeight
```

Ví dụ không có Interaction:

```text
availableWeight = 85%
```

Sau đó normalize weight của:

- Recency
- Frequency
- Monetary
- Trend

Score cuối vẫn nằm 0-100.

Response phải lưu:

```text
missingComponents
```

## 9.6 Potential Level

**[DEFAULT ĐỀ XUẤT]**

| Score | Level |
|---|---|
| 80-100 | HIGH |
| 50-79 | MEDIUM |
| <50 | LOW |

---

# 10. SEGMENTATION

## 10.1 Nguyên tắc

Một Customer chỉ có một `primary_segment` tại một Analysis Run.

Segment phải:

- Có code
- Có name
- Có reason
- Có priority
- Có config version

## 10.2 Default Segments

**[DEFAULT ĐỀ XUẤT]**

### HIGH_VALUE

```text
Monetary Score >= 80
AND
Frequency Score >= 70
```

### LOYAL

```text
Frequency Score >= 70
AND
Recency Score >= 70
AND
not HIGH_VALUE
```

### AT_RISK

```text
Customer có lịch sử mua
AND
Recency vượt ngưỡng cấu hình
AND
Trend IN (DECREASE, STRONG_DECREASE)
```

### POTENTIAL

```text
Potential Score >= 80
AND
not HIGH_VALUE
AND
not LOYAL
AND
not AT_RISK
```

### NEW_CUSTOMER

**[DEFAULT ĐỀ XUẤT]**

```text
first_purchase_date trong 30 ngày gần nhất
AND
frequency <= 2
```

### NORMAL

Các trường hợp còn lại.

## 10.3 Segment Priority

```text
HIGH_VALUE
> LOYAL
> AT_RISK
> POTENTIAL
> NEW_CUSTOMER
> NORMAL
```

## 10.4 Output

```json
{
  "customerId": "...",
  "segmentCode": "LOYAL",
  "reason": "...",
  "analysisRunId": "...",
  "evaluatedAt": "..."
}
```

---

# 11. PRODUCT PREFERENCE

## 11.1 Mục tiêu

Xác định nhóm sản phẩm khách hàng ưu tiên dựa trên:

- Frequency
- Monetary
- Quantity
- Recency

## 11.2 Preference Score

**[DEFAULT ĐỀ XUẤT]**

```text
Preference Score =
Frequency Score × 35%
+ Monetary Score × 30%
+ Quantity Score × 20%
+ Recency Score × 15%
```

## 11.3 Output

- Top 1
- Top 3
- Rank
- Score
- Purchase Share

Ví dụ:

```json
{
  "customerId": "CUS001",
  "topCategory": "COFFEE",
  "preferences": [
    {
      "categoryId": "CAT01",
      "rank": 1,
      "score": 87.5,
      "purchaseShare": 42.3
    }
  ]
}
```

---

# 12. MACHINE LEARNING

## 12.1 MVP Prediction Problem

**[DEFAULT ĐỀ XUẤT]**

```text
Dự đoán khách hàng có ít nhất 1 Valid Order
trong 30 ngày tiếp theo hay không.
```

Target:

```text
1 = Có mua
0 = Không mua
```

## 12.2 Feature Window

**[DEFAULT ĐỀ XUẤT]**

```text
180 ngày trước Prediction Date
```

## 12.3 Prediction Horizon

```text
30 ngày
```

## 12.4 Feature

Có thể gồm:

- Recency
- Frequency
- Monetary
- AOV
- Purchase Cycle
- Trend
- Product behavior
- Interaction nếu có

Không được sử dụng dữ liệu thuộc prediction horizon làm feature.

## 12.5 Training Flow

```text
Historical Data
↓
Feature Generation
↓
Target Generation
↓
Dataset Split
↓
Training
↓
Evaluation
↓
Model Version
↓
Approval
↓
Deployment
```

## 12.6 Inference Flow

```text
Current Customer Data
↓
Feature Generation
↓
DEPLOYED Model
↓
Probability
↓
Prediction History
```

## 12.7 Model Status

```text
DRAFT
TRAINING
EVALUATING
APPROVED
DEPLOYED
RETIRED
FAILED
```

Chỉ `DEPLOYED` được dùng inference.

## 12.8 Prediction Output

Phải có:

- customer_id
- prediction_date
- prediction_horizon
- probability
- model_version
- feature_window_from
- feature_window_to
- created_at

## 12.9 ML Evaluation

Metric tối thiểu:

- Precision
- Recall
- F1
- ROC-AUC
- PR-AUC

Khuyến nghị thêm:

- Precision@K
- Recall@K
- Lift@K

Acceptance threshold phải do Business/Data Owner xác nhận trước UAT.

---

# 13. ANALYSIS RUN

## 13.1 Entity

```text
AnalysisRun
```

Fields:

```text
id
type
status
data_from
data_to
started_at
completed_at
created_by
configuration_version
model_version
total_records
success_records
failed_records
error_message
```

## 13.2 Status

```text
PENDING
PROCESSING
COMPLETED
FAILED
```

## 13.3 History

Kết quả mới không được overwrite lịch sử.

Lưu riêng:

- customer_behavior_history
- customer_segment_history
- customer_score_history
- customer_prediction_history
- customer_preference_history

---

# 14. CONFIGURATION VERSION

Các cấu hình phải versioning.

Ví dụ:

```text
CONFIG_V1
CONFIG_V2
```

Mỗi version có:

- scoring weights
- scoring thresholds
- trend thresholds
- segmentation rules
- valid order statuses
- analysis periods

Mỗi Analysis Run phải tham chiếu đúng config version đã sử dụng.

---

# 15. PHÂN QUYỀN

## 15.1 Role

```text
ADMIN
MANAGER
ANALYST
SALES
CSKH
```

## 15.2 Permission Code

```text
CUSTOMER_VIEW
CUSTOMER_CREATE
CUSTOMER_UPDATE
CUSTOMER_DELETE

IMPORT_DATA

ANALYSIS_VIEW
ANALYSIS_RUN

SEGMENT_VIEW

PREDICTION_VIEW
PREDICTION_RUN

REPORT_VIEW
REPORT_EXPORT

SYSTEM_CONFIG

USER_MANAGE
ROLE_MANAGE
```

## 15.3 Data Scope

| Role | Scope |
|---|---|
| ADMIN | ALL |
| MANAGER | TEAM |
| ANALYST | ASSIGNED_SCOPE |
| SALES | ASSIGNED_CUSTOMERS |
| CSKH | ASSIGNED_CUSTOMERS |

## 15.4 Customer Assignment

Entity:

```text
customer_assignment
```

Fields:

```text
customer_id
user_id
assigned_at
assigned_by
active
```

---

# 16. AUTHENTICATION

Technical implementation có thể thay đổi theo Technical Design.

**[DEFAULT ĐỀ XUẤT CHO MVP]**

- Username + Password
- Access Token: JWT
- Refresh Token
- Password hashing: BCrypt hoặc Argon2
- Token expiration configurable

---

# 17. CUSTOMER DETAIL

Màn hình/API Customer Detail phải trả:

## Customer Info

- Basic information
- Assigned user

## Behavior

- Recency
- Frequency
- Monetary
- AOV
- Purchase Cycle
- Trend

## Segment

- segment code
- reason

## Potential Score

- total score
- component score
- weight
- missing component
- config version

## ML Prediction

- probability
- horizon
- model version

## Product Preference

- Top 1
- Top 3

## History

- Behavior history
- Segment history
- Score history
- Prediction history

---

# 18. DASHBOARD

## 18.1 KPI

**[DEFAULT ĐỀ XUẤT]**

- Total Customers
- Customers With Purchase
- Total Valid Orders
- Total Revenue
- Average Order Value
- High Potential Customers
- Medium Potential Customers
- Low Potential Customers

## 18.2 Chart

- Customer by Segment
- Customer by Potential Level
- Revenue Trend
- Order Trend
- Revenue by Product Category
- Top Product Preferences

## 18.3 Filter

- Date range
- Segment
- Potential Level
- Product Category
- Assigned User

---

# 19. API CONVENTION

## 19.1 Pagination

```text
GET /api/customers?page=0&size=20&sort=createdAt,desc
```

Response:

```json
{
  "content": [],
  "page": 0,
  "size": 20,
  "totalElements": 1532,
  "totalPages": 77
}
```

## 19.2 Common Filters

- keyword
- segment
- potentialLevel
- assignedUserId
- productCategory
- fromDate
- toDate

## 19.3 Error Response

```json
{
  "code": "CUS_001",
  "message": "Customer not found",
  "details": null,
  "timestamp": "..."
}
```

## 19.4 Error Code

```text
CUS_001 CUSTOMER_NOT_FOUND
CUS_002 CUSTOMER_DUPLICATED

IMP_001 INVALID_FILE_FORMAT
IMP_002 INVALID_ROW
IMP_003 DUPLICATE_BUSINESS_KEY

ANA_001 INSUFFICIENT_DATA
ANA_002 ANALYSIS_RUNNING

ML_001 MODEL_NOT_AVAILABLE
ML_002 MODEL_NOT_DEPLOYED

AUTH_001 ACCESS_DENIED
```

---

# 20. SOFT DELETE

## Customer / Product

Dùng soft delete.

Fields:

```text
is_deleted
deleted_at
deleted_by
```

## Order / Analysis Result

Không được physical delete thông qua luồng nghiệp vụ thông thường.

---

# 21. AUDIT

Các thao tác phải audit:

- Login
- Import
- Delete
- Config change
- Analysis run
- Prediction run
- User management
- Role management
- Report export

Audit log tối thiểu:

```text
actor
action
entity_type
entity_id
timestamp
before_data
after_data
ip
```

---

# 22. NON-FUNCTIONAL REQUIREMENTS

## 22.1 Performance Target

**[DEFAULT ĐỀ XUẤT MVP]**

Dataset:

```text
<= 100,000 customers
<= 1,000,000 orders
<= 5,000,000 order details
```

Response:

```text
Customer List P95 < 2 sec
Customer Detail P95 < 2 sec
Dashboard P95 < 5 sec
```

Import lớn và Analysis phải xử lý asynchronous.

## 22.2 Security

- Authentication bắt buộc
- Authorization theo permission
- Data Scope bắt buộc
- Không trả stacktrace cho user
- TLS trong môi trường production
- Audit export
- Mask dữ liệu nhạy cảm khi cần

## 22.3 Availability

**[DEFAULT ĐỀ XUẤT]**

```text
99.5%
```

---

# 23. BUSINESS RULES

| Rule | Nội dung |
|---|---|
| BR-01 | Customer ID là duy nhất |
| BR-02 | Dữ liệu thiếu bắt buộc không được dùng cho phân tích cần field đó |
| BR-03 | Potential Score nằm 0-100 |
| BR-04 | HIGH = 80-100 |
| BR-05 | MEDIUM = 50-79 |
| BR-06 | LOW < 50 |
| BR-07 | Customer có thể có nhiều Product Preference |
| BR-08 | Tổng scoring weight = 100% |
| BR-09 | Invalid Order không được tính |
| BR-10 | Một Order chỉ tính một lần |
| BR-11 | Threshold phải configurable |
| BR-12 | Kết quả mới không overwrite lịch sử |
| BR-13 | Thiếu dữ liệu phải trả trạng thái phù hợp |
| BR-14 | Prediction phải lưu Model Version |
| BR-15 | Analysis phải lưu Configuration Version |
| BR-16 | Potential Score không được diễn giải thành Probability |
| BR-17 | Sales/CSKH chỉ xem customer thuộc Data Scope |
| BR-18 | Chỉ DEPLOYED model được inference |
| BR-19 | Feature Window không được overlap Prediction Horizon |
| BR-20 | Import lỗi từng dòng không làm mất các dòng hợp lệ trong chế độ Partial Success |

---

# 24. ACCEPTANCE CRITERIA TỐI THIỂU

## AC-01 Import

**Given** file có 100 dòng, 95 hợp lệ và 5 lỗi  
**When** import hoàn tất  
**Then**

- 95 dòng hợp lệ được lưu
- 5 dòng lỗi không được lưu như valid record
- user xem được row và error reason

## AC-02 Frequency

**Given** Customer có 5 valid orders và 2 cancelled orders  
**When** chạy Frequency  
**Then**

```text
Frequency = 5
```

## AC-03 Potential Score

**Given** Interaction không có dữ liệu  
**When** tính Potential Score  
**Then**

- Không tự gán Interaction = 0
- Weight còn lại được normalize
- Score cuối nằm 0-100
- missingComponents chứa INTERACTION

## AC-04 Segment

**Given** Customer thỏa nhiều segment  
**When** segmentation chạy  
**Then**

segment có priority cao nhất được chọn làm primary segment.

## AC-05 ML

**Given** không có DEPLOYED model  
**When** user yêu cầu prediction  
**Then**

```text
status = MODEL_NOT_AVAILABLE
```

và hệ thống không tự sinh probability.

## AC-06 History

**Given** Customer đã có Score Run A  
**When** chạy Score Run B  
**Then**

Run A vẫn được truy xuất.

---

# 25. OUT OF SCOPE MVP

Chưa bắt buộc trong MVP:

- Marketing automation
- Email campaign
- Zalo campaign
- CRM full workflow
- Lead management
- Recommendation AI nâng cao
- Collaborative Filtering
- Market Basket Analysis
- Automated retraining pipeline hoàn chỉnh
- Real-time streaming analytics

---

# 26. ROADMAP GỢI Ý

## Phase 1

- Data Management
- Excel Import
- RFM
- AOV
- Purchase Cycle
- Trend
- Segmentation
- Potential Score
- Product Preference
- Dashboard
- History
- RBAC

## Phase 2

- ML Training
- Model Management
- Probability Prediction
- Target Customer List
- Model Explainability

## Phase 3

- Sales Action
- Campaign Integration
- Conversion Tracking
- Feedback Loop
- Model Retraining

---

# 27. CHECKLIST TRƯỚC KHI GIAO CODING AGENT

Agent không được tự suy đoán các nội dung sau:

- Monetary threshold
- Segment threshold ngoài rule đã xác nhận
- Business status của Order
- Production dataset size
- ML acceptance threshold
- Authentication implementation nếu Technical Design có quy định khác

Nếu chưa có thông tin:

```text
phải giữ configurable
hoặc đánh dấu TODO/TBD
```

Không hardcode logic business chưa được xác nhận.

---

# 28. KẾT LUẬN

Hệ thống được thiết kế theo flow:

```text
Customer Data
    ↓
Data Quality
    ↓
Behavior Analytics
    ↓
Segmentation
    ↓
Potential Score
    ↓
Product Preference
    ↓
ML Purchase Prediction
    ↓
Dashboard / Target Customer
```

SRS này được viết nhằm giảm tối đa việc Coding Agent phải tự suy đoán business logic.

Các giá trị **[DEFAULT ĐỀ XUẤT]** cần được Business Owner xác nhận trước production/UAT.
