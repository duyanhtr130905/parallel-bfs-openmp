# Role C — thực nghiệm thật và hồ sơ nghiệm thu

Commit đo `ab588fb8ab535b796f0c8b6d5e98a7efe5ebc76c`, sau local correctness và
[CI3/3 PASS](https://github.com/duyanhtr130905/parallel-bfs-openmp/actions/runs/43191978766).
Không sửa module thuật toán A/B, header API A/B hoặc CSR semantics.

## Bằng chứng đã thực thi

- MSYS2 UCRT64 có sẵn tại C:/tools/msys64, cập nhật đầy đủ; GCC/libgomp16.2.0-6,
  Make4.4.1-5, Python3.14.10-1. Target x86_64-w64-mingw32, _OPENMP202111.
- `mingw32-make -B CC=gcc PYTHON=python build test check-openmp` thay binary Clang
  cũ sau khi backup. Sau commit đo, chạy lại toàn bộ test PASS, gồm1296 integration
  calls với Floyd–Warshall từ input edges, full distance/CSR byte equality,
  70 CLI,15 faults, parallel stress, parser/serial và OpenMP strict/negative tests.
- Plot tests PASS: ideal S=p và schedule theo actual team; analyzer regression
  từ chối thiếu nhóm/warm-up, lặp trùng, hash sai và binary thay sau correctness.
- Probe OpenMP Windows1ms làm Serial path=0; người dùng duyệt QPC10MHz,
  ADR-0003 ghi quyết định, test timer và toàn correctness/CI lại trước đo.
- Ma trận được commit trước mẫu chính thức: 6 graphs/9 tổ hợp đồ thị-nguồn,225 configs,
  warm-up225 + measured2250; không lỗi/timeout/loại outlier. Requested=actual1/2/4/8.
- Thời gian16:32:58–16:42:26 UTC+7 ngày12/11/2026. Monitor AC=1 suốt,
  min free RAM11.135.807.488byte; CPU nền trước phiên1,30–19,01%.
- Mọi raw/log hash đã so với bản sao ổ D. sessions.json chứa session/hash đầy đủ.

## Kết quả và sản phẩm

Không có speedup>1 trong216 cấu hình OpenMP. MaxS0,2914 là Optimized1/static/
grid512/source0. Basic8/static: path8192 922,0907ms so Serial0,05185ms;
star1M26,41575ms so3,1294ms; grid512112,67435ms so1,6942ms.
Optimized không thắng nhất quán; dynamic chậm rõ trên star/grid nhiều luồng.
Mọi kết luận chỉ cho một BFS/process mới; warm-up không tạo warmed team.

- [Bảng225 cấu hình, dữ liệu/provenance và lệnh tái tạo](../results/experiment-20261112/README.md).
- [Ma trận đã đăng ký](experiment-20261112-matrix.json).
- 36 figures tái tạo từ raw,12 hình lớn trong báo cáo; runtime/IQR, speedup/ideal,
  efficiency và scheduling/IQR. Trục log khi cần, không giấu slowdown.
- Chương1/4/5/6 và abstract đã điền số thật; giữ nội dung lý thuyết/thuật toán A/B,
  chỉ cập nhật các câu chuyển tiếp đã lỗi thời. Bìa ghi Nguyễn Hải Vinh theo xác nhận.
- Tài liệu QPC/MSYS2 chính thức thêm vào bibliography; DOI/URL được hiển thị.
- PDF do XeLaTeX+BibTeX CI đúng PR HEAD; lấy artifact mới, kiểm log và render/xem
  mọi trang trước bàn giao. Hồ sơ cuối cục bộ ở build/experiment-20261112/.

## Dữ liệu và giới hạn

Raw: results/raw/SESSION. Backup:
D:/Code/parallel-bfs-evidence/20261112-1616/official-ab588fb/SESSION.
Không commit raw hoặc binary; giữ đến hết phúc khảo. Backup cùng laptop chưa
phải off-device. Không đo nhiệt, profiling/race detector hoặc tái lập máy thứ hai.
Shuffle trong từng dataset/source; khác biệt giữa khối còn confound thời điểm.
Một số cấu hình có IQR cao; không đưa kết luận nhân quả từ khác biệt nhỏ.

Review công cụ/timer bởi Codex agent độc lập không tìm thấy blocker; đây là
AI-assisted review, không thay human approval. CI final/PDF theo đúng HEAD mới
nhất ở PR #7, không dùng run của commit đo làm bằng chứng cho thay đổi report sau.

## Checklist cho người nghiệm thu độc lập

- [ ] Đối chiếu đo commit ab588fb, proof log/binary hash, CI43191978766.
- [ ] Kiểm chín manifest: đầy đủ25 configs ×11,2250 raw samples, actual teams.
- [ ] So raw/log hashes với ổ D và tái tạo CSV/tables/figures.
- [ ] Đọc mô hình timer/QPC, fresh process, số mẫu, limits và toàn bộ kết luận.
- [ ] Kiểm artifact PDF/LaTeX log đúng final PR HEAD, mọi trang và tài liệu tham khảo.
- [ ] Reviewer nhóm nghiệm thu/approval độc lập. PR #7 giữ Draft, Issue #5 OPEN;
  không tự approve hoặc merge.
