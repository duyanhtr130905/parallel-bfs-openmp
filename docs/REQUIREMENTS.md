# Yêu cầu và bằng chứng

| Yêu cầu | Nguồn triển khai/kiểm chứng | Trạng thái |
|---|---|---|
| C11/OpenMP trên Linux và Windows | Makefile, tests/openmp_probe.c, GitHub Actions | Có build/test và probe |
| API thống nhất, n tường minh | CONTRACT, include/*.h | Chốt v1 |
| CLI phân biệt lỗi và kết quả | src/main.c, tests/test_cli.py, tests/test_cli_failures.py | Đã triển khai và kiểm thử |
| Đo wall-clock và kiểm chứng kết quả | scripts/benchmark_six_graphs.c, scripts/benchmark_supplement.c, results/ | Hai phiên đo có dữ liệu raw |
| Ba chương tiếng Việt | report/main.tex, report/chapters/, report/refs.bib | Có PDF bàn giao và quy trình tái tạo |
| Workflow ba vai trò/review | CONTRIBUTING, DELIVERY_PLAN | Tài liệu |
| Thuật toán/hiệu năng | src/, tests/test_integration.c, báo cáo Chương 3 | Ba hiện thực và hai phiên đo |

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
