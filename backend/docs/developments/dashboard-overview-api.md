# Tổng quan khách hàng và hợp đồng Dashboard Overview API

Trang `/dashboard` hiện dùng dữ liệu giả để duyệt giao diện; backend đã triển khai hợp đồng live tương ứng tại `/api/v1/analytics/dashboard/overview`. UI demo tiếp tục nhận diện fixture bằng `meta.source: mock`; API backend trả `meta.source: live` và không dùng fixture.

Nguồn nghiệp vụ: SRS “Hệ thống phân tích dữ liệu khách hàng và dự đoán tiềm năng mua hàng” được cung cấp ngày 14/09/2026; các màn khách hàng, sản phẩm, giao dịch, phân khúc, dự đoán, ưu tiên, mô hình và import trong FE; các kiểu API trong `frontend/src/api/analytics.ts`. Checkout backend được khảo sát hiện có module identity; không dùng mô tả trong README để suy diễn rằng các endpoint analytics mới đã được triển khai.

## Biểu đồ và câu hỏi nghiệp vụ

| Thành phần | Câu hỏi được trả lời | Biểu diễn và lý do | Yêu cầu SRS |
| --- | --- | --- | --- |
| Bốn KPI | Có bao nhiêu khách hàng, đơn hợp lệ, doanh thu và AOV? | Số tổng hợp và phần trăm thay đổi; không dùng gauge vì chưa có mục tiêu kinh doanh được chốt | FUNC-02-01, 02-05, 06-01 |
| Xu hướng kinh doanh | Doanh thu/đơn hàng tăng hay giảm theo ngày? | Area/line, đường kỳ trước nét đứt; chuyển tab giữa tiền và số đơn để tránh trộn đơn vị trên một trục | FUNC-02-03, 02-04, 02-08 |
| Phân bố khách hàng | Quy mô từng phân khúc chính? | Donut kèm số lượng và tỷ trọng trong chú giải; mỗi khách hàng được đếm đúng một lần | FUNC-03-01 |
| Điểm tiềm năng | Điểm tập trung ở khoảng nào? Có bao nhiêu khách hàng điểm cao? | Histogram theo các khoảng 20 điểm, kèm số khách hàng thiếu dữ liệu riêng | FUNC-04-01, AN-01–04 |
| Nhóm sản phẩm nổi bật | Nhóm nào đóng góp doanh thu lớn nhất? | Cột ngang giảm dần, phù hợp tên danh mục dài | FUNC-02-07, MOD-05 |
| Xác suất mua hàng | Mô hình dự đoán xác suất mua phân bố thế nào? | Histogram tỷ lệ phần trăm riêng với Potential Score; luôn kèm horizon, phiên bản và ngày dự đoán | ML-04–06 |
| Ma trận cơ hội khách hàng | Khách hàng nào đồng thời có điểm tiềm năng và xác suất mua cao, đồng thời đã tạo doanh thu đáng kể? | Bubble/scatter: trục X là xác suất mua, trục Y là Potential Score, kích thước là doanh thu trong kỳ và màu là phân khúc. Hai chỉ số vẫn được ghi nhãn độc lập | FUNC-04-01, ML-04, MOD-06 |
| Khách hàng tiềm năng cao | Nên xem xét chăm sóc ai trước? | Bảng top 10 điểm cao, cột điểm và xác suất độc lập, doanh thu trong kỳ và người phụ trách | MOD-04, MOD-06 |
| Chất lượng/truy vết | Có dữ liệu nào bị loại hoặc chưa thể phân tích? | Số đơn bị loại, khách hàng chưa đủ dữ liệu, nguồn tương tác và metadata lần chạy | DR-DQ, DR-HIS, CON-03 |

Biểu đồ sản phẩm trên trang này thể hiện **doanh thu**, chưa đại diện cho thuật toán xếp hạng sở thích tổng hợp từ tần suất, số lượng, giá trị và lần mua gần nhất của MOD-05. Phân khúc hành vi cũng là một trục khác với mức Potential Score, dù cả hai có nhãn “Tiềm năng”.

Các phần nghiệp vụ còn lại nằm ở màn chuyên biệt: import và lỗi từng dòng ở Nhập dữ liệu; RFM/AOV/chu kỳ mua/lịch sử ở hồ sơ phân tích; PR-AUC, Precision, Recall, F1 và lịch sử phiên bản ở Quản lý mô hình; tài khoản/quyền/cấu hình ở Quản trị. Dashboard không thay thế các màn này. Có thể bổ sung scatter Frequency–Monetary hoặc heatmap retention khi có dữ liệu và mục tiêu phân tích phù hợp. SRS hiện mô tả xác suất mua, chưa chốt mô hình dự báo giá trị mua/doanh thu tương lai dù README đề cập “purchase value”; vì vậy demo không tạo biểu đồ dự báo tiền.

