# Kiến trúc và ranh giới bootstrap

Stack do người dùng xác định: C11, OpenMP CPU, Windows/MSYS2 UCRT64/GCC,
Python cho công cụ kiểm tra/phân tích; LaTeX tiếng Việt cho báo cáo.
Một chương trình CLI, một CSR dùng chung bất biến. Không dùng C++/GPU/MPI.

Luồng tương lai: CLI → đọc edge list với n tường minh → CSR → cấp phát output →
đo đúng một hàm BFS → kiểm chứng distance → xuất JSONL. Chưa nối pipeline này.
CLI hiện chỉ parse, kiểm tra đối số và trả exit 3. Không dùng fallback serial,
không điền distance giả và không phát result thành công.

| Thành phần | File dự kiến | Trạng thái/owner đề xuất |
|---|---|---|
| Shared API | include/*.h, CONTRACT.md | Đã chốt v1; lead quản lý |
| CLI | src/main.c | Scaffold đã có; pipeline chờ tích hợp |
| CSR + serial | src/graph.c, src/bfs_serial.c | Chưa có; TV1 |
| OpenMP basic | src/bfs_parallel_basic.c | Chưa có; TV2 |
| OpenMP optimized | src/bfs_parallel_optimized.c | Chưa có; TV3 |
| Test correctness | tests/ | Chỉ CLI/probe hiện có; cả nhóm bổ sung |
| Benchmark/report | scripts/, results/, report/ | Protocol/khung; chưa có số đo |

Tách CSR khỏi BFS để cùng dữ liệu được dùng cho mọi phiên bản.
Không lưu visited/parent vào CSR. Distance có thể phục vụ discovery nhưng chỉ sau
khi thiết kế đồng bộ được review: kiểm tra chưa thăm và claim phải là một thao tác
đồng bộ; không trộn đọc thường với ghi atomic trên cùng ô đang được truy cập đồng thời.
Chốt barrier giữa các mức trước khi hợp nhất frontier/chuyển mức.
Đây là yêu cầu thiết kế cho thành viên, chưa phải cài đặt thuật toán.

Các tối ưu (buffer cục bộ, giảm contention, schedule) là giả thuyết cần thực nghiệm.
Không kết luận nhanh hơn trước số đo. Không đưa tối ưu direction-optimizing hoặc
thay đổi CSR/API vào bài nếu chưa thống nhất phạm vi.
