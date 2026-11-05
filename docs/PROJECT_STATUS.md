# Bootstrap PR #1 — sửa review ngày 05/11/2026

Gate: FIXES PREPARED — AWAITING CI AND INDEPENDENT CHATGPT RE-REVIEW.
Canonical D:/Code/parallel-bfs-openmp; chore/bootstrap-contracts → main.
Baseline 389282d557d09fa08bb05bdd7833195195ac9952, working tree ban đầu sạch,
fetch không có commit mới. PR OPEN/Draft; đã đọc review chính và issue comment,
không inline comments. Review COMMENTED không phải approval.

Ủy quyền: sửa P1/P2/P3, API revision, ownership, commit/push thường và cập nhật
PR #1; không BFS, benchmark, fork/giao việc, cài local, ruleset change hoặc merge.

Đã chuẩn bị: explicit UCRT64 libgomp/package/search diagnostics; strict two-team
probe và negative case; BFSMetrics caller-owned theo ADR-0002; bìa tabular/style
và artifact PDF; nested auxiliary ignore/clean giữ PDF; raw retention/provenance.
Ownership cuối: A graph+serial; B basic+optimized; C CLI+benchmark+report.
Xem ARCHITECTURE/CONTRIBUTING/DELIVERY_PLAN và REPORT_DESIGN.

Local thiếu GCC UCRT64/Make/XeLaTeX trên PATH, không cài phần mềm. CI cung cấp
bằng chứng Windows/OpenMP/report; static/local và CI/PDF sẽ ghi trong PR handoff.
Runtime metrics chưa test vì chưa BFS. docs/review và REVIEW_20261105 giữ evidence
baseline, không dùng làm bằng chứng bản sửa. CLI tests không phải BFS tests.

Ruleset 26620761 đọc lại Active: 1 approval, last-push/stale/thread resolution,
strict bootstrap-linux/bootstrap-windows-ucrt64/report-xelatex, bypass rỗng,
cấm force/delete. Không thêm quyền/reviewer, không thử merge để test enforcement.

Tiếp theo: static/diff → commit/push → ba CI jobs và PDF → evidence → re-review.
Giữ Draft. Chưa được independent reviewer approve; không tự merge.
