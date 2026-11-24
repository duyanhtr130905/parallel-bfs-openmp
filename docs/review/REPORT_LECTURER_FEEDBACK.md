# Rà soát báo cáo theo góp ý giảng viên

## Ánh xạ nội dung

| Chương cũ | Vị trí trong bản mới | Nội dung được chuyển |
| --- | --- | --- |
| 1. Mở đầu | 1.1–1.4, 1.6 | Bối cảnh xử lý đồ thị, lý do chọn OpenMP, phạm vi và phương pháp. Tách phát biểu BFS khỏi phép so sánh hiệu năng và viết lại câu hỏi nghiên cứu. |
| 2. Cơ sở lý thuyết | 2.1–2.2, 2.4.1 | Đồ thị sáu đỉnh, bảng frontier và khoảng cách, ví dụ CSR, quy ước đọc cạnh, độ phức tạp và giả mã Serial. |
| 3. Thiết kế BFS song song | 2.3–2.5, 3.2 | OpenMP, giả mã Basic và Optimized, sơ đồ ghép frontier, đồng bộ, API và metrics. Chuyển bằng chứng kiểm thử sang phần thực nghiệm. |
| 4. Môi trường và phương pháp | 3.1–3.3, 3.6 | Cấu hình máy, sáu đồ thị và chín nguồn theo tổ hợp, oracle, QPC, thiết kế phép đo, thống kê, provenance và giới hạn. |
| 5. Kết quả và đánh giá | 3.4–3.6 | Bảng tổng hợp, 81 dòng chi tiết static, 12 biểu đồ đã công bố, phân tích Path/Star/Grid và độ phân tán. |
| 6. Kết luận và hướng phát triển | 1.5, 3.6–3.7 | Đóng góp có bằng chứng, giới hạn, câu trả lời nghiên cứu và các hướng chưa triển khai. Bỏ ghi nhận mẫu trình bày khỏi bản học thuật. |

## Kiểm toán tài liệu tham khảo

Đối chiếu trang gốc ngày 24/11/2026. Nguồn trực tuyến chỉ ghi năm khi tài liệu hoặc thông tin học kỳ xác định được. Tên tổ chức được dùng cho tài liệu không ký tên cá nhân.

