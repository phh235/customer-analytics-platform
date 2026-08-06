# Kế hoạch triển khai Backend Python — Giai đoạn 1 và 2

## 1. Mục tiêu

Hoàn thành nền móng backend trước khi xây dựng Data Import và Machine Learning.

Sau hai giai đoạn, hệ thống phải chạy được luồng:

```text
Khởi động hệ thống
→ Kết nối PostgreSQL
→ Tạo tài khoản
→ Đăng nhập
→ Nhận Access Token và Refresh Token
→ Truy cập API được bảo vệ
→ Phân quyền ADMIN/ANALYST
→ Refresh Token Rotation
→ Đăng xuất
→ Ghi nhận Audit Log
```

---

# Giai đoạn 1 — Backend Foundation

## 1.1. Khởi tạo dự án

- [ ] Khởi tạo Git repository.
- [ ] Khởi tạo Python project bằng `uv`.
- [ ] Sử dụng Python 3.13.
- [ ] Tạo `pyproject.toml`.
- [ ] Cài FastAPI và Uvicorn.
- [ ] Tổ chức source code theo `src layout`.
- [ ] Tạo `.gitignore`, `.env.example` và `README.md`.
- [ ] Cấu hình version ban đầu.
- [ ] Thêm health-check endpoint.

### Dependency ban đầu

```bash
uv add fastapi uvicorn pydantic-settings
uv add sqlalchemy asyncpg alembic
uv add structlog
uv add --dev pytest pytest-asyncio httpx pytest-cov
uv add --dev ruff mypy
```

### Cấu trúc source code

```text
customer-analytics-backend/
├── pyproject.toml
├── uv.lock
├── README.md
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── compose.yml
├── src/
│   └── customer_analytics/
│       ├── __init__.py
│       ├── main.py
│       ├── configuration/
│       │   ├── settings.py
│       │   ├── database.py
│       │   ├── logging.py
│       │   └── dependencies.py
│       ├── shared/
│       │   ├── domain/
│       │   ├── application/
│       │   ├── infrastructure/
│       │   └── presentation/
│       └── identity/
├── migrations/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── scripts/
```

### Health endpoint

```http
GET /health
GET /api/v1/health
```

```json
{
  "status": "UP",
  "version": "0.1.0"
}
```

## 1.2. Configuration theo môi trường

- [ ] Dùng `pydantic-settings`.
- [ ] Đọc cấu hình từ environment variables.
- [ ] Tách development, test và production.
- [ ] Không hard-code password, JWT secret hoặc database URL.
- [ ] Fail fast nếu thiếu cấu hình bắt buộc.
- [ ] Không commit file `.env` thật.
- [ ] Cung cấp `.env.example` không chứa secret thật.

```dotenv
APP_NAME=customer-analytics
APP_ENV=development
APP_DEBUG=true
APP_VERSION=0.1.0
API_V1_PREFIX=/api/v1

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=customer_analytics
POSTGRES_USER=customer_analytics
POSTGRES_PASSWORD=change_me

JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_TTL_MINUTES=15
JWT_REFRESH_TOKEN_TTL_DAYS=7

LOG_LEVEL=INFO
```

```text
Local/Test: có thể đọc từ .env
Production: truyền secret qua environment hoặc secret manager
```

## 1.3. PostgreSQL và SQLAlchemy

- [ ] Cấu hình SQLAlchemy 2 async engine với `asyncpg`.
- [ ] Tạo `AsyncSession`.
- [ ] Tạo base class cho ORM model.
- [ ] Tạo dependency cung cấp database session.
- [ ] Quản lý transaction đúng phạm vi use case.
- [ ] Rollback khi có lỗi.
- [ ] Kiểm tra kết nối database khi khởi động.
- [ ] Không để router tự tạo session hoặc truy vấn SQL.
- [ ] Thiết lập convention đặt tên constraint và index.

```text
FastAPI Router
→ Application Service
→ Repository
→ AsyncSession
→ PostgreSQL
```

