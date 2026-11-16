# Hướng dẫn bộ nộp Parallel BFS

Đây là bộ nộp tiêu chuẩn; chưa có quy định nộp chính thức của giảng viên.
Xem HANDOFF.md trong thư mục bàn giao để biết commit và hash sản phẩm.
PDF báo cáo là bản để đọc/nộp. ZIP nguồn giữ cả LaTeX, tests và công cụ tái lập;
raw lớn và binary đo được giữ riêng, không nằm trong ZIP nguồn.

## Biên dịch và kiểm thử

GCC + libgomp, GNU Make, Python 3. Windows dùng MSYS2 UCRT64 hiện có;
Linux dùng GCC. Trong thư mục nguồn đã giải nén:

```sh
# Linux
make CC=gcc PYTHON=python3 build test check-openmp
# Windows, trong terminal UCRT64
mingw32-make CC=gcc PYTHON=python build test check-openmp
```

Ba thuật toán, cùng fixture có khoảng cách chuẩn `0 1 1 2 -1 -1`:

```sh
./build/bfs --graph datasets/small/disconnected.edgelist --vertices 6 --source 0 --algo serial --directed
./build/bfs --graph datasets/small/disconnected.edgelist --vertices 6 --source 0 --algo omp-basic --threads 4 --schedule static --directed
./build/bfs --graph datasets/small/disconnected.edgelist --vertices 6 --source 0 --algo omp-opt --threads 4 --schedule guided --directed
```

Windows thêm `.exe` vào `build/bfs` nếu terminal yêu cầu. JSONL stdout chỉ phát
khi BFS/validation thành công; lỗi ở stderr. Team thực ở threads_actual.
Timing fixture chỉ là kiểm tra chạy, không phải kết quả thực nghiệm chính thức.

## Tái tạo báo cáo và thống kê từ raw đã lưu

XeLaTeX/BibTeX và font/package theo preamble:

```sh
make report
```

Make chạy XeLaTeX → BibTeX → XeLaTeX hai lần; PDF ở report/main.pdf.
CI Linux lưu artifact PDF và log theo commit. PDF build lại có thể khác hash
vì metadata thời điểm; đối chiếu nguồn và bảng/hình, không thay PDF đã nghiệm thu.

Khôi phục 9 thư mục SESSION từ backup vào `results/raw`, không sửa nội dung.
Danh sách locator/hash: `results/experiment-20261112/sessions.json`.
Backup: `D:/Code/parallel-bfs-evidence/20261112-1616/official-ab588fb`.
Lệnh kiểm độc lập (backup cần đọc được; `--out` chưa tồn tại):

```sh
python scripts/audit_final_evidence.py --out build/audit-new.json
```

Nếu chuyển máy, dùng `--backup PATH` để chỉ đúng bản sao. Khôi phục datasets
theo ma trận vào `datasets/experiment-20261112/` và giữ raw/manifest nguyên vẹn.
Python plotting environment chính thức: matplotlib 3.11.2 / numpy 2.5.4.

```sh
python scripts/publish_experiment.py results/experiment-20261112/sessions.json --out build/reproduced-summary-new --figures build/reproduced-figures-new --tables build/reproduced-tables-new.tex
```

Các đích phải mới. Publisher nhận sessions.json để tái tạo số liệu; provenance
index_sha256 mới sẽ là hash đầu vào này. Provenance công bố ban đầu dùng
batch-index.json trong backup. Summary CSV và bảng cần khớp bản công bố;
figure PDF có thể khác metadata nhưng nội dung phải khớp.

## Tái lập thực nghiệm mới khi được yêu cầu

Không cần chạy lại để nộp bộ hiện tại. Protocol/matrix chính thức nằm ở
`docs/EXPERIMENT_PROTOCOL.md` và `docs/experiment-20261112-matrix.json`.
Sinh lại deterministic graph vào thư mục mới, ví dụ:

```sh
python scripts/generate_graph.py path --vertices 8192 --out datasets/recreated-path8192
python scripts/generate_graph.py star --vertices 1000000 --out datasets/recreated-star1000000
python scripts/generate_graph.py grid --rows 512 --cols 512 --out datasets/recreated-grid512
```

Đối chiếu hash graph.edges với ma trận trước sử dụng. Khi đo mới cần Git checkout
đúng source commit sạch, correctness và binary hash/log tương ứng, CI PASS,
metadata máy/compiler/timer/nguồn/RAM/tải nền mới. ZIP nguồn không có .git:
để runner xác minh commit/dirty state, dùng checkout canonical đúng commit ghi
trong HANDOFF.md, không giả lập Git metadata trong ZIP. OMP_DYNAMIC=FALSE,
OMP_PROC_BIND/OMP_PLACES unset; 1 warm-up +10 mẫu/config, p=1/2/4/8, ba schedule.

```sh
python scripts/benchmark.py --binary build/bfs.exe --dataset DATASET_JSON --environment VERIFIED_ENVIRONMENT_JSON --evidence MATCHING_CORRECTNESS_JSON --threads 1 2 4 8 --repeats 10 --seed 2026 --timeout 60
```

DATASET_JSON/môi trường cần đúng source/reachable theo từng job. Runner tạo
session mới exclusive-create. Không overwrite raw cũ hoặc dùng metadata cũ
đại diện máy/phiên mới. Không gộp timing khác build/máy/timer.

## Giới hạn và việc cần đối chiếu trước nộp

Mỗi mẫu là một BFS/process mới, có team startup trong BFS; warm-up không làm
nóng team ở process sau. 216 cấu hình OpenMP đều S<1; giữ slowdown/outlier.
Một laptop, đồ thị có cấu trúc, chưa profiling/thermal/máy thứ hai.
IQR không phải khoảng tin cậy. Backup ổ D vẫn trên cùng thiết bị.

Đối chiếu với giảng viên: quy tắc đặt tên, nền tảng/hạn nộp, dung lượng,
có cần nguồn LaTeX/dataset/raw/slide/video hay bản in không. Không coi việc
chuẩn bị bộ này là đã nộp hoặc đã được chấm/approval. PR #7 cần approval
độc lập; người dùng quyết định merge sau đó. Issue #5 chưa đóng.
