# ADR-0003 — QPC cho phép đo Windows

Trạng thái: được chủ dự án chấp thuận trực tiếp ngày 12/11/2026 trong phiên thực nghiệm.

Pilot GCC/libgomp16.2.0 UCRT64 có `omp_get_wtick()=0.001s`, bước dương quan sát
nhỏ nhất khoảng0.001s; BFS serial path8192 nhận0. Không thể suy speedup từ0.
QPC thực tế có tần số10.000.000Hz. Chủ dự án chọn dùng đồng hồ Windows chính xác
hơn thay cho ràng buộc omp_get_wtime ban đầu.

Windows caller dùng QueryPerformanceCounter; lấy frequency trước tick bắt đầu,
trừ ticks nguyên trước rồi đổi sang giây. Lỗi clock → RUNTIME, không xuất mẫu.
Linux giữ omp_get_wtime. Không đổi BFS API, CSR semantics, metrics, thuật toán
A/B, JSONL schema v1 hoặc ranh giới đo. Không dùng timeBeginPeriod, sửa timer hệ
thống hoặc thay power plan. Ghi timer/tần số trong environment của mọi session.

Test timer đo khoảng Sleep/nanosleep30ms để bắt lỗi đơn vị/conversion; chạy lại
oracle/CLI/fault và Windows/Linux CI. QPC không khắc phục overhead, tải nền hoặc
ảnh hưởng khởi tạo team mới cho mỗi tiến trình.

Nguồn chính thức:
https://learn.microsoft.com/en-us/windows/win32/sysinfo/acquiring-high-resolution-time-stamps
https://learn.microsoft.com/en-us/windows/win32/api/profileapi/nf-profileapi-queryperformancecounter

Thay đổi cần reviewer nhóm đọc trong Draft PR #7; quyết định chủ dự án không
thay GitHub approval độc lập hoặc quyền merge.
