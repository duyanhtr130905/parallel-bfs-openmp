# Quy trình làm việc chung cho Codex và nhóm Parallel BFS

Áp dụng cho toàn repository và mọi phiên Codex của A/B/C, kể cả khi prompt riêng
không nhắc lại. Đọc quy tắc này trước khi lập kế hoạch, sửa file, commit hoặc review.
Repository canonical: https://github.com/duyanhtr130905/parallel-bfs-openmp .
Mọi thay đổi đi qua feature branch và Pull Request (PR) về canonical `main`.

## 1. Nguồn chuẩn và phạm vi được giao

- Đọc [CONTRACT](docs/CONTRACT.md), `include/graph.h`, `include/bfs.h`,
  `include/status.h`, [Architecture](docs/ARCHITECTURE.md),
  [Test plan](docs/TEST_PLAN.md) và [Experiment protocol](docs/EXPERIMENT_PROTOCOL.md).
  Đọc issue được giao, các PR phụ thuộc và chỉ dẫn thư mục con nếu có.
- Đọc [Project status](docs/PROJECT_STATUS.md), [.techlead/project.yaml](.techlead/project.yaml),
  [Contributing](docs/CONTRIBUTING.md), [Delivery plan](docs/DELIVERY_PLAN.md),
  [GitHub setup](docs/GITHUB_SETUP.md) và [Review lịch sử](docs/REVIEW_20261105.md)
  để hiểu quyết định và bằng chứng trước đó; đối chiếu với trạng thái GitHub thực tế.
- Quy trình tại đây thay phần chỉ dẫn bootstrap đã hết hiệu lực: không tiếp tục
  giới hạn mọi công việc ở scaffold, không coi PR #1 còn Draft và không tái sử dụng
  quyền push riêng của phiên sửa PR #1. PR #1 đã merge; công việc A/B/C theo issue
  #3/#4/#5. Các ghi chú bootstrap trong tài liệu/status/project.yaml là lịch sử
  khi mâu thuẫn với mốc này; chúng không tự cấp quyền mới hoặc chứng minh test đã chạy.
  Theo dõi dọn tài liệu còn lại ở issue #2; không sửa lại hồ sơ audit lịch sử.
- Header + CONTRACT là nguồn chuẩn API; ADR-0001/ADR-0002 ghi quyết định stack/metrics.
  Nếu chúng không thống nhất, báo xung đột với lead trước khi sửa phần bị ảnh hưởng.
  Prompt riêng phải nêu role, issue, phạm vi file, dependency và tiêu chí nghiệm thu;
  không âm thầm đổi hợp đồng hoặc bỏ review/CI vì hạn nộp.
- Chỉ thực hiện phạm vi được người dùng giao. Được giao A/B/C không đồng nghĩa
  được sửa toàn dự án, cài phần mềm, đổi PATH hệ thống, tải dữ liệu lớn, đổi quyền,
  ruleset, remote hay tạo fork thay người khác. Commit/push/tạo PR cần ủy quyền
  phù hợp trong nhiệm vụ hiện tại; khi đã có thì tiếp tục trong phạm vi đó.
  Merge cần ủy quyền riêng và đủ các gate ở mục 6; không tự merge/auto-merge.
- Vị trí làm việc chính trước đây là `D:/Code/parallel-bfs-openmp`; bản OneDrive
  được giữ làm snapshot. Xác minh workspace thực tế và quyền của phiên hiện tại;
  không tự đồng bộ, di chuyển hoặc ghi đè snapshot hay dự án Windows khác.

## 2. Stack, ownership và dependency

Stack cố định: **C11 + OpenMP trên CPU**, GCC/MSYS2 UCRT64 cho Windows; Linux CI;
Python cho kiểm tra/benchmark/phân tích; báo cáo **LaTeX tiếng Việt, XeLaTeX + BibTeX**.
Không chuyển C++, GPU hoặc MPI. Không sao chép code tham khảo khi chưa audit logic
và kiểm tra giấy phép; không chép nội dung nghiên cứu của template báo cáo.

