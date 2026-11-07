# Công cụ C độc lập — chưa đo chính thức

Chạy từ root repository với Python 3.9+ (stdlib). Không cần cài thêm cho generator/runner/analysis. `make test` nay gọi `test-tools` trên cả Linux và Windows CI; không sửa workflow hay code A/B. Unit tests chứa SYNTHETIC TEST DATA ONLY, mock subprocess trong thư mục tạm, không tạo raw trong results của nhóm.

## Sinh dữ liệu
```
python scripts/generate_graph.py path --vertices 1000 --out datasets/path1000
python scripts/generate_graph.py star --vertices 1000 --out datasets/star1000
python scripts/generate_graph.py grid --rows 32 --cols 32 --out datasets/grid32
```
Mặc định vô hướng: mỗi cạnh xuất đúng một lần, loader mirror. `--directed` giữ path tăng ID, star từ tâm ra lá, grid sang phải/xuống. Đây là lựa chọn có chủ đích, không tự coi các chế độ hay nguồn tương đương. Metadata JSON ghi n tường minh; file edge-list không header. Không random nên seed=null; cùng config sinh byte/hash giống nhau. Streaming O(1) bộ nhớ phụ, giới hạn bảo thủ 1 triệu đỉnh để tránh vô tình sinh quá lớn; không bảo đảm BFS vừa RAM máy chưa xác minh. Kích thước ví dụ chỉ là lệnh chuẩn bị, chưa phải tập đo đã chốt. Không overwrite thư mục tồn tại.

## Gate trước chạy chính thức
C2 BLOCKED bởi #3/#4 chưa merge/correctness. Các lệnh sau chỉ được dùng sau khi gate được nhóm xác nhận, CLI đã tích hợp, build và kiểm thử trên chính HEAD; không dùng với scaffold.

Chuẩn bị `build/environment.json` với các trường đã xác minh: cpu, physical_cores, logical_cores, ram_bytes, os, compiler (version), flags, openmp (_OPENMP), runtime (version), power, background_load, source, reachable. Không có giá trị mặc định giả. reachable phải từ kết quả kiểm chứng. Affinity được runner ghi từ môi trường, unset được giữ null.

Chuẩn bị `build/correctness.json`: commit (SHA đầy đủ chính HEAD), status="PASS", command (lệnh test thật), log (đường dẫn log thật). Đây là xác nhận có trách nhiệm của người đo, không phải runner chứng minh distance: schema CLI không xuất toàn bộ distance. Người đo phải đọc log/oracle/review, không chỉ tự viết PASS để vượt gate. Runner yêu cầu working tree sạch. Không đưa metadata nhạy cảm vào Git.

```
python scripts/benchmark.py --binary build/bfs.exe --dataset datasets/path1000/dataset.json --environment build/environment.json --evidence build/correctness.json --threads 1 2 4 --out results/raw
python scripts/analyze_results.py results/raw/SESSION --out results/summary-SESSION.json
```
Điều chỉnh thread counts theo máy thật và metadata; runner từ chối vượt logical cores. Mỗi dataset/source gọi riêng, không trộn máy/build/nguồn giữa session. Mỗi cấu hình warm-up một lần rồi >=10 mẫu, xáo thứ tự từng round bằng seed lưu trong manifest. Lưu stdout/stderr bytes mọi call, timeout/nonzero/invalid giữ lỗi và runner exit1; raw chỉ nhận measured valid. Session mới dùng UTC-SHA-UUID, không ghi đè. Không tự retry lỗi hoặc bỏ outlier. Phiên có lỗi bị analysis từ chối, giữ nguyên để điều tra rồi chạy session mới. Ctrl+C có thể để thư mục dở không manifest; không được phân tích như phiên hoàn tất.

Analysis xác minh hashes và raw/manifest, yêu cầu đủ mẫu và actual team ổn định; cùng requested nhưng actual thay đổi bị từ chối thay vì âm thầm lấy max. Q1/Q3 nội suy tuyến tính (N-1)q; speedup là tỉ số median serial/parallel, efficiency chia actual. Median zero => chỉ số không xác định (null), không chia zero. Baseline serial mỗi session/source; tuyệt đối không gộp summary nhiều session thành một baseline. Giữ mọi mẫu hợp lệ kể cả outlier.

## Biểu đồ (tùy chọn)
Chỉ cài vào môi trường ảo người đo chọn, không cài hệ thống:
```
python -m venv build/analysis-venv
build/analysis-venv/Scripts/python -m pip install matplotlib
build/analysis-venv/Scripts/python scripts/plot_results.py results/raw/SESSION --out results/figures/SESSION
```
Linux dùng `build/analysis-venv/bin/python`. Lưu version matplotlib bằng pip freeze kèm hồ sơ phiên. Plot đọc lại session đã kiểm hash, không nhận CSV tùy ý. Tối đa bốn PDF: median (IQR), speedup, efficiency, scheduling. Không gộp đường khác dataset/source/build; provenance.json giữ summary và manifest hash. Caption/label và diễn giải được tích hợp LaTeX khi có dữ liệu thật. Không dùng test synthetic làm hình báo cáo.

## Kiểm thử
```
python -m unittest discover -s tests -p test_experiment_tools.py -v
python scripts/check_scaffold.py
# Optional plotting test, with matplotlib venv:
build/analysis-venv/Scripts/python -m unittest discover -s tests -p test_plot_tools.py -v
```
Nếu môi trường hạn chế quyền thư mục temp, đặt TEMP/TMP vào thư mục build đã tạo trong workspace cho phiên lệnh. Test không phải BFS correctness hay benchmark. Cần kiểm lại CLI/timer/actual-team và full-distance validation sau A/B trước khi dùng đo thật.
