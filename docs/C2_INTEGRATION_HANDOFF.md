# Bàn giao tích hợp C — 12/11/2026

Relates to #5. Giữ duy nhất Draft PR #7 và branch docs/c1-academic-report.
Người dùng cho phép serial-only sau #8; không đổi API v1 hay sửa module A/B.

## Phạm vi C hiện tại

main f73514d đã có graph/serial. CLI serial link hai module thật, cấp phát
output, lấy BFSMetrics và đo omp_get_wtime trên cùng caller ngay quanh BFS.
Bộ xác minh ngoài timer kiểm edge inequalities + predecessor giảm khoảng cách:
mọi vertex reachable có đường về source và không có cạnh cho đường ngắn hơn.
Chỉ xuất JSONL một dòng khi status/metrics/timer/distance hợp lệ, cleanup mọi
đường thoát. Serial requested giữ nguyên, actual=1, schedule=none.
OpenMP trả exit3 trước I/O vì chưa link module B; không fallback serial.

Makefile giữ correctness A và tools C, thêm CLI validation/integration trong
cả hai job OS sẵn có. Không đổi workflow hoặc required checks.
Không có benchmark chính thức hoặc bằng chứng full integration ba thuật toán.

## Dũng: cập nhật chính PR #9

HEAD kiểm tra: 640c0201f51cb7313d524447dca9bb5c116084ab; sau #8 merge PR bị conflict.
Không tạo PR mới, không rewrite/force push. Trên checkout sạch của B:

```text
git status --short --branch
git fetch upstream
git switch main
git merge --ff-only upstream/main
git switch feat/parallel-bfs
git merge upstream/main
```

Nếu main không fast-forward hoặc có thay đổi chưa commit, bảo toàn và kiểm tra
trước; không reset để ép khớp. Sau resolve, chạy tests trước commit/push thường.
Giữ test-bfs (graph+serial) và test-parallel, beamer2012 và openmp52,
clean danh sách test_graph/test_serial/test_parallel trên cả Windows/Linux.
B không nhập nhánh C hoặc sửa CLI; C sẽ merge main sau #9.

- Test parallel hiện standalone: cần link graph.c + bfs_serial.c thật trong
  test target và đối chiếu toàn distance cho cả Basic/Optimized với serial đã
  qua oracle; test loader, nhiều source, directed/undirected, seed, nhiều
  threads và static/dynamic/guided. Kiểm metrics/reset/CSR bất biến và contention.
- Chương 3: sửa barrier=mức=đường kính; mức phụ thuộc source, mỗi mức có thể có
  nhiều barriers. Mô tả overhead prefix p mỗi tầng L của optimized (pL), không
  khẳng định work luôn độc lập p. Đây là việc B cần tự cập nhật.
- Điền PR title/body bằng scope, dependency #8 đã merge, command/results/CI,
  giới hạn và reviewer. Nên giữ Draft đến khi đủ tích hợp; không coi CI cũ là
  bằng chứng sau resolve. GCC C11/OpenMP trên Linux và Windows UCRT64 + report
  phải PASS tại HEAD cuối, sau đó nhờ Đức review/approve độc lập.

## C sau #9 merge

Merge main vào cùng nhánh #7, link cả hai module B, dispatch đúng hàm 5 đối số,
actual lấy metrics trong BFS, mở rộng CLI test ba thuật toán và đối chiếu đầy
đủ distance trên cùng commit. Không giả actual từ request/probe.
Chỉ sau correctness mới dùng runner: máy/dataset/flags/commit xác minh, 1 warm-up
và >=10 mẫu/config, order seed, raw/manifest/hash và giữ lỗi/outlier. Chạy ít nhất
path/star/grid với kích thước phù hợp; median/IQR/speedup/efficiency từ raw thật.
Điền Chương 5/6 và abstract/kết luận theo kết quả, kể cả slowdown; build và xem PDF.

## Ghi nhận polish báo cáo cho giai đoạn cuối

Theo approval #8: chapter2.tex dòng 87 thiếu line break; hình mũi tên hụt cần
kiểm PDF và self-loop đỉnh 4 cần rõ. ARCHITECTURE/CONTRACT còn câu bootstrap
chưa có graph/BFS; REFERENCES_AUDIT cần ghi Beamer. Ghi nhận, chưa sửa chương A
hoặc nội dung hợp đồng trong phiên CLI này. Test dùng assert có thể mất tác dụng
nếu NDEBUG; flags mặc định không định nghĩa NDEBUG. Không tuyên bố report đã
được visual QA lại chỉ từ job LaTeX xanh.
