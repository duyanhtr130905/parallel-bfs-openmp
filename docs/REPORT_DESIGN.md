# Thiết kế báo cáo tiếng Việt

Khảo sát 05/11/2026: [mẫu SVD](https://github.com/minhhhduc/svd/tree/main/LATEX_template),
main.tex, preamble.tex, bia.tex, sáu chương và bibliography. Chỉ tham khảo bố cục;
không lấy tên, MSSV, logo, nội dung SVD hoặc dữ liệu của nhóm trước.

| Thành phần mẫu | Áp dụng và lý do |
|---|---|
| A4; lề trái30/phải20/trên-dưới25mm | Giữ thông số |
| Body 14pt, giãn 1.5 | extreport 14pt thay patch normalsize để cỡ chữ ổn định |
| Chapter18/section16/subsection15pt | Heading nhất quán, chapter căn giữa |
| Khung bìa và bảng sinh viên | minipage/tabular, ba hàng placeholder có braces |
| Header chapter, footer số trang giữa | Header ngắn cố định tránh tràn tên chapter; trang đầu chapter chỉ footer |
| Roman phần đầu, Arabic nội dung, TOC/LOF/LOT | Giữ; danh mục hình/bảng trống vì chưa có dữ liệu |
| inputenc/T5/babel, biblatex/Biber | Giữ XeLaTeX/fontspec Unicode, Latin Modern Roman và BibTeX/plain của bootstrap; giảm thay đổi toolchain, hỗ trợ dấu Việt/citation |

Tách preamble/bia/main theo mẫu, sáu chương tiếng Việt. Không thêm cảm ơn giả.
Trường/khoa/giảng viên/ba sinh viên/MSSV/địa điểm/thời gian giữ placeholder.
`make report` chạy XeLaTeX, BibTeX, hai lượt XeLaTeX. PDF/log/bbl/toc lưu artifact
CI để mở kiểm tra; compile không tự chứng minh layout đã xem.
