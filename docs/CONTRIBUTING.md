# Quy trình đóng góp

Theo quyết định 05/11/2026: repository public chính là
https://github.com/duyanhtr130905/parallel-bfs-openmp . Chủ repo dùng feature branch;
hai thành viên còn lại dùng fork. Mỗi fork có origin trỏ fork cá nhân và upstream
trỏ canonical. Bản D của lead có origin trỏ canonical, chưa upload commit nào.
Ruleset main-pr-review đã Active; xem GITHUB_SETUP.md về CI và lần seed main đầu.
Chưa có username hai thành viên nên chưa mời reviewer/cấp write hoặc tạo fork.

1. Đồng bộ main sạch bằng fetch upstream và cập nhật fast-forward; giữ thay đổi
   đang làm trên branch riêng. Không reset hard, clean -fdx hoặc force push.
2. Tạo branch `feat/tv1-csr-serial`, `feat/tv2-omp-basic`, `feat/tv3-omp-opt`;
   nhánh sửa lỗi `fix/<mo-ta>`, tài liệu `docs/<mo-ta>`.
3. Commit nhỏ, rõ mục đích: `feat(graph): validate edge-list input`,
   `test(bfs): cover disconnected vertices`, `docs(report): describe methodology`.
4. PR từ fork vào repository chính/main. Nội dung: hành vi thay đổi, file/module,
   CONTRACT v1, lệnh kiểm chứng thực tế, giới hạn, rủi ro đồng bộ/bộ nhớ.
5. Ít nhất một thành viên khác review trước merge; tác giả không tự phê duyệt.
   Thay đổi API cần lead và các bên dùng API xem lại cùng một PR.
6. Chỉ người được nhóm giao quyền mới merge; automation/agent không tự merge/push.

C11: include rõ, kiểm tra size overflow/NULL/lỗi cấp phát, dọn bộ nhớ khi lỗi;
không ép cast che warning. Không global mutable, không trộn C++.
Không commit binary, dữ liệu lớn, kết quả không provenance hoặc token cá nhân.
Không sao chép mã repo tham khảo trước khi audit logic và kiểm tra giấy phép.

Hiện `make test` chỉ kiểm tra CLI scaffold; không được mô tả là kiểm thử BFS.
PR thuật toán phải thêm kiểm thử thực: oracle tay + so serial, directed/undirected,
đỉnh cô lập, n=1, self-loop, cạnh trùng, chu trình, diamond nhiều tranh chấp,
source khác 0, input sai, threads/schedule lặp nhiều lần. Thêm module/test vào
Makefile một cách tường minh; không để file thuật toán tồn tại nhưng không được build.
