# Bằng chứng sửa bootstrap PR #1 — 05/11/2026

Baseline reviewed: 389282d557d09fa08bb05bdd7833195195ac9952.
Implementation fix: 3499561c4ab68990104a30f3e16ad1801adb9081.
Working tree trước sửa sạch; fetch origin, PR Draft OPEN và reviews/comments được
đọc đầy đủ; không có inline comments. Không reset/rewrite/force/merge/cài local.

## CI đã quan sát thực tế ở 3499561

[PR run 42052508468](https://github.com/duyanhtr130905/parallel-bfs-openmp/actions/runs/42052508468)
và [push run 42052494736](https://github.com/duyanhtr130905/parallel-bfs-openmp/actions/runs/42052494736)
đều SUCCESS cả ba job.

| Job PR run | Kết quả và giới hạn |
|---|---|
| bootstrap-linux / 127332048449 | Build, header syntax -Werror, 31 CLI, cleanup, strict/negative probe PASS |
| bootstrap-windows-ucrt64 / 127332048564 | C11 -Wall -Wextra -Wpedantic -fopenmp, cùng kiểm tra PASS |
| report-xelatex / 127332047698 | make report đủ XeLaTeX/BibTeX/2xXeLaTeX, PDF 13 trang |

Windows pacman -Qo xác nhận /ucrt64/lib/libgomp.dll.a và libgomp.a thuộc
mingw-w64-ucrt-x86_64-libgomp 16.2.0-6. GCC16.2, UCRT64 Make4.4.1-5,
Python3.14.10-1; command paths đều /ucrt64/bin, target x86_64-w64-mingw32.
Probe: OpenMP=202111 team=2 participants=2 mode=strict; subprocess thread-limit=1
strict thất bại đúng, basic thành công, invalid mode exit2.
Baseline run thiếu package này (log chỉ liệt kê OpenMP optional dependency),
không phải compiler chọn nhầm MSYS; khai báo package trực tiếp sửa link thật.

PDF artifact PR run id13426908535, tên dùng GitHub merge-ref SHA094f83a2,
workflow head3499561. Đã tải vào build/pdf-review-initial, đọc bằng pypdf,
render PDFium sẵn có và mở contact sheet toàn bộ cùng bìa. Tiếng Việt/ba sinh viên/
sáu chương/3 references hiển thị; final log không undefined citation, missing glyph,
overfull/font error. Có một underfull bibliography và TOC hai dòng trang riêng;
commit tiếp theo chỉnh TOC small/singlespacing và bibliography small/raggedright.
**Bằng chứng final HEAD phải lấy lại từ PR comment cuối; không nhận run3499561
là bằng chứng của commit mới.** Không commit PDF/render/build artifacts.

## Local và scope

Python AST, scaffold/API-document signatures, ignore main/nested auxiliaries,
cleanup isolated fixture giữ PDF/TeX/BibTeX/unknown files PASS. Heuristic scan
candidate sources không token/private-key patterns; không chứng nhận toàn máy.
Local make/GCC/XeLaTeX không có trên PATH; dùng CI, không cài toolchain.
src/main.c, graph.h, status.h giữ nguyên; chỉ thêm khai báo metrics/test chữ ký,
không định nghĩa BFS/graph, không raw benchmark, không kết luận hiệu năng.

## Quyết định và gate

ADR-0002 chốt caller-owned metrics, năm tham số, stable actual team từ vùng BFS,
error reset0, timer ngoài BFS. A graph+serial; B basic+optimized; C CLI/benchmark/
report. Không tạo fork/giao việc. Ruleset Active26620761, 1 approval, ba contexts
khớp, bypass rỗng; không sửa policy/quyền và không thử merge. Còn cần independent
ChatGPT re-review và reviewer hợp lệ trước merge; không tự nhận approval.
