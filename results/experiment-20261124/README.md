# Thực nghiệm ngày 24/11/2026

Mã BFS tại commit `fb990bf2ddb3adb6bac5e218ef32fd40adfc35cd`. Đo trên Windows 11, Intel Core i5-12450HX, GCC UCRT64 16.2.0 và libgomp. Các đồ thị có hướng, sinh trực tiếp trong RAM với nguồn 0. Cấu trúc, số đỉnh và seed nằm trong chương trình đo. Chạy ở thư mục gốc repo.

```powershell
gcc -O2 -std=c11 -Wall -Wextra -Werror -fopenmp -Iinclude -Isrc scripts/benchmark_six_graphs.c src/graph.c src/bfs_serial.c src/bfs_parallel_basic.c src/bfs_parallel_optimized.c -o benchmark_six_graphs.exe
if ($LASTEXITCODE -ne 0) { throw 'Biên dịch thất bại' }
cmd /c ".\benchmark_six_graphs.exe > benchmark_six_graphs.csv"
if ($LASTEXITCODE -ne 0) { throw 'Phép đo hoặc kiểm tra khoảng cách thất bại' }
```

Trên Linux bỏ hậu tố `.exe` và chuyển hướng stdout bằng shell. Cây lớn có 16,8 triệu đỉnh nên cần RAM trống cho CSR và các vùng đệm. Mỗi cấu hình có hai lượt khởi động (vòng -2 và -1) và 12 mẫu chính thức (vòng 0–11). Ba cấu hình chạy luân phiên thứ tự. Chỉ tính trung vị từ mẫu chính thức, theo từng cặp đồ thị và thuật toán. Speedup so với Serial là trung vị Serial chia cho trung vị OpenMP tương ứng. Mỗi lần chạy xác minh toàn bộ mảng khoảng cách và số luồng thực tế. Phép đo dùng chung CSR trong một tiến trình, quanh lời gọi BFS.

[CSV gốc](raw.csv) chứa 252 dòng đo, trong đó 216 mẫu chính thức. Bộ đo này thay bộ đồ thị cũ trong README và báo cáo. Dữ liệu trước đây vẫn có trong lịch sử của dự án để đối chiếu.
