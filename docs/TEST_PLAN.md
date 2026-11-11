# Kế hoạch kiểm thử

Các kiểm tra được chia theo module để không nhầm CLI scaffold với correctness
của BFS. Role A đã nối test graph và serial vào `make test-bfs`; các module B/C
sẽ mở rộng target này khi được tích hợp.

## Role A: CSR và BFS tuần tự

`make test-bfs` phải build và chạy thật `build/test_graph` cùng
`build/test_serial`. Bộ test của A dùng expected distances viết độc lập và
kiểm tra:

- CSR directed/undirected, self-loop, cạnh trùng, đỉnh cô lập, đồ thị rỗng và
  no-edge n=3 với expected distance `{0,-1,-1}`;
- edge-list LF/CRLF, comment toàn dòng, dòng cuối không newline, BOM, comment
  cuối dòng, token sai, ID ngoài phạm vi và số vượt `UINT32_MAX`;
- BFS n=1, no-edge, path, star, diamond, cycle, source khác 0, directed và
  undirected;
- `NULL`, enum/config sai, reset metrics khi lỗi, `threads_actual=1` khi thành
  công, checksum CSR trước/sau BFS để kiểm tra bất biến và `graph_free` gọi lặp lại.

## Role B: BFS OpenMP

B phải đối chiếu toàn bộ mảng distance với serial đã xác minh trên fixture và
random graph seed cố định, với nhiều threads và schedule static/dynamic/guided.
Phạm vi gồm disconnected/isolated, duplicate/self-loop, high degree, frontier
lớn, đồng bộ claim visited, barrier theo level và team size thực tế.

## Role C: CLI và benchmark

C kiểm tra tích hợp CLI, JSONL/schema/status/exit codes, timing boundary và
parser dữ liệu lỗi. Benchmark chỉ chạy sau correctness trên cùng commit đo;
không coi CLI scaffold hoặc probe OpenMP là bằng chứng BFS correctness.

Race cần review mô hình bộ nhớ; việc lặp test không thay cho review. Benchmark
phải độc lập với thời gian validation và có provenance theo
`docs/EXPERIMENT_PROTOCOL.md`.
