# Phạm vi được yêu cầu

Nhóm ba sinh viên, khoảng 14 ngày, bài tập lớn Tính toán song song.
Mục tiêu cuối dự án: BFS C11 tuần tự/basic/optimized OpenMP, kiểm thử,
thực nghiệm tái lập và báo cáo tiếng Việt. Phiên hiện tại chỉ BOOTSTRAP:
khảo sát môi trường, API, CLI scaffold, build/test skeleton và report skeleton.
Không bao gồm thuật toán, benchmark thật, cài hệ thống hoặc merge.
Phiên sửa review được phép commit/push thường lên PR #1 Draft.
Done bootstrap: đủ cấu trúc, contract không mâu thuẫn, lỗi module rõ ràng,
kiểm chứng những gì môi trường hỗ trợ và ghi rõ phần chưa xác minh.

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
