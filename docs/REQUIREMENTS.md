# Yêu cầu và bằng chứng

| Yêu cầu | Nguồn triển khai/kiểm chứng | Trạng thái |
|---|---|---|
| C11/OpenMP, Windows | Makefile, openmp_probe.c, ENVIRONMENT | Khung + khảo sát |
| API thống nhất, n tường minh | CONTRACT, include/*.h | Chốt v1 |
| CLI rõ lỗi module | src/main.c, tests/test_cli.py | Scaffold |
| Timing/JSONL không bịa | CONTRACT, EXPERIMENT_PROTOCOL | Chỉ contract |
| Sáu chương tiếng Việt | report/main.tex, chapters | Khung |
| Workflow ba vai trò/review | CONTRIBUTING, DELIVERY_PLAN | Tài liệu |
| Thuật toán/hiệu năng | Chưa có | Ngoài bootstrap |

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
