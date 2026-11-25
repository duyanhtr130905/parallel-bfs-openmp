# Nhật ký biên tập báo cáo Parallel BFS

## Cập nhật ngày 25/11/2026

- Lời cảm ơn ghi Hà Nội, thứ Ba, ngày 24 tháng 11 năm 2026 và đặt dòng ngày cùng chữ ký sát lề phải.
- Kiểm tra cấu hình bằng bộ đọc Registry, Windows API và danh mục gói MSYS2. Kết quả gồm Intel Core i5-12450HX, 4 P-core, 4 E-core, 12 luồng logic, L2 tổng 7 MiB, L3 12 MiB và 23,71 GiB RAM hệ điều hành sử dụng được. Dung lượng RAM lắp đặt và số kênh chưa xác nhận được vì truy vấn CIM và SMBIOS bị chặn.
- Tại thời điểm kiểm tra, máy dùng Windows 11 Home Single Language 26H2, build 26300.9974, libgomp UCRT64 16.2.0-6 và chế độ nguồn Balanced. Các giá trị này mô tả ngày 25/11. Báo cáo giữ các trường chưa có bằng chứng của phiên đo ngày 24/11, gồm phiên bản gói libgomp của phiên đo, cách gắn luồng, chế độ chờ, chế độ nguồn và tải nền.
- Rút thư mục tài liệu xuống 10 mục. Giữ ParallelBFS làm nguồn mã công khai cho kỹ thuật cấp vùng ghi bằng tổng tiền tố. ScienceDirect từ chối truy cập URL PII S1877050924005623. Chưa xác minh được tiêu đề, DOI và nội dung để đưa vào danh mục.
- Tạo lại các biểu đồ thời gian, hệ số tăng tốc, từng mẫu Serial và thời gian chia số tầng từ CSV gốc. Biểu đồ bề rộng tầng được tính từ cấu trúc đồ thị. Chương 2 giữ ba sơ đồ TikZ dùng để giải thích thuật toán. Bỏ hình minh họa cấu trúc sáu họ đồ thị ở Chương 3.
- Bản cập nhật có 34 trang, 8 hình, 9 bảng và 10 tài liệu tham khảo. Đã đối chiếu PDF, nhật ký LaTeX và SHA-256 của dữ liệu gốc. Không chạy lại benchmark.
- Nhóm cần xác nhận mã học phần MAT3148. Các mục cấu hình chưa có dữ liệu lịch sử vẫn được đánh dấu khi cần.

## Nhật ký bản ngày 24/11/2026

Ngày rà soát 24/11/2026. Phạm vi gồm nguồn LaTeX, hình, bảng, phân tích CSV và kịch bản chuẩn bị phép đo mở rộng.

## Đầu vào và đường cơ sở

| Đầu vào | Đối chiếu |
|---|---|
| LaTeX gốc | Lấy `report/main.tex`, preamble, bìa, ba chương và thư mục tài liệu tham khảo từ nhánh `main` của kho gốc. Giữ `extreport` 14 pt, A4, lề 30/20/25/25 mm, XeTeX, Latin Modern Roman và giãn dòng 1,5. |
| PDF gốc | Bản `main.pdf` 22 trang có Tóm tắt cũ và Chương 3 có bảng sáu đồ thị. Bản chuẩn trước sửa được lưu trong `baseline/`. |
| Mã đo và CSV | Các tệp `scripts/benchmark_six_graphs.c` và `results/experiment-20261124/raw.csv` trùng blob với GitHub. Giữ nguyên từng byte trong gói bàn giao. |
| Mã BFS | Đọc mã tại `fb990bf2ddb3adb6bac5e218ef32fd40adfc35cd`. Hai tệp OpenMP của snapshot cục bộ trùng blob tại commit đó. Không sửa BFS hoặc chạy lại phép đo ngày 24/11. |
| Báo cáo mẫu SVD | Đọc phần đầu và cách tổ chức báo cáo. Dùng để tham khảo bố cục, danh sách và cách dẫn bảng/hình. Mã MAT3148 trên bìa lấy từ mẫu và cần nhóm xác nhận. |

## Bản đồ mục cũ sang mục mới