## Tổ chức FE

- Route: `frontend/src/pages/admin/dashboard.tsx`.
- UI: `frontend/src/features/dashboard/`.
- Kiểu response: `frontend/src/types/dashboard.ts` là hợp đồng đầy đủ có kiểm tra TypeScript.
- Adapter: `frontend/src/api/dashboard.ts` → `frontend/src/mocks/dashboard.ts`.
- Query/cache/bộ lọc URL: `frontend/src/hooks/use-dashboard.ts`.
- Chart: shadcn `ChartContainer`, `ChartTooltipContent`, Recharts **3.8.0**.
- Palette chart do người dùng chọn: `#689d4b`, `#576a8f`, `#91ae6e`, `#d96868`, `#a6b1e1`, qua token `--chart-1` đến `--chart-5` ở cả light/dark. Nhóm nguy cơ rời bỏ dùng màu đỏ `--chart-4`.
- Bộ chọn dùng `AppSelect`; bảng dùng `CommonTable` đã chuẩn hóa.
- File `docs/dashboard-overview.example.json` là response mẫu đầy đủ cho bộ lọc mặc định, sinh từ cùng mock mà UI sử dụng.

Mock có 240 khách hàng, đơn hàng xác định trước bằng công thức cố định, năm danh mục và bốn nhân viên giả. Không dùng `Math.random`, không ghi dữ liệu thật. Ngày chốt demo là **19/09/2026**. Phân khúc, điểm và xác suất là fixture minh họa, không phải kết quả thuật toán thực hay huấn luyện ML. Chỉ phần tổng hợp/lọc và kiểm tra tính nhất quán được thực hiện trong mock. Khách hàng không có đơn hợp lệ trước ngày chốt không được gán điểm/xác suất.

## Endpoint tổng quan đã triển khai

`GET /api/v1/analytics/dashboard/overview`

Giữ endpoint cũ `/analytics/dashboard` cho các client đang dùng hợp đồng cũ. Endpoint mới trả object trực tiếp, theo cùng quy ước hiện dùng ở các typed client FE.

Quyền đọc: `analytics:read`. BE phải tự áp dụng phạm vi dữ liệu theo người đăng nhập: Admin toàn bộ, Quản lý theo team, Phân tích viên theo phạm vi cấp, Kinh doanh/CSKH theo khách được phân công. `employee` chỉ thu hẹp phạm vi đã được cấp, không cấp thêm quyền. Tài khoản khách hàng `USER/CLIENT` không được gọi API này.

| Query | Kiểu và giá trị | Ý nghĩa |
| --- | --- | --- |
| `period` | `30d`, `90d`, `6m`, `12m`, `custom`; mặc định `90d` | Preset thời gian. Khi không custom, BE xác định khoảng theo ngày chốt thực tế |
| `from`, `to` | `YYYY-MM-DD`; bắt buộc khi custom | Hai đầu bao gồm cả ngày. Giới hạn demo tối đa 366 ngày; BE cần chốt giới hạn tương đương |
| `segment` | `all`, `HIGH_VALUE`, `LOYAL`, `AT_RISK`, `POTENTIAL`, `NEW_CUSTOMER`, `NORMAL`, `INSUFFICIENT_DATA` | Một phân khúc chính tại snapshot đánh giá |
| `potential` | `all`, `HIGH`, `POTENTIAL`, `NORMAL`, `INSUFFICIENT_DATA` | Mức điểm theo cấu hình, không phải ngưỡng xác suất ML |
| `category` | `all` hoặc ID danh mục | Lọc sản phẩm mua trong kỳ; ID thực lấy từ endpoint options |
| `employee` | `all` hoặc ID nhân viên | Lọc nhân viên phụ trách trong phạm vi được phép |
| `opportunity_page`, `opportunity_page_size` | Số nguyên; mặc định `1`, `80`; page size tối đa `100` | Phân trang `opportunity_customers`, sắp theo `potential_score * purchase_probability` giảm dần |
| `priority_page`, `priority_page_size` | Số nguyên; mặc định `1`, `10`; page size tối đa `100` | Phân trang `priority_customers`, sắp theo Potential Score giảm dần |

Ví dụ: `?period=90d&segment=all&potential=HIGH&category=phone&employee=nv-01`.

`from`/`to` trong state FE mặc định vẫn tồn tại khi đổi preset; BE **bỏ qua hai field này nếu period không phải custom**, tránh dùng nhầm ngày của lần chọn cũ. Các ID `phone`, `nv-01` chỉ là ID demo, không phải mã bắt buộc cho dữ liệu thật.

## Nội dung response