| Khóa | Đối chiếu nguồn gốc | Luận điểm hỗ trợ | Quyết định |
| --- | --- | --- | --- |
| trobec2018 | Trobec, Slivnik, Bulić và Robič, Springer Cham, 2018. [DOI 10.1007/978-3-319-98833-7](https://doi.org/10.1007/978-3-319-98833-7). | Chương về lập trình đa lõi và bộ nhớ chia sẻ bằng OpenMP, tr. 47–86. | Giữ và dẫn ở phần chọn mô hình, thực thi OpenMP. |
| openmp52 | OpenMP Architecture Review Board, *OpenMP Application Programming Interface*, 5.2, tháng 11/2021. [Đặc tả](https://www.openmp.org/spec-html/5.2/openmp.html). | Mục 1.2–1.4, 10.1, 11.1, 11.5, 15.3, 15.8 và 18.10.1: team, chia việc, schedule, barrier, đồng bộ bộ nhớ, đồng hồ. | Giữ và dùng nhất quán cả cho ngữ nghĩa API đồng hồ. Các phép exchange trong mã được ghi rõ là C11. |
| openmpwtime | OpenMP Architecture Review Board, đặc tả 5.1, tháng 11/2020. [Mục 3.10.1](https://www.openmp.org/spec-html/5.1/openmpsu185.html). | Wall-clock theo giây trên luồng gọi, tương ứng mục 18.10.1 của 5.2. | Gộp vào openmp52, xóa khóa riêng để tránh trộn phiên bản. |
| beamer2012 | Scott Beamer, Krste Asanović và David Patterson, SC ’12, IEEE, 2012. [DOI 10.1109/SC.2012.50](https://doi.org/10.1109/SC.2012.50), [hội nghị](https://sc12.supercomputing.org/schedule/event_detail.php-evid=pap525.html), [bản tác giả](https://scottbeamer.net/pubs/beamer-sc2012.pdf). | Khó khăn của BFS song song và chuyển giữa top-down và bottom-up. | Giữ với phạm vi công trình liên quan và hướng phát triển. Sửa dấu tên tác giả và tên kỷ yếu; bỏ trường trang khỏi mục trích. |
| cornellbfs | Cornell CS 312, học kỳ xuân 2007. [Lecture 26](https://www.cs.cornell.edu/courses/cs312/2007sp/lectures/lec26.html). | Mục bài toán một nguồn trên đồ thị không trọng số, FIFO, đếm số cạnh và độ phức tạp tuyến tính. | Giữ như tài liệu giảng dạy, dùng tác giả tổ chức. |
| microsoftqpc | Microsoft, *Acquiring high-resolution time stamps*. [Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/sysinfo/acquiring-high-resolution-time-stamps). | Đo khoảng thời gian ngắn bằng QPC, tần số, độ phân giải và chi phí truy cập. Tần số 10 MHz lấy từ hồ sơ máy đo. | Giữ, bỏ ngày truy cập cũ và ghi rõ tài liệu công cụ. |
| msys2update | MSYS2 Project, *Updating MSYS2*. [Hướng dẫn chính thức](https://www.msys2.org/docs/updating/). | Chính sách cập nhật toàn hệ thống cho môi trường công cụ được dùng. | Giữ cho mô tả chuẩn bị hệ thống. |
| parallelbfs | chibinz, [ParallelBFS](https://github.com/chibinz/ParallelBFS). README mô tả chương trình riêng. | Báo cáo cũ không có trích dẫn nội dung, chỉ ép hiển thị qua nocite. | Xóa. Chưa có căn cứ quy việc triển khai hoặc số liệu của nhóm về nguồn này. |
| svdtemplate | minhhhduc/svd, thư mục LATEX_template. Hồ sơ cũ ghi dùng để khảo sát trình bày. | Ghi nhận lịch sử về mẫu định dạng. | Xóa khỏi báo cáo và BibTeX theo yêu cầu. |
| barrett1994 | Richard Barrett và chín đồng tác giả, SIAM, ấn bản 2, 1994. [Metadata do Netlib cung cấp](https://netlib.org/linalg/html_templates/Templates.html), [mục CRS](https://netlib.org/linalg/html_templates/node91.html). | Lưu liên tục theo hàng, mảng chỉ số cột và mảng điểm đầu. Quy ước đồ thị và định dạng tệp lấy từ CONTRACT. | Bổ sung để có nguồn trực tiếp cho CSR. |

## Các điểm cần đọc khi review

- Kiểm tra phát biểu khoảng cách, đặc biệt đỉnh nguồn, đỉnh cô lập và hướng cạnh. Xem đối chiếu triển khai ở PR #8, #9 và #7.
- Kiểm tra lập luận về FIFO, từng mức BFS, atomic claim và barrier. Đọc tên Optimized theo mục tiêu thiết kế. Direction-optimizing BFS được ghi nhận là công trình liên quan và một hướng chưa triển khai.
- Kiểm tra số liệu và câu chữ giới hạn phép đo. Bảng static sinh tự động, 36 biểu đồ nguồn và các tệp kết quả giữ nguyên. Kiểm tra PDF và log trên HEAD của PR.
- Đọc [hồ sơ nghiệm thu dữ liệu](../FINAL_HANDOFF_20261114.md) và [thống kê công bố](../../results/experiment-20261112/README.md) cùng phần phân tích. Đối chiếu tách kết quả thời gian tổng khỏi giả thuyết về từng thành phần.

## Kiểm tra dữ liệu và phạm vi

Tại bản biên tập, chạy lại công cụ kiểm toán hồ sơ đã có bằng lệnh `python scripts/audit_final_evidence.py --out build/lecturer-feedback-evidence.json`. Kết quả PASS cho 9 phiên, 4.968 tệp session đối chiếu bản sao, 225 dòng thống kê, 81 dòng bảng static và 36 hash hình. Giá trị speedup cao nhất là 0,29140006879944963; 216 cấu hình OpenMP có speedup dưới 1 và 162 cấu hình nhiều luồng có scaling dưới 1. Kiểm tra riêng cấu trúc LaTeX xác nhận ba chương, 18 mục, 7 khóa được trích dẫn, 12 biểu đồ nhúng và không có khóa hoặc nhãn thiếu trong mã nguồn. Quy trình này đọc dữ liệu hiện có và không đo lại.
