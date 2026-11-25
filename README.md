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

## Phiên đo ngày 24/11/2026

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

## Phiên đo bổ sung ngày 25/11/2026

Cùng ba phiên bản và cấu hình 1/8 luồng, lịch tĩnh, nguồn 0. Mỗi ô là trung vị 12 mẫu, tính bằng ms. Các lượt được kiểm chứng toàn bộ khoảng cách với BFS tham chiếu.

| Đồ thị tổng hợp | Serial | Basic | Optimized | Nhanh nhất |
|---|---:|---:|---:|---|
| Đường đi | 0,0048 | 105,218 | 174,767 | Serial |
| Sao | 0,7051 | 3,858 | 3,290 | Serial |
| Hai lưới rời | 0,1293 | 60,829 | 104,869 | Serial |
| Vòng và cung ngẫu nhiên | 22,785 | 25,015 | 19,487 | Optimized |
| Phân tầng hội tụ | 51,802 | 48,431 | 37,575 | Optimized |
| Phân tầng hoán vị | 151,158 | 85,308 | 71,168 | Optimized |

Xem [dữ liệu, manifest và lệnh tái lập](results/experiment-20261125/README.md).

## Khảo sát theo số luồng

Trong bộ 12 đồ thị cố định, Serial có trung vị thấp nhất ở 7 đồ thị và
Optimized ở 5 đồ thị. Phiên khảo sát luồng riêng đo 1, 2, 4, 8 và 12 luồng
trên ba đầu vào. Optimized đạt trung vị tốt nhất tại 12 luồng trên vòng
có cung ngẫu nhiên và phân tầng hoán vị, lần lượt khoảng 1,02× và 1,61×
so với Serial cùng phiên. Trên đường đi, tăng số luồng làm hai bản OpenMP
chậm hơn. [Kế hoạch, raw và lệnh kiểm thử](results/experiment-scaling-20261125/)

## Báo cáo

Mã LaTeX ở [report/](report/). Chạy `make report` với XeLaTeX và BibTeX để tạo `report/main.pdf`. Báo cáo có ba chương. Xem thêm [giao diện lập trình](docs/CONTRACT.md) và [thiết kế](docs/ARCHITECTURE.md).

[Bản PDF bàn giao](report/published/main.pdf) và [nhật ký biên tập](CHANGELOG_BAOCAO.md). Bản PDF mới nhất của nguồn LaTeX có thể tải từ artifact `bootstrap-report-*` của GitHub Actions tại commit tương ứng.
Dùng `make tables figures supplement-artifacts review-artifacts report` để tái tạo từ dữ liệu đã lưu. Cần Python 3.11+, Matplotlib, psutil, XeLaTeX và BibTeX. Trong UCRT64, dùng `mingw32-make` thay cho `make`.

## Kịch bản khảo sát đồ thị SNAP

Kịch bản này dùng CLI trong tiến trình mới cho mỗi mẫu. Các phiên trong báo cáo đo nhiều lần trên một CSR trong cùng tiến trình. SNAP vẫn là hướng phát triển.

Xem kế hoạch mà chưa gọi BFS:

```powershell
python scripts/benchmark_extended.py
```

Trên máy của nhóm, dùng bản CLI đã biên dịch từ commit đo. Cung cấp edge list SNAP gốc dạng văn bản hoặc gzip từ [roadNet-CA](https://snap.stanford.edu/data/roadNet-CA.html) và [web-Stanford](https://snap.stanford.edu/data/web-Stanford.html).

```powershell
python scripts/benchmark_extended.py --run --bfs build/bfs.exe --road roadNet-CA.txt.gz --web web-Stanford.txt.gz --output extended.jsonl
```

Script ánh xạ các nhãn đỉnh xuất hiện trong edge list về một đoạn liên tiếp. Mỗi đồ thị dùng ba nguồn theo thứ tự nhãn gốc. roadNet-CA giữ ngữ nghĩa vô hướng, còn web-Stanford giữ hướng cung. Mỗi cặp đồ thị và nguồn dùng hai vòng khởi động, 12 vòng chính thức và thứ tự cấu hình xáo bằng hạt giống cố định. Mốc Serial dùng một luồng. Hai bản OpenMP thử sáu số luồng và ba chính sách lập lịch. Script tạo tệp kết quả mới và để nguyên CSV ngày 24/11/2026.

