# Parallel BFS Using OpenMP

Bài tập lớn nhóm 3 sinh viên — C11/OpenMP trên CPU, Windows/MSYS2 UCRT64.
**Trạng thái: BOOTSTRAP. Chưa có loader CSR hoặc bất kỳ thuật toán BFS nào.**
CLI chỉ kiểm tra đối số và từ chối thực thi bằng exit 3. Không có benchmark/result.

Đọc [CONTRACT](docs/CONTRACT.md) trước khi viết module; đó là API v1 cuối cùng.
[Kiến trúc](docs/ARCHITECTURE.md), [đóng góp](docs/CONTRIBUTING.md),
[protocol thực nghiệm](docs/EXPERIMENT_PROTOCOL.md), [kế hoạch](docs/DELIVERY_PLAN.md),
[môi trường](docs/ENVIRONMENT.md), [trạng thái kiểm chứng](docs/PROJECT_STATUS.md).

## Build trong MSYS2 UCRT64

Cài đủ dependency theo quyền của người dùng: GCC, libgomp, Python và UCRT64 Make
(`mingw-w64-ucrt-x86_64-{gcc,libgomp,python,make}`). UCRT64 Make có tên
`mingw32-make`; các target giống `make` trên Linux. Mở đúng terminal UCRT64; dùng GCC của `/ucrt64/bin`, không compiler MSYS `/usr/bin`.
Trong đường dẫn có khoảng trắng, luôn quote đường dẫn:

```sh
cd '/d/Code/parallel-bfs-openmp'
gcc --version
mingw32-make build
mingw32-make check-openmp
mingw32-make test
./build/bfs.exe --help
./build/bfs.exe --graph datasets/small/disconnected.edgelist --vertices 6 --source 0 --algo omp-basic --threads 2 --schedule static --directed
```

Lệnh cuối phải exit 3 với NOT_IMPLEMENTED, stdout trống; không phải chạy BFS thành công.
Makefile dùng Python 3 (`PYTHON=python3` nếu terminal chỉ có python3).
Nếu dùng PowerShell/native Make, truyền đầy đủ đường dẫn compiler hoặc mở UCRT64;
không sửa PATH toàn hệ thống. Công cụ thiếu phải được người dùng cho phép cài riêng.

`make test` kiểm tra CLI thật (help, validate input, từ chối module chưa có).
`make test-bfs` cố ý thất bại vì chưa có bộ kiểm thử/thuật toán BFS.
`python scripts/check_scaffold.py` chỉ kiểm tra dependency khung báo cáo và oracle fixture;
`make clean` chỉ xóa danh sách file build/LaTeX đã biết, không đụng datasets/results.

## Báo cáo tiếng Việt

Trong UCRT64 có XeLaTeX và BibTeX trên PATH: `make report`.
Hoặc tại `report/`: `xelatex -halt-on-error main.tex`, `bibtex main`, rồi chạy
XeLaTeX thêm hai lần. Cần fontspec, geometry, hyperref, setspace, amsmath và
font Latin Modern Roman có dấu tiếng Việt. Có thể dùng một TeX distribution đã
cài; bootstrap không tự cài. Output `report/main.pdf` bị gitignore.
Khung đủ sáu chương, placeholder trường/giảng viên/thành viên; chưa có kết quả.

## Git và nơi làm việc chính

Bản làm việc: `D:\Code\parallel-bfs-openmp`. Bản OneDrive được giữ làm snapshot,
không phát triển song song ở cả hai nơi. Origin trỏ repository public chính:
https://github.com/duyanhtr130905/parallel-bfs-openmp .
Chủ repo dùng branch, hai thành viên còn lại fork, PR về canonical/main.

Repository local vẫn chưa có commit trên chore/bootstrap-contracts; chưa push,
main baseline và PR #1 Draft đã có trên GitHub. Ruleset main-pr-review đã Active trước lần upload đầu.
CI và PR template mới chuẩn bị local, chưa có CI run. Mọi upload/PR/merge cần xác nhận.
Main sau tích hợp sẽ là nguồn chuẩn; PR mở và công việc chỉ ở local chưa được gọi hoàn thành.

Review đủ 42 file, findings P0-P3 và evidence: [REVIEW_20261105](docs/REVIEW_20261105.md).
**REQUEST_CHANGES**: lỗi placeholder bìa LaTeX P1 còn mở; GCC/Make/OpenMP/PDF chưa xác minh.
Clang C11 CLI và 31+24 ca CLI đã PASS, không phải correctness/performance BFS.
[Thiết lập GitHub](docs/GITHUB_SETUP.md) ghi chính xác phần đã bật và bước tiếp theo.
Mẫu PR bootstrap vẫn ở docs/BOOTSTRAP_PR.md.

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
