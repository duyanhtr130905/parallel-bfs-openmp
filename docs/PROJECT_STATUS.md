# Role C — tích hợp sau PR #9, 12/11/2026

PR #9 đã merge `0b0c71fb1ead16285dd66b056830e7ff83385456`, Đức approve đúng
HEAD1048833, CLEAN, threads resolved, đủ checks; main CI43176595134 PASS.
Merge main vào chính nhánh `docs/c1-academic-report` bằng2656448; giữ Draft #7.
CLI đã link cả ba BFS thật, giữ API/timing/metrics/schema; không sửa module A/B.
Thêm oracle Floyd–Warshall từ input edges, 1296 calls, full distance/CSR byte
comparison; fault CLI15 cases; requested4/actual1; giữ tests A/B/C.
Tools bổ sung scaling vs omp1 và checkpoint incomplete; report abstract/1/4/5/6
cập nhật blocker, không bịa số đo. Chi tiết/lệnh/checklist: ROLE_C_ACCEPTANCE.md.

Local Clang14 graph+serial tests PASS; Python tools/static/cleanup PASS.
Local GCC/OpenMP/Make và XeLaTeX BLOCKED; CI final phải kiểm đúng HEAD PR #7.
Chưa có benchmark thật/raw/manifest/figures/speedup. PDF chỉ là bản review,
chưa đủ nội dung thực nghiệm để nộp. Issue #5 OPEN, không approve/merge #7.

Tiếp theo: xác minh CI/PDF đúng commit cuối → reviewer nghiệm thu tích hợp →
chuẩn bị máy đủ công cụ được phép, pilot/benchmark thật và hoàn tất báo cáo.
Không cài phần mềm hoặc thay thiết lập hệ thống trong phiên này.

---
## Lịch sử trước tích hợp C2 (giữ để truy vết)

# Trạng thái hiện hành — 12/11/2026, Role C / tích hợp

- PR #8 đã merge theo approval Terivn tại aa573bd; merge/main:
  `f73514d2cc5439923972bab8abb0fdbf1780c6e7`.
  CI sau merge [43170202116](https://github.com/duyanhtr130905/parallel-bfs-openmp/actions/runs/43170202116)
  PASS đủ Linux, Windows UCRT64 và report. Không bypass ruleset.
- Giữ cùng branch `docs/c1-academic-report` và Draft PR #7; merge main bằng
  commit thường, giải conflict Makefile bằng cách giữ test-bfs và test-tools.
- C nối loader + serial production vào CLI, kiểm chứng toàn distance ngoài timer,
  JSONL schema v1/metrics/exit codes, bổ sung CLI và loader-to-serial oracle tests.
  Chỉ serial sẵn sàng trên nhánh C. omp-basic/omp-opt vẫn exit3, stdout rỗng.
- Local: Clang14 C11 -O2 -Wall -Wextra -Wpedantic -Werror build/run graph và
  serial tests PASS (không OpenMP). Python scaffold, cleanup, 4 nhóm tool tests PASS.
  GCC/Make/XeLaTeX không có tại các vị trí đã kiểm; không cài phần mềm.
  CLI dùng omp_get_wtime thật; kiểm GCC/OpenMP/CLI mới bằng CI sau push,
  kết quả final theo PR #7, không suy từ CI ancestor.
- PR #9 tại `640c0201f51cb7313d524447dca9bb5c116084ab` đã CONFLICTING sau #8,
  chưa approval. Không sửa module B, không approve/merge #9.
- Chưa chạy benchmark ba thuật toán, chưa có speedup/kết quả Chương 5/6.
  PR #7 tiếp tục Draft; còn phụ thuộc #9 và independent review.

## Ba bước tiếp theo

1. B làm theo [hướng dẫn tích hợp](C2_INTEGRATION_HANDOFF.md), cập nhật main,
   so toàn distance với serial thật, CI và Đức review sau commit cuối.
2. Sau #9 merge: C merge main vào cùng Draft #7, nối hai hàm OpenMP thật,
   kiểm correctness + CLI cả ba trên Linux/Windows cùng commit.
3. Xác minh máy/dataset, chạy protocol warm-up + >=10 mẫu/config với raw/hash,
   sinh biểu đồ; hoàn thiện báo cáo và xem PDF rồi review độc lập.

---

## Lịch sử bootstrap (giữ để truy vết; không phải trạng thái hiện hành)

# Bootstrap PR #1 — sửa review ngày 05/11/2026

Gate: AWAITING INDEPENDENT CHATGPT RE-REVIEW; final CI evidence ở PR #1.
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

## Bằng chứng cập nhật

Commit sửa3499561 đã push thường, ba CI jobs PASS ở cả PR run42052508468 và
push run42052494736. Windows xác minh libgomp ownership và team2/negative1 thật.
Đã đọc/render PDF13 trang và xem bìa/toàn bộ; polish TOC/bibliography trong commit
kế tiếp phải có CI và PDF mới. Xem review/REVIEW_FIXES_20261105.md. Kết quả final
HEAD, URLs, PDF inspection và working tree được ghi ở PR handoff comment sau
khi chạy xong; không coi CI ancestor là final. Local không cài toolchain.

Ba bước sau bàn giao: independent re-review → người dùng xác định reviewer có
quyền approval/merge khi sẵn sàng → chỉ triển khai A/B/C trong nhiệm vụ mới.
Không merge hoặc phân việc trong phiên sửa bootstrap.
