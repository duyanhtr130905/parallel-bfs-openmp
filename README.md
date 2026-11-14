# Parallel BFS Using OpenMP

Bộ bàn giao cuối: [nghiệm thu 14/11/2026](docs/FINAL_HANDOFF_20261114.md),
[hướng dẫn biên dịch/chạy ba thuật toán/tái lập/nộp](docs/SUBMISSION_README.md).

C11/OpenMP CPU, cùng CSR loader cho Serial, Basic và Optimized. A/B đã merge;
CLI tích hợp đang ở **PR #7**, nhánh `docs/c1-academic-report`.
**Đã thực nghiệm thật** trên laptop Windows: 6 đồ thị/9 tổ hợp nguồn,225 cấu hình,
225 warm-up và2250 mẫu chính thức, không lỗi/timeout. Commit đo ab588fb sau
correctness local và CI3/3 PASS. Không cấu hình OpenMP nào nhanh hơn Serial;
max speedup0,2914 ở Optimized1/static/grid512. Không dùng timing CI làm số đo.
[Dữ liệu và tái lập](results/experiment-20261112/README.md),
[hồ sơ nghiệm thu mới](docs/EXPERIMENT_20261112_RESULTS.md),
[ma trận trước đo](docs/experiment-20261112-matrix.json).

Đọc [hồ sơ nghiệm thu](docs/ROLE_C_ACCEPTANCE.md), [trạng thái](docs/PROJECT_STATUS.md),
[API v1](docs/CONTRACT.md) và [protocol](docs/EXPERIMENT_PROTOCOL.md).

## Build và test

Cần GCC + libgomp, GNU Make và Python3. Windows dùng MSYS2 UCRT64 đã cài đủ
`mingw-w64-ucrt-x86_64-{gcc,libgomp,python,make}`; không tự cài hoặc đổi PATH hệ thống.

```sh
# Linux; Windows UCRT64 dùng mingw32-make và PYTHON=python
make CC=gcc PYTHON=python3 build test check-openmp
make CC=gcc PYTHON=python3 test-bfs test-parallel test-integration test-cli-failures
./build/bfs --graph datasets/small/disconnected.edgelist --vertices 6 --source 0 --algo omp-opt --threads 4 --schedule guided --directed
```

Lệnh CLI thành công xuất một JSONL schema v1; thời gian chỉ gồm lời gọi BFS,
actual team lấy từ metrics. Error diagnostics ở stderr; không xuất result sai.
Test tools không phải benchmark; fixtures synthetic không dùng làm số liệu báo cáo.
`make test-plots` cần matplotlib, chạy riêng trên Linux CI bằng môi trường tạm.
`make clean` chỉ xóa known outputs, giữ PDF/datasets/results.

## Báo cáo và thực nghiệm

`make report`: XeLaTeX → BibTeX → XeLaTeX hai lần, output `report/main.pdf`.
CI lưu PDF artifact theo SHA để tải và xem. Sáu chương và abstract đã điền số
thật,9 bảng cấu hình chi tiết và12 biểu đồ từ raw (36 figures được lưu để tái tạo).
GCC/libgomp16.2.0, Make4.4.1, Python3.14.10 tại C:/tools/msys64. Windows dùng QPC
theo ADR-0003; Linux giữ omp_get_wtime. PDF cần được kiểm theo final PR HEAD.

Raw/hash/backup/lệnh tái lập ở [results README](results/experiment-20261112/README.md).
Runner cần working tree sạch, correctness log/binary hash đúng SHA và môi trường
đã xác minh. Không overwrite session cũ. Fresh process/team startup được tính,
warm-up không tạo warmed team; không suy rộng kết quả sang mọi đồ thị/runtime.

## Quy trình Git

Canonical https://github.com/duyanhtr130905/parallel-bfs-openmp .
Giữ feature branch và PR #7; không force push, direct push main, tự approve,
merge #7 hoặc đóng Issue #5 khi benchmark/report chưa đạt. AGENTS.md là quy trình
chung; hồ sơ bootstrap cũ trong docs là lịch sử, không phải trạng thái hiện tại.

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
CLI/benchmark/report. Trạng thái triển khai và bằng chứng hiện hành xem hồ sơ nghiệm thu.
