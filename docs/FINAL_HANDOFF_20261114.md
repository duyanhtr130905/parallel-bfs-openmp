# Nghiệm thu và bàn giao cuối — 14/11/2026

Role C, Issue #5, PR #7, nhánh `docs/c1-academic-report`. Tiếp tục từ commit
`21a765cb180f1fb20b57cac70efa5858fc7759cb`; commit đo vẫn là
`ab588fb8ab535b796f0c8b6d5e98a7efe5ebc76c`. Không sửa thuật toán/API,
raw, manifest, dataset hoặc kết quả khoa học; không chạy lại benchmark.

## Nghiệm thu dữ liệu độc lập

`scripts/audit_final_evidence.py` dùng Python stdlib và Decimal, không import
analyzer/publisher/plotter. Chạy tại root, ghi ra một đường dẫn mới:

```powershell
python scripts/audit_final_evidence.py --out build/acceptance-new.json
```

- PASS 9 session, mỗi phiên 25 cấu hình, 25 warm-up và 250 mẫu chính thức.
  Tổng 225 warm-up + 2250 mẫu; không thiếu/trùng index hoặc repetition,
  stdout khớp manifest/raw, stderr rỗng, exit 0; actual=requested 1/2/4/8.
- SHA-256 của 9 manifest, raw JSONL, toàn bộ stdout/stderr, 6 dataset và
  binary đo khớp hồ sơ. So **4968 file** của 9 session với backup ổ D, gồm
  manifest: tên và nội dung khớp. Dataset JSON/edges, 6 build-evidence hashes,
  20 file phụ trợ tại backup cũng khớp bản gốc. Source archive đo có src/include
  khớp Git commit ab588fb sau chuẩn hóa CRLF/LF (archive dùng CRLF, Git LF);
  log correctness gắn đúng binary/commit.
- Tính lại median/min/max/Q1/Q3/IQR bằng nội suy tuyến tính tại (n−1)q,
  speedup so Serial, efficiency theo actual team và scaling so omp-1 cùng
  schedule. Cả 225 dòng CSV/JSON khớp (sai số float rel 1e-12, abs 1e-15).
  Chín bảng LaTeX chỉ chọn static: đã đối chiếu đủ **81 dòng**, đúng đơn vị ms,
  E theo %, làm tròn; không diễn giải nhầm thành 225 dòng trong PDF.
- Provenance của 36 hình khớp manifest/dataset/script và thống kê tính độc lập.
  Dùng các thống kê độc lập thay đầu vào analyzer để tái vẽ: **36/36 hình
  raster giống từng byte ở cạnh dài 1400 px**. Chương 5 dùng đúng 12 hình.
- Kiểm các headline và diễn giải: max S=0,2914000688 ở Opt1/static/grid512-s0;
  216 cấu hình OpenMP S<1, 162 cấu hình nhiều luồng C<1; max C nhiều luồng
  0,7535998363 ở Basic2/static/star1000000-s0; max IQR/median xấp xỉ 67,0%.
  Các median, IQR, tỷ lệ kích thước/nguồn/schedule trong Chương 5/6 khớp raw.
  **Không phát hiện sai lệch kết quả khoa học.** Không bỏ outlier.

Kết quả máy đọc: [raw/hash/statistics](../results/experiment-20261112/acceptance-20261114.json),
[36 hình](../results/experiment-20261112/figure-acceptance-20261114.json).
`index_sha256` trong provenance cũ là hash **batch-index.json đầu vào** tại
backup/build, không phải hash sessions.json đầu ra; đã xác minh đúng tệp.

## Chỉnh báo cáo và kiểm thử

- Bìa: **TS Nguyễn Hải Vinh**. Giữ nguyên tên/MSSV ba thành viên.
- Bỏ câu lịch sử “Bản C1 đã kiểm chứng thông tin xuất bản...” ở Chương 1;
  giữ nhận định học thuật và citation của giáo trình. Không viết lại sáu chương.
- Local UCRT64: `mingw32-make -B CC=gcc PYTHON=python build test check-openmp`
  PASS; gồm tests graph/serial/parallel, 1296 integration calls với oracle
  Floyd–Warshall, full distance/CSR equality, 70 CLI, 15 faults, timer, tools
  và OpenMP strict/negative. Hai plotting tests trong venv hiện có PASS.
- Máy không có XeLaTeX local; build đủ XeLaTeX → BibTeX → XeLaTeX ×2 bằng
  job `report-xelatex` trên CI. Chỉ dùng PDF mới từ đúng HEAD cuối.
  Log CI, PDF mới, SHA-256, số trang và phiếu kiểm trực quan được lưu tại
  bộ bàn giao dưới đây và cập nhật PR body sau khi CI hoàn tất; không dùng hash cũ.

## Bộ bàn giao và gate

Thư mục riêng tại workspace cha:
`output/Parallel_BFS_BanGiao_20261114/`. Xem `HANDOFF.md` và `SHA256SUMS.txt`
trong thư mục đó để biết **HEAD, PDF/hash/số trang và ZIP chính xác**. Hồ sơ
nghiệm thu cuối ở `evidence/final-acceptance.json`; CI và review hiện hành ở
[PR #7](https://github.com/duyanhtr130905/parallel-bfs-openmp/pull/7).
Hướng dẫn nộp/tái lập: [SUBMISSION_README](SUBMISSION_README.md).

ZIP nguồn chỉ lấy file đã commit, không .git/token/venv/build/raw lớn.
Raw giữ ở `results/raw/SESSION`; backup đọc được tại
`D:/Code/parallel-bfs-evidence/20261112-1616/official-ab588fb/SESSION`.
Backup cùng laptop chưa phải off-device; giữ đến hết phúc khảo.

Sau final CI/PDF PASS: chuyển Ready for Review và mời ducnt05/Terivn
(đều có quyền write đã xác minh). Human approval đúng HEAD vẫn bắt buộc.
Không tự approve, merge, bật auto-merge hoặc đóng Issue #5.
Chưa có quy định nộp chính thức; người dùng cần đối chiếu tên file, định dạng,
giới hạn dung lượng, nền tảng/hạn nộp và yêu cầu slide/video/in bản nếu có.