| Role / chủ sở hữu | Issue / branch | Phạm vi chính |
| --- | --- | --- |
| A — `ducnt05` | [#3](https://github.com/duyanhtr130905/parallel-bfs-openmp/issues/3), `feat/graph-serial-bfs` | `src/graph.c`, `src/bfs_serial.c`, `tests/test_graph.c`, `tests/test_serial.c`, fixture/oracle; lý thuyết BFS/CSR ở `report/chapters/chapter2.tex` |
| B — `Terivn` | [#4](https://github.com/duyanhtr130905/parallel-bfs-openmp/issues/4), `feat/parallel-bfs` | `src/bfs_parallel_basic.c`, `src/bfs_parallel_optimized.c`, `tests/test_parallel.c`; đồng bộ/frontier/schedule; `report/chapters/chapter3.tex` |
| C — `duyanhtr130905` | [#5](https://github.com/duyanhtr130905/parallel-bfs-openmp/issues/5), `feat/benchmark-report` | `src/main.c`, benchmark/analyze/plot scripts, raw/manifest/figures; tích hợp báo cáo, chương 1/4/5/6 |

- Lead C quản lý hợp đồng chung; thay đổi `include/*.h`, CONTRACT, schema, status
  hoặc semantics phải có đề xuất rõ và lead + mọi consumer A/B/C review cùng PR.
  Cập nhật header/tài liệu/consumer/test nhất quán; không tự đổi chữ ký ở nhánh cá nhân.
- `Makefile`, CI, tài liệu chung, preamble/bibliography và fixtures dùng chung cần
  phối hợp trước khi sửa. Mỗi PR chỉ nối module/test liên quan, nêu người chịu trách
  nhiệm; không sửa ngoài scope hoặc để nhiều người ghi đè cùng file/section.
- **Thứ tự tích hợp A → B → C**: A cung cấp CSR + serial đã qua oracle; B chỉ
  nghiệm thu/merge sau A, so với serial thật; C tích hợp CLI gọi cả ba BFS và đo
  thực nghiệm sau A/B đã merge và correctness PASS trên cùng commit đo.
- B có thể thiết kế/triển khai dựa vào header và fixture CSR độc lập trước A.
  C có thể chuẩn bị parser/automation/protocol/report skeleton trước A/B (C1).
  PR chuẩn bị độc lập có thể review riêng; không tuyên bố integration PASS từ stub.
  C2 nối CLI/benchmark phụ thuộc cả #3 và #4; ghi `Depends on #3, #4` trong PR.
  Không mang bản sao implementation chưa merge của người khác vào PR để bỏ dependency.

## 3. Hợp đồng kỹ thuật bắt buộc

Đọc toàn bộ [CONTRACT](docs/CONTRACT.md) và
[ADR-0002](docs/adr/ADR-0002-caller-owned-bfs-metrics.md); các điểm sau không thay thế chúng.

- Cả `bfs_serial`, `bfs_parallel_basic`, `bfs_parallel_optimized` trả `BFSStatus`
  và nhận đúng **5 tham số**:
  `(const CSRGraph *, uint32_t source, int32_t *distance, const BFSConfig *, BFSMetrics *)`.
  Không quay lại API bốn tham số.
- CSR bất biến trong BFS; `vertex_count` tường minh gồm isolates, từ 1 đến INT32_MAX;
  `edge_count` là số cung lưu. Directed giữ mỗi cung; undirected mirror cạnh không
  self-loop, self-loop chỉ một cung; giữ duplicates. Tôn trọng grammar edge-list,
  ownership, zero-on-builder-error, free idempotent và kiểm tra range/size overflow.
- Caller sở hữu `distance[n]` và metrics riêng không alias cho mỗi call. Khi OK:
  source có distance 0, unreachable -1 và toàn bộ distance đúng shortest path.
  Lỗi thì distance không được dùng làm kết quả; giải phóng mọi scratch cả đường lỗi.
- Nếu metrics khác NULL, reset `threads_actual=0` **trước validation**, lỗi giữ 0.
  Chỉ công bố >=1 khi `BFS_OK`; serial luôn 1. Parallel lấy
  `omp_get_num_threads()` trong single của chính mỗi vùng xử lý BFS, có đồng bộ.
  Team thay đổi giữa các vùng trong một call => `BFS_ERR_RUNTIME`, metrics=0;
  không mở team vì không có việc => 1. Không suy từ request,
  `omp_get_max_threads()` hoặc probe bên ngoài.
- Không global mutable hoặc gọi API từ parallel region bên ngoài. Khôi phục OpenMP
  ICV nếu thay đổi. Schedule static/dynamic/guided phải áp dụng đúng vòng frontier,
  mô tả rõ trong PR. Atomic visited claim, publish distance, barrier theo level và
  frontier capacity/overflow cần review mô hình bộ nhớ; không trộn truy cập thường
  và atomic đồng thời lên cùng location.
- C đo wall-clock trên cùng caller thread ngay trước/sau BFS: Windows dùng QPC
  theo ADR-0003 được chủ dự án duyệt 12/11/2026; Linux dùng `omp_get_wtime()`.
  Gồm init distance và
  scratch trong BFS; loại I/O, dựng CSR, cấp phát output, validation và serialization.
  JSONL schema v1 chỉ xuất trên stdout khi BFS_OK + metrics hợp lệ; diagnostics ở
  stderr, lỗi không có result. Giữ exit codes CLI 0/2/3/4 khác status API.
  Serial ghi schedule="none", requested đúng đối số, actual=1; parallel dùng metrics
  thật. Không fallback giả hoặc xuất dữ liệu thành công khi module chưa triển khai.
- C11: include rõ, kiểm tra NULL/enum/range/cấp phát, không cast che warning;
  tránh rò bộ nhớ, double free và thay đổi input. Module mới phải được build/link
  và test tường minh trong Makefile, không chỉ tồn tại dưới dạng file.

## 4. Git an toàn, fork, branch và issue

1. Trước sửa: kiểm tra `git status --short --branch`, `git remote -v`,
   `git branch --show-current` và commit HEAD. Giữ thay đổi của người khác; khi có
   phần việc chưa commit chồng scope, dừng phần bị ảnh hưởng để phối hợp.
2. A/B dùng fork cá nhân: `origin` là fork của đúng người, `upstream` là canonical.
   C dùng feature branch trong canonical với `origin` là canonical, không cần fork.
   Xác minh URL trước fetch/push; chỉ thiết lập remote theo topology đã được giao,
   không tự thay URL remote hiện có. Không tạo fork hộ tài khoản khác.
3. Với working tree sạch: fetch canonical remote (`upstream` cho A/B, `origin`
   cho C), cập nhật main bằng fast-forward. Ví dụ A/B: `git fetch upstream`,
   `git switch main`, `git merge --ff-only upstream/main`; C dùng `origin/main`.
   Nếu không fast-forward được, kiểm tra lịch sử và phối hợp, không reset để ép khớp.
4. Tạo feature branch từ canonical main mới nhất; dùng tên role ở mục 2 hoặc
   `fix/<mo-ta>`, `docs/<mo-ta>`, `feat/<mo-ta>` cho việc riêng. Kiểm tra branch
   có sẵn trước khi tạo; không dùng lại nhánh bootstrap đã merge. Đồng bộ branch
   đang làm bằng merge canonical main khi cần; không rewrite lịch sử đã chia sẻ.
5. Issue canonical phải có owner, phạm vi/ngoài phạm vi, dependency, acceptance
   checklist, lệnh kiểm chứng, rủi ro và reviewer khác tác giả. Dùng #3/#4/#5 thay
   vì tạo trùng. Ghi blocker bằng issue/PR link và phần việc còn có thể làm.
6. Trước commit xem `git diff`, `git diff --check`, stage từng path, xem
   `git diff --cached`; commit nhỏ, rõ mục đích. Khi được phép push, push thường
   đúng feature branch lên origin; A/B mở PR từ fork vào canonical main, C từ branch
   canonical vào main. Không push trực tiếp main hoặc dùng push không kiểm tra đích.
7. Không `reset --hard`, `clean -fdx`, force push, xóa branch của người khác,
   amend/rebase lịch sử đã công bố hoặc sửa ruleset để vượt gate. Không commit token,
   binary, dataset lớn, raw không provenance hoặc file sinh tự động ngoài quy định.
   Không sửa Git identity để giả danh đóng góp của thành viên khác.

## 5. Kiểm chứng và bằng chứng thực chạy

- Lệnh nền tại root: `make build`, `make test`, `make check-api`,
  `make check-openmp`, `make report`; Windows UCRT64 dùng `mingw32-make`,
  Linux dùng GCC và `PYTHON=python3` khi cần. Python
  `scripts/check_scaffold.py` chỉ kiểm cấu trúc/chữ ký, không thay compiler/runtime.
- Baseline bootstrap: `make test` kiểm CLI/scaffold, API chỉ compile-only;
  `make test-bfs` cố ý báo NOT IMPLEMENTED và thất bại. Không đổi thành PASS rỗng,
  skip rồi gọi correctness PASS, hoặc mô tả build/probe/CLI là kiểm thử BFS.
  A phải thêm correctness target thật; B/C mở rộng và nối nó vào **cả Linux/Windows CI**.
- A kiểm parser/CSR/ownership/overflow/invalid input và serial bằng oracle tay
  độc lập. B kiểm oracle nhỏ và so **mọi phần tử distance** với serial đã xác minh:
  n=1, no-edge, path, star, diamond, disconnected/isolated, cycles,
  duplicate/self-loop, nonzero/multiple source, directed/undirected, high degree,
  large frontier, random fixed seed, nhiều threads và static/dynamic/guided lặp lại.
  Test metrics, NULL/error/reset, CSR không đổi và các đường lỗi liên quan.
  Stress PASS không chứng minh tuyệt đối không có race; cần review đồng bộ.
- C kiểm CLI tích hợp, JSONL/schema/status/exit codes, timing boundary, actual team
  và parser với dữ liệu lỗi. Synthetic fixtures chỉ ở test và ghi rõ synthetic;
  không đưa vào raw thực nghiệm hay báo cáo như kết quả đo.
- Mỗi check ghi lệnh, môi trường, SHA, kết quả và giới hạn. Phân biệt PASS, FAIL,
  NOT RUN, BLOCKED; không khẳng định đã chạy khi chỉ đọc source. CI của commit cũ,
  máy khác hoặc probe không chứng minh correctness/performance của HEAD hiện tại.
- Report dùng `make report` (XeLaTeX/BibTeX đủ vòng), kiểm PDF thực tế sau thay đổi
  nội dung/layout. Không coi compile LaTeX là chứng minh bảng/biểu đồ đúng.
  Thiếu toolchain thì ghi BLOCKED và dùng CI phù hợp, không tự cài lên máy người dùng.

## 6. PR, review độc lập và điều kiện merge

- Mở Draft PR sớm cho implementation còn thiếu dependency/evidence, theo
  [.github/pull_request_template.md](.github/pull_request_template.md). Nêu vấn đề,
  hành vi sau sửa, module/owner, hợp đồng giữ/đổi, issue/dependency, lệnh + log/link
  kiểm chứng theo SHA, rủi ro bộ nhớ/đồng bộ và phần chưa hoàn tất.
  Dùng `Relates to #N` khi còn thiếu; chỉ `Closes #N` khi đủ toàn bộ acceptance.
- Reviewer mặc định: A mời Terivn; B mời ducnt05; C mời ducnt05 hoặc Terivn.
  Người được mời phải đọc diff, test/evidence và ghi findings có vị trí, tác động,
  cách tái hiện/khắc phục. Tác giả sửa; reviewer xác minh việc đóng finding.
  API/shared-contract change cần thêm lead và mọi bên dùng API.
- Trước merge phải đủ: scope/acceptance + dependencies được đáp ứng; không còn
  P0/P1 hoặc blocker correctness/contract; review threads đã xử lý; test thực liên
  quan PASS; ít nhất **1 GitHub approval hợp lệ từ người khác có quyền write**,
  độc lập với tác giả và người push cuối theo ruleset. Codex tự review, COMMENT,
  CI xanh hoặc chủ repo tự xác nhận không thay approval độc lập.
- Xác minh các required checks thực tế trên GitHub theo HEAD mới nhất và base mới
  nhất: hiện gồm `bootstrap-linux`, `bootstrap-windows-ucrt64`, `report-xelatex`.
  Giữ cả ba; thuật toán còn cần correctness tests thật theo mục 5. Không dùng tên
  job bootstrap để suy thuật toán đã test, không bypass/giảm checks.
- Ruleset main yêu cầu cập nhật base, dismissal approval cũ sau push và approval
  cho lần push cuối. Sau thay đổi tiếp theo phải có CI/re-review phù hợp; không
  dựa vào approval trước một diff đã thay đổi. Deadline không bỏ gate.
- Chỉ người được nhóm giao quyền mới merge sau xác nhận tương ứng. Agent dừng ở
  bàn giao PR khi không có ủy quyền merge riêng; không bật auto-merge, tự approve
  thay thành viên, đổi quyền hoặc thử merge để kiểm tra enforcement.
  Sau merge thật mới cập nhật issue/status là merged; PR mở chỉ là đang đề xuất.

## 7. Benchmark, báo cáo và bàn giao trung thực

- Chỉ benchmark sau correctness + integration gates trên chính commit đo.
  Theo [Experiment protocol](docs/EXPERIMENT_PROTOCOL.md): cùng dataset/source/
  semantics/build flags, 1 warm-up và **ít nhất 10 mẫu đo** mỗi cấu hình;
  OMP_DYNAMIC=FALSE, ghi requested/actual team, schedule và môi trường thực tế.
- Mỗi session dùng thư mục mới `results/raw/<UTC-timestamp>-<short-sha>-<run-id>/`
  và exclusive-create; không ghi đè raw, sửa raw cho đẹp, giấu lỗi/outlier hoặc
  tự retention-delete. Lưu JSONL/CSV gốc, stderr/lỗi, warm-up/thứ tự đo; manifest
  có commit/dirty state, lệnh, compiler/flags/runtime, CPU/cores/RAM/OS/nguồn điện/
  background load, dataset URL/license/hash/seed/n/m/source, cấu hình, validation,
  repetition và SHA-256 mọi raw/log, cùng script/dependencies tái tạo biểu đồ.
- Báo median/min/max/IQR; speedup so **serial thật**, efficiency theo **actual team
  size ổn định**. Actual thay đổi thì tách nhóm/đánh dấu không so sánh; scaling
  so omp-1 là đại lượng riêng. Không bịa speedup, ép kết quả >1, lấy số repo tham
  khảo làm số nhóm hoặc coi dữ liệu giả là thực nghiệm. Chưa đo thì ghi TODO/chưa đo.
- Raw/figures đang ignore; chỉ `git add -f` từng file nhỏ đã review có manifest và
  provenance, không cả thư mục. Dữ liệu lớn dùng kho được phép + locator/hash;
  giữ bản sao raw đến hết chấm/bảo vệ/phúc khảo, không chỉ dựa vào Git.
- A/B bàn giao chương lý thuyết/thuật toán cho C tích hợp; C chỉ điền chương kết quả/
  kết luận từ số liệu nhóm thực chạy, nêu cả slowdown và giới hạn.
- Kết thúc phiên: ghi role/issue, branch + HEAD, file đã đổi, test/CI/evidence,
  dependency/blocker, rủi ro và bước tiếp theo trong PR/issue; cập nhật
  PROJECT_STATUS ở PR phù hợp khi được giao. Phân biệt đã viết, đã test, đã approve,
  đã merge; không ghi hoàn thành khi còn thiếu gate.
