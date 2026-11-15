# Portable provenance v1 — sửa review P2 ngày 15/11/2026

`results/experiment-20261112/provenance.json` và provenance của 36 hình được
bảo tồn nguyên bytes/hash lịch sử. Không đổi schema hoặc tái xuất kết quả.
Commit đo vẫn `ab588fb8ab535b796f0c8b6d5e98a7efe5ebc76c`.

## Quy ước kiểm chứng lịch sử

`scripts/audit_final_evidence.py` định nghĩa danh sách đóng `PUBLICATION_TEXT_V1`:

| Trường provenance | File văn bản Git | Bytes dùng để so hash lịch sử |
| --- | --- | --- |
| publisher_sha256 | scripts/publish_experiment.py | LF |
| analyzer_sha256 | scripts/analyze_results.py | CRLF |
| plotter_sha256 | scripts/plot_results.py | CRLF |
| matrix_sha256 | docs/experiment-20261112-matrix.json | CRLF |
| summary_csv_sha256 | results/experiment-20261112/summary.csv | CRLF |
| tables_sha256 | report/chapters/experiment_tables.tex | CRLF |

Đây là cách diễn giải v1 lịch sử, không phải hash canonical mới. Ví dụ CSV:
LF `e22bd332f2db7a5d6e5255d43cb69753df6e6da8b793714bff48b166a094d9e1`
được tái dựng CRLF để kiểm đúng hash đã công bố
`d29321e28e43fed82a67d50928671b2bc2d17f80ef86c5e6b105adcf7cfcf66c`.
Publisher vốn lưu hash LF; không giả định tất cả file Windows đều CRLF.

Chỉ chấp nhận UTF-8 với xuống dòng đồng nhất LF hoặc CRLF; từ chối mixed endings
và CR đơn. Tái dựng đúng xuống dòng lịch sử, giữ mọi bytes còn lại: BOM,
whitespace, nội dung và sự có/vắng newline cuối. Nội dung bị sửa phải FAIL.
Hash plot script trong provenance hình dùng cùng cơ chế này.

`digest()` vẫn hash bytes nguyên bản: không chuẩn hóa raw JSONL, stdout/stderr,
manifest, dataset/metadata, binary, PDF, batch-index hay build evidence. Chúng
vẫn phải khớp SHA-256 và backup từng byte. Không sửa raw hoặc chạy benchmark.

## Kiểm chứng

`make test` trên cả Linux và Windows gọi `test-provenance` (stdlib, không cần D:).
Test tạo hai bản sao LF/CRLF của sáu file công bố, kiểm hash lịch sử và cả chín
provenance hình; sửa nội dung từng file phải bị từ chối trong cả hai kiểu.
Test cũng kiểm mixed/bare CR, BOM/whitespace/newline cuối và chứng minh thay
newline trong raw/manifest/dataset/binary/PDF làm đổi hash bytes, không được
đưa các file ấy vào hàm kiểm văn bản.

Kiểm toán đầy đủ khi có raw/dataset/backup:

```
python scripts/audit_final_evidence.py --out build/acceptance-new.json
```

Linux cần sao chép bằng chứng gốc nguyên bytes và dùng `--backup /path/to/backup`.
CI chỉ chứng minh phần provenance portable bằng file công khai; không tuyên bố
CI đã kiểm raw riêng tư hoặc truy cập backup ổ D.

## Kết quả local 15/11/2026

- Baseline Windows trước sửa: audit PASS. So sánh bằng hàm digest cũ trên hai
  bản CSV: CRLF PASS, LF FAIL `publication provenance summary_csv_sha256`.
- Sau sửa: audit đầy đủ PASS trên working tree Windows và hai bản sao tracked
  text LF/CRLF với raw/dataset được sao chép nguyên bytes, cùng backup ổ D.
  Bốn báo cáo audit (baseline + ba bản sau sửa) bằng nhau: 4968 file session,
  225 dòng, 81 dòng bảng, 36 hash PDF. Đây là kiểm LF/CRLF trên Windows;
  kiểm runtime Linux của phần portable do CI thực hiện, không đưa raw lên CI.
- UCRT64 full rebuild `mingw32-make -B CC=gcc PYTHON=python build test check-openmp`
  PASS: 1296 oracle BFS calls, 70 CLI, 15 fault cases, graph/serial/parallel,
  tools/timer/strict-negative OpenMP và ba regression tests provenance.
- Hai plotting tests trong venv hiện có PASS.
- Git diff xác nhận src/include/results/report, ba publication scripts và
  experiment matrix không đổi. Không chạy lại benchmark hoặc build lại hình.

Log/báo cáo local: `build/review-p2-tests.log`, `build/review-p2-baseline.json`,
`build/review-p2-windows.json`, `build/review-p2-checkout-{lf,crlf}/acceptance.json`.
