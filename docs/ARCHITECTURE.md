# Kiến trúc và ranh giới bootstrap

C11/OpenMP CPU, Windows/MSYS2 UCRT64/GCC, Python kiểm tra/phân tích, XeLaTeX
báo cáo tiếng Việt. Một CLI, CSR bất biến dùng chung, không C++/GPU/MPI.
Pipeline tương lai: CLI → loader → CSR → caller output/metrics → timer quanh BFS
→ validation → JSONL. Hiện chỉ parse/validate rồi exit 3, không graph/BFS/timing.

Ba hàm bfs_serial/bfs_parallel_basic/bfs_parallel_optimized cùng nhận
`(const CSRGraph *, uint32_t, int32_t *, const BFSConfig *, BFSMetrics *)`,
trả BFSStatus. Metrics chỉ có threads_actual, không timer/global. Serial=1;
parallel đo trong vùng xử lý; team thay đổi trả RUNTIME, lỗi metrics=0.
[CONTRACT](CONTRACT.md) và [ADR-0002](adr/ADR-0002-caller-owned-bfs-metrics.md)
quy định reset/lifetime/alias/trường hợp không mở team và thay đổi chữ ký v1.
Chưa có module BFS/graph; test chữ ký chỉ compile, không link BFS.

| Module | File dự kiến | Owner/trạng thái |
|---|---|---|
| API | include/*.h, CONTRACT | Lead quản lý |
| CSR + serial | src/graph.c, src/bfs_serial.c | A, chưa có |
| Basic + optimized | src/bfs_parallel_basic.c, src/bfs_parallel_optimized.c | B, chưa có |
| CLI | src/main.c | C, scaffold |
| Benchmark/report | scripts/, results/, report/ | C, protocol/khung |

Không sửa CSR trong BFS. Claim visited phải đồng bộ; không trộn đọc thường và
ghi atomic đồng thời. Barrier giữa các mức, overflow/frontier capacity phải được
review trong PR thuật toán. Buffer cục bộ/contention/schedule là giả thuyết cần
đo; chưa kết luận nhanh hơn, chưa thêm direction-optimizing.

## Phân công cuối cùng — chủ dự án chọn 05/11/2026

| Vai trò | Branch | Phạm vi |
|---|---|---|
| A — Graph & Sequential BFS | feat/graph-serial-bfs | CSR, edge-list parser, serial BFS, graph/oracle tests, lý thuyết BFS |
| B — Parallel BFS & Optimization | feat/parallel-bfs | Top-down basic và optimized; synchronization/atomic visited/frontier; static/dynamic/guided; correctness/stress; thiết kế song song |
| C — Benchmark & Report Integration | feat/benchmark-report | CLI, automation, protocol, raw CSV/JSONL/manifest, biểu đồ, LaTeX tiếng Việt, thực nghiệm/kết luận từ dữ liệu thật |

A cung cấp graph + serial; B phụ thuộc graph API; C phụ thuộc cả ba BFS APIs.
Cả ba có thể chuẩn bị độc lập sau bootstrap theo CONTRACT: A/B nhận tham số cuối
`BFSMetrics *metrics`, C chuẩn bị caller/timing/serialization. Tích hợp theo
A → B → C; benchmark chỉ sau correctness. B sở hữu basic lẫn optimized; C sở hữu
CLI/benchmark/report. Đây là kế hoạch, chưa giao việc hoặc tạo fork.
