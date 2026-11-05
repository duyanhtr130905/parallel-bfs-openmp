# Kế hoạch 14 ngày — chưa triển khai công việc thành viên

| Ngày | Việc/owner | Điều kiện ra |
|---|---|---|
| 1 | Lead: bootstrap/API/CI/report | Independent re-review, không tự merge |
| 2–4 | A CSR/parser/serial; B thiết kế parallel; C CLI/protocol/report | Oracle tay, API thống nhất |
| 5–7 | A graph/serial tests; B basic + optimized; C automation | So mọi distance với oracle/serial |
| 8–9 | B stress/synchronization; A review; C CLI integration | A → B → C, correctness |
| 10–11 | C benchmark/raw/manifest; A/B hỗ trợ | Actual team, provenance |
| 12–13 | C PDF/figures; A lý thuyết; B thiết kế song song | Tái tạo biểu đồ, xem PDF |
| 14 | Cả nhóm diễn tập/đóng gói | Demo và giới hạn có bằng chứng |

Lead giữ contract, review khác tác giả. Deadline không bỏ gate.

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
