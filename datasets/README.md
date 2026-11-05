# Dữ liệu

`small/disconnected.edgelist`: fixture tự tạo, n=6, source=0, directed,
5 cung; đỉnh 5 cô lập, đỉnh 4 có self-loop nhưng không reachable từ 0.
Expected distance do phân tích tay trong `small/disconnected.expected.txt`.
Đây là oracle cho kiểm thử tương lai, chưa có BFS để chạy so sánh.
Không tải dataset lớn trong bootstrap. Dữ liệu ngoài small bị gitignore;
mỗi dataset sau này phải có provenance, giấy phép, SHA-256, n, số dòng và chế độ cạnh.
