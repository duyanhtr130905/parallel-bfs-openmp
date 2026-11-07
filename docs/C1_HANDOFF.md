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