### Quy tắc transaction

- Application service xác định ranh giới transaction.
- Repository không tự ý `commit`.
- Một use case dùng chung một database session.
- Chỉ `commit` sau khi toàn bộ use case thành công.
- Có exception thì `rollback`.

## 1.4. Alembic migration

- [ ] Khởi tạo Alembic.
- [ ] Kết nối SQLAlchemy metadata.
- [ ] Lấy database URL từ configuration.
- [ ] Tạo migration đầu tiên.
- [ ] Kiểm tra upgrade và downgrade ở local.
- [ ] Quy định cách đặt tên migration.
- [ ] Không sửa migration đã chạy ở môi trường dùng chung.

```bash
uv run alembic revision --autogenerate -m "create initial schema"
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic current
uv run alembic history
```

## 1.5. API response và error handling

- [ ] Tạo base business exception.
- [ ] Tạo global exception handler.
- [ ] Chuẩn hóa lỗi validation của FastAPI/Pydantic.
- [ ] Không trả stack trace cho client.
- [ ] Sinh `request_id`.
- [ ] Phân biệt validation, authentication, authorization và business error.
- [ ] Dùng mã lỗi ổn định để frontend xử lý.

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email hoặc mật khẩu không chính xác.",
    "details": [],
    "trace_id": "01JXYZ..."
  }
}
```

| Trường hợp | HTTP status |
|---|---:|
| Request không hợp lệ | `400` |
| Validation thất bại | `422` |
| Chưa đăng nhập hoặc token sai | `401` |
| Không đủ quyền | `403` |
| Không tìm thấy | `404` |
| Xung đột dữ liệu | `409` |
| Rate limit | `429` |
| Lỗi hệ thống | `500` |

## 1.6. Logging và request tracing

- [ ] Cấu hình structured logging.
- [ ] Gắn `request_id` cho mỗi HTTP request.
- [ ] Log method, path, status code và duration.
- [ ] Log exception tại một điểm thống nhất.
- [ ] Che password, token và dữ liệu nhạy cảm.
- [ ] Dùng JSON log ở production.
- [ ] Dùng log dễ đọc ở development.

Không được log password, access token, refresh token, JWT secret, Authorization header đầy đủ, database password hoặc dữ liệu import nhạy cảm.

## 1.7. Docker Compose

- [ ] Viết `Dockerfile` cho FastAPI.
- [ ] Tạo PostgreSQL container.
- [ ] Tạo Redis container.
- [ ] Thêm healthcheck.
- [ ] Tạo PostgreSQL volume.
- [ ] Không chạy container bằng root nếu không cần.
- [ ] Chạy migration trước khi nhận request.
- [ ] Khởi động toàn bộ hệ thống bằng một lệnh.

```text
postgres healthy
→ redis healthy
→ alembic upgrade head
→ FastAPI start
→ backend healthcheck
```

MinIO và Celery sẽ được thêm ở giai đoạn Data Import.

## 1.8. Testing foundation

- [ ] Cấu hình `pytest` và `pytest-asyncio`.
- [ ] Tạo FastAPI test client.
- [ ] Tách database test.
- [ ] Tạo database session fixture.
- [ ] Dọn hoặc rollback dữ liệu sau mỗi test.
- [ ] Test health endpoint.
- [ ] Test exception handler.
- [ ] Test configuration.
- [ ] Thiết lập coverage.

Test tối thiểu:

```text
GET /health → 200 OK
Database lỗi → readiness báo lỗi
Request sai → đúng error format
Business exception → đúng HTTP status
```

## 1.9. Code quality và CI

- [ ] Cấu hình Ruff lint và formatter.
- [ ] Cấu hình mypy.
- [ ] Quy định import sorting và line length.
- [ ] Có thể thêm `pre-commit`.
- [ ] CI chạy lint, type-check và test.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

### Definition of Done — Giai đoạn 1

- [ ] Backend chạy bằng Docker Compose.
- [ ] `/health` trả `200 OK`.
- [ ] Kết nối PostgreSQL thành công.
- [ ] Alembic upgrade schema thành công.
- [ ] Không hard-code secret.
- [ ] Error response thống nhất.
- [ ] Mỗi request có `request_id`.
- [ ] Log không lộ password hoặc token.
- [ ] Test chạy thành công.
- [ ] Ruff và mypy không có lỗi nghiêm trọng.
- [ ] README có hướng dẫn chạy local.

---

# Giai đoạn 2 — Identity, Authentication và RBAC

## 2.1. Phạm vi Identity MVP

### Vai trò

```text
ADMIN
ANALYST
```

### Trạng thái người dùng

```text
ACTIVE
DISABLED
LOCKED
```

MVP có thể bắt đầu với `ACTIVE` và `DISABLED`.

### Chức năng

- [ ] ADMIN tạo người dùng.
- [ ] Đăng nhập bằng email/password.
- [ ] Cấp Access Token và Refresh Token.
- [ ] Refresh-token rotation.
- [ ] Đăng xuất một phiên hoặc tất cả phiên.
- [ ] Xem tài khoản hiện tại.
- [ ] Phân quyền ADMIN/ANALYST.
- [ ] Vô hiệu hóa tài khoản.
- [ ] Audit các hành động bảo mật quan trọng.

## 2.2. Thiết kế database — RBAC 4 bảng

### Schema tổng quan

```text
roles ──< role_permissions >── permissions
                 ↑
                 │
