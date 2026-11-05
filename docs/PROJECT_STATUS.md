# Publication handoff — 05/11/2026 (Asia/Saigon)

Current gate: **AWAITING INDEPENDENT REVIEW**, with existing REQUEST_CHANGES
findings still open. The user explicitly authorized a minimal main baseline,
normal pushes and a Draft bootstrap PR; no merge or member assignments.
Canonical worktree: `D:/Code/parallel-bfs-openmp`. OneDrive remains unchanged.

- Initial audit: no local commits/tracked files; origin correct; remote refs empty.
- The D copy contains all 42 snapshot files: 36 byte-identical, 6 governance/docs
  differences, plus 9 previously prepared CI/review files. No copy/overwrite needed.
- Publish layout: main contains only a minimal README root commit; the feature
  branch `chore/bootstrap-contracts` restores the complete original README and
  adds the bootstrap, governance and publication evidence. No history rewrite.
- Fresh evidence: [publication-verification.json](review/publication-verification.json).
  Scaffold PASS; direct Clang 14 C11 -Werror CLI build PASS; three headers syntax
  PASS; 31 real CLI cases PASS. This build does not use OpenMP.
- GCC UCRT64/Make/XeLaTeX/BibTeX absent from checked PATH/locations; Clang probe
  fails because omp.h is missing. OpenMP runtime, Makefile targets, report/PDF,
  BFS correctness and benchmarks are not verified. No dependencies installed.
- Existing P1 LaTeX placeholder and P2 metrics/team/layout findings remain open;
  see [REVIEW_20261105.md](REVIEW_20261105.md). No technical source/API changes.
- Candidate-file secret pattern scan found no matches. Build/cache files stay
  ignored; no large datasets, credentials or binaries are included.
- Historical documents/config below retain the state before this authorization;
  references to source not uploaded/no authorization describe that earlier audit.
  The Draft PR and Git refs are authoritative for publication state and SHAs.

Next actions: independent ChatGPT review of the Draft PR, inspect CI evidence,
then resolve findings in separately authorized work. Do not merge or assign the
three members during this publication task. CI is not claimed as passed here.

---

# Review và chuyển nơi làm việc — 05/11/2026 (Asia/Saigon)

Trạng thái hiện tại: **BOOTSTRAP_REQUEST_CHANGES**. Bản làm việc chính:
`D:\Code\parallel-bfs-openmp`; bản OneDrive giữ nguyên snapshot.

- Đã đọc đủ 42 file; review từng file và P0-P3: [REVIEW_20261105.md](REVIEW_20261105.md).
- Đã copy/đối chiếu 63 file, gồm 18 metadata Git; không xóa bản gốc.
- C11 headers/CLI Clang14 -Werror và 31+24 ca CLI PASS. Chưa có BFS tests/benchmark.
- GCC UCRT64/GNU Make/OpenMP runtime/XeLaTeX/PDF còn chưa xác minh; Clang thiếu omp.h.
- P1 LaTeX placeholder sau linebreak còn mở. P2 metrics transport, probe team,
  mức bám layout mẫu cần xử lý trước gate tương ứng. Không đổi API trong phiên audit.
- Repo public canonical đã tạo: https://github.com/duyanhtr130905/parallel-bfs-openmp .
  Origin bản D đã kết nối; chủ repo dùng branch, hai thành viên khác fork.
- Ruleset main-pr-review 26620761 Active, 1 approval, strict ba CI contexts,
  stale/last-push/thread-resolution, cấm force/xóa main, bypass list trống trên UI.
  Miễn status checks lúc tạo ref để seed được duyệt riêng; chưa thử enforcement bằng PR.
- Local có workflow Linux/Windows UCRT64/XeLaTeX + PR template và policy snapshot.
  Chưa commit/push/publish source/PR/merge hoặc CI run. Branch local unborn:
  chore/bootstrap-contracts, toàn bộ source/governance chưa tracked, không staged.
- GitHub API trả branches=[]; chưa có main ref. Main chỉ trở thành nguồn chuẩn tiến độ
  sau lần bootstrap được upload, review và merge có phép. PR mở vẫn là việc đang làm.

Ba bước tiếp theo:
1. Sửa P1 và chốt layout/metrics; xác minh toolchain + build/test/OpenMP/report, xem PDF.
2. Người dùng duyệt diff/commit/lần tạo main đầu và upload bootstrap; không tự push.
3. Nhận username reviewer, PR + CI + review độc lập; chỉ merge sau xác nhận.

Xem [GITHUB_SETUP.md](GITHUB_SETUP.md), docs/review/ và docs/github/main-ruleset.json.
Thay đổi lần này: tài liệu/CI/remote; không implementation BFS, không số liệu.

---

## Bàn giao gốc được giữ lại để truy vết (trạng thái trước review)

# Trạng thái bàn giao bootstrap — 05/11/2026

Phạm vi bootstrap đã tạo xong; kiểm chứng build/CLI runtime/OpenMP/PDF còn chờ
toolchain. Không gọi đây là ứng dụng BFS hoàn chỉnh hay kết quả thực nghiệm.

## Đã có

- Cấu trúc repository và local Git trên branch chore/bootstrap-contracts.
- CONTRACT v1 cuối cùng cùng status.h/graph.h/bfs.h; chỉ khai báo API thuật toán.
- CLI scaffold parse/validate rồi exit 3; không loader, không gọi BFS, không timing.
- Makefile build/test/clean, OpenMP probe, test CLI và structural check.
- Fixture tự tạo với expected distance tay; chưa có thuật toán chạy oracle này.
- Báo cáo LaTeX tiếng Việt sáu chương và nguồn đã xác minh; chưa có PDF/số đo.
- Quy trình fork/review, kế hoạch 14 ngày, protocol thực nghiệm và audit checklist.

## Bằng chứng và giới hạn

`python scripts/check_scaffold.py` PASS. `make build`, `make test` không chạy được
vì thiếu Make trên PATH; GCC UCRT64 cũng chưa thấy. Test CLI trực tiếp báo NOT RUN
vì chưa có binary. XeLaTeX không có trên PATH; chưa biên dịch/xem PDF.
Chi tiết tại ENVIRONMENT.md. Không có kiểm thử BFS hoặc đo hiệu năng.
Không audit implementation ParallelBFS, không sử dụng số liệu README.

## Bước tiếp theo cần phiên giao việc mới

1. Nhóm xác định/cài toolchain khi được phép, chạy build/test/check-openmp/report;
   xem PDF và xử lý font/layout nếu có lỗi.
2. Giao TV1 graph+serial, TV2 basic, TV3 optimized theo CONTRACT và DELIVERY_PLAN.
3. Bổ sung correctness tests và nối CLI pipeline trong PR riêng; chỉ bỏ exit 3
   khi module thật đã link, kiểm chứng và có xử lý lỗi đầy đủ.
4. Benchmark sau correctness; hoàn thiện báo cáo bằng dữ liệu raw thực.

Phiên này dừng tại bootstrap. Chưa commit/push, chưa tạo PR/remote hoặc merge main.
Danh sách file: FILES.md. Mẫu PR: BOOTSTRAP_PR.md.
