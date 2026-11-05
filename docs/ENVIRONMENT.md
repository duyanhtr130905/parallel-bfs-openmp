# Khảo sát môi trường — 05/11/2026 (Asia/Saigon)

Workspace ban đầu: `C:\Users\PC\OneDrive\Documents\ChatGPT\Tính toán song song`.
Thư mục trống; `git status --short --branch` báo không phải Git repository.
Không tìm thấy AGENTS.md trong workspace và các thư mục cha đã kiểm tra.
Đã tạo repository con `parallel-bfs-openmp`, branch `chore/bootstrap-contracts`,
chưa commit, chưa remote, chưa push. Không sửa các dự án khác hoặc PATH.

| Công cụ | Quan sát thực tế |
|---|---|
| Python | 3.13.2; chạy được script kiểm tra |
| Git | 2.54.0.windows.1; init local thành công |
| GCC | Không có trên PATH; không thấy C:/tools/msys64/ucrt64/bin/gcc.exe |
| Make | Không có make/mingw32-make trên PATH; không thấy bản trong usr/bin hoặc ucrt64/bin |
| OpenMP | Chưa kiểm chứng compile/link/runtime vì thiếu GCC |
| MSYS2 | Có C:/tools/msys64, launcher ucrt64.exe, usr/bin/bash.exe và pacman.exe |
| UCRT64 | Có thư mục môi trường; chưa có GCC/Make ở các đường dẫn kiểm tra |
| XeLaTeX/pdfLaTeX/latexmk | Không tìm thấy trên PATH |

Không khẳng định đã tìm toàn bộ ổ đĩa; công cụ có thể được cài ở vị trí khác.
Để build cần bổ sung/xác định GCC UCRT64 và GNU Make; để xuất PDF cần XeLaTeX,
BibTeX, packages và font đã nêu trong README. Chưa cài bất kỳ phần mềm nào.
Không chạy cập nhật pacman, không tải dataset, không sửa PATH hệ thống.

## Lệnh đã thử và kết quả

| Lệnh (tại root repository trừ khi ghi rõ) | Kết quả |
|---|---|
| python --version | Python 3.13.2 |
| git --version | Git 2.54.0.windows.1 |
| python scripts/check_scaffold.py | PASS: dependency report, nguồn citation và oracle fixture; không chạy C/BFS/TeX |
| python tests/test_cli.py --binary build/bfs.exe | Exit 1: NOT RUN, chưa build binary |
| make build | Exit 1: không tìm thấy make |
| make test | Exit 1: không tìm thấy make; chưa chạy test CLI |
| xelatex -halt-on-error main.tex (tại report/) | Exit 1: không tìm thấy xelatex; chưa có PDF |
| git init -b chore/bootstrap-contracts | Thành công, repository local mới |

`tests/openmp_probe.c` và `make check-openmp` đã chuẩn bị nhưng chưa compile/run.
Kiểm tra cấu trúc LaTeX bằng Python không chứng minh biên dịch hoặc bố cục PDF đúng.

## Bổ sung từ review 05/11/2026

Đã tìm thấy Clang14 cùng GHC tại C:/tools/ghc-9.8.2/mingw/bin/clang.exe.
Build trực tiếp C11 -O2 -Wall -Wextra -Wpedantic -Werror thành công, không OpenMP;
headers syntax PASS; 31 ca CLI gốc +24 ca biên PASS. Clang thiếu omp.h nên không
chạy OpenMP; GCC UCRT64/Make/XeLaTeX vẫn thiếu ở các vị trí đã kiểm tra.
Đặt TMP/TEMP chỉ cho tiến trình compile vào thư mục evidence để tránh lỗi quyền
temp mặc định; không sửa PATH/cài công cụ hoặc đổi stack.
Repo đã copy có đối chiếu sang D:/Code/parallel-bfs-openmp, bản gốc được giữ.
GitHub public/ruleset/remote đã thiết lập theo quyết định mới; mã chưa upload.
Ghi chép ở trên là khảo sát ban đầu, không thay bằng chứng review mới.
Chi tiết lệnh: review/verification.json; kết luận: REVIEW_20261105.md.