users ──── role_id (column trong users)
```

Mỗi user chỉ có 1 role. Roles có nhiều permissions.

### `users`

| Cột | Kiểu gợi ý | Ghi chú |
|---|---|---|
| `id` | UUID | Primary key |
| `email` | VARCHAR | Unique, lowercase |
| `password_hash` | VARCHAR | Không lưu password thuần |
| `full_name` | VARCHAR | Tên hiển thị |
| `status` | VARCHAR/ENUM | ACTIVE, DISABLED, LOCKED |
| `role_id` | UUID | FK → roles.id |
| `failed_login_count` | INTEGER | Số lần đăng nhập sai |
| `locked_until` | TIMESTAMP | Khóa tạm thời |
| `last_login_at` | TIMESTAMP | Lần đăng nhập gần nhất |
| `created_at` | TIMESTAMP | Thời gian tạo |
| `updated_at` | TIMESTAMP | Thời gian cập nhật |

### `roles`

| Cột | Kiểu gợi ý |
|---|---|
| `id` | UUID |
| `code` | VARCHAR, unique |
| `name` | VARCHAR |
| `description` | VARCHAR |
| `created_at` | TIMESTAMP |

### `permissions`

| Cột | Kiểu gợi ý |
|---|---|
| `id` | UUID |
| `code` | VARCHAR, unique |
| `resource` | VARCHAR |
| `action` | VARCHAR |
| `description` | VARCHAR |
| `created_at` | TIMESTAMP |

### `role_permissions`

| Cột | Kiểu gợi ý |
|---|---|
| `role_id` | UUID, foreign key |
| `permission_id` | UUID, foreign key |

Primary key: `(role_id, permission_id)`

### `refresh_sessions`

| Cột | Kiểu gợi ý | Ghi chú |
|---|---|---|
| `id` | UUID | Session ID |
| `user_id` | UUID | Chủ phiên |
| `token_family_id` | UUID | Chuỗi rotation |
| `token_hash` | VARCHAR | Chỉ lưu hash |
| `expires_at` | TIMESTAMP | Hết hạn |
| `revoked_at` | TIMESTAMP | Thu hồi |
| `replaced_by_id` | UUID | Token thay thế |
| `user_agent` | VARCHAR | Metadata thiết bị |
| `ip_address` | VARCHAR | Cân nhắc riêng tư |
| `created_at` | TIMESTAMP | Thời gian tạo |
| `last_used_at` | TIMESTAMP | Lần dùng gần nhất |

### `audit_logs`

| Cột | Kiểu gợi ý |
|---|---|
| `id` | UUID |
| `actor_user_id` | UUID, nullable |
| `action` | VARCHAR |
| `resource_type` | VARCHAR |
| `resource_id` | VARCHAR, nullable |
| `result` | VARCHAR |
| `ip_address` | VARCHAR, nullable |
| `request_id` | VARCHAR |
| `metadata` | JSONB |
| `created_at` | TIMESTAMP |

## 2.3. Cấu trúc module Identity

```text
identity/
├── domain/
│   ├── entities.py
│   ├── enums.py
│   ├── exceptions.py
│   ├── repositories.py
│   └── services.py
├── application/
│   ├── commands.py
│   ├── queries.py
│   ├── schemas.py
│   ├── register_user.py
│   ├── authenticate_user.py
│   ├── refresh_access_token.py
│   ├── logout_user.py
│   └── manage_user.py
├── infrastructure/
│   ├── sqlalchemy_models.py
│   ├── repositories.py
│   ├── password_hasher.py
│   ├── jwt_service.py
│   └── refresh_session_repository.py
└── presentation/
    ├── router.py
    ├── dependencies.py
    └── schemas.py
