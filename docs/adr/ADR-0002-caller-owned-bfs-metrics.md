# ADR-0002 — Metrics do caller sở hữu trong API v1 bootstrap

Trạng thái: Chọn theo ủy quyền sửa bootstrap ngày 05/11/2026; chờ re-review PR #1.
Decision owner: chủ dự án; không phải approval của reviewer.

## Bối cảnh và lựa chọn
JSONL cần threads_actual nhưng API cũ chỉ trả status/distance. Chưa có module BFS
hoặc caller link thật nên sửa chữ ký ngay ít rủi ro hơn giữ một API thiếu dữ liệu.
Đã cân nhắc global mutable (loại vì race/ownership), callback instrumentation
(phức tạp, làm khó timing) và BFSMetrics output tường minh (chọn).

## Quyết định
Cả ba hàm nhận thêm `BFSMetrics *metrics` bắt buộc ở cuối, vẫn trả BFSStatus.
BFSMetrics có `int threads_actual`. Header và CONTRACT là nguồn chữ ký chuẩn.
Caller cấp phát một metrics riêng không alias cho mỗi lời gọi; không cấp phát hay
free metrics trong BFS. Khi có con trỏ, đặt trường về 0 ngay cả khi validation lỗi;
chỉ công bố >=1 sau thành công. NULL trả BFS_ERR_ARGUMENT.
Serial báo 1. Parallel đo omp_get_num_threads() từ single bên trong từng team
xử lý BFS, với đồng bộ; mọi team trong lời gọi phải bằng nhau, nếu khác trả
BFS_ERR_RUNTIME và metrics=0. Đường chạy không mở team vì không có việc báo 1.
Không dùng max threads, probe ngoài BFS hay global. Không cộng dồn hoặc lấy max
nhiều team khác nhau thành một threads_actual gây hiểu sai efficiency.

Caller đo omp_get_wtime trước/sau BFS; initialization distance/scratch và ghi
metrics thuộc lời gọi BFS được tính, I/O/validation/serialization ở ngoài.
CLI chỉ xuất JSONL khi BFS_OK và metrics hợp lệ. Schema JSONL vẫn version=1.

## Tương thích và hệ quả
Đây là thay đổi source API có chủ đích trong v1 chưa phát hành, không ABI-compatible
với chữ ký bốn tham số ở 389282d. Không có implementation/consumer cần wrapper;
CLI scaffold chưa gọi BFS. A, B, C phải dùng chữ ký năm tham số mới. Không giữ
hai chữ ký cùng tên hoặc âm thầm suy metrics. Test compile-only xác nhận ba
function pointer cùng kiểu mà không triển khai/link thuật toán.

## Kiểm chứng và điều kiện xem lại
Header C11 và CONTRACT đối chiếu trong scaffold check, compile-only test trong CI.
Sau bootstrap, A kiểm tra serial=1, B kiểm tra team thực và reset-on-error,
C kiểm tra JSONL/timing và từ chối lỗi. Chưa có runtime test metrics vì BFS chưa có.
Nếu cần nhiều team khác cỡ hoặc nested parallelism, đề xuất ADR/schema mới trước
triển khai; API v1 hiện không hỗ trợ gọi từ parallel region bên ngoài.
