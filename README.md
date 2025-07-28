# learning-simulation

## Link practice:
https://aistudio.google.com/prompts/1Iie8Wr0f-i8Dqpe8Ce2ADLB9hyvpRRjf

## Link thư viện: 
https://github.com/haodpsut/StarPerf_Simulator
https://github.com/SpaceNetLab/StarPerf_Simulator

Lộ trình tổng thể: Từ Người mới bắt đầu đến Nhà nghiên cứu
Mục tiêu cuối cùng: Xuất bản một bài báo khoa học chất lượng về tối ưu hóa hiệu năng mạng vệ tinh (LEO/GEO).
Nguyên tắc chỉ đạo: "Đi chậm mà chắc". Hiểu sâu sắc từng bước trước khi chuyển sang bước tiếp theo.

## Giai đoạn 1: Làm chủ công cụ (Mastering the Simulator) - ~1-2 tuần

Mục tiêu của giai đoạn này là bạn phải hiểu StarPerf_Simulator "từ trong ra ngoài". Bạn phải biết nó làm gì, làm như thế nào, và giới hạn của nó ở đâu.

Tuần 1: Cài đặt và Chạy các ví dụ cơ bản

Nhiệm vụ 1.1: Thiết lập môi trường.

Hành động: Thực hiện theo hướng dẫn cài đặt tôi đã gửi trước. Cài đặt trên Ubuntu, tạo môi trường ảo, cài đặt requirements.txt, và tải dữ liệu TLE.
Mục tiêu: Chạy thành công lệnh python main_latency_over_time.py mà không gặp lỗi.

Nhiệm vụ 1.2: "Phá vỡ" và Sửa chữa.

Hành động: Mở file scenarios/starlink_550/starlink_550_isls_plus_grid.json. Thử thay đổi các tham số: start_time, end_time, time_step_s. Thêm một thành phố mới vào danh sách city_ground_stations_to_be_placed. Chạy lại và xem kết quả thay đổi ra sao.
Mục tiêu: Hiểu được cấu trúc của một file kịch bản và ý nghĩa của từng tham số.

Nhiệm vụ 1.3: Đọc hiểu mã nguồn cốt lõi.

Hành động: Mở và đọc các file sau. Đừng cố gắng hiểu từng dòng, hãy tập trung vào chức năng chính của mỗi file:
main_latency_over_time.py: Luồng chính của một kịch bản là gì? Dữ liệu được tải, xử lý và vẽ biểu đồ như thế nào?
starperf/simulation.py: Tìm hàm run_simulation(). Đây là trái tim của simulator. Nó lặp qua từng bước thời gian (time step) như thế nào?
starperf/static_graph.py và starperf/dynamic_graph.py: Sự khác biệt giữa đồ thị tĩnh và động là gì? Hàm nào chịu trách nhiệm thêm các "cạnh" (liên kết ISL/GSL) vào đồ thị?
Mục tiêu: Vẽ ra được sơ đồ khối (flowchart) đơn giản về cách simulator hoạt động.

Tuần 2: Mở rộng và Tùy chỉnh cơ bản

Nhiệm vụ 2.1: Thêm một chỉ số đo lường mới.

Hành động: Trong main_latency_over_time.py, ngoài việc tính độ trễ (latency), hãy sửa đổi để tính và lưu cả số bước nhảy (hop count) của đường đi ngắn nhất. (Gợi ý: nx.shortest_path_length(G, source, target, weight=None)).
Mục tiêu: Chứng tỏ bạn có thể can thiệp vào vòng lặp mô phỏng để trích xuất dữ liệu mình muốn.

Nhiệm vụ 2.2: Trực quan hóa Topo mạng.

Hành động: Viết một script Python đơn giản. Tại một thời điểm cụ thể, script này sẽ tạo ra đồ thị mạng và sau đó sử dụng networkx cùng matplotlib để vẽ đồ thị đó ra file ảnh. Bạn không cần vẽ trên bản đồ Trái đất, chỉ cần vẽ các nút và cạnh.
Mục tiêu: Hiểu được cấu trúc dữ liệu đồ thị mà simulator tạo ra.

Nhiệm vụ 2.3 (Nâng cao): Thử nghiệm với một thuật toán định tuyến khác.

Hành động: Như ví dụ trước, hãy so sánh độ trễ của đường đi "lowest-latency" (dùng weight='latency_s') và đường đi "least-hop" (dùng weight=None). In kết quả so sánh ra màn hình.
Mục tiêu: Nắm vững cách thay đổi "bộ não" định tuyến của simulator.
Kết thúc Giai đoạn 1, bạn có thể tự tin trả lời:
Làm thế nào để chạy một kịch bản mô phỏng?
Làm thế nào để thay đổi các tham số đầu vào?
Phần nào của mã nguồn chịu trách nhiệm cho việc tính toán quỹ đạo, xây dựng mạng, và tìm đường đi?
Làm thế nào để lấy thêm dữ liệu từ mô phỏng và lưu nó?

