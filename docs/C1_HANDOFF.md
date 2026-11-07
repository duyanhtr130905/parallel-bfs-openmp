# Bàn giao C — trạng thái trung gian, cập nhật 07/11/2026

## Trạng thái hiện hành — chốt phần C độc lập
- Duy nhất branch `docs/c1-academic-report`, PR #7 Draft trên canonical. Base `origin/main` đã kiểm tra: `7a1b855bf5a8436839bd73d022d0e2df6eb84876`. Không tạo PR/branch/clone mới; không merge, không yêu cầu approval cuối.
- Workspace làm việc: `parallel-bfs-c1`; snapshot `parallel-bfs-openmp` cũ được giữ nguyên. Không sửa dự án D: ngoài quyền phiên.
- Đã viết Chương 1/4, chuẩn bị khung Chương 5/6, sửa abstract đúng trạng thái trung gian và thêm nguồn Cornell/OpenMP. Không có số liệu hoặc kết luận hiệu năng. Chương 2/3 và API/CLI A/B giữ nguyên.
- **Đã triển khai** `generate_graph.py` (path/star/grid), `benchmark.py` (runner/schema/raw/manifest), `analyze_results.py` (thống kê/speedup/efficiency), `plot_results.py` (tối đa bốn nhóm). Hướng dẫn tại EXPERIMENT_TOOLS.md. Không mở rộng công cụ thêm trong cleanup.
- `make test` chạy CLI, scaffold/API và `test-tools`; plotting smoke test riêng dùng matplotlib trong venv. Các fixture synthetic chỉ dùng trong tests/temp, không phải số liệu báo cáo.
- Review COMMENT độc lập tại `7b49886d14d3dba82bc23c764229e8bfd51bd680` chấp nhận gate hiện tại của C độc lập, yêu cầu cleanup bìa/help/handoff. Không phải GitHub approval cuối cho toàn vai trò C.
- Cleanup lịch sử 5c2853f đã cập nhật help và tách trạng thái. Yêu cầu hình thức tiếp theo bỏ toàn bộ nhãn trạng thái trên bìa; quy cách mới tại REPORT_DESIGN.md.
- **Dừng triển khai C độc lập sau cleanup.** C2 vẫn BLOCKED: cần A (#3) CSR/serial/oracle/Chương 2 và B (#4) hai bản OpenMP/correctness/Chương 3 được review và merge. Không coi issue OPEN hay CI bootstrap là bằng chứng BFS. Chưa hoàn thành toàn #5.

## Bằng chứng và giới hạn hiện hành
- Tại `7b49886`: CI Linux, Windows UCRT64 và XeLaTeX đều PASS; run https://github.com/duyanhtr130905/parallel-bfs-openmp/actions/runs/42348551526 . Bốn nhóm unit test công cụ chạy trên cả Linux/Windows.
- Local: stdlib tests 4 nhóm PASS; plotting smoke 1 test/4 PDF synthetic PASS với matplotlib 3.11.2 trong `build/plot-venv`; scaffold và diff check PASS. Không cài hệ thống.
- PDF tại mốc đó 21 trang, đã render/xem; không overfull/undefined citation/missing glyph trong log cuối. Local thiếu XeLaTeX/BibTeX/Make trên PATH, dùng CI. Kết quả cleanup và SHA cuối được ghi tại PR body để tránh tự tham chiếu SHA trong commit.
- Chưa có BFS correctness, CLI tích hợp hoặc benchmark thật. Runner kiểm metadata/schema và tham chiếu evidence/log, không chứng minh toàn mảng distance. Trước đo phải xác nhận gate A/B, máy/build và giữ log thật theo protocol.

## Thông tin cần từ người dùng/nhóm
- Bìa đã xác nhận: ĐHQG Hà Nội / Trường ĐH Khoa học Tự nhiên; Trần Duy Anh — 23001828, Lê Huy Anh Dũng — 23001846, Nguyễn Anh Đức — 23001865, đúng thứ tự; Hà Nội – 2026 và logo HUS người dùng cung cấp. Còn thiếu tên giảng viên, xác nhận mã học phần nếu muốn ghi; không tự thêm khoa/bộ môn.
- Máy đo: model CPU, số lõi vật lý/luồng logic, RAM, OS/build, GCC và runtime OpenMP/version/flags, nguồn điện/power mode, affinity và tải nền; xác nhận máy dự kiến dùng và khả năng chạy đo sau bàn giao A/B.
- Thời hạn: ngày/giờ nộp chính thức, múi giờ, ngày bảo vệ nếu có; yêu cầu định dạng/nơi nộp và giới hạn trang nếu học phần quy định.
- Từ A/B: commit/PR merged, log correctness, tài liệu/hình/giả mã/nguồn thực đã đọc. Sau đó mới chốt ma trận path/star/grid vừa tài nguyên, kích thước/nguồn/threads/schedule trước đo thật.

## Nguồn thực sự kiểm chứng
1. Trobec, Slivnik, Bulić, Robič (2018), Introduction to Parallel Computing, Springer; DOI https://doi.org/10.1007/978-3-319-98833-7. Đã đọc metadata, mô tả và mục lục tại https://link.springer.com/book/10.1007/978-3-319-98833-7. Chưa đọc toàn văn; không gán lập luận BFS, định luật hoặc số trang cho sách.
2. OpenMP ARB, OpenMP 5.1 (2020), mục 3.10.1, https://www.openmp.org/spec-html/5.1/openmpsu185.html. Đã đọc định nghĩa wall-clock theo giây và giới hạn đồng hồ theo thread; dùng cho ranh giới timer.
3. Cornell University, CS312 Lecture 26 (2007), https://www.cs.cornell.edu/courses/cs312/2007sp/lectures/lec26.html. Đã đọc phần BFS không trọng số, shortest paths và O(V+E); dùng cho Chương 1.

Trong lần khảo sát C1 ban đầu chưa tìm thấy PDF môn học trong workspace (các PDF báo cáo CI được tạo sau đó). Không giả định đã đọc PDF môn học. ParallelBFS là nguồn khảo sát kế thừa, chưa audit implementation. Mẫu SVD đã được đọc trực tiếp để nghiên cứu trình bày trong phiên công cụ tiếp theo; xem SVD_PRESENTATION_NOTES.md. Không dùng hai repository này làm nguồn kết quả hiệu năng BFS.


## Lịch sử C1 ban đầu — chỉ để tra cứu, không phải trạng thái hiện hành
- Base main 7a1b855; lần đầu chỉ viết báo cáo. Tại thời điểm đó scripts benchmark **chưa triển khai**; nhận định này đã hết hiệu lực sau mốc công cụ 7b49886.
- Commit 8071bd0: ba CI jobs PASS, PDF 20 trang; phát hiện một dòng tràn Chương 5. Commit 6c09a55 sửa và CI/PDF kiểm lại đạt. Review C1 chấp nhận như bản trung gian.
- Phiên tiếp theo triển khai công cụ và nâng cấp abstract/Chương 1/khung Chương 5; nghiên cứu đủ main/preamble/abstract/sáu chương SVD, không lấy hình/số liệu/chuyên môn/CPU của mẫu.
- Commit 4ddb1cb: CI Linux lỗi mock subprocess lan sang platform probe. Commit 7b49886 thu hẹp mock vào alias execute_binary, local và CI sau sửa PASS. Lần test local đầu cũng gặp quyền temp; đặt TEMP/TMP vào build rồi chạy lại PASS.
- Các ghi chú “chờ PDF CI” hoặc “scripts chưa triển khai” của phiên đầu không còn áp dụng. Mốc hiện hành nằm ở đầu tài liệu và PR #7.
