# Thiết lập repository chính — chuẩn bị ngày 05/11/2026

Trạng thái: repository public đã tạo trống, ruleset main-pr-review Active
(id26620761), chưa đưa mã lên và chưa có CI trên GitHub. Bản D có origin
trỏ canonical, đã xác minh sau khi đối chiếu snapshot. GitHub main chưa tồn tại dưới dạng ref.
Policy đã được đọc lại qua public API; chưa có PR để thử enforcement thực tế.

## Quyết định và thông tin còn thiếu

- Kết nối GitHub xác nhận tài khoản duyanhtr130905; không thấy organization nào.
- Người dùng đã chọn public `duyanhtr130905/parallel-bfs-openmp` và mô hình
  chủ repo dùng branch, hai người kia fork. Repo trống đã tạo bằng browser;
  public API xác nhận private=false, branches=[], default_branch=main.
- Chưa có ba GitHub username/role. Không tạo CODEOWNERS placeholder hoặc tự mời người.
- GitHub CLI đang có token không hợp lệ. Connector đọc được nhưng không có công cụ
  tạo repository hoặc quản lý protection; dùng trình duyệt đăng nhập nếu cần.

Public repo dùng branch protection trên GitHub Free. Private repo cần gói hỗ trợ
và policy cho phép fork. Không đổi visibility hoặc mua gói tự động.

## Các bước kích hoạt, thực hiện tuần tự

1. ĐÃ XONG: repo public trống, không README/license/gitignore tự sinh.
   Ruleset Active tại https://github.com/duyanhtr130905/parallel-bfs-openmp/rules/26620761 .
   Bypass list được để trống trên UI. Cả admin chịu các quy tắc này.
2. Tại `D:\Code\parallel-bfs-openmp`, kiểm tra git status, review toàn bộ file mới,
   sửa P1 ở report/main.tex và chạy build/CLI/OpenMP/report khi có toolchain.
   Bản gốc OneDrive chỉ là snapshot, không phát triển đồng thời ở hai bản.
3. Origin trên bản D: https://github.com/duyanhtr130905/parallel-bfs-openmp.git .
   Script cài cấu hình chỉ thêm khi chưa có remote; không set-url hoặc push.
4. Trước lần upload đầu, người dùng duyệt file/commit và cách tạo main. Repo hiện
   chưa có bất kỳ commit nào nên chưa có main hoặc base để tạo bootstrap PR.
   Phương án review toàn bộ bootstrap: tạo một root commit rỗng có chủ đích trên
   main, rồi branch bootstrap mang toàn bộ file. Phải xác nhận rõ lần seed main
   này trước khi publish; không coi đó là merge bootstrap được duyệt.
   Có thể dùng root bootstrap trực tiếp nếu người dùng chấp thuận sau review,
   nhưng đó là một quyết định khác; không âm thầm bỏ qua PR đầu tiên.
5. Policy đã lưu và đọc lại. `docs/github/main-ruleset.json` là cấu hình tương ứng,
   `docs/review/github-readback.json` là kết quả GET repo/ruleset/branches thực tế.
   Nếu dùng CLI đã đăng nhập hợp lệ để kiểm tra lại:

   ```powershell
   gh api repos/duyanhtr130905/parallel-bfs-openmp/rulesets/26620761
   gh api repos/duyanhtr130905/parallel-bfs-openmp/branches
   ```

   Đây là lệnh đọc, không ghi cấu hình khác. Kiểm tra tên context thực tế sau CI đầu tiên;
   nếu khác, sửa policy theo check đã quan sát, không bỏ required checks để merge.
   Hiện status contexts dùng Any source; sau run đầu bind GitHub Actions khi hỗ trợ.
   Checks miễn lúc **tạo nhánh**, cho phép seed main được duyệt riêng; mọi cập nhật
   main vẫn cần PR/checks. Chưa thực hiện seed hoặc thử một push bị chặn.
6. Policy: ít nhất 1 approval từ người khác có write, dismiss stale approvals,
   approval cho lần push cuối từ người khác, resolve conversations, CI đủ ba job,
   branch up to date, áp dụng cả admin, cấm force-push và xóa main.
   Không auto-merge; chỉ maintainer được nhóm chỉ định thao tác merge sau xác nhận.
   Một approval kỹ thuật của Codex không thay approval độc lập của sinh viên.
   Nếu cả ba cần approval hợp lệ, phải gán quyền write phù hợp sau khi biết username;
   quyền write cũng cho phép merge khi gate đạt, nên quy tắc maintainer là quy ước
   nhóm, không tuyên bố có hạn chế merge-only riêng trên repo cá nhân.
7. Upload nhánh bootstrap và mở PR sau xác nhận riêng. Chờ CI, xử lý P0/P1,
   review độc lập rồi mới xin merge. Không reset, rebase đã publish, force-push,
   hoặc tự thay đổi branch protection để lách lỗi.
8. Sau main bootstrap được merge, ba thành viên mới fork/clone và mở nhánh riêng.
   `origin` là fork cá nhân, `upstream` là canonical. Fetch upstream, cập nhật
   main fast-forward; xử lý divergence bằng merge reviewable, không reset.
   Mỗi PR hướng canonical/main, tham chiếu issue/owner/acceptance/tests.

## Theo dõi tiến độ bằng main

Main chứa phần đã tích hợp và kiểm chứng. PR mở là work in progress, không gọi là
hoàn thành. Issue trên canonical ghi owner, acceptance, dependency và PR liên quan;
docs/PROJECT_STATUS.md trên main tóm tắt evidence và công việc tiếp theo.
Hiện main GitHub chưa được thiết lập, nên chưa thể gọi GitHub là nguồn chuẩn đang hoạt động.

CI chỉ kiểm tra bootstrap: không thay `make test-bfs` hoặc chứng minh thuật toán BFS.
PR thuật toán phải nối correctness tests thực vào CI trước khi được duyệt.
Workflow dùng pull_request, quyền contents:read, không secrets và không
pull_request_target. Actions đã pin SHA; phiên bản package từ MSYS2/apt vẫn có thể
thay đổi và cần ghi môi trường thực ở từng run. Job report dự kiến bắt lỗi P1 hiện có.

Nguồn: [GitHub protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches),
[forks](https://docs.github.com/en/pull-requests/reference/forks),
[protection API](https://docs.github.com/en/rest/branches/branch-protection).

Log kiểm chứng lại từ mã trên bản D: docs/review/destination-verification.json.
Nếu lần seed main được duyệt nhưng bị ruleset từ chối, dừng và kiểm tra đánh giá
quy tắc; không tự tắt protection/thêm bypass để đưa mã lên.
