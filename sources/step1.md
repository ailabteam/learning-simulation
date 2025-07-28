Chắc chắn rồi. Tôi đã đọc kỹ tài liệu và mã nguồn của repository StarPerf_Simulator để đưa ra hướng dẫn chi tiết cho bạn trên môi trường Ubuntu và giải quyết các yêu cầu của bạn.

Phân tích nhanh

Về việc sử dụng GPU: Câu trả lời ngắn gọn là KHÔNG. Simulator này không được thiết kế để tận dụng GPU. Các thư viện cốt lõi của nó (skyfield để tính toán quỹ đạo, networkx để xử lý đồ thị) là các thư viện chạy trên CPU. Các tác vụ của nó không phải là các phép tính ma trận song song quy mô lớn (như trong deep learning) để GPU có thể tăng tốc hiệu quả. Do đó, bạn sẽ chạy nó hoàn toàn bằng CPU, tuy nhiên một CPU đa nhân mạnh mẽ vẫn sẽ giúp ích.

Về việc lưu file hình ảnh (figures): Hoàn toàn có thể. Mặc định, mã nguồn sử dụng plt.show() để hiển thị hình ảnh trực tiếp. Chúng ta chỉ cần sửa một dòng mã để thay thế bằng plt.savefig() để lưu nó ra file.

Dưới đây là hướng dẫn chi tiết từng bước.

Hướng dẫn cài đặt và chạy StarPerf_Simulator trên Ubuntu
Bước 1: Cài đặt các công cụ cần thiết (Prerequisites)

Mở Terminal (Ctrl + Alt + T) và chạy các lệnh sau để cài đặt Git, Python, Pip và môi trường ảo:

Generated bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv

Bước 2: Cài đặt các thư viện phụ thuộc của GeoPandas

GeoPandas là một thư viện "khó tính" vì nó yêu cầu các thư viện hệ thống khác. Cài đặt chúng trước để tránh lỗi khi cài đặt qua pip.

Generated bash
sudo apt install -y libgdal-dev gdal-bin
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END
Bước 3: Tải (Clone) Repository và tạo môi trường ảo

Tải mã nguồn từ GitHub:

Generated bash
git clone https://github.com/SpaceNetLab/StarPerf_Simulator.git
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Di chuyển vào thư mục dự án:

Generated bash
cd StarPerf_Simulator
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Tạo một môi trường ảo Python. (Đây là cách làm tốt nhất để các thư viện của dự án này không ảnh hưởng đến hệ thống của bạn)

Generated bash
python3 -m venv venv
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Kích hoạt môi trường ảo:

Generated bash
source venv/bin/activate
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Sau khi chạy lệnh này, bạn sẽ thấy (venv) ở đầu dòng lệnh Terminal, cho biết bạn đang ở trong môi trường ảo.

Bước 4: Cài đặt các thư viện Python

Bây giờ, bạn có thể cài đặt tất cả các thư viện Python được liệt kê trong file requirements.txt một cách an toàn.

Generated bash
pip install -r requirements.txt
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END
Bước 5: Tải dữ liệu cần thiết cho mô phỏng

Simulator cần dữ liệu về quỹ đạo vệ tinh (TLE) và vị trí các trạm mặt đất. Repository đã cung cấp sẵn các script để tải chúng.

Tải dữ liệu TLE cho chòm sao Starlink:

Generated bash
python download_tle.py
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Lệnh này sẽ tải file starlink.txt vào thư mục constellations/starlink/.

Tải dữ liệu trạm mặt đất:

Generated bash
cd scenarios/starlink_550/
python download_ground_stations_starlink.py
cd ../..
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Lệnh này sẽ tải file ground_stations_starlink.json vào thư mục scenarios/starlink_550/.

Bây giờ, môi trường của bạn đã sẵn sàng để chạy mô phỏng.

Bước 6: Chạy một kịch bản mô phỏng ví dụ

Hãy chạy kịch bản tính toán độ trễ (latency) theo thời gian.

Generated bash
python main_latency_over_time.py
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Quá trình này có thể mất một vài phút tùy thuộc vào sức mạnh CPU của bạn. Nó sẽ tính toán, xử lý và sau đó hiển thị một biểu đồ. Tuy nhiên, chúng ta sẽ sửa đổi nó để lưu biểu đồ ra file ở phần tiếp theo.

Kết quả dữ liệu (dạng file .csv) sẽ được lưu trong thư mục outputs/data/starlink_550_isls_plus_grid/latency_over_time/.

Hướng dẫn lưu hình ảnh (figures) ra file

Mặc định, các script như main_latency_over_time.py sẽ hiển thị biểu đồ. Để lưu nó, bạn cần chỉnh sửa file Python.

Ví dụ với main_latency_over_time.py:

Mở file để chỉnh sửa:
Bạn có thể dùng bất kỳ trình soạn thảo văn bản nào, ví dụ gedit hoặc nano.

Generated bash
gedit main_latency_over_time.py
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Tìm và thay thế dòng mã:
Tìm đến cuối file, bạn sẽ thấy một đoạn mã tương tự như sau (khoảng dòng 212):

Generated python
# Before editing
# .
# . (các dòng code vẽ biểu đồ)
# .
plt.grid()
plt.legend()
plt.show()
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

Chỉnh sửa đoạn mã đó:
Hãy bình luận (comment out) dòng plt.show() và thêm vào dòng plt.savefig(). Để cho gọn gàng, chúng ta sẽ tạo một thư mục để lưu hình ảnh.

Generated python
# After editing
import os # Thêm dòng này ở đầu file nếu chưa có

# .
# . (các dòng code vẽ biểu đồ)
# .
plt.grid()
plt.legend()
# plt.show() # Vô hiệu hóa việc hiển thị trực tiếp

# Tạo thư mục lưu ảnh nếu chưa tồn tại
figure_dir = "outputs/figures/"
os.makedirs(figure_dir, exist_ok=True)

# Lưu biểu đồ ra file PNG chất lượng cao
figure_path = os.path.join(figure_dir, "latency_over_time.png")
plt.savefig(figure_path, dpi=300) 

print(f"Figure saved to: {figure_path}")
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

os.makedirs(..., exist_ok=True): Tạo thư mục outputs/figures/ một cách an toàn.

plt.savefig(figure_path, dpi=300): Lệnh chính để lưu biểu đồ.

figure_path: Đường dẫn và tên file.

dpi=300: (Dots Per Inch) Đặt độ phân giải cho ảnh, giúp ảnh sắc nét hơn.

Lưu file và chạy lại:
Lưu lại thay đổi trong trình soạn thảo của bạn. Bây giờ, chạy lại script:

Generated bash
python main_latency_over_time.py
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Lần này, chương trình sẽ không hiển thị biểu đồ. Thay vào đó, sau khi chạy xong, nó sẽ in ra một dòng thông báo, và bạn sẽ tìm thấy file latency_over_time.png trong thư mục StarPerf_Simulator/outputs/figures/.

Bạn có thể áp dụng phương pháp tương tự cho các file main_*.py khác (ví dụ: main_coverage_over_time.py) để lưu các biểu đồ tương ứng.

Tóm tắt luồng công việc của bạn

Mở Terminal.

cd StarPerf_Simulator

source venv/bin/activate (Luôn kích hoạt môi trường ảo mỗi khi bạn làm việc với dự án).

Chỉnh sửa file main_... .py bạn muốn chạy để thay plt.show() bằng plt.savefig(...).

Chạy script: python main_... .py.

Kiểm tra kết quả trong thư mục outputs/data/ (cho file dữ liệu) và outputs/figures/ (cho file hình ảnh).