```

```text
presentation → application → domain
infrastructure → implements domain ports
```

Domain không import FastAPI, SQLAlchemy, Pydantic hoặc Redis client.

## 2.4. Password security

- [ ] Hash password bằng Argon2id.
- [ ] Không tự viết thuật toán hash.
- [ ] Không dùng mã hóa có thể giải mã.
- [ ] Không log password.
- [ ] Tối thiểu 8–12 ký tự và cho phép password dài.
- [ ] Dùng thông báo đăng nhập sai chung.
- [ ] Giới hạn số lần đăng nhập thất bại.
- [ ] Hỗ trợ rehash khi cấu hình thay đổi.

```bash
uv add pwdlib argon2-cffi
```

Không tiết lộ email có tồn tại:

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email hoặc mật khẩu không chính xác."
  }
}
```

## 2.5. JWT Access Token

```json
{
  "sub": "user-uuid",
  "jti": "token-uuid",
  "type": "access",
  "roles": ["ADMIN"],
  "iat": 1785300000,
  "exp": 1785300900,
  "iss": "customer-analytics-api",
  "aud": "customer-analytics-web"
}
```

- [ ] Tạo JWT service.
- [ ] Kiểm tra signature, `exp`, `iss`, `aud` và `type`.
- [ ] Kiểm tra tài khoản còn hoạt động.
- [ ] Tạo dependency lấy current user.
- [ ] Chỉ chấp nhận thuật toán đã cấu hình.

```text
Access Token: 15 phút
Refresh Token: 7 ngày
```

MVP có thể dùng `HS256`; cân nhắc `RS256` hoặc `EdDSA` nếu nhiều hệ thống cùng xác minh token.

## 2.6. Refresh-token rotation

```text
Client gửi R1
→ API kiểm tra hash của R1
→ Thu hồi R1
→ Tạo R2 trong cùng transaction
→ Trả Access Token mới và R2
```

- [ ] Refresh token là chuỗi ngẫu nhiên an toàn.
- [ ] Chỉ lưu hash.
- [ ] Mỗi lần refresh thu hồi token cũ.
- [ ] Liên kết token cũ và mới.
- [ ] Rotation phải atomic.
- [ ] Phát hiện token reuse.
- [ ] Nếu reuse, thu hồi toàn bộ token family.

```text
R1 đã tạo R2
→ R1 bị dùng lại
→ Phát hiện R1 đã revoked
→ Thu hồi toàn bộ token family
→ Yêu cầu đăng nhập lại
```

Đây là phần bảo mật trọng tâm. Không dùng refresh JWT sống dài ngày mà không có cơ chế lưu trạng thái và thu hồi.

## 2.7. Authentication API

```http
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
POST /api/v1/auth/logout-all
GET  /api/v1/auth/me
POST /api/v1/admin/users
```

