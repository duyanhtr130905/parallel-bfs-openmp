# Hợp đồng API v1 — CUỐI CÙNG cho đợt giao việc

Ngày chốt: 05/11/2026; revision bootstrap theo ADR-0002, thay chữ ký trước implementation. Nguồn chuẩn: tài liệu này và `include/*.h`.
Đổi API phải có PR riêng cập nhật đồng thời tài liệu, header và mọi bên gọi;
không tự đổi chữ ký trong nhánh cá nhân. C11, OpenMP, không C++.

## Kiểu dữ liệu và chữ ký

```c
typedef struct { uint32_t src; uint32_t dst; } Edge;
typedef struct {
    uint32_t vertex_count;
    size_t edge_count;
    size_t *row_offsets;
    uint32_t *col_indices;
} CSRGraph;
typedef enum { GRAPH_DIRECTED = 0, GRAPH_UNDIRECTED = 1 } GraphMode;
typedef enum {
    BFS_SCHEDULE_STATIC = 0, BFS_SCHEDULE_DYNAMIC = 1,
    BFS_SCHEDULE_GUIDED = 2
} BFSSchedule;
typedef struct { int threads; BFSSchedule schedule; } BFSConfig;
typedef struct { int threads_actual; } BFSMetrics;

BFSStatus graph_from_edges(uint32_t vertex_count, const Edge *edges,
                          size_t input_edge_count, GraphMode mode, CSRGraph *out);
BFSStatus graph_read_edge_list(const char *path, uint32_t vertex_count,
                              GraphMode mode, CSRGraph *out);
void graph_free(CSRGraph *graph);
BFSStatus bfs_serial(const CSRGraph *graph, uint32_t source,
                     int32_t *distance, const BFSConfig *config, BFSMetrics *metrics);
BFSStatus bfs_parallel_basic(const CSRGraph *graph, uint32_t source,
                             int32_t *distance, const BFSConfig *config, BFSMetrics *metrics);
BFSStatus bfs_parallel_optimized(const CSRGraph *graph, uint32_t source,
                                 int32_t *distance, const BFSConfig *config, BFSMetrics *metrics);
```

## CSR và ownership

- `1 <= vertex_count <= INT32_MAX`. Giới hạn này bảo đảm mọi khoảng cách đơn
  ngắn nhất (tối đa n-1) biểu diễn được bằng int32_t. Đồ thị rỗng n=0 bị từ chối.
- ID đỉnh từ 0 đến n-1, gồm cả đỉnh cô lập. Không suy n từ ID lớn nhất.
- `edge_count` là số cung lưu trong CSR (m), KHÔNG là số dòng input.
- Directed: mỗi Edge tạo một cung. Undirected: thêm cung ngược khi src != dst;
  self-loop chỉ lưu một lần. Giữ cạnh trùng và thứ tự láng giềng không được bảo đảm.
  Nếu input đã có cả hai chiều, chế độ undirected vẫn nhân đôi các cạnh không loop.
- `row_offsets` dài n+1, bắt đầu 0, không giảm, phần tử cuối bằng m.
  `col_indices` dài m và mọi giá trị < n; m=0 cho phép col_indices=NULL.
- Hàm dựng kiểm tra mọi phép cộng/nhân cấp phát (kể cả n+1 sau khi đổi size_t,
  nhân đôi m, prefix sum, kích thước phần tử); tràn trả RANGE, không wrap.
- Caller truyền `CSRGraph g = {0}`. out không NULL và không chứa tài nguyên sống.
  Caller chịu trách nhiệm precondition này; không đọc bộ nhớ chưa khởi tạo.
  Builder không sửa Edge input; chỉ chuyển ownership các buffer mới khi thành công.
  Nếu lỗi, out vẫn zero và không rò bộ nhớ; muốn tái sử dụng phải graph_free trước.
- edges=NULL hợp lệ chỉ khi input_edge_count=0. path phải khác NULL và không rỗng.
- `graph_free(NULL)` hợp lệ; graph_free giải phóng hai buffer do builder tạo,
  đặt toàn bộ trường về zero và gọi lặp an toàn. Không free graph chứa con trỏ mượn.
- CSR sau khi dựng là bất biến. Caller phải giữ graph/buffer sống trong suốt BFS,
  không sửa đồng thời; các lần BFS đồng thời phải dùng output riêng.

## Edge list

UTF-8/ASCII, mỗi dòng dữ liệu đúng hai số nguyên thập phân không dấu `src dst`,
phân cách bằng space/tab; cho phép whitespace đầu/cuối, LF/CRLF, dòng cuối không LF.
Cho phép dòng trắng và comment cả dòng khi ký tự đầu tiên khác whitespace là `#`.
Không header n/m, không weight, không comment cuối dòng, không dấu +/-, không BOM.
File rỗng hợp lệ khi n hợp lệ. Không cắt cụt dòng dài rồi chấp nhận một phần.
Token sai/thiếu/thừa/BOM trả FORMAT; số không biểu diễn uint32_t hoặc ID >= n
trả RANGE. Không mở/đọc/đóng file được trả IO. Builder đóng file của chính nó.

## BFS

- graph, distance, config, metrics không NULL. source < n; config.threads >= 1 và enum hợp lệ.
- Caller cấp phát distance đủ n int32_t, không alias bất kỳ buffer graph/config/metrics.
  Output không cần khởi tạo; mỗi lần thành công phải ghi đầy đủ n phần tử.
- Khi OK: distance[source]=0; unreachable=-1; mọi đỉnh khác là số cạnh ngắn nhất.
  Không yêu cầu parent hoặc thứ tự duyệt giống nhau. Không có parent trong API v1.
