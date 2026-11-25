# Nghiệm thu báo cáo Parallel BFS ngày 25/11/2026

Bản cơ sở là commit `11b86b53cfdbd14e72eab51ab13f5b19b70ebc43` và PDF 39 trang.
PR #13 tiếp tục ở chế độ Draft để nhóm quyết định sau nghiệm thu.

| ID | Trạng thái kiểm tra | Bằng chứng |
|---|---|---|
| P0-01 | PASS | Đối chiếu 33 Git blob gồm mã, hai trình đo, dữ liệu hai phiên và lịch sử lần biên dịch lỗi. CSV 24/11 có SHA-256 `aa557801b81e9eefd6807d799d8228e83bb9dce0115ebfefe86c0515bb898920`. |
| P0-02 | PASS | Tóm tắt tổng hợp 7/12 và 5/12. Chương 1 chuẩn hóa phát biểu. Chương 2 giải thích cờ nguyên tử và phân pha. Chương 3 liên kết cấu trúc đầu vào với kết quả. |
| P0-03 | PASS | Chương 1–3 dùng ký hiệu riêng cho số liên kết đầu vào, số cung trong CSR và số cung BFS thực sự xét. |
| P0-04 | PASS | Các mục 3.2–3.4 đặt dữ liệu, giao thức và kết quả hai ngày trong cùng cấu trúc. Scaling dùng phép đo riêng. |
| P0-05 | PASS | Bảng 3.6 có đủ 12 đồ thị. Phụ lục B có 36 cặp, mỗi cặp 12 mẫu chính thức, trung vị, Q1, Q3, IQR, min và max. |
| P0-06 | PASS | Ba sơ đồ lý thuyết, hai nhóm mẫu cấu trúc và toàn bộ ý nghĩa của hình hiệu năng được bảo toàn. Các hình thời gian dùng điểm/IQR, các sơ đồ có hướng có mũi tên. |
| P0-07 | PASS | Mục 3.5–3.6 ghi độ nhạy mốc Serial, cực trị vòng ngẫu nhiên và tải CPU lấy mẫu một giây. Các tỷ số không được diễn giải là khoảng tin cậy. |
| P0-08 | PASS | BBL có 10 mục được trích. Hồ sơ nguồn ghi giới hạn đọc abstract và quyết định giữ Barrett. |
| P0-09 | PASS | PDF đã render đủ 41 trang A4. Kiểm bìa, ngày căn phải, danh mục, bảng, hình và phụ lục. Log cuối không có lỗi cite/ref, missing glyph hay overfull. |
| P1-01 | PASS | 3 đồ thị, 33 cấu hình, 462 lượt. Mỗi lượt kiểm đúng toàn bộ khoảng cách và số luồng. [Bằng chứng](../results/experiment-scaling-20261125/) |
| P1-02 | PASS | Mục 2.5.2 có ví dụ C rút gọn từ mã Basic và giải thích tranh chấp dữ liệu, nguyên tử C11 và rào OpenMP. |
| P1-03 | PASS | [Hồ sơ tài liệu](REFERENCE_AUDIT_20261125.md) giải thích phạm vi của Agarwal và lý do giữ Barrett. |
| P2-01 | PASS | 25 bảng/hình/thống kê được tái tạo trong thư mục tạm và so sánh byte trên cùng môi trường. Build PDF cục bộ bằng Tectonic. |
| P2-02 | PASS | README, yêu cầu, trạng thái, nhật ký và tài liệu nộp ghi riêng ba phiên. |
| P2-03 | NOT RUN tại thời điểm ghi hồ sơ cục bộ | [Kết quả trên HEAD của PR](https://github.com/duyanhtr130905/parallel-bfs-openmp/pull/13/checks) được ghi trực tiếp theo lần chạy. Windows dùng UCRT64 và job báo cáo dùng XeLaTeX/BibTeX. |
| P2-04 | PASS | Tiếp tục PR #13 Draft; công việc dừng tại nghiệm thu báo cáo. |

## Kiểm PDF theo trang vật lý

| Trang | Hạng mục đã đối chiếu |
|---|---|
| 1–3 | Bìa, mã MAT3148, tên giảng viên và nhóm, ngày 24/11 căn phải, tóm tắt 7/12 và 5/12. |
| 4–7 | Mục lục, danh mục hình/bảng và viết tắt; đánh số La Mã. |
| 8–10 | Phát biểu bài toán, tài liệu liên quan và phạm vi. Chương 1 kết thúc gọn trong ba trang nội dung. |
| 11–18 | Ví dụ BFS/CSR, mã giả, ví dụ C rút gọn, sơ đồ đồng bộ và cận công việc/bộ nhớ. |
| 19–24 | Môi trường, hai nhóm minh họa đồ thị, bảng cấu trúc và giao thức kiểm chứng. |
| 25–32 | Bảng chi tiết, đối chiếu 12 đầu vào và hình scaling, chuỗi mẫu Serial và thời gian chuẩn hóa theo tầng. |
| 33–35 | Phân tích giới hạn, kết luận và hướng phát triển. |
| 36–37 | Danh mục tham khảo gọn trong một trang và phụ lục tái lập gọn trong một trang. |
| 38–41 | Hai bảng thống kê bộ chính và ba bảng scaling, không tràn lề. |

PDF `report/published/main.pdf` có 41 trang, 3 chương chính, 13 hình, 15 bảng và 10 tài liệu.
SHA-256: `989ebfe844baaca412538f32435b9e51bbb9e1b69d8b1ae15e33bdc05f09162e`.

Sau lần sửa cuối để caption mô tả đúng biểu đồ điểm, render lại toàn bộ PDF.
Chỉ trang vật lý 26 và 27 khác bản trước khi đối chiếu ảnh; cả hai trang được kiểm lại ở độ phân giải 120 dpi. Bản build sau khi chuẩn hóa dòng cuối của tệp nguồn cho ảnh giống toàn bộ 41 trang.

## Lệnh đã kiểm tra

    mingw32-make CC=gcc PYTHON=python build test check-openmp test-plots test-supplement test-review
    python scripts/analysis/summarize.py
    python scripts/figures/plot.py
    python scripts/summarize_supplement.py results/experiment-20261125
    python scripts/review_artifacts.py --scaling results/experiment-scaling-20261125

Các lệnh Python chạy với Python 3.13 trên Windows. Ba hình TikZ được dựng trong thư mục tạm bằng `render_tikz.py --tectonic` và gói TeX cục bộ. Bản PDF nộp dùng XeTeX/BibTeX đi kèm Tectonic; `make report` dùng XeLaTeX/BibTeX trong CI. Ngày ký 24/11/2026 giữ theo yêu cầu của chủ dự án dù có phép đo ngày 25/11.