```json
{
  "email": "admin@example.com",
  "password": "StrongPassword123!"
}
```

```json
{
  "token_type": "Bearer",
  "access_token": "<access-token>",
  "expires_in": 900,
  "refresh_token": "<refresh-token>",
  "user": {
    "id": "user-uuid",
    "email": "admin@example.com",
    "full_name": "System Admin",
    "roles": ["ADMIN"]
  }
}
```

Với Next.js:

```text
Access Token: giữ ngắn hạn trong memory
Refresh Token: Secure + HttpOnly + SameSite cookie
```

Tránh lưu refresh token trong `localStorage` vì rủi ro XSS.

## 2.8. RBAC

| Chức năng | ADMIN | ANALYST |
|---|:---:|:---:|
| Xem hồ sơ | ✅ | ✅ |
| Xem dashboard/khách hàng | ✅ | ✅ |
| Chạy segmentation/prediction | ✅ | ✅ |
| Export dữ liệu | ✅ | Có thể giới hạn |
| Upload dữ liệu | ✅ | Có thể cho phép |
| Quản lý user và role | ✅ | ❌ |
| Quản lý recommendation rule | ✅ | ❌ |
| Kích hoạt model | ✅ | ❌ |

- [ ] Tạo `get_current_user`.
- [ ] Tạo dependency kiểm tra role.
- [ ] Trả `401` nếu chưa xác thực.
- [ ] Trả `403` nếu đã xác thực nhưng thiếu quyền.
- [ ] Kiểm tra quyền tại backend, không chỉ ẩn nút frontend.
- [ ] Audit hành động quản trị.

## 2.9. User management

```http
POST  /api/v1/admin/users
GET   /api/v1/admin/users
GET   /api/v1/admin/users/{id}
PATCH /api/v1/admin/users/{id}
PUT   /api/v1/admin/users/{id}/roles
POST  /api/v1/admin/users/{id}/disable
POST  /api/v1/admin/users/{id}/enable
```

- [ ] Email unique, không phân biệt hoa/thường.
- [ ] ADMIN gán role, bật/tắt tài khoản.
- [ ] Không cho ADMIN cuối cùng tự disable hoặc bị xóa.
- [ ] Disable user phải revoke các refresh session.
- [ ] Danh sách user có pagination, search và filter.

## 2.10. Audit log

```text
AUTH_LOGIN_SUCCEEDED
AUTH_LOGIN_FAILED
AUTH_TOKEN_REFRESHED
AUTH_REFRESH_TOKEN_REUSED
AUTH_LOGOUT
AUTH_LOGOUT_ALL
USER_CREATED
USER_UPDATED
USER_DISABLED
USER_ENABLED
USER_ROLE_CHANGED
```

- [ ] Lưu actor, action, resource, result và `request_id`.
- [ ] Không lưu password hoặc token.
- [ ] User thường không được sửa audit log.
- [ ] Xác định rõ audit có cần atomic với nghiệp vụ hay không.

## 2.11. Seed tài khoản quản trị

- [ ] Seed role `ADMIN` và `ANALYST`.
- [ ] Tạo ADMIN đầu tiên bằng script hoặc environment.
- [ ] Không hard-code password mặc định.
- [ ] Seed phải idempotent.
- [ ] Nếu dùng bootstrap password, bắt buộc đổi password.

```bash
uv run python -m customer_analytics.scripts.create_admin \
  --email admin@example.com
```

Nên nhập password qua prompt hoặc environment tạm thời, không ghi trực tiếp trong command để tránh shell history.

## 2.12. Kiểm thử Identity

### Unit test

- [ ] Normalize email.
- [ ] Hash/verify password.
- [ ] Từ chối password sai.
- [ ] Từ chối token hết hạn, sai issuer/audience/signature.
- [ ] Hash refresh token trước khi lưu.
- [ ] User disabled không đăng nhập được.
- [ ] User thiếu role không gọi được API ADMIN.

### Integration test

