# Kiểm toán tài liệu tham khảo ngày 25/11/2026

## Rà soát bản nghiệm thu cuối

- Giữ Barrett và cộng sự. Mục CRS trên Netlib mô tả cách lưu chỉ số cột theo hàng và dùng mảng chỉ số bắt đầu từng hàng, đúng phần được vận dụng trong ví dụ CSR của Chương 2. Báo cáo giải thích riêng quy tắc nhân đôi cạnh vô hướng theo mã dự án.
- Đối chiếu bản tác giả của Agarwal, Petrini, Pasetto và Bader, *Scalable Graph Exploration on Multicore Processors*, SC 2010, DOI 10.1109/SC.2010.46. Abstract và mục thiết kế mô tả tối ưu truy cập bộ nhớ cùng chiến lược riêng cho nền tảng nhiều socket. Phép đo của đề tài không thu bộ đếm phần cứng hay kiểm soát NUMA, nên giữ Barrett để dẫn trực tiếp cách biểu diễn dữ liệu. [Bản tác giả](https://davidbader.net/publication/2010-appb/2010-appb.pdf)
- Hai mục OpenMP năm 2024 chỉ được dùng trong phạm vi đã đọc: abstract và metadata công khai của Wiley và ScienceDirect, đối chiếu DOI 10.1002/cpe.8119 và 10.1016/j.procs.2024.03.203. Nhận định về cấu trúc bag và quy mô mạng lấy từ các phần này. Các chỉ số phổ biến thiếu nguồn nhất quán được giữ ở trạng thái chưa xác minh.
- Intel xác nhận 4 P-core, 4 E-core, 12 luồng logic và thông số ghi là 12 MB Intel Smart Cache. Bản cuối dùng đơn vị của hãng. Tổng L2 chưa đối chiếu độc lập, nên bỏ trị số khỏi phần cấu hình đã xác minh. [Đặc tả Intel](https://www.intel.com/content/www/us/en/products/sku/228794/intel-core-i512450hx-processor-12m-cache-up-to-4-40-ghz/specifications.html)

Các con số trong cột cuối là dữ liệu công khai khi tra cứu. Các nền tảng dùng phạm vi đếm khác nhau.

| Tài liệu | Bằng chứng và phạm vi đọc | Quyết định và vị trí dùng | Số liệu công khai |
|---|---|---|---|
| Cormen, Leiserson, Rivest và Stein, bản 4, 2022 | [MIT Press](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/), thông tin sách | Giữ cho định nghĩa BFS và khoảng cách. Chương 1–2 | Chưa xác minh |
| Barrett và cộng sự, 1994 | [Netlib](https://netlib.org/linalg/html_templates/node91.html), mục nén theo hàng | Giữ cho quy tắc CSR. Chương 2 | Chưa xác minh |
| Beamer, Asanović và Patterson, 2013 | [Toàn văn tạp chí](https://onlinelibrary.wiley.com/doi/epdf/10.3233/SPR-130370), 21(3–4), 137–148 | Giữ bản tạp chí cho cơ chế top-down/bottom-up. Chương 1 và 3 | Chưa xác minh |
| Beamer, Asanović và Patterson, 2015 | [arXiv](https://arxiv.org/abs/1508.03619), abstract và metadata, cùng [mã GAP](https://github.com/sbeamer/gapbs) | Giữ cho tổ chức benchmark và baseline. Chương 1 và 3 | Chưa xác minh |
| Leiserson và Schardl, 2010 | [ACM](https://doi.org/10.1145/1810479.1810534), metadata và abstract được lập chỉ mục | Giữ để mô tả bag trong Cilk++. Chương 1 | Chưa xác minh |
| Gonzaga de Oliveira, Santana, Brandão và Osthoff, 2024 | [Wiley](https://onlinelibrary.wiley.com/doi/10.1002/cpe.8119), abstract và metadata, 36(16), e8119 | Giữ cho BFS OpenMP với bag. Chương 1 và 3 | Chưa xác minh |
| Juneja và Khurana, 2024 | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1877050924005623), abstract được lập chỉ mục. [Springer](https://link.springer.com/article/10.1007/s13202-025-02096-3) đối chiếu tác giả, tên, DOI, tập 233 và trang 138–146 | Giữ để mô tả phạm vi khảo sát OpenMP trên mạng 100–1.000 đỉnh. Chương 1 | [ResearchGate](https://www.researchgate.net/publication/379673999_A_Multithreaded-BFS_Algorithm_for_Optimizing_the_Graph_Computation_in_Multicore_Processing_System) hiển thị 3 trích dẫn |
| Trobec, Slivnik, Bulić và Robič, 2018 | [Springer](https://link.springer.com/book/10.1007/978-3-319-98833-7), metadata, đề cương và mục OpenMP | Giữ làm giáo trình nền cho mô hình bộ nhớ chia sẻ. Chương 2 | Springer hiển thị khoảng 1,47 triệu lượt truy cập và 37 trích dẫn |
| OpenMP ARB, 2021 | [Đặc tả 5.2](https://www.openmp.org/spec-html/5.2/openmp.html), các mục parallel, worksharing, single, barrier, schedule | Giữ cho ngữ nghĩa các cấu trúc dùng trong mã. Chương 2 | Chưa xác minh |
| chibinz/ParallelBFS | [README và giấy phép](https://github.com/chibinz/ParallelBFS), phần tổ chức vùng ghi bằng tổng tiền tố | Giữ để ghi nhận nguồn đối chiếu thiết kế. Chương 1 và 3 | GitHub hiển thị 3 sao |
| Microsoft QueryPerformanceCounter | [Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/api/profileapi/nf-profileapi-queryperformancecounter), định nghĩa bộ đếm | Dẫn trong chú thích phương pháp ở Chương 3 | Chưa xác minh |
| Intel, Bhaskar & Kanakagiri, Agarwal và cộng sự, Ligra, SNAP | [Intel SKU 228794](https://www.intel.com/content/www/us/en/products/sku/228794/), [bản tác giả Agarwal](https://davidbader.net/publication/2010-appb/), [SNAP](https://snap.stanford.edu/data/) | Intel chuyển vào ghi chú cấu hình. Bản tiền ấn hành Bhaskar được thay bằng hai công trình sát chủ đề OpenMP hơn. Agarwal và Ligra ngoài phạm vi đối chiếu trực tiếp. SNAP chỉ dùng cho hướng phát triển. | Chưa xác minh |
