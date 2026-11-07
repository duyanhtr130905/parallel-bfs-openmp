# Nghiên cứu cách trình bày mẫu tiền nhiệm — 07/11/2026

Nguồn đọc trực tiếp qua GitHub API: https://github.com/minhhhduc/svd/tree/main/LATEX_template — main.tex, preamble.tex, Abstract.tex, chapters/chapter1.tex đến chapter6.tex. Không tải/copy hình, dữ liệu hoặc mã chuyên môn.

- main tổ chức bìa, abstract, mục lục/danh mục rồi sáu chương, bibliography. Giữ XeLaTeX + BibTeX của BFS; không chuyển sang T5/babel/biber của mẫu.
- Chương 1 nối bối cảnh giảm chiều với mục tiêu; học cách gắn bài toán với động cơ, không lấy nội dung SVD vào BFS. Chương 2 dùng công thức, hình pipeline có caption/label và chỉ số hiệu năng; BFS cần hình đồ thị/CSR và ví dụ theo tầng từ A.
- Chương 3 có giả mã algorithmic đánh số, đầu vào/đầu ra, region song song và barrier, kèm sơ đồ. BFS cần B bàn giao hai giả mã thật và sơ đồ frontier/thread đúng implementation; C không tự điền thay.
- Chương 4 có mô tả máy, bảng kích thước, đồ thị theo thuật toán và nhận xét sau hình, rồi bảng tổng hợp. Áp dụng chuỗi bảng/hình → quan sát → giải thích → giới hạn; không mặc định lời giải thích cache hay đồng bộ đã được đo trực tiếp. Mẫu có label fig:placeholder lặp: BFS dùng label riêng. Không sao chép CPU, kích thước, speedup hay nhận định superlinear của mẫu.
- Chương 5 mở rộng SVD/PCA với công thức, hình và bảng classification. BFS giữ Chương 5 là kết quả BFS, không bắt chước nội dung mở rộng hoặc tăng tính năng ngoài học phần.
- Chương 6 kết luận/hạn chế/hướng phát triển; BFS phải trả lời ba câu hỏi Chương 1 từ raw đã kiểm chứng. Abstract cuối cần mô tả kết quả thực tế; bản hiện tại ghi rõ chưa đo.

## Áp dụng C trong phiên này
Bổ sung động cơ so Basic/Optimized, sửa abstract hết mô tả bootstrap-only, thống nhất schema bảng/caption/label và khung đối chiếu câu hỏi/giả thuyết Chương 5. Không thêm package khi chưa có hình/giả mã bàn giao. Bảng máy/dataset cuối vẫn BLOCKED trước đo; trường nguồn, input edges và CSR arcs riêng. Công cụ vẽ tạo bốn nhóm từ cùng session/source/build và lưu provenance, không có hình giả trong báo cáo.