- [ ] Tạo user và role trong PostgreSQL.
- [ ] Database từ chối email trùng.
- [ ] Login cập nhật `last_login_at`.
- [ ] Rotation thu hồi token cũ.
- [ ] Logout thu hồi đúng session.
- [ ] Logout-all thu hồi toàn bộ session.
- [ ] Disable user thu hồi session.
- [ ] Token reuse thu hồi toàn bộ family.

### API/E2E test

```text
Tạo ADMIN
→ Đăng nhập
→ Gọi /auth/me
→ Tạo ANALYST
→ ANALYST đăng nhập
→ ANALYST gọi API ADMIN
→ Nhận 403
→ Refresh token
→ Token cũ không dùng lại được
→ Logout
→ Refresh token không còn hợp lệ
```

| Trường hợp | Kết quả |
|---|---|
| Đăng nhập đúng | `200` |
| Sai email/password | `401` |
| User bị disable | `401` hoặc `403` theo convention |
| Thiếu/hết hạn/sai Access Token | `401` |
| ANALYST gọi API ADMIN | `403` |
| Refresh token hợp lệ | Cấp cặp token mới |
| Dùng lại refresh token cũ | Thu hồi token family |
| Logout rồi refresh | `401` |
| Email tạo mới bị trùng | `409` |

---

# Thứ tự triển khai

## Sprint 1 — Foundation

- [ ] Project structure và configuration.
- [ ] FastAPI application.
- [ ] PostgreSQL + SQLAlchemy async.
- [ ] Alembic.
- [ ] Error handling.
- [ ] Logging và request ID.
- [ ] Docker Compose.
- [ ] Pytest, Ruff và mypy.
- [ ] CI cơ bản.

## Sprint 2 — Identity Core

- [ ] User, role, permission, role_permission, refresh-session schema (4-table RBAC).
- [ ] Migration.
- [ ] Password hashing (Argon2id).
- [ ] Login và Access Token.
- [ ] Current user và RBAC permission check.
- [ ] Refresh-token rotation.
- [ ] Logout và logout-all.

## Sprint 3 — Identity Management

- [ ] ADMIN user management.
- [ ] Disable/enable tài khoản.
- [ ] Audit log.
- [ ] Brute-force protection cơ bản.
- [ ] Test đầy đủ.
- [ ] Cập nhật OpenAPI và README.

---

# Definition of Done — Giai đoạn 2

- [ ] Roles, permissions tồn tại trong database.
- [ ] ADMIN và ANALYST tồn tại trong database.
- [ ] ADMIN quản lý được user.
- [ ] Người dùng đăng nhập được.
- [ ] Password chỉ lưu dưới dạng Argon2 hash.
- [ ] Access Token TTL ngắn và được validate đầy đủ.
- [ ] Refresh Token rotation sau mỗi lần dùng.
- [ ] Database chỉ lưu hash của Refresh Token.
- [ ] Phát hiện được Refresh Token reuse.
- [ ] Logout và logout-all revoke đúng session.
- [ ] User disabled không thể tiếp tục dùng hệ thống.
- [ ] API phân biệt đúng `401` và `403`.
- [ ] Hành động quản trị có audit log.
- [ ] Không log password hoặc token.
- [ ] Unit, integration và API test đều pass.
- [ ] OpenAPI mô tả đầy đủ authentication API.
- [ ] Docker Compose khởi động toàn bộ hệ thống.

---

# Kết quả cuối giai đoạn 1–2

```text
FastAPI foundation ổn định
→ PostgreSQL có migration
→ Logging và error response thống nhất
→ Có automated test
→ Có ADMIN và ANALYST
→ Login an toàn
→ JWT Access Token
→ Refresh-token rotation
→ RBAC
→ Logout/revoke
→ Audit log
```

Sau đó chuyển sang **Giai đoạn 3 — Data Import**:

```text
Upload CSV/XLSX
→ Lưu file
→ Validate schema
→ Tạo background job
→ Làm sạch theo batch
→ Chống trùng
→ Lưu dữ liệu và import errors
```
