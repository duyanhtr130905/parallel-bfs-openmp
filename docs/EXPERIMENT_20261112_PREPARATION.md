# Chuẩn bị thực nghiệm Windows — 12/11/2026

Trạng thái: correctness và pilot PASS; chưa thu benchmark chính thức.
Người dùng đã cho phép cài công cụ, thực nghiệm thật và tiếp tục Draft PR #7.
Không approve/merge, không đóng Issue #5.

## Checkout và bảo toàn

Checkout thực tế là `parallel-bfs-c1` trong workspace OneDrive, nhánh
`docs/c1-academic-report`, ban đầu sạch tại `3e7cfde749578960185ca67f65709cc3e9a4abdf`.
Checkout `D:/Code/parallel-bfs-openmp` ở main sạch; không sửa checkout đó.
Thư mục `parallel-bfs-openmp` bên cạnh workspace là snapshot có file untracked;
không chỉnh sửa. Binary Clang cũ đã được sao lưu trước khi rebuild bắt buộc.
PDF và dữ liệu cũ được giữ nguyên.

## Môi trường đã xác minh

- Windows 11 Home Single Language, 10.0.26300.
- Intel Core i5-12450HX, 8 lõi vật lý / 12 luồng logic.
- RAM OS-visible 24.866.680 KiB; trước cài còn 10.749.548 KiB trống.
- Dung lượng trống trước cài: C khoảng 24,7 GB, D khoảng 93,6 GB.
- Active power scheme Balanced, BatteryStatus=2, pin 76% lúc khảo sát.
  Phiên đo phải kiểm AC trực tiếp bằng GetSystemPowerStatus, không chỉ suy từ WMI.
- MSYS2 hiện có tại `C:/tools/msys64`; cập nhật đầy đủ bằng `pacman -Syu`,
  mở shell mới sau core update. Mirror đầu bị kẹt khi tải; ngắt bằng SIGINT
  trước transaction, sau đó dùng cấu hình riêng trỏ máy chủ chính thức
  `https://repo.msys2.org`. Không sửa mirror config hệ thống.
- UCRT64: GCC 16.2.0-6, libgomp 16.2.0-6, Make 4.4.1-5,
  Python 3.14.10-1. `_OPENMP=202111`, target `x86_64-w64-mingw32`.
- `gcc`, `python`, `mingw32-make` trong shell UCRT64 đều thuộc `/ucrt64/bin`;
  pacman xác nhận ownership `libgomp.dll.a` và `libgomp.a`.
- Windows Modules của tiến trình BFS pilot xác nhận DLL thực nạp là
  `C:/tools/msys64/ucrt64/bin/libgomp-1.dll`, SHA-256
  `ccaf59dc8cff15ace88ab47acd68a5b014167cad8f960e7683466a4c821e41c4`.
- Flags chung: `-O2 -Wall -Wextra -Wpedantic -Werror -std=c11 -fopenmp`,
  include `-Iinclude`, link `-fopenmp` cho cả ba phiên bản.
- Không cài TeX local; tiếp tục dùng CI để build XeLaTeX + BibTeX.
  Matplotlib 3.11.2 có sẵn trong `build/plot-venv`; bổ sung PyMuPDF 2.1
  trong đúng venv này để hỗ trợ xem PDF. Poppler cũng có sẵn trong runtime Codex.
- PATH chỉ bổ sung cho tiến trình; không đổi PATH User/Machine, power plan,
  Defender, firewall hoặc registry. Không có cảm biến nhiệt CPU đáng tin cậy
  được sử dụng; không công bố nhiệt độ.

## Correctness và công cụ

Commit `e2f37ff0a42eec209c17d293fb6c1214d3e548be`:

```powershell
$env:PATH = 'C:\tools\msys64\ucrt64\bin;' + $env:PATH
$env:OMP_DYNAMIC = 'FALSE'
mingw32-make -B CC=gcc PYTHON=python build test check-openmp
```

