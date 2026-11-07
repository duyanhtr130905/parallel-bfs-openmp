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

Mục lục dùng cỡ small (12pt) và single spacing để tránh trang thừa chỉ có vài
dòng trong khung; body vẫn 14pt/1.5. Bibliography small/raggedright để URL đọc
được và tránh khoảng trắng giãn quá mức. Đã mở PDF CI đầu: bìa đủ ba sinh viên,
các chương và citation có mặt; bản chỉnh mục lục phải được CI/render lại.

## Chuẩn hóa hình thức bìa — 07/11/2026
Đọc trực tiếp `LATEX_template/bia.tex`, `preamble.tex`, `main.tex` của mẫu SVD theo yêu cầu mới. Bìa BFS dùng hai dòng trường đã xác nhận cỡ 13pt đậm, logo HUS gốc từ người dùng (185×238 PNG có alpha), chiều cao 5.1cm giữ tỷ lệ, tên đề tài 18pt đậm hai dòng, học phần 14pt, giảng viên 13pt, bảng sinh viên 14pt theo đúng thứ tự đã xác nhận và Hà Nội – 2026. Không còn nhãn trạng thái nội bộ trên bìa. Chưa xác minh tên giảng viên và mã MAT3148 nên giữ [TÊN GIẢNG VIÊN], không ghi mã học phần hoặc khoa/bộ môn.

Khung 1.2pt, padding 15pt như mẫu; dùng fbox/minipage đã có thay vì thêm fancybox, tính chiều rộng trừ khung/padding để giữ trong lề A4. Khoảng cách dọc điều chỉnh cho tiêu đề BFS và ba sinh viên thay vì hai của mẫu; không ép width/height logo đồng thời như mẫu (tránh méo tỷ lệ).

Giữ Latin Modern Roman, họ serif LaTeX gần Computer Modern mặc định của mẫu; không đổi Times New Roman. Giữ extreport 14pt, A4 oneside, giãn 1.5, lề 30/20/25/25mm, headings 18/16/15pt; bổ sung spacing section/subsection đúng mẫu. XeLaTeX/BibTeX giữ nguyên. Mục lục small/single và header ngắn hiện có được giữ để đọc rõ, tránh tràn; không bê toàn bộ preamble hay Biber/T5 của mẫu. Không sửa nội dung khoa học sáu chương. Kiểm chứng PDF/CI cuối được ghi tại PR #7.