## Giai đoạn 2: Xây dựng nền tảng cho nghiên cứu (Building the Research Foundation) - ~2-3 tuần
Bây giờ chúng ta sẽ bắt đầu xây dựng các "viên gạch" cần thiết cho bài toán giảm độ trễ của bạn.

Nhiệm vụ 3.1: Mô hình hóa Băng thông và Độ trễ truyền tải.

Hành động: Viết một lớp Link trong Python. Mỗi đối tượng Link sẽ có các thuộc tính: bandwidth (ví dụ: 10 Gbps), source_node, destination_node. Thêm một phương thức calculate_transmission_delay(packet_size) cho lớp này.
Hành động: Sửa đổi code tạo đồ thị. Thay vì chỉ thêm một cạnh với trọng số là latency_s, bây giờ mỗi cạnh sẽ được liên kết với một đối tượng Link.
Mục tiêu: Chuyển đổi mô hình mạng từ "chỉ có độ trễ truyền lan" sang một mô hình thực tế hơn.

Nhiệm vụ 3.2: Mô hình hóa Tải và Hàng đợi (đơn giản).

Hành động: Thêm thuộc tính current_load (tải hiện tại) vào lớp Link. Viết một hàm update_load(traffic_volume).
Hành động: Viết một hàm calculate_queuing_delay(packet_size) đơn giản. Ban đầu, có thể dùng công thức tuyến tính: delay = current_load * constant.
Mục tiêu: Xây dựng một mô hình trừu tượng về tắc nghẽn mạng.

Nhiệm vụ 3.3: Tổng hợp các thành phần độ trễ.

Hành động: Tạo một hàm get_total_expected_latency(link, packet_size) trả về tổng của: propagation_delay + transmission_delay + queuing_delay.
Hành động: Sửa đổi thuật toán định tuyến. Bây giờ, trọng số của mỗi cạnh sẽ được tính động bằng hàm này.
Mục tiêu: Tạo ra một thuật toán định tuyến nhận biết được tắc nghẽn (congestion-aware). Chạy so sánh với thuật toán ban đầu và xem đường đi thay đổi như thế nào.
Kết thúc Giai đoạn 2, bạn sẽ có một phiên bản "nâng cấp" của StarPerf có khả năng:
Mô phỏng băng thông và tắc nghẽn.
Tính toán một cách toàn diện hơn các thành phần của độ trễ.
Tìm đường đi thông minh hơn để tránh các liên kết đang bận.

## Giai đoạn 3: Thực hiện nghiên cứu và Viết bài (Conducting Research & Writing the Paper) - ~4+ tuần
Đây là lúc áp dụng những gì đã xây dựng để tạo ra tri thức mới.

Nhiệm vụ 4.1: Hoàn thiện Ý tưởng nghiên cứu.

Hành động: Dựa trên những gì bạn đã làm, hãy chốt lại câu hỏi nghiên cứu chính. Ví dụ: "Một chiến lược phân lớp dữ liệu kết hợp với định tuyến nhận biết tắc nghẽn có thể cải thiện chất lượng trải nghiệm cho các ứng dụng thời gian thực trên mạng LEO đến mức độ nào?"
Hành động: Thực hiện khảo sát tài liệu (literature review) một cách nghiêm túc để xác định tính mới của đề tài.

Nhiệm vụ 4.2: Triển khai mô hình Phân lớp dữ liệu.

Hành động: Triển khai mô hình QoS/phân lớp dữ liệu mà chúng ta đã thảo luận. Tạo các luồng dữ liệu giả lập thuộc các lớp khác nhau.
Hành động: Hoàn thiện thuật toán định tuyến của bạn để nó ưu tiên các lớp dữ liệu khác nhau.

Nhiệm vụ 4.3: Thiết kế và Chạy thực nghiệm toàn diện.

Hành động: Thiết kế các kịch bản so sánh (baseline vs. proposed solution). Chạy mô phỏng và thu thập dữ liệu một cách có hệ thống.

Nhiệm vụ 4.4: Phân tích và Viết bài.

Hành động: Vẽ biểu đồ, phân tích kết quả, và bắt đầu viết bài báo theo cấu trúc chuẩn. Chúng ta có thể cùng nhau xem xét từng phần: từ Abstract, Introduction đến Conclusion.

## Giai đoạn 4: Mở rộng sang GEO (Optional)
Sau khi đã thành công với LEO, việc chuyển sang GEO sẽ dễ dàng hơn.
Thách thức chính với GEO: Độ trễ truyền lan rất lớn (hàng trăm ms), nhưng topo mạng lại tĩnh. Các bài toán về tắc nghẽn và phân bổ băng thông (beam allocation) sẽ quan trọng hơn là định tuyến động. Bạn có thể tái sử dụng các mô hình về tải và hàng đợi đã xây dựng để nghiên cứu các vấn đề này.
