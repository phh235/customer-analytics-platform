# Customer Analytics Platform — API Documentation

> **Base URL:** `http://localhost:8000`  
> **Swagger UI:** `http://localhost:8000/docs`  
> **ReDoc:** `http://localhost:8000/redoc`

---

## Authentication

### `POST /api/v1/auth/login`
Đăng nhập, nhận JWT token.

**Input:**
```json
{
  "email": "user@example.com",      // required, email hợp lệ
  "password": "StrongPassword123!"  // required
}
```

**Output (200):**
```json
{
  "token_type": "Bearer",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 900,
  "refresh_token": "dGhpcyBpcyBhIHJl...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "status": "ACTIVE",
    "role_code": "ADMIN",
    "permissions": [
      "users:create",
      "users:read",
      "users:update",
      "users:delete",
      "customers:read",
      "customers:export",
      "analytics:read",
      "analytics:predict"
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "last_login_at": "2024-01-15T10:30:00Z"
  }
}
```

**Lỗi:**
| Status | Message | Ghi chú |
|--------|---------|---------|
| 401 | Email hoặc mật khẩu không chính xác | `INVALID_CREDENTIALS` |
| 401 | Tài khoản đã bị vô hiệu hóa | `USER_DISABLED` |
| 401 | Tài khoản đã bị khóa | `USER_LOCKED` |
| 500 | Internal server error | `INTERNAL_SERVER_ERROR` |

---

### `GET /api/v1/auth/me`
Lấy thông tin người dùng hiện tại (cần Bearer token).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Output (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Nguyen Van A",
  "status": "ACTIVE",
  "role_code": "ADMIN",
  "permissions": [
    "users:create",
    "users:read",
    "users:update",
    "users:delete",
    "customers:read",
    "customers:export",
    "analytics:read",
    "analytics:predict"
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "last_login_at": "2024-01-15T10:30:00Z"
}
```

**Lỗi:**
| Status | Message | Ghi chú |
|--------|---------|---------|
| 401 | Token hết hạn hoặc không hợp lệ | `INVALID_TOKEN` |

---

### `POST /api/v1/auth/logout`
Đăng xuất (thu hồi current session). Cần Bearer token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Output (200):**
```json
{
  "message": "Đăng xuất thành công."
}
```

---
### `POST /api/v1/auth/register`
Đăng ký tài khoản public. Không cần Bearer token. Backend luôn gán
`role_code=USER`; client không được chọn role hoặc team.

**Input:**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "full_name": "Nguyen Van A"
}
```

**Output (201):**
```json
{
  "message": "Đăng ký tài khoản thành công.",
  "user": {
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "status": "ACTIVE",
    "role_code": "USER"
  }
}
```

### Password reset bằng OTP

```text
POST /api/v1/auth/password/forgot/request
POST /api/v1/auth/password/forgot/verify
POST /api/v1/auth/password/reset
```

Request OTP:
```json
{
  "email": "user@example.com"
}
```

API luôn trả `202` với message generic để không làm lộ email tồn tại.
OTP có 6 chữ số, hiệu lực 10 phút và chỉ sử dụng một lần.
Sau khi verify OTP, API trả `reset_token` ngắn hạn để gọi endpoint reset password.
Reset thành công sẽ revoke toàn bộ refresh sessions của user.

SMTP phải được cấu hình bằng `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`,
`SMTP_PASSWORD` và `SMTP_FROM_EMAIL`.

---


## User Management (cần quyền `users:create`)

### `POST /api/v1/users`
Tạo tài khoản mới.

**Headers:**
```
Authorization: Bearer <access_token>  (cần quyền "users:create")
```

**Input:**
```json
{
  "email": "newuser@example.com",     // required, email hợp lệ, phải unique
  "password": "StrongPassword123!",   // required, tối thiểu 8 ký tự
  "full_name": "Nguyen Van B",        // required
  "role_code": "USER"               // optional, default "USER". Giá trị: "ADMIN" | "USER"
}
```

**Output (201):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "email": "newuser@example.com",
  "full_name": "Nguyen Van B",
  "status": "ACTIVE",
  "role_code": "USER",
  "created_at": "2024-01-15T10:00:00Z",
  "last_login_at": null
}
```

**Lỗi:**
| Status | Message | Ghi chú |
|--------|---------|---------|
| 401 | Token hết hạn hoặc không hợp lệ | `INVALID_TOKEN` |
| 403 | Bạn không có quyền thực hiện thao tác này | `ACCESS_DENIED` |
| 404 | Role không tồn tại | `ROLE_NOT_FOUND` |
| 409 | Email đã tồn tại trong hệ thống | `USER_ALREADY_EXISTS` |
| 422 | Validation error | `VALIDATION_ERROR` |
| 500 | Internal server error | `INTERNAL_SERVER_ERROR` |

---

## Product Catalog

### `GET /api/v1/products`
Lấy danh sách sản phẩm phân trang (cần quyền `products:read`).

Mỗi product response gồm:

- `id`, `name`, `category`, `price`, `status`
- `sku`: mã SKU, có thể `null`
- `description`: mô tả, có thể `null`
- `image_url`: URL ảnh Cloudinary, có thể `null`
### `GET /api/v1/products/{product_id}`
Lấy chi tiết sản phẩm và tối đa 4 sản phẩm liên quan cùng category (cần quyền
`products:read`). Response giữ các field product chuẩn và thêm:

- `related_products`: danh sách product cùng category, không bao gồm product hiện tại

### `POST /api/v1/products/{product_id}/view`
Ghi nhận một lượt xem sản phẩm cho tài khoản đã xác thực (cần quyền
`products:read`).

- Không cần request body; gửi `Authorization: Bearer <access_token>`.
- Response `201` gồm `event_id` và `interaction_type: "product_view"`.
- Tài khoản được liên kết với customer profile theo email sau migration. Nếu
  chưa có profile tương ứng, backend tạo profile tối thiểu và liên kết tài khoản
  ở lượt xem đầu tiên.


### `POST /api/v1/products/{product_id}/image`
Tải ảnh sản phẩm lên Cloudinary và lưu `image_url` (cần quyền
`products:update`).

- Content type: `multipart/form-data`
- Field: `image`
- Giới hạn: 10 MB, chỉ nhận MIME type ảnh
- Cấu hình backend: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`,
  `CLOUDINARY_API_SECRET`, và tùy chọn `CLOUDINARY_PRODUCT_FOLDER`

