# BFS song song với OpenMP

Bài tập lớn học phần **Tính toán song song**. Dự án viết bằng C11 và dùng OpenMP để so sánh ba cách duyệt BFS trên CPU. Cả ba dùng cùng đồ thị CSR, nhận một đỉnh nguồn và tính khoảng cách ngắn nhất trên đồ thị không trọng số.

| Tùy chọn | Cách triển khai |
|---|---|
| `serial` | Hàng đợi FIFO |
| `omp-basic` | Duyệt theo tầng, dùng bộ đếm nguyên tử để ghi vào danh sách đỉnh kế tiếp |
| `omp-opt` | Duyệt theo tầng, ghi vào vùng đệm theo luồng rồi ghép danh sách đỉnh kế tiếp |

## Biên dịch và chạy thử

Trên Linux cần GCC, libgomp, GNU Make và Python 3. Trên Windows dùng môi trường MSYS2 UCRT64 với GCC, libgomp, Python và Make.

```sh
# Linux
make CC=gcc PYTHON=python3 build test check-openmp

# Windows, trong shell UCRT64
mingw32-make CC=gcc PYTHON=python build test check-openmp
```

```sh
./build/bfs --graph datasets/small/disconnected.edgelist --vertices 6 --source 0 --algo omp-opt --threads 4 --schedule static --directed
```

Trên Windows chạy `./build/bfs.exe`. Tệp đồ thị chứa một cặp đỉnh trên mỗi dòng. Đỉnh được đánh số từ 0. Dùng đúng một trong hai cờ `--directed` và `--undirected`. Ví dụ trên đi tới 4 đỉnh. Chương trình xuất JSON gồm trạng thái, số luồng thực tế, số đỉnh đi tới được và thời gian tính bằng giây. Thời gian chỉ tính lời gọi BFS.

## Kết quả thực nghiệm

Đo trên laptop Intel Core i5-12450HX, Windows 11, GCC 16.2.0. Mỗi ô là trung vị của 12 lượt đo sau khởi động, tính bằng ms. Hai bản OpenMP chạy 8 luồng với `static`.

| Đồ thị | Đỉnh | Serial | Basic | Optimized | Nhanh nhất |
|---|---:|---:|---:|---:|---|
| Chu trình | 2.048 | 0,0105 | 321,5206 | 516,1245 | Serial |
| Lưới | 6.144 | 0,0357 | 21,5734 | 36,0463 | Serial |
| Thang | 2.048 | 0,0161 | 136,3073 | 231,4461 | Serial |
| Cây bậc 3 nhỏ | 29.524 | 0,0951 | 2,8444 | 3,2873 | Serial |
| Cây nhị phân lớn | 16.777.215 | 1169,4313 | 765,4272 | 496,7921 | Optimized |
| Cây bậc 4 lớn | 5.592.405 | 163,6413 | 214,8783 | 130,3664 | Optimized |

Optimized đạt **2,35×** trên cây nhị phân lớn và **1,26×** trên cây bậc 4 lớn. Serial nhanh nhất trên bốn đồ thị còn lại. Xem cách tái lập và dữ liệu từng lượt trong [thư mục thực nghiệm](results/experiment-20261124/).

## Báo cáo

Mã LaTeX ở [report/](report/). Chạy `make report` với XeLaTeX và BibTeX để tạo `report/main.pdf`. Báo cáo có ba chương. Xem thêm [giao diện lập trình](docs/CONTRACT.md) và [thiết kế](docs/ARCHITECTURE.md).
