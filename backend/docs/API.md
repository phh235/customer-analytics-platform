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
  "role_code": "ANALYST"             // optional, default "ANALYST". Giá trị: "ADMIN" | "ANALYST"
}
```

**Output (201):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "email": "newuser@example.com",
  "full_name": "Nguyen Van B",
  "status": "ACTIVE",
  "role_code": "ANALYST",
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

| Code | Tên | Mô tả | Quyền |
|------|-----|-------|-------|
| `ADMIN` | Administrator | Quản trị viên hệ thống | **Tất cả quyền** |
| `ANALYST` | Data Analyst | Phân tích dữ liệu | `customers:read`, `customers:export`, `analytics:read`, `analytics:predict` |

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
- `ANALYST` role has only specific permissions (see table above)
- To add new roles, update `scripts/seed_data.py` and run seed again

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
