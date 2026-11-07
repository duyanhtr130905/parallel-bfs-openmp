# C1 — báo cáo học phần, 07/11/2026

## Phạm vi và trạng thái
- Base main `7a1b855bf5a8436839bd73d022d0e2df6eb84876`; nhánh `docs/c1-academic-report`.
- Clone mới `parallel-bfs-c1` trong workspace được cấp quyền; snapshot `parallel-bfs-openmp` chưa có commit được giữ nguyên. Không truy cập/sửa bản D: ngoài quyền phiên.
- Đã viết Chương 1 và phương pháp Chương 4; Chương 5–6 là đề cương có nhãn chưa đo. Giữ nguyên Chương 2/3, API, CLI, Makefile và CI.
- Bibliography dùng chung: C chỉ thêm hai entry cho các citation mới; A/B cần kiểm tra khóa khi bàn giao. Không sửa preamble.
- Issue #3 A (ducnt05), #4 B (Terivn), #5 C đều OPEN khi kiểm tra 07/11; PR list chỉ có #1 và #6 đã MERGED, chưa có PR A/B. Đã đọc cả body và comment điều chỉnh trọng tâm báo cáo của ba issue. Không suy tiến độ code cá nhân từ trạng thái issue.
- C1 hiện giới hạn báo cáo theo yêu cầu phiên. Parser/benchmark scripts trong checklist rộng của #5 chưa triển khai; issue #5 chưa hoàn tất. C2 phụ thuộc #3/#4 và chưa bắt đầu.

## Nguồn thực sự kiểm chứng
1. Trobec, Slivnik, Bulić, Robič (2018), Introduction to Parallel Computing, Springer; DOI https://doi.org/10.1007/978-3-319-98833-7. Đã đọc metadata, mô tả và mục lục tại https://link.springer.com/book/10.1007/978-3-319-98833-7. Chưa đọc toàn văn; không gán lập luận BFS, định luật hoặc số trang cho sách.
2. OpenMP ARB, OpenMP 5.1 (2020), mục 3.10.1, https://www.openmp.org/spec-html/5.1/openmpsu185.html. Đã đọc định nghĩa wall-clock theo giây và giới hạn đồng hồ theo thread; dùng cho ranh giới timer.
3. Cornell University, CS312 Lecture 26 (2007), https://www.cs.cornell.edu/courses/cs312/2007sp/lectures/lec26.html. Đã đọc phần BFS không trọng số, shortest paths và O(V+E); dùng cho Chương 1.

Không tìm thấy PDF trong workspace khi tìm đệ quy. Không giả định đã đọc PDF môn học. Hai nguồn repository ParallelBFS/SVD có sẵn trong bibliography là nguồn khảo sát/trình bày kế thừa; không coi chúng là nguồn hiệu năng hay nguồn học thuật đã kiểm chứng trong phiên này.

## Thông tin chờ nhóm
- A: Chương 2, hình CSR/đồ thị, oracle độc lập, tests và commit bàn giao; nguồn lý thuyết thực đã đọc.
- B: Chương 3, giả mã/sơ đồ, khác biệt basic/optimized, lập luận atomic/barrier, metrics và kết quả kiểm thử sau A.
- Nhóm: toàn văn giáo trình/PDF môn học nếu muốn viện dẫn sâu; thông tin bìa và quy định độ dài/ngày nộp.
- Máy đo: CPU/lõi vật lý/luồng logic/RAM/OS, compiler/runtime/flags, power mode, affinity và tải nền.
- Trước đo: chốt kích thước path/star/grid, nguồn, seed, ma trận threads/schedules, giới hạn bộ nhớ; dataset công khai/giấy phép nếu bổ sung.
- Sau correctness: raw/manifest/hash, mẫu lỗi, số lần lặp, actual team và lệnh tái tạo bảng/biểu đồ. Không điền kết luận trước đó.

