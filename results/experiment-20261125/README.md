# Phiên bổ sung ngày 25/11/2026

Phiên chính thức chạy lúc 08:56–08:57 giờ Việt Nam. Mỗi cặp đồ thị–phiên bản có
2 lượt khởi động và 12 mẫu chính thức. Tổng cộng 252 lượt đều trả đúng toàn bộ
mảng khoảng cách và đúng số luồng. Dữ liệu đo hiệu năng chỉ thuộc máy này.

- [Kế hoạch chốt trước khi đo](plan.json), [manifest](manifest.json) và [thống kê](summary.json).
- Mỗi CSV chứa số vòng, thứ tự, thời điểm UTC, phiên bản, số luồng, số đo ms,
  trạng thái và kết quả kiểm chứng. Mỗi tệp profile lưu số cung CSR, số cung
  xét từ nguồn và số đỉnh từng tầng.
- Trình sinh edge list và trình điều phối ở [run_supplement.py](../../scripts/run_supplement.py),
  trình đo ở [benchmark_supplement.c](../../scripts/benchmark_supplement.c).
  Khôi phục edge list từ tham số trong plan và đối chiếu SHA-256 trong manifest.

## Tái lập

```sh
python scripts/run_supplement.py --commit 0d5a53b53d94d2cee584323ad7209591539876cf --output results/repeat-local
python scripts/summarize_supplement.py results/experiment-20261125
```

Cần Python 3.11+, psutil, GCC với OpenMP và Matplotlib. Lệnh thứ nhất chạy phép
đo mới và chỉ chấp nhận thư mục đầu ra chưa tồn tại. Lệnh thứ hai đọc CSV và
profile đã lưu, kiểm manifest rồi tạo bảng và hình trong report. Có thể chỉ
định `--report` để ghi vào thư mục khác. Bộ phân tích dùng tứ phân vị nội suy
tuyến tính và chỉ dùng vòng 0–11.

Đầu vào lớn nhất có gần tám triệu bản ghi và khoảng một triệu đỉnh, tương ứng
khoảng 100 MiB cho danh sách cung và CSR chưa tính các mảng phụ trợ, dung
lượng dự phòng của trình đọc và bộ đệm BFS. Phiên chạy kiểm tra tối thiểu
2 GiB RAM trống trước từng đầu vào, đồng thời áp timeout 180 giây mỗi đồ thị.
Danh sách cạnh được sinh cục bộ. Thư mục Git lưu các hash cùng raw đo, không
đóng gói các edge list lớn.

## Môi trường và điều kiện đo

Mã CPU từ Registry là Intel Core i5-12450HX. Windows báo 8 lõi vật lý, 12 luồng
logic, khoảng 23,71 GiB RAM khả dụng cho hệ điều hành và build 26300.9974. Intel
công bố 4 P-core, 4 E-core và 12 MB Smart Cache. Xem [đặc tả Intel](https://www.intel.com/content/www/us/en/products/sku/228794/).
Windows không cung cấp dữ liệu dung lượng vật lý lắp đặt qua
`GetPhysicallyInstalledSystemMemory` trong phiên kiểm tra. Số thanh, số kênh,
vị trí từng luồng và nhiệt độ chưa được xác định.

GCC 16.2.0 ở MSYS2 UCRT64. Kiểm tra sau khi chạy, cơ sở dữ liệu gói cục bộ
ghi libgomp 16.2.0-6 và DLL tại thư mục UCRT64 có SHA-256
`ccaf59dc8cff15ace88ab47acD68a5b014167cad8f960e7683466a4c821e41c4`.
Manifest ghi nguồn điện, RAM và tải nền lấy mẫu một giây trước/sau từng đồ thị.
Các trường theo thời gian diễn tả phiên 25/11, riêng thông tin thực tế ngày
24/11 được giữ theo hồ sơ gốc.

Lần thử biên dịch đầu thiếu khai báo `omp_set_dynamic` trên Windows. Trình đo
được bổ sung `omp.h` rồi chạy trong thư mục phiên mới với cùng danh sách đồ thị.
Lần biên dịch thất bại không ghi mẫu, xem [kế hoạch và manifest lần thử](compile-attempt/).
