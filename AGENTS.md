# Quy tắc làm việc

Đọc docs/PROJECT_STATUS.md và docs/CONTRACT.md trước khi sửa.
C11/OpenMP/Windows/LaTeX tiếng Việt là stack cố định. Bootstrap kết thúc tại khung;
không tự triển khai BFS hoặc giao việc thành viên nếu không có yêu cầu mới.
API v1 là nguồn chuẩn; đổi phải cập nhật header/tài liệu/consumer cùng PR.
Không số liệu giả, không mô tả CLI tests là BFS tests. Không tự push/merge. Origin chính đã được người dùng cho phép kết nối; không tự đổi URL hoặc thêm remote khác.
Giữ thay đổi của người khác, không reset hard/clean -fdx/force push.
Lệnh: make build, make test (CLI only), make check-openmp, make report;
python scripts/check_scaffold.py chạy được khi chưa có compiler.

Bản làm việc chính là D:/Code/parallel-bfs-openmp; bản OneDrive giữ làm snapshot.
Đọc thêm docs/REVIEW_20261105.md và docs/GITHUB_SETUP.md. Repo public chính:
https://github.com/duyanhtr130905/parallel-bfs-openmp . Chủ repo dùng branch,
hai thành viên khác dùng fork. Ruleset Active không thay cho review thực tế.
Mã nguồn chưa upload, main chưa có ref; chưa được tự seed main hoặc tạo PR.