## Kiểm chứng
Local: `python scripts/check_scaffold.py` PASS; `git diff --check` PASS; kiểm tra khóa citation và số ngoặc LaTeX PASS (chỉ static). Không có XeLaTeX/BibTeX/Make trên PATH; biên dịch local BLOCKED, dùng job report-xelatex của PR. PDF visual QA chờ artifact CI. Không có benchmark/BFS correctness test nào được chạy trong C1 tài liệu.

CI commit 8071bd0: cả ba job PASS, run https://github.com/duyanhtr130905/parallel-bfs-openmp/actions/runs/42346860168 (PR merge ref c22e143). PDF 20 trang đã render và xem toàn bộ; phát hiện một dòng tràn ở Chương 5, sửa câu và rút mục ghi nhận Chương 6 thành paragraph để tránh trang thưa. Bản sửa cần CI/PDF mới; kết quả cuối ghi trong PR.

## Tiếp tục vai trò C — bản trung gian ngày 07/11/2026
Quyết định mới: dùng duy nhất PR #7 và nhánh docs/c1-academic-report cho toàn vai trò C; không yêu cầu approval cuối trước khi đủ việc. Đã đọc review COMMENT tại 6c09a55 (C1 interim accepted, chưa final), issue #5 và xác minh live #3/#4 OPEN, canonical chỉ có PR #1/#6 merged, #7 draft. origin/main vẫn 7a1b855, không có thay đổi để merge. Giữ snapshot cũ.

Đã thêm generator path/star/grid deterministic, runner/schema validator, analysis median/Q1/Q3/IQR/speedup/efficiency và plotting tối đa 4 nhóm; hướng dẫn và gate tại EXPERIMENT_TOOLS.md. Test synthetic chỉ ở tests và thư mục temp; không benchmark scaffold. Makefile nối test-tools vào make test, CI hiện hữu chạy trên Linux/Windows. Không đổi API/CLI/A/B.

Đã tự review C1, làm rõ so Basic/Optimized, phân biệt đóng góp dự kiến/thực tế, sửa abstract, thêm label bảng và khung giả thuyết/caption; không viết lại toàn bộ. Đã nghiên cứu đủ main/preamble/abstract/sáu chương SVD, ghi ở SVD_PRESENTATION_NOTES.md. Chưa sao chép hình/số liệu/chuyên môn/CPU.

Local unit tests stdlib PASS (4 nhóm, nhiều subcases); lần đầu lỗi quyền temp của môi trường, đặt TEMP/TMP vào build và chạy lại PASS. Scaffold/API static PASS; diff check PASS. Plot smoke test riêng dùng matplotlib trong venv build, không cài hệ thống; kết quả cuối và CI/PDF ở PR body. Không coi các test này là BFS correctness.

BLOCKED: CLI tích hợp, benchmark thật, bảng môi trường/dataset cuối, Chương 5/6 kết quả và abstract cuối phụ thuộc #3/#4 merge + correctness trên commit đo. Bìa thiếu thông tin trường/khoa/giảng viên/MSSV/quy định nộp đã xác minh. Chưa hoàn thành toàn vai trò C, không đóng #5 hoặc Ready for Review. Bước tiếp theo khi đủ dependency: fetch/merge main an toàn vào đúng nhánh này, kiểm A/B, nối CLI, test thật rồi đo theo hướng dẫn; không chờ vô hạn trong phiên.

Plot smoke test PASS: 1 test sinh 4 PDF synthetic trong temp bằng matplotlib 3.11.2 (venv build/plot-venv), không lưu vào results hoặc báo cáo. Không yêu cầu/cấp human approval trong phiên tiếp tục.

CI Linux tại 4ddb1cb phát hiện mock subprocess lan sang platform.platform() (Linux dùng subprocess đọc processor). Sửa bằng alias execute_binary riêng và patch đúng alias, không mock module subprocess toàn cục. Cần CI mới xác nhận; ghi kết quả cuối tại PR body.