PASS graph/parser, serial oracle, parallel oracle/stress và CSR bất biến,
1296 integration BFS calls (Floyd–Warshall từ input edges), 15 fault cases,
70 CLI cases, tool tests, cleanup và OpenMP strict2/negative1.
`-B` buộc thay binary Clang cũ bằng GCC, không chỉ dựa timestamp Make.
Hai plotting tests cũng PASS, gồm đường lý tưởng S=p và nhóm schedule theo
actual team. Analyzer đối chiếu toàn ma trận cấu hình/repetition/warm-up khai báo,
từ chối thiếu nguyên nhóm ngay cả khi raw đã được tính lại hash.

CI cùng commit PASS Linux, Windows UCRT64 và XeLaTeX:
https://github.com/duyanhtr130905/parallel-bfs-openmp/actions/runs/43188174425

Review công cụ bởi một Codex agent độc lập: không phát hiện blocker ở hai bản sửa.
Đây là review hỗ trợ AI, không phải GitHub approval của người khác.

## Pilot và vấn đề đồng hồ cần quyết định

Pilot riêng, không phải benchmark chính thức: path32, path8192, star1.000.000,
grid512×512; mỗi đồ thị chạy serial và hai OpenMP với static/dynamic/guided,
OpenMP yêu cầu/thực tế 8. Tổng 28 lời gọi, không lỗi correctness/timeout.
Peak working set quan sát tối đa khoảng 36,4 MiB. Path8192 OpenMP khoảng 1–1,8 s;
grid512 khoảng 0,13–0,24 s; star1M khoảng 0,026–0,102 s trong pilot.
Các khoảng này chỉ để chọn tải an toàn, không suy kết luận thống kê.

Probe độc lập xác nhận `omp_get_wtick()=0.001 s`, bước dương quan sát nhỏ nhất
`0.000999927520752 s`; serial path8192 nhận 0 s. QPC frequency thực tế 10 MHz.
Không gán epsilon, sửa raw hoặc tính speedup từ baseline bằng 0.
Chủ dự án đã trả lời cho phép dùng QueryPerformanceCounter trên Windows.
Đã cập nhật timer caller, CONTRACT/protocol/ADR-0003; Linux giữ omp_get_wtime,
không đổi module BFS A/B. Test timer30ms và toàn bộ correctness PASS trước commit.
Pilot QPC riêng28 calls PASS; serial path8192=52,7 microsecond, peak RAM<40MiB.
Không dùng thời gian pilot cho thống kê chính thức.

Runner dùng tiến trình mới cho mỗi warm-up/mẫu. Phải diễn giải đây là thời gian
một lời gọi độc lập gồm khởi tạo team/runtime trong BFS; warm-up không làm nóng
team của tiến trình đo kế tiếp. Process launch/I/O/CSR/validation ở ngoài timer.

## Bằng chứng cục bộ

- Trước/sau cài và log pacman: `../output/experiment-20261112/` ngoài Git.
- Correctness/probe/runtime: `build/experiment-20261112/`.
- Pilot stdout/stderr/JSONL: `build/pilot-20261112/`.
- Sao lưu độc lập ổ D: `D:/Code/parallel-bfs-evidence/20261112-1616/`,
  có hash của file preparation/pilot; chưa có raw chính thức.
- Tên giảng viên được người dùng cung cấp: Nguyễn Hải Vinh; đã điền bìa.

Ma trận đã chốt tại `docs/experiment-20261112-matrix.json`: 9 dataset/source,
225 cấu hình, 225 warm-up và2250 mẫu chính thức. Không mở rộng12 threads,
random/layered hoặc chọn lại tham số sau khi xem số liệu chính thức.

Tiếp theo: commit timer/ma trận trước đo → kiểm thử/CI đúng
commit đo → thu raw/manifest/backup → phân tích/biểu đồ và báo cáo cuối.
