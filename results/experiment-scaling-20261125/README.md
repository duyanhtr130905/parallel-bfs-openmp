# Khảo sát theo số luồng ngày 25/11/2026

Phiên độc lập chạy khoảng 09:37–09:38 giờ Việt Nam. Ba đầu vào, đường đi,
vòng có cung ngẫu nhiên và phân tầng hoán vị, được tái tạo theo bộ sinh
ngày 25/11. SHA-256 danh sách cung và hồ sơ bề rộng từng tầng khớp phiên
tham chiếu. Mốc Serial được đo trong phiên này.

- [Kế hoạch trước khi đo](plan.json) và [manifest](manifest.json).
- Mỗi CSV có 154 lượt: 22 khởi động và 132 chính thức. Có 33 cấu hình và 396
  mẫu chính thức trên ba đồ thị. Mỗi lượt đều khớp toàn bộ mảng khoảng cách
  tham chiếu và số luồng yêu cầu.
- CPU bận trước từng đồ thị lần lượt là 14,9%, 5,3% và 10,1% trong các
  cửa sổ 1 giây. Máy có cắm điện và dùng Balanced; việc gắn luồng theo mặc
  định của hệ điều hành và runtime.
- [Thống kê](../../report/generated/scaling-summary.json) và
  [biểu đồ](../../report/figures/thread-scaling.pdf). Chỉ số nội bộ của mỗi
  bản OpenMP dùng chính phiên bản đó ở một luồng làm mốc.

## Tái lập và kiểm thử

Chạy từ thư mục gốc với GCC/OpenMP, Python 3.11+, psutil và Matplotlib.

    python scripts/run_scaling.py --commit 11b86b53cfdbd14e72eab51ab13f5b19b70ebc43 --output results/repeat-scaling
    make review-artifacts test-review

Lệnh đầu chỉ dùng thư mục mới. Trình đo xác minh hash đầu vào rồi kiểm tra
RAM trống, nguồn điện và tải CPU. Raw lưu cả lượt khởi động và thứ tự
thực thi. Tệp đầu vào lớn được tái tạo từ tham số và seed.