- Lỗi: distance không xác định, caller không được dùng hoặc xuất benchmark.
  Mọi bộ nhớ tạm do hàm tự cấp phát và tự giải phóng cả khi lỗi.
- Serial kiểm tra config nhưng luôn chạy một luồng; threads/schedule không chi phối
  thuật toán serial. Hai phiên bản OpenMP dùng threads làm số luồng yêu cầu,
  schedule cho vòng phân phối frontier, chunk mặc định OpenMP (không có chunk CLI).
  Nếu có nhiều vòng khác loại, phải mô tả vòng nào áp dụng schedule trong PR.
- Caller sở hữu `BFSMetrics`; không alias graph/config/distance/scratch và không
  chia sẻ metrics giữa các lời gọi đồng thời. Nếu metrics khác NULL, hàm đặt
  threads_actual=0 trước kiểm tra đối số; khi lỗi giá trị này vẫn 0, không xuất mẫu.
  Chỉ khi BFS_OK mới công bố giá trị >=1; serial luôn ghi 1.
- Hai hàm OpenMP lấy omp_get_num_threads() trong single của chính từng parallel
  region xử lý BFS; barrier bảo đảm quan sát an toàn. Mọi team xử lý BFS trong một
  lời gọi phải có cùng kích thước. Nếu team thay đổi giữa các vùng, trả
  BFS_ERR_RUNTIME, giữ metrics=0 và không xuất kết quả thành công. Dùng cùng một
  persistent team là lựa chọn đơn giản. Trường hợp không mở vùng song song vì
  không có công việc phải báo 1 (thực thi serial), không giả báo config.threads.
- Tắt dynamic team cho phiên benchmark; team thực tế vẫn có thể khác request.
  Không suy threads_actual từ omp_get_max_threads(), config hoặc probe bên ngoài.
  Metrics chỉ chứa team size, không chứa thời gian. Xem ADR-0002.
- Không gọi từ vùng parallel bên ngoài trong API v1. Không dùng trạng thái global
  mutable; mọi thay đổi OpenMP ICV phải được khôi phục trước khi trả về.
- Caller phải cung cấp CSR thỏa invariants, capacity/pointer hợp lệ; C không thể
  kiểm tra vùng cấp phát. BFS kiểm tra đối số đơn giản O(1); kiểm tra sâu CSR diễn ra
  khi dựng/kiểm thử, ngoài thời gian BFS. CSR hỏng ngoài precondition không được hỗ trợ.

## Mã trạng thái (giá trị cố định trong status.h)

| Mã | Giá trị | Ý nghĩa |
|---|---:|---|
| BFS_OK | 0 | Hoàn tất |
| BFS_ERR_ARGUMENT | 1 | NULL, enum/config sai |
| BFS_ERR_RANGE | 2 | n/source/ID ngoài miền, tràn kích thước |
| BFS_ERR_MEMORY | 3 | Cấp phát thất bại |
| BFS_ERR_IO | 4 | Lỗi file |
| BFS_ERR_FORMAT | 5 | Sai cú pháp edge list |
| BFS_ERR_NOT_IMPLEMENTED | 6 | Module chưa triển khai |
| BFS_ERR_RUNTIME | 7 | Lỗi runtime được phát hiện |

Không quy định ưu tiên khi nhiều lỗi đồng thời. Mã API khác mã thoát CLI.
Hiện chỉ có khai báo; chưa có định nghĩa graph/BFS, không thể link ứng dụng BFS thật.

## CLI v1

`bfs --graph PATH --vertices N --source S --algo serial|omp-basic|omp-opt
[--threads P] [--schedule static|dynamic|guided] (--directed|--undirected)`

Bắt buộc graph, vertices, source, algo và đúng một chế độ cạnh. Mặc định threads=1,
schedule=static. Từ chối option lặp, option lạ, thiếu value, số âm/tràn,
N ngoài [1,INT32_MAX], S>=N, P ngoài [1,INT_MAX]. `--help` phải đứng một mình.
Không hỗ trợ dạng `--key=value`; path có khoảng trắng phải quote; path bắt đầu
`--` dùng prefix `./`. Serial có thể nhận threads khác 1 nhưng kết quả phải ghi
threads_requested đúng đối số và threads_actual=1.

Exit: 0 help hoặc BFS thật thành công; 2 sai CLI; 3 module chưa triển khai;
4 lỗi thực thi (graph/BFS/validation). stderr nhận chẩn đoán; lỗi không có result
trên stdout. Bootstrap parse/validate CLI rồi exit 3, chưa mở graph hay đo runtime.

## Kết quả benchmark v1 (chỉ quy định, chưa phát ra)

Một JSON object một dòng stdout cho mỗi BFS thành công, locale số C, không NaN/Inf:
`schema_version`=1, `status`="ok", `algorithm` thuộc enum CLI,
`runtime_seconds` số thực hữu hạn >=0, `threads_requested` nguyên >=1,
`threads_actual` nguyên >=1, `schedule` enum CLI (serial ghi "none"),
`vertices`=n, `edges`=m cung CSR, `source`=S, `reachable` số phần tử distance>=0,
`directed` boolean. Không in mẫu số liệu giả. CLI lấy threads_actual từ BFSMetrics của lời gọi BFS_OK tương ứng.
Thiếu team measurement thì chưa được
phát result thành công. Log chẩn đoán chỉ stderr.

Đo wall-clock `omp_get_wtime()` trên cùng master thread trước/sau một lời gọi BFS.
Không gồm đọc file, dựng CSR, cấp phát output, kiểm chứng và ghi kết quả;
có gồm khởi tạo distance và cấp phát scratch bên trong hàm BFS.
Chi tiết lặp đo/so sánh trong EXPERIMENT_PROTOCOL.md.
