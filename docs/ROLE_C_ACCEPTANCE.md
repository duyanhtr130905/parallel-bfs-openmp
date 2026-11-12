# Role C — hồ sơ nghiệm thu 12/11/2026

## Phạm vi và trạng thái

Giữ `docs/c1-academic-report` và Draft PR #7. PR #9 đã merge bằng merge commit
`0b0c71fb1ead16285dd66b056830e7ff83385456`; Đức (`ducnt05`, quyền write)
APPROVED đúng HEAD `1048833f783b396ac7dd50d557bb7402521b647d`, các thread
resolved, CLEAN và ba required checks SUCCESS. Main sau merge PASS tại
[43176595134](https://github.com/duyanhtr130905/parallel-bfs-openmp/actions/runs/43176595134).
Merge main vào C: `2656448`, giải conflict Makefile giữ toàn bộ test A/B/C.
Không sửa implementation A/B, header hoặc semantics API v1. Chỉ sửa Chương2 vị trí nhãn cô lập; Chương3 bổ sung khởi tạo visited vào hai giả mã và làm rõ optimized dùng prefix single, không dùng atomic counter mỗi mức.

CLI gọi ba hàm thật qua con trỏ hàm, cùng loader CSR; timer chỉ quanh BFS.
Validation toàn distance bằng bất đẳng thức cạnh và predecessor giảm khoảng
cách diễn ra ngoài timer. Metrics lấy từ BFS, serial actual=1; OpenMP actual>=1.
JSONL chỉ phát khi BFS_OK, timer/metrics/distance hợp lệ. Exit 0/2/3/4 giữ nguyên;
exit3 chỉ khi backend thật trả NOT_IMPLEMENTED (không còn nhánh stub OpenMP).

## Kiểm thử và review đồng bộ

```sh
make CC=gcc PYTHON=python3 build test check-openmp
make CC=gcc PYTHON=python3 test-bfs test-parallel test-integration test-cli-failures
# Windows: mingw32-make CC=gcc PYTHON=python ... trong terminal UCRT64
```

- A: parser/CSR/ownership/overflow/invalid input và serial oracle.
- B: cả ba implementation so mọi distance với queue oracle độc lập và fixture
  tính tay; path/star/diamond/cycle/self-loop/duplicate/disconnected/isolated,
  contention 64×256 và random seed; 1/2/4/8 luồng, ba schedule, lặp các fixture.
- C `test-integration`: Floyd–Warshall dựng trực tiếp từ **input edges**, không
  dùng CSR làm oracle; grid 5×7 và random seed `0x12345678`, directed/undirected,
  sources 0/17/34, 1/2/4/8 luồng, static/dynamic/guided, 3 lần lặp = **1296 BFS
  calls**. So toàn distance và byte equality của CSR sau mỗi call.
- CLI: 70 ca schema/exit/error/loader và tất cả algorithm/schedule/thread;
  request4 với OMP_THREAD_LIMIT=1 phải xuất actual1. Backend fault tách riêng
  production: 15 ca lỗi memory/runtime/NOT_IMPLEMENTED/metrics/distance, không
  có JSONL thành công. Không sử dụng test backend làm benchmark.
- Compiler mặc định C11/OpenMP `-O2 -Wall -Wextra -Wpedantic -Werror`.
- Tools: schema strict, generator deterministic, raw/hash/provenance, error và
  timeout retention, incomplete checkpoint khi ngắt; median/min/max/IQR,
  speedup/efficiency và `scaling_vs_omp1` riêng. Plot test dùng synthetic fixtures
  trong thư mục tạm, chỉ CI Linux cài matplotlib trên runner tạm.

Review tĩnh: atomic exchange trên visited chọn một winner ghi distance[v];
loser không đọc distance[v]. Frontier hiện tại chỉ gồm các đỉnh đã công bố sau
barrier tầng trước. Basic dùng atomic counter cho slot riêng rồi implicit barrier
trước swap. Optimized có buffer riêng theo tid, for-barrier trước prefix,
single-barrier công bố offsets, copy các đoạn rời rồi explicit barrier trước
swap/single-barrier. Mỗi call dùng một persistent team, không đổi ICV toàn cục.
Đây là review do bên tích hợp thực hiện, không thay approval độc lập hoặc chứng
minh race-free. Chưa chạy ThreadSanitizer/race detector; không stress đến OOM.

Local Windows: Clang14 C11 `-O2 -Wall -Wextra -Wpedantic -Werror` chạy graph và
serial tests PASS. Python tools/static/cleanup PASS. Local OpenMP **BLOCKED**:
Clang thiếu `omp.h`; GCC/Make không có tại vị trí đã kiểm. Kết quả Linux/Windows
OpenMP và XeLaTeX phải đối chiếu **đúng HEAD** tại checks của
[PR #7](https://github.com/duyanhtr130905/parallel-bfs-openmp/pull/7); không coi
CI ancestor hay compile-only là kiểm thử runtime. Log/PDF được tải về `build/`
để giữ bằng chứng cục bộ, không commit binary.

## Benchmark — BLOCKED, chưa có số liệu

Khảo sát Windows 12/11/2026: Intel Core i5-12450HX, 8 physical / 12 logical,
Windows 11 Home Single Language 10.0.26300; OS-visible RAM 24,866,680 KiB,
free RAM tại khảo sát 9,427,640 KiB (không cố định), power scheme Balanced,
BatteryStatus=2, 74% tại khảo sát. Không đặt biến OMP trong môi trường shell.
GCC/UCRT64, Make, XeLaTeX/BibTeX không tìm thấy trên PATH, C:/tools/msys64,
C:/msys64, D:/msys64 hay các vị trí chuẩn đã kiểm; không khẳng định tìm toàn ổ.
Clang14 có sẵn chỉ đủ kiểm A, chưa có OpenMP headers/runtime hợp lệ.
Không cài công cụ, sửa PATH/power mode hoặc lấy timing CI thay benchmark.

Chưa chốt compiler/runtime/flags thực đo; flags mục tiêu là flags Makefile nêu
trên. Chưa sinh dataset chính thức, chưa warm-up hay lấy 10 mẫu/config, chưa có
raw/manifest/hash/median/speedup/figures thực nghiệm. Không có dữ liệu giả.

Khi có máy đủ công cụ, chạy lại checks trên cùng commit sạch, lưu log và tạo
evidence JSON gồm `commit`, `status: "PASS"`, `command`, `log` (path log thật).
Điền environment JSON theo required fields trong `scripts/benchmark.py`, gồm
compiler/version/flags/_OPENMP/runtime/power/background load đã xác minh; source
và reachable phải kiểm chứng. Không dùng nguyên metadata khảo sát thay metadata
phiên đo. Chạy thử một cấu hình nhỏ, theo dõi tài nguyên trước khi tăng quy mô.

```sh
python scripts/generate_graph.py path --vertices 1024 --out datasets/c2-path-1024
python scripts/generate_graph.py star --vertices 10000 --out datasets/c2-star-10000
python scripts/generate_graph.py grid --rows 32 --cols 32 --out datasets/c2-grid-32
python scripts/benchmark.py --binary build/bfs.exe --dataset datasets/c2-path-1024/dataset.json --environment build/environment.json --evidence build/correctness.json --threads 1 2 4 8 --repeats 10 --seed 2026 --timeout 60
python scripts/analyze_results.py results/raw/SESSION --out build/summary.json
python scripts/plot_results.py results/raw/SESSION --out results/figures/SESSION
```

Thay `.exe` trên Linux; `SESSION` là thư mục duy nhất runner vừa trả về. Lặp lại
cho star/grid và nguồn đã chốt; dừng tăng quy mô khi path có nhiều tầng làm
pilot chậm. Đây chỉ là **kích thước pilot đề xuất**, không phải dataset đã đo.
Runner tạo session mới, 1 warm-up + 10 samples/config, shuffle seed2026, giữ
stdout/stderr và lỗi/outlier, hash raw/log cuối phiên; checkpoint incomplete khi
ngắt. Analyzer từ chối phiên lỗi/dirty/hash sai, team không ổn định hoặc <10 mẫu.
Giữ backup raw ở kho nhóm được phép đến hết chấm/phúc khảo; chưa có kho backup
được xác nhận. Không git-add cả datasets/raw/figures hoặc thông tin riêng máy.

## Báo cáo và checklist review độc lập

Đã cập nhật abstract, Chương 1/4/5/6 theo trạng thái tích hợp và blocker; giữ thiết kế và mã A/B; chỉnh tối thiểu nhãn hình/giả mã như nêu trên. Bibliography hợp nhất có cả beamer2012/openmp52.
Bản PDF hiện là **bản tích hợp để review**, chưa phải báo cáo hiệu năng cuối.
Chương 5 chưa có bảng/đồ thị đo thật; Chương 6 không kết luận tăng tốc.

- [ ] Đọc diff C so main; kiểm dispatch, timing boundary, metrics, validation.
- [ ] Kiểm ba required checks trên đúng final HEAD và log chạy đủ test targets.
- [ ] Chạy lại oracle/CLI/fault tests; đọc atomic/barrier A/B và giới hạn bằng chứng.
- [ ] Hoàn tất máy đo/pilot, raw/manifest/hash và backup, >=10 samples/config.
- [ ] Tái tạo summary/figures; phân tích slowdown, IQR, scaling riêng với speedup.
- [ ] Điền kết quả Chương 5/6, abstract; XeLaTeX+BibTeX và xem toàn PDF mới.
- [ ] Reviewer độc lập nghiệm thu; sau đó mới approval/merge PR #7 do người có quyền.

Issue #5 vẫn OPEN; không tự approve hoặc merge PR #7.

## Bằng chứng trước lần polish PDF cuối

Commit `d8c39da279be305d20667e81c4ff23e88640393b` PASS đủ 3 jobs trên
[PR run43182035650](https://github.com/duyanhtr130905/parallel-bfs-openmp/actions/runs/43182035650)
và [push run43182026201](https://github.com/duyanhtr130905/parallel-bfs-openmp/actions/runs/43182026201).
Log xác nhận Linux/Windows chạy đủ 1296 integration calls, 15 faults, 70 CLI,
A/B tests và OpenMP probe; Linux plot smoke PASS. PDF31 trang được render và xem
đủ trước polish: phát hiện2 overfull hbox Chương5, TOC tràn một dòng sang trang
riêng, nhãn cô lập chạm đỉnh. Đã chỉnh tối thiểu và cần CI/PDF mới trên final HEAD.
Giảng viên còn `[TÊN GIẢNG VIÊN]` chưa được cung cấp, không tự điền.