| Field | Nội dung và đơn vị |
| --- | --- |
| `meta` | `source: live`, `generated_at`, `analysis_date`, `run_id`, `config_version`, `currency: VND`, `timezone: Asia/Ho_Chi_Minh` |
| `period` | `from`, `to`, `previous_from`, `previous_to`; so sánh hai kỳ liên tiếp có cùng số ngày |
| `filters` | Bộ lọc đã áp dụng, dùng để truy vết |
| `metrics` | `customers`, `orders`, `revenue`, `aov`; mỗi metric có `current`, `previous`, `change_percent` |
| `trend[]` | Một bản ghi mỗi ngày, kể cả ngày không có đơn: `date`, `previous_date`, `revenue`, `previous_revenue`, `orders`, `previous_orders` |
| `segments[]` | `key`, `label`, `count`; luôn trả đủ nhóm, kể cả nhóm có count 0 |
| `potential` | `distribution[]`, `high_count`, `eligible_count`, `insufficient_count`, `average_score`, `thresholds`, `weights` |
| `opportunity_customers[]` | Trang hiện tại của danh sách khách có Potential Score và kết quả ML; gồm `id`, `name`, `segment`, `potential_score`, `purchase_probability`, `revenue` |
| `priority_customers[]` | Trang hiện tại của danh sách khách hàng điểm cao; chi tiết field xem kiểu `DashboardPriorityCustomer` |
| `opportunity_pagination`, `priority_pagination` | `page`, `page_size`, `total`, `total_pages`, `has_next`, `has_previous` tương ứng từng danh sách |
| `priority_total` | Tổng số khách đạt ngưỡng cao trong phạm vi lọc, giữ tương thích với client cũ |
| `data_quality` | `valid_orders`, `excluded_orders`, `unscored_customers`, `interaction_source: real/simulated` |

Tiền trong hợp đồng này dùng **number nguyên VND**, trong giới hạn số nguyên an toàn JavaScript. Nếu BE trả Decimal dạng chuỗi, adapter cần chuyển đổi có kiểm tra. `purchase_probability` dùng **0–1**, UI nhân 100 khi trình bày. `potential_score` dùng **0–100**; hai field độc lập. Thời điểm timestamp có múi giờ; date-only được cắt theo múi giờ nghiệp vụ, không theo múi giờ trình duyệt.

Histogram có `label`, `min`, `max`, `count`: `[min, max)`, riêng khoảng cuối `[80, 100]`. Điểm nguyên được hiển thị `0–19`, `20–39`, `40–59`, `60–79`, `80–100`; histogram ML dùng phần trăm `0–20%` ... `80–100%`. Không đưa các giá trị thiếu vào cột 0.

## Quy tắc tính và những điểm cần BE thống nhất

1. Chỉ lấy đơn hợp lệ theo cấu hình; loại đơn hủy. Đếm `COUNT(DISTINCT order_id)` khi join chi tiết đơn; tránh nhân đôi doanh thu hay số đơn. Ngày không có đơn vẫn có điểm dữ liệu bằng 0 trên chuỗi thời gian.
2. AOV = doanh thu / số đơn hợp lệ; không có đơn thì AOV = 0. `(current - previous) / previous * 100`; nếu previous = 0 thì `change_percent = null`, không trả Infinity và không tự coi là tăng 100%.
3. KPI khách hàng là tổng khách trong tập dữ liệu được phép và phù hợp bộ lọc đến ngày chốt, **không phải số khách đã mua trong kỳ**. Nhóm chưa đủ dữ liệu vẫn nằm trong KPI và donut.
4. Demo dùng cohort khách hàng được chọn tại kỳ hiện tại cho cả kỳ đối chiếu. Khi lọc danh mục, cohort là khách có đơn hợp lệ mua danh mục đó trong kỳ hiện tại; doanh thu là giá trị dòng hàng của danh mục được lọc, số đơn là số đơn khác nhau chứa các dòng đó. Đây là đề xuất ngữ nghĩa bộ lọc cần BE thống nhất; nếu dùng hai cohort độc lập cho hai kỳ, phải đổi mock và phần mô tả so sánh tương ứng.
5. Phân khúc hành vi phải lấy snapshot một nhóm chính/khách; không đếm một khách vào nhiều nhóm. Nhóm sản phẩm ưa thích có thể nhiều; không dùng donut cho tập nhiều nhãn nếu tỷ trọng không cộng thành 100%.
6. Potential Score mặc định: Recency 35%, Frequency 30%, Monetary 20%, Interaction 15%; tổng = 1 trong response. Ngưỡng cao 80, tiềm năng 60; BE tính theo cấu hình thực tế. Không dùng Trend trong điểm Phase 1. UI đọc ngưỡng từ response để mô tả; fixture không thay thế use case chấm điểm BE.
7. ML chỉ có `available` khi đã có kết quả mô hình phù hợp; `not_deployed` khi chưa triển khai và `insufficient_data` khi không đủ đầu vào. Không dựng xác suất từ điểm tiềm năng. `feature_window` phải là khoảng input thực sự của mô hình, có thể khác kỳ lọc dashboard. Demo dùng khoảng đang xem để minh họa metadata; mô hình thật không được thay đổi window hoặc chạy lại chỉ vì người dùng đổi biểu đồ.
8. Với status khác `available`, trả `model_version/prediction_date = null` nếu chưa có metadata, `evaluated_customers = 0`, distribution rỗng. Dữ liệu lịch sử/phiên bản không bị xóa bởi lần chạy mới. Nếu snapshot cũ được dùng, response và UI phải thể hiện ngày chạy thực tế.
9. Danh sách `priority_customers` sắp theo điểm giảm dần và khóa ID ổn định khi bằng điểm; mặc định trả 10 bản ghi/trang. `priority_total` là tất cả khách đạt ngưỡng.
10. `opportunity_customers` chỉ gồm khách có cả điểm và xác suất; không suy xác suất từ điểm. Sắp theo tích `potential_score * purchase_probability`, khóa ID ổn định khi bằng nhau; mặc định trả 80 bản ghi/trang. `revenue` là doanh thu giao dịch hợp lệ trong đúng kỳ/bộ lọc dashboard.
11. `interaction_source: simulated` phải được giữ trong response/metadata để phân biệt nguồn tương tác; nhãn này được ẩn trên UI bản duyệt. SRS nhắc 480 tương tác trong dataset Phase 1; dataset đó chưa được cung cấp cho mock này. Không coi các fixture là dữ liệu sản xuất hoặc dùng huấn luyện production.