| Nguồn cũ | Vị trí mới | Thay đổi |
|---|---|---|
| Bìa, Tóm tắt, danh sách đầu báo cáo | Phần đầu | Thêm mã học phần theo mẫu, lời cảm ơn và viết tắt. Viết lại Tóm tắt theo đợt 24/11. |
| 1.1 Bối cảnh | 1.1 | Rút gọn bối cảnh, gắn với câu hỏi về tổ chức công việc. |
| 1.2.1–1.2.2 Phát biểu | 1.3.1–1.3.2 | Giữ bài toán khoảng cách một nguồn và quy tắc đầu ra. So sánh cách triển khai chuyển sang 1.4 và 2.4. |
| Nghiên cứu liên quan rải trong các chương | 1.2 và 3.5.5 | Gom các nguồn theo hướng duyệt, hệ thống bộ nhớ và cách tập hợp đỉnh. |
| 1.3–1.6 Mục tiêu, phạm vi, đóng góp, bố cục | 1.4–1.7 | Sửa câu hỏi 3, viết đóng góp theo kết quả khoa học. Thông tin kho mã chuyển sang Phụ lục A. |
| 2.1, Hình 2.1 và Bảng 2.1–2.2 | 2.1 | Vẽ lại ví dụ BFS và gộp hai bảng. |
| 2.2 CSR | 2.2 | Dùng hai mảng trên ví dụ ba đỉnh. |
| 2.3 OpenMP, phần chỉ số trong 3.3 | 2.3–2.4 | Gộp định nghĩa hệ số, hiệu suất, độ nhạy và mô hình theo tầng. |
| 2.4 Ba phiên bản và Hình 2.2 | 2.5 | Định dạng lại ba thuật toán và vẽ một tầng Basic/Optimized theo mã thật. |
| 2.5 Tính đúng đắn và chi phí | 2.6 | Làm rõ tính nguyên tử, rào và chặn chi phí. |
| 3.1–3.3 Môi trường, dữ liệu, phương pháp | 3.1–3.3 | Thêm bảng cấu hình, quy tắc sinh và mô tả thứ tự đo. |
| 3.4, Bảng 3.2–3.4, Hình 3.1 | 3.4 và Phụ lục B | Gộp bảng chính, bỏ hình thanh quy đổi, bổ sung các hình vector. |
| 3.5–3.6 Thảo luận, kết luận | 3.5–3.8 | Thêm độ nhạy, chi phí theo tầng, hạn chế và hướng phát triển. |

## Các mâu thuẫn đã xử lý

- Báo cáo dùng duy nhất dữ liệu ngày 24/11/2026 cho kết quả chính. Tóm tắt, phạm vi và đóng góp thống nhất sáu đồ thị có hướng, 12 mẫu mỗi cặp cấu hình, 216 mẫu chính thức trong 252 lượt. Phụ lục A ghi một câu về dữ liệu lưu trong lịch sử.
- Câu hỏi 3 dùng số tầng, bề rộng tầng và cách thu tập đỉnh biên. So sánh số luồng và lập lịch chuyển sang hướng phát triển.
- Trên chu trình, thang và lưới, Serial **nhanh hơn** OpenMP theo CSV. Bản viết theo dữ liệu tại đây vì một câu mô tả mục Tóm tắt trong yêu cầu ghi chiều so sánh ngược.
- Đánh số theo cấu trúc không đồng nghĩa khoảng cách bằng nhãn. Quan hệ đó đúng với chu trình. Thang và lưới dùng khoảng cách theo tọa độ. Các cây xáo mọi nhãn khác gốc với các hạt giống 71, 2026 và 83.
- Các tứ phân vị và hiệu suất dựa trên mẫu chính thức. Nhãn `E₈ (%)` biểu thị đại lượng theo phần trăm.

## Đối chiếu nhanh với CSV

- SHA-256 của CSV `aa557801b81e9eefd6807d799d8228e83bb9dce0115ebfefe86c0515bb898920`.
- Script xác minh tính duy nhất của vòng đo, số luồng, thời gian dương, thứ tự luân phiên và đặc trưng cấu trúc trước khi sinh bảng.
- Đã so 72 ô thời gian, 12 ô hiệu suất và 12 giá trị hệ số trong bảng/hình cũ với giá trị chưa làm tròn. Tất cả nằm trong nửa đơn vị chữ số cuối của giá trị cũ. Có 32 ô đúng tại biên nửa đơn vị, do nội suy tạo giá trị ở giữa hai cách làm tròn. Một số chữ số cuối thay đổi khi định dạng thống nhất bằng số thập phân chính xác.
- Từ trung vị gốc, Serial đứng đầu trên bốn đồ thị. Optimized đứng đầu trên cây nhị phân lớn và cây bậc bốn lớn, với `S₈` lần lượt khoảng 2,3540 và 1,2552.

