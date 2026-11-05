# Kế hoạch đề xuất 14 ngày — chưa thực hiện phần thành viên

| Ngày | Việc/owner | Điều kiện ra |
|---|---|---|
| 1 | Lead: bootstrap và chốt API | Hợp đồng/header đồng nhất |
| 2–4 | TV1: parser CSR + serial; TV2: thiết kế basic; TV3: test/protocol | Oracle tay/input validation |
| 5–7 | TV2: basic; TV3: optimized; TV1: review/integration | So mọi distance với oracle/serial |
| 8–9 | Cả nhóm: stress correctness, review đồng bộ | Không lỗi đã biết, không data race đã xác định |
| 10–11 | Cả nhóm: benchmark theo protocol | Raw/manifest, actual threads, provenance |
| 12–13 | Cả nhóm: báo cáo/figures | Tái tạo số liệu, PDF đã xem |
| 14 | Cả nhóm: diễn tập bảo vệ và đóng gói | Demo và giải thích giới hạn |

Lead giữ contract chung. Mỗi người review module người khác trước merge.
Phụ thuộc: API → CSR + oracle serial → OpenMP correctness → benchmark → kết luận.
Không coi deadline là lý do bỏ kiểm chứng. Phân công là đề xuất cho nhóm,
không phải các thuật toán đã được tạo hoặc đã giao cho agent.
