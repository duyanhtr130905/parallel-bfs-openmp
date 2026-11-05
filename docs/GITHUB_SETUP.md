# GitHub hiện tại — 05/11/2026

Canonical: https://github.com/duyanhtr130905/parallel-bfs-openmp . Main baseline
1b6dc0f đã có, PR #1 OPEN/Draft trên chore/bootstrap-contracts. Phiên sửa bootstrap
được phép commit mới/push thường và cập nhật PR #1, không merge hoặc tạo PR khác.

Đọc lại ruleset 26620761 qua API: Active, refs/heads/main, 1 approval, dismiss
stale, last-push approval, resolve threads, strict required checks:
bootstrap-linux, bootstrap-windows-ucrt64, report-xelatex. Bypass actors rỗng;
cấm force/delete. do_not_enforce_on_create chỉ cho tạo ref, không miễn merge.
Tên job trong ci.yml khớp các context; push branch chore/** và pull_request vào
main đều kích hoạt ba job. Không paths filter hoặc continue-on-error.

Không thay ruleset, không giảm check, không thử merge để kiểm tra enforcement.
Chủ repo dùng branch, hai thành viên khác dùng fork sau bootstrap; không tự tạo
fork/collaborator. Approval hợp lệ cần người khác có quyền write, không phải review
của chính tác giả hoặc CI. Username/reviewer permissions cần quản trị viên xác
định khi chuẩn bị merge. Phiên này không tự cấp quyền.

Main là phần đã merge; PR mở là đang làm. Theo dõi CI theo đúng HEAD, phân biệt
Linux/Windows/report, xem PDF artifact. Mỗi PR thuật toán sau phải nối correctness
tests thật; make test hiện chỉ CLI/API scaffold. Không nhận làm bằng chứng BFS.

## Chẩn đoán Windows bootstrap
Run baseline 42049780134 dùng GCC UCRT64 16.2.0 đúng đường dẫn nhưng link thất bại
-lgomp. MSYS2 tách [libgomp](https://packages.msys2.org/packages/mingw-w64-ucrt-x86_64-libgomp)
thành package riêng (GCC chỉ optional); workflow baseline chỉ yêu cầu gcc/python/
MSYS make. Sửa install explicit libgomp, dùng UCRT64 mingw32-make thay MSYS make.
CI kiểm tra gcc/python/make ở /ucrt64/bin, target/linker/search paths và pacman -Qo
cho cả import/static libgomp. Không sửa PATH hệ thống hoặc cài local.
[Package GCC](https://packages.msys2.org/packages/mingw-w64-ucrt-x86_64-gcc).