## Kiểm tra các mục 2.3–2.6 của yêu cầu

| Kiểm tra | Phát hiện | Cách dùng |
|---|---|---|
| 2.3 Phân bố Serial của hai cây lớn | Cây nhị phân có 5 vòng 0–4 trong 573,66–604,68 ms, 7 vòng 5–11 trong 1 116,47–1 303,45 ms. Giả thuyết các lượt chậm tập trung ở vòng đầu bị bác bỏ bởi thứ tự mẫu. Cây bậc bốn dao động 154,83–174,94 ms. | Vẽ từng mẫu theo vòng. Giữ trung vị làm kết quả chính. Bảng độ nhạy thay mốc Serial bằng Q₁ hoặc Q₃. Optimized trên cây nhị phân đạt 1,201–2,579 theo hai mốc, với trung vị 2,354. Basic đổi thứ hạng theo Q₁. |
| 2.4 Đánh số | Bộ sinh giữ nhãn gốc, chỉ xáo các nhãn còn lại của cây. Chu trình, thang, lưới giữ thứ tự cấu trúc. | Nêu nhiễu do nhãn và quy mô cùng thay đổi. Chồng lấp độ trễ là giả thuyết chưa đo. |
| 2.5 Chi phí theo tầng | Basic có 0,157 / 0,133 / 0,136 ms mỗi tầng. Optimized có 0,252 / 0,226 / 0,227 ms mỗi tầng. Thứ tự chu trình, thang, lưới. Tỷ số thời gian 1,605–1,698 gần tỷ số rào 5/3. | Giữ phân tích. Đây là thời gian toàn lời gọi chia số tầng. Số rào hỗ trợ một giả thuyết về chi phí, chưa tách thời gian từng rào. |
| 2.6 Mã và thuật toán | Basic có 3 rào ngầm từ `single`, `omp for`, `single`; không có rào tường minh trong vòng tầng. Optimized có 4 rào ngầm và 1 tường minh giữa chép đoạn với hoán đổi. Cả hai có một vùng `parallel` suốt lời gọi, không có `nowait` trong các pha này. | Cập nhật mã giả, vị trí rào, `memory_order_relaxed` và phát biểu độ phức tạp. Loại rào khởi tạo, kết thúc vùng và nhánh lỗi khỏi số rào mỗi tầng. Giải thích chặn `O(n+p)` cho bộ đệm có tăng dung lượng theo cấp số nhân. |

## Thuật ngữ thống nhất

| Khái niệm | Dạng dùng |
|---|---|
| Level | tầng |
| Directed edge | cung |
| Frontier | tập đỉnh biên |
| Thread team | nhóm luồng |
| Barrier | rào đồng bộ |
| Overhead | chi phí phụ trội |
| Schedule | chính sách lập lịch |
| Speedup | hệ số tăng tốc |
| Parallel efficiency | hiệu suất |
| Scaling | khả năng mở rộng |
| IQR | độ rộng khoảng tứ phân vị |
| Benchmark configurations | bộ cấu hình thực nghiệm |
| Đại từ | nhóm trong thân báo cáo, chúng em ở lời cảm ơn |

## Tài liệu tham khảo

- Đối chiếu thông tin xuất bản với MIT Press, IEEE/SC qua bản tác giả, Wiley, MIT DSpace/ACM, arXiv, Springer, Netlib, OpenMP, Microsoft Learn, Intel và SNAP. Báo cáo dùng trích dẫn số qua một tệp `refs.bib`.
- Sửa tác giả công trình so sánh hệ xử lý đồ thị thành Samuel Pollard và Boyana Norris. Bản arXiv là tài liệu được trích.
- Danh mục của Quinten De Man xác nhận thứ tự De Man, Wen, Dhulipala và nơi công bố FCPC 2025. URL PDF của NSF chưa đọc được, nên chưa đưa số liệu riêng về việc giới hạn nhóm luồng 8–16 vào thân báo cáo.
- README ParallelBFS xác nhận cách phân vùng và tổng tiền tố trên bậc ra. Báo cáo phân biệt tổng tiền tố bậc ra của dự án đó và tổng tiền tố số phần tử đã thu của Optimized.

## Kiểm chứng bản bàn giao

