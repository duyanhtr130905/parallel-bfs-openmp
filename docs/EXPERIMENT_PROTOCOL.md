# Quy trình thực nghiệm v1 (chưa thực thi)

Chỉ bắt đầu khi loader + serial + OpenMP đã triển khai và qua correctness review.
Không dùng số liệu README của repository tham khảo làm số liệu nhóm.

## Kiểm chứng trước đo

Xác minh oracle tay trên đồ thị nhỏ; so mọi phần tử distance với serial.
Serial cũng phải qua oracle tay, không tự coi serial là đúng. Bao gồm chuỗi, sao,
diamond, disconnected/isolated, cycle, self-loop/duplicate, n=1, nhiều source.
Mỗi cấu hình OpenMP kiểm thử lặp nhiều lần để phát hiện race; test lặp không phải
bằng chứng toán học không có race. Review claim visited, barrier và frontier capacity.
Test input lỗi và size overflow độc lập. Sai kết quả thì không nhận mẫu benchmark.

## Mẫu và metadata

- Cố định SHA commit, compiler/version/flags, OpenMP `_OPENMP`, Windows build,
  CPU/model, physical/logical cores, RAM, nguồn điện, chế độ nguồn, background load.
- Ghi dataset URL/giấy phép, SHA-256, seed tạo nếu có, n, input edges, CSR arcs,
  directed, source, reachable. Cùng dataset/source/CSR semantics cho mọi thuật toán.
- Ghi OMP_NUM_THREADS, OMP_DYNAMIC=FALSE, OMP_PROC_BIND và OMP_PLACES (giá trị
  dùng thực tế hoặc unset), requested và actual team size. Tránh oversubscription.
  Chưa giả định runtime Windows hỗ trợ mọi affinity policy.
- Tập đề xuất: 1,2,4,... đến số logical cores; ghi thêm số physical cores nếu khác.
  So static/dynamic/guided. Không thay build flags giữa các thuật toán so sánh.

## Đo

Wall-clock omp_get_wtime cùng thread, đơn vị giây, chỉ quanh lời gọi BFS;
output cấp phát trước, distance init/scratch trong BFS được tính. Loại I/O,
CSR construction, correctness check, serialization khỏi khoảng đo.
Một warm-up không ghi thống kê, ít nhất 10 mẫu đo cho mỗi cấu hình/dataset/source;
đồ thị quá nhỏ phải báo hạn chế độ phân giải/overhead. Không trừ overhead tùy ý.
Đảo thứ tự cấu hình với seed cố định để giảm sai lệch nhiệt; lưu thứ tự thực tế.
Một JSONL mỗi mẫu thành công theo CONTRACT, metadata/run index/warm-up lưu
ở manifest kèm SHA-256 file raw. Không chạy benchmark qua CLI bootstrap.

Lưu mọi mẫu và lỗi; không âm thầm bỏ outlier. Báo median, min, max và IQR;
speedup = median(T_serial)/median(T_parallel,p), efficiency = speedup/p (p là
team thực tế ổn định). Nếu p thay đổi thì tách nhóm hoặc đánh dấu không so sánh.
Nêu speedup so serial và scaling so omp-1 là hai đại lượng riêng.
Không coi speedup>1 là điều kiện correctness. Chưa đặt ngưỡng hiệu năng bảo đảm.

Các file raw/figures chưa có. Chỉ thêm bảng/biểu đồ báo cáo từ mẫu có manifest
và script tái tạo; biểu đồ phải có đơn vị, số lần lặp, source, cấu hình, độ biến thiên.
