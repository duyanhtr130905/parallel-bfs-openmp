# Thực nghiệm laptop Windows 12/11/2026

Dữ liệu thật trên i5-12450HX, 8 physical/12 logical, Windows11 10.0.26300,
GCC/libgomp UCRT64 16.2.0, cùng flags -O2/C11/OpenMP. Commit đo:
`ab588fb8ab535b796f0c8b6d5e98a7efe5ebc76c`.

- 6 đồ thị, 9 tổ hợp đồ thị/source, 25 cấu hình/tổ hợp.
- 225 warm-up và 2250 mẫu chính thức, 10 mẫu/config; không lỗi/timeout/loại outlier.
- Requested=actual tại 1/2/4/8; static/dynamic/guided; OMP_DYNAMIC=FALSE,
  OMP_PROC_BIND/OMP_PLACES unset. Mỗi mẫu là một process mới.
- Timer Windows QPC10MHz được chủ dự án duyệt (ADR-0003); không dùng timer CI.
- 16:32:58–16:42:26 UTC+7. AC ổn định, free RAM thấp nhất10,37GiB;
  CPU nền trước phiên1,30–19,01%. Không có số đo nhiệt CPU.
- Cả216 cấu hình OpenMP có speedup<1. Giá trị lớn nhất0,2914 là
  Optimized1/static/grid512/source0; không suy rộng ngoài phép đo này.

`summary.csv` và `summary.json` giữ đủ225 cấu hình: median/min/max/Q1/Q3/IQR,
speedup, efficiency theo actual team và scaling_vs_omp1. Đơn vị thời gian là
giây. CSV dùng dấu chấm thập phân; bảng PDF dùng dấu phẩy và làm tròn4 chữ số
có nghĩa. `sessions.json` nối từng dòng/figure với session và manifest/raw hashes.
`provenance.json` ghi hash ma trận/scripts/CSV/bảng. 36 figure PDFs và provenance
từng nhóm ở `report/figures/experiment-20261112/`; 12 hình lớn được đưa vào báo cáo.

## Raw và backup (không commit raw)

Raw chính: `results/raw/SESSION/`, mỗi session có551 raw/log files và manifest.
Danh sáchSESSION/hash đầy đủ: `sessions.json`. Backup đã so hash từng file:
`D:/Code/parallel-bfs-evidence/20261112-1616/official-ab588fb/SESSION/`.
Đây là ổ D trên cùng laptop, chưa phải bản sao ngoài thiết bị.

Giữ dữ liệu đến hết chấm/bảo vệ/phúc khảo, không tự retention-delete. Không sửa
raw/manifest để làm đẹp số. Muốn đo lại phải tạo session mới.

## Tái tạo thống kê/biểu đồ

Chạy tại repository root, với raw đã có ở đúng các locator trong sessions.json:

```powershell
$env:MPLCONFIGDIR = "$PWD/build/matplotlib-cache"
build/plot-venv/Scripts/python.exe scripts/publish_experiment.py results/experiment-20261112/sessions.json --out build/reproduced-summary --figures build/reproduced-figures --tables build/reproduced-tables.tex
```

Các đích phải chưa tồn tại. So hash CSV tái tạo với `provenance.json`; PDF có thể
khác metadata thời điểm tạo nhưng phải giữ cùng số liệu. Python plotting env dùng
matplotlib3.11.2/numpy2.5.4. Không chạy tái tạo plot trong lúc benchmark.

## Đo lại

Ma trận đã đăng ký: `docs/experiment-20261112-matrix.json`. Sinh lại từng đồ thị
với `scripts/generate_graph.py` từ kind/n hoặc rows/cols trong ma trận, rồi so
SHA-256 graph.edges. Tất cả undirected, source theo từng job, reachable=n.

```powershell
$env:PATH = 'C:\tools\msys64\ucrt64\bin;' + $env:PATH
$env:OMP_DYNAMIC = 'FALSE'
mingw32-make -B CC=gcc PYTHON=python build test check-openmp
python scripts/benchmark.py --binary build/bfs.exe --dataset DATASET_JSON --environment VERIFIED_ENVIRONMENT_JSON --evidence MATCHING_CORRECTNESS_JSON --threads 1 2 4 8 --repeats 10 --seed 2026 --timeout 60
```

Phải đo lại CPU/RAM/nguồn/tải nền, ghi timer/frequency, compiler/flags/runtime,
source/reachable; proof có commit/status/command/log và binary_sha256 đúng binary
đã test. Commit sạch và ba CI jobs PASS trước đo. Không dùng nguyên metadata cũ
để đại diện phiên mới. Không gộp dữ liệu build/máy/source khác nhau.