- Bản mới biên dịch từ mã LaTeX bằng Tectonic 0.17 (XeTeX, BibTeX và xdvipdfmx) với tài nguyên TeX Live tương thích, ra 34 trang A4. Giữ công thức Makefile cho XeLaTeX và BibTeX. Nhật ký bản cuối không có lỗi LaTeX, cảnh báo tham chiếu, ký tự thiếu hoặc hộp chữ tràn.
- Kiểm tra bố cục PDF, ba chương và hai phụ lục, chín hình vector và chín bảng. Mọi hình, bảng và thuật toán có tham chiếu trong thân văn bản. Kiểm tra chuỗi cũ và các giá trị trọng tâm trên PDF.
- PDF đường cơ sở là bản 22 trang đã biên dịch của kho, lấy từ gói CI mang mã 150d97682797113a9737a0bbd90a1013abcf8f37. Lần dựng lại bản cũ với Tectonic báo lỗi ánh xạ phông cho hình dùng môi trường picture. Dùng PDF CI làm bản đối chiếu chính.
- Kịch bản mở rộng đã qua kiểm tra cú pháp và chế độ lập kế hoạch gồm 37 cấu hình mỗi cặp đồ thị và nguồn. Chưa chạy lệnh đo mở rộng.

## Việc nhóm cần tự làm

1. Xác nhận mã học phần MAT3148 và điền ngày, tháng, năm ở Lời cảm ơn.
2. Bổ sung dung lượng/kênh RAM, L2, bản build Windows, phiên bản gói libgomp, bố trí luồng, chế độ chờ/nguồn và tải nền của **phiên đo gốc** khi còn bằng chứng. Thông số hiện tại của laptop chỉ xác nhận cấu hình máy tại thời điểm kiểm tra.
3. Nếu muốn trích kết quả chi tiết của De Man, Wen và Dhulipala, đối chiếu lại bài toàn văn từ proceedings hoặc bản tác giả.
4. Nếu muốn trả lời câu hỏi về số luồng và lịch, chạy script mở rộng trên laptop của nhóm. Kết quả ghi JSONL riêng. Quy trình này gọi CLI theo cấu hình nên cần mô tả riêng khi báo cáo.

Lệnh PowerShell để thu thông tin máy:

```powershell
Get-CimInstance Win32_Processor |
    Select Name,NumberOfCores,NumberOfLogicalProcessors,L2CacheSize,L3CacheSize
Get-CimInstance Win32_ComputerSystem | Select TotalPhysicalMemory
Get-CimInstance Win32_OperatingSystem | Select Caption,Version,BuildNumber
powercfg /getactivescheme
```

## 25/11/2026 — Thực nghiệm bổ sung và nghiệm thu báo cáo

- Giữ sáu đồ thị phiên 24/11 và dữ liệu CSV SHA-256 `aa557801b81e9eefd6807d799d8228e83bb9dce0115ebfefe86c0515bb898920`. Giữ ba sơ đồ lý thuyết, các bảng và biểu đồ phiên trước.
- Đo sáu đồ thị tổng hợp bổ sung với 216 mẫu chính thức và 36 warm-up. Serial và Optimized mỗi bản dẫn đầu ở ba đầu vào. Thêm bảng, hình thời gian/IQR, speedup, frontier và hình minh họa cấu trúc cho cả hai đợt.
- Bổ sung kiểm chứng toàn mảng khoảng cách sau mỗi lời gọi, hồ sơ băm, kiểm thử parser, generator, và tái tạo bảng trong CI. Giao thức dùng một CSR trong mỗi tiến trình; phép khảo sát SNAP qua CLI hiện có dùng giao thức khác.
- Biên tập ba chương, cập nhật danh mục tài liệu được trích và làm rõ giới hạn dữ liệu môi trường lịch sử. [Hồ sơ nguồn](docs/REFERENCE_AUDIT_20261125.md) và [hồ sơ phép đo](results/experiment-20261125/README.md) ghi bằng chứng.
- Bản bàn giao có 39 trang, ba chương, 11 hình, 11 bảng và 10 mục tham khảo. SHA-256 PDF là `9c692007d668bb3fc42a4f3d5d0753afaa9ec3057a6bf2e9100bc0fb617be407`. Cấu hình bìa và ngày ký giữ theo bản gốc.
- UCRT64 đã chạy build, test, check-openmp, test-plots và test-supplement. Windows thiếu lệnh xelatex độc lập, nên bản PDF cục bộ được biên dịch bằng XeTeX và BibTeX đi kèm Tectonic, với cùng font Latin Modern Roman và gói TeX đã có. Quy trình XeLaTeX/BibTeX của Makefile được giữ để chạy trên CI.

