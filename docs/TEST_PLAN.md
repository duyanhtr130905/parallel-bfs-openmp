# Kế hoạch kiểm thử

Hiện có kiểm tra cấu trúc Python, CLI thực khi build được và OpenMP toolchain probe.
Chưa có implementation/test correctness BFS. `make test-bfs` phải báo thiếu và lỗi.

Gate tiếp theo: TV1 kiểm tra parser (n tường minh/isolated, format/range/overflow,
ownership/free/error); serial đối chiếu oracle tay; TV2/TV3 đối chiếu toàn bộ distance
qua nhiều threads/schedule trên fixture và random graph seed cố định. Thêm test
không thay đổi CSR, cấp phát thất bại nếu có injection, stress diamond/high-degree.
Race cần review mô hình bộ nhớ; việc lặp test không thay cho review.
Benchmark chỉ sau correctness và độc lập với thời gian validation.
