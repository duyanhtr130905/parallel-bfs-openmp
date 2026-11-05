# ADR-0001 — Stack cố định theo đề bài

Ngày 05/11/2026. Trạng thái: đã được người dùng chỉ định trong yêu cầu bootstrap.
Chọn C11, OpenMP CPU, Windows/MSYS2 UCRT64/GCC; Python cho tooling;
LaTeX tiếng Việt/XeLaTeX + BibTeX cho báo cáo. Không chuyển C++/GPU/MPI.
Hệ quả: cần kiểm tra GCC/OpenMP thật và font/TeX packages; không thể suy build
thành công từ file scaffold. Chỉ xét lại nếu người dùng đổi yêu cầu rõ ràng.