Khi chưa cấu hình đủ credential Cloudinary, endpoint trả `503`.

---

## Analytics scenario workflow

### Potential score levels

The API uses the scenario names and thresholds:

| Score | Level |
|-------|-------|
| `>= 80` | `HIGH` |
| `60-<80` | `POTENTIAL` |
| `< 60` | `NORMAL` |
| No valid order in window | `INSUFFICIENT_DATA` |

For `INSUFFICIENT_DATA`, `recency_days`, R/F/M component scores, and
`potential_score` are `null`. The response includes the missing component names
instead of substituting zero-valued scores.

The Script_Duan score uses five-point component scores configured through
`SCORE_*` settings:

```text
Potential Score =
  (R * 0.35 + F * 0.30 + M * 0.20 + Interaction * 0.15) * 20
```

`R`, `F`, `M`, and `Interaction` are derived from the configured business
bands; they are not hard-coded per customer. Missing interaction data causes
the available component weights to be renormalized. The default configuration
is `SCRIPT_DUAN_V4_EXCEL_PARITY`.

`GET /api/v1/analytics/segments` returns `potential_score`, `potential_level`,
`rfm`, and `score_components` for every record. `rfm` contains the source
recency/frequency/monetary metrics; `score_components` contains the five-point
R/F/M/Interaction inputs, raw interaction value, applied weights, missing
components, and configuration version. This allows the score to be recomputed
from the response and audited against the formula above.

### Model lifecycle

`POST /api/v1/analytics/models/train` trains and evaluates a Logistic Regression
or Random Forest model. A model is not deployed automatically.

`GET /api/v1/analytics/models` lists registered versions. An `APPROVED` version
can be deployed with:

```text
POST /api/v1/analytics/models/{version}/deploy
```

Approval requires all configured gates to pass:

- PR-AUC greater than the baseline conversion PR-AUC.
- Lift@Top10 at least `ML_MIN_LIFT_TOP10` (default `2.0`).
- Precision@Top10 at least
  `ML_MIN_PRECISION_TOP10_MULTIPLIER × overall_conversion` (default `2.0×`).

The purchase prediction and priority-list endpoints return `503` when no
deployed model artifact is available. This prevents serving unapproved or
missing model output.

### Priority list

`GET /api/v1/analytics/priority-list` returns customers where:

```text
potential_score >= 80
OR
purchase_probability >= ML_PRIORITY_PROBABILITY_THRESHOLD
```

The response includes the preferred category, purchase cycle, priority reason,
and recommended next action.

---
### Deterministic scenario fixture

To replace business data with the minimal local test scenario while preserving
users and configuration, run from `backend/`:

```bash
uv run python scripts/reset_scenario_fixture.py --confirm
```

This destructive reset keeps 6 users and creates 6 customers, 3 products, 21
delivered orders, 21 order items, and 3 interactions. The primary scenario
customer is `KH0013` (`10000000-0000-4000-8000-000000000013`), with 8 historical
orders, VND 18.5M monetary value, and interaction score 76.

