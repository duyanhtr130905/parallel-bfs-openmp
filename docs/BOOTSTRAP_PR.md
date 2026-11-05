# Đề xuất PR — chưa tạo trên GitHub

Title: Bootstrap C11/OpenMP BFS API, CLI scaffold và báo cáo tiếng Việt

Chốt API v1 cho CSR và ba phiên bản BFS, ownership/error/schedule, CLI/JSONL và
protocol timing để ba thành viên triển khai nhất quán. Thêm CLI chỉ validate rồi
báo NOT_IMPLEMENTED, Makefile, kiểm tra scaffold/CLI và khung LaTeX sáu chương.
Không có thuật toán BFS, số đo, pipeline graph hoặc kết quả hiệu năng.

Validation: xem docs/PROJECT_STATUS.md và docs/ENVIRONMENT.md để biết lệnh thực
tế và phần chưa chạy. Review tập trung semantics undirected/m, lifetime output,
giới hạn int32, timing boundary, actual team instrumentation và lỗi module.

Branch đề xuất: chore/bootstrap-contracts
Commit đề xuất: chore: bootstrap C11 OpenMP BFS contracts and Vietnamese report