## Options và xuất báo cáo

`GET /api/v1/analytics/dashboard/options` trả danh sách phân khúc, mức tiềm năng, danh mục và nhân viên trong phạm vi người dùng, cùng các ngưỡng và trọng số hiện tại. Các danh sách option là tập filter bounded, không dùng pagination.

Nút CSV dùng endpoint `GET /api/v1/analytics/dashboard/export.csv`, nhận cùng bộ lọc overview và xuất toàn bộ chuỗi doanh thu/đơn hàng trong khoảng đã chọn. Đây là bulk export nên không dùng pagination. Endpoint yêu cầu `customers:export`, tự kiểm tra quyền và data scope trên server; ẩn nút FE không phải cơ chế phân quyền.

## Lỗi và trạng thái giao diện

- `401`: phiên hết hạn, đi qua cơ chế refresh hiện có.
- `403`: không có quyền; không tự fallback sang mock hoặc dữ liệu toàn hệ thống.
- `422`: ngày sai, `from > to`, khoảng quá dài, filter không hợp lệ; hiển thị lỗi rõ và giữ form để sửa.
- `200` với tập khách rỗng: KPI = 0, trend các ngày = 0, các phân bố count = 0, danh sách rỗng; UI hiện “Không có dữ liệu phù hợp”.
- `500`/mất mạng: thông báo lỗi an toàn và nút thử lại; không hiển thị exception thô.

## Checklist nối API và nghiệm thu

- Thống nhất các quyết định cohort, doanh thu khi lọc danh mục và ngày chốt trước khi triển khai.
- Thay adapter demo bằng typed Axios request, giữ TanStack Query và query key theo toàn bộ bộ lọc.
- Đổi adapter dữ liệu, nguồn options và giới hạn ngày theo `meta`/options API khi chuyển sang live; không trộn dữ liệu giả và thật trong một response.
- Tổng trend.revenue = metrics.revenue.current; trend.orders = metrics.orders.current; doanh thu các nhóm = tổng doanh thu trong phạm vi lọc.
- Tổng donut = metrics.customers.current; số đã chấm + thiếu dữ liệu = tổng khách; số có ML + thiếu ML = tổng khách.
- Thử 30/90 ngày, 6/12 tháng và custom; nhiều bộ lọc đồng thời; ngày không có đơn; không có kỳ trước; ML chưa có; thiếu dữ liệu; quyền hạn; mobile và dark mode.

Tham khảo UI: [shadcn Chart](https://ui.shadcn.com/docs/components/base/chart), [Recharts AreaChart](https://recharts.github.io/en-US/api/AreaChart/), [BarChart](https://recharts.github.io/en-US/api/BarChart/), [PieChart](https://recharts.github.io/en-US/api/PieChart/), [ScatterChart](https://recharts.github.io/en-US/api/ScatterChart/) và [ZAxis](https://recharts.github.io/en-US/api/ZAxis/).