The script is for a dedicated local/test database only. It truncates business
records (`customers`, `products`, `orders`, `import_jobs`, `model_registry`, and
`analysis_runs`) and requires the explicit `--confirm` flag.

---

### E2E data cleanup

E2E imports and model artifacts are intentionally not deleted automatically.
Before removing them, verify the target database and collect the generated
customer/product/order IDs. Delete dependent rows in this order inside one
transaction:

```text
order_items -> orders -> customer_interactions -> customers
```

Then remove only model artifacts whose filenames start with `e2e-` and model
registry versions whose versions start with `e2e-`. Do not use a broad
`TRUNCATE` or unscoped delete against a shared database.

---


## Health

### `GET /health`
Kiểm tra trạng thái server (không cần auth).

**Output (200):**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

### `GET /api/v1/health`
Kiểm tra trạng thái server và database connection.

**Output (200):**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "checks": {
    "database": "healthy"
  }
}
```

**Lỗi:**
| Status | Message | Ghi chú |
|--------|---------|---------|
| 503 | Service unavailable | Database không khả dụng |

---

## Roles & Permissions

### Roles

| Code | Tên | Mô tả | Quyền chính |
|------|-----|-------|-------------|
| `ADMIN` | Administrator | Toàn quyền hệ thống | Tất cả quyền |
| `USER` | User | Tài khoản người dùng | `products:read` |


### Tài khoản demo

Các tài khoản được tạo bởi `customer_analytics.scripts.seed_data`:

| Email | Mật khẩu | Role | Mục đích |
|-------|----------|------|----------|
| `admin@example.com` | `Admin123!` | `ADMIN` | Kiểm tra toàn quyền |
| `user@example.com` | `User123!` | `USER` | Kiểm tra quyền người dùng |
### Màn hình theo role

| Màn hình | ADMIN | USER |
|----------|:-----:|:----:|
| Dashboard tổng quan | Có | Không |
| Sản phẩm / danh mục | Có | Không |
| Khách hàng | Có | Không |
| Giao dịch | Có | Không |
| Phân khúc / dự đoán / ưu tiên | Có | Không |
| Nhập dữ liệu | Có | Không |
| Quản lý mô hình | Có | Không |
| Quản lý tài khoản | Có | Không |
| Sản phẩm phía khách hàng | Không áp dụng | Có |
 

Frontend ẩn menu không có permission và hiển thị màn hình `403 — Không có quyền truy cập`
cho đường dẫn dashboard bị truy cập trực tiếp. Backend vẫn là lớp bảo vệ bắt buộc và trả HTTP 403.
### Permissions

| Code | Resource | Action | Mô tả |
|------|----------|--------|-------|
| `users:create` | users | create | Tạo người dùng mới |
| `users:read` | users | read | Xem thông tin người dùng |
| `users:update` | users | update | Cập nhật thông tin người dùng |
| `users:delete` | users | delete | Xóa người dùng |
| `customers:read` | customers | read | Xem dữ liệu khách hàng |
| `customers:export` | customers | export | Xuất dữ liệu khách hàng |
| `analytics:read` | analytics | read | Xem phân tích |
| `analytics:predict` | analytics | predict | Chạy dự đoán |

### How RBAC Works

1. **Login** → System loads user's permissions from DB (via role → role_permissions → permissions)
2. **JWT Token** → Contains `permissions` array (e.g., `["users:create", "users:read", ...]`)
3. **API Request** → Decode JWT, extract permissions, check against required permission

### Using require_permission in Code

```python
from customer_analytics.app.features.identity.presentation.dependencies import require_permission

# Check single permission
@router.get("/users", dependencies=[Depends(require_permission("users:read"))])
async def list_users():
    ...

# Check multiple permissions (all required)
@router.post(
    "/users",
    dependencies=[
        Depends(require_permission("users:create")),
        Depends(require_permission("users:read")),  # To return the created user
    ],
)
async def create_user():
    ...
```

### Permission Hierarchy

- `ADMIN` role has **all permissions** automatically
- `USER` role has only product read access
- Keep the supported role list in `scripts/seed_data.py` aligned with the API schemas

---

## Error Response Format

### Standard Error
```json
{
  "success": false,
  "error": {
    "code": 401,
    "message": "Email hoặc mật khẩu không chính xác.",
    "error": "Unauthorized",
    "path": "/api/v1/auth/login",
    "timestamp": 1705312200000,
    "details": null
  }
}
```

### Validation Error (422)
```json
{
  "detail": [
    {
      "type": "string",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "invalid-email"
    }
  ]
}
```
