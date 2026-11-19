# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Bối cảnh và lý do chọn đề tài

Thị trường ô tô đã qua sử dụng là một bộ phận quan trọng của thị trường ô tô ở các nền kinh tế đang phát triển,
nơi nhiều hộ gia đình chọn mua xe cũ vì chi phí thấp hơn đáng kể so với xe mới. Ấn Độ là một ví dụ điển hình:
các nền tảng giao dịch trực tuyến như CarDekho.com cho phép hàng nghìn người bán cá nhân và đại lý đăng tin rao
bán, kèm theo thông tin về năm sản xuất, số km đã chạy, nhiên liệu, hộp số, số đời chủ và các thông số kỹ thuật.

Khác với xe mới có giá niêm yết của hãng, giá xe cũ được hình thành từ thoả thuận giữa người mua và người bán,
nên chịu ảnh hưởng đồng thời của nhiều yếu tố: tuổi xe và mức độ hao mòn (số km), đặc điểm kỹ thuật (dung tích động
cơ, công suất), thương hiệu, loại nhiên liệu, loại hộp số và lịch sử sở hữu. Cả người mua lẫn người bán đều gặp khó
khăn khi định giá một chiếc xe cụ thể: người bán dễ đặt giá quá cao hoặc quá thấp, người mua thiếu căn cứ để đánh
giá mức giá rao có hợp lý hay không.

Bài toán này phù hợp với môn Xác suất – Thống kê vì ba lý do. **Thứ nhất**, dữ liệu có đủ cả biến định lượng
(giá, số km, tuổi xe, dung tích, công suất) và biến định tính (nhiên liệu, hộp số, người bán, số đời chủ), cho phép áp
dụng trọn vẹn chuỗi phương pháp từ thống kê mô tả, ước lượng, kiểm định giả thuyết đến hồi quy. **Thứ hai**, dữ liệu
thực có nhiều "khuyết tật" điển hình — dòng trùng lặp, giá trị khuyết, đơn vị đo không thống nhất, giá trị vô lý,
phân phối lệch mạnh — buộc nhóm phải kiểm tra giả định của từng phương pháp thay vì áp dụng máy móc. **Thứ ba**, kết
quả có ý nghĩa thực tiễn rõ ràng: lượng hoá được mỗi năm tuổi xe hay mỗi lựa chọn hộp số làm giá thay đổi bao nhiêu
phần trăm.

## 1.2. Mục tiêu nghiên cứu

**Mục tiêu tổng quát:** vận dụng các phương pháp thống kê để mô tả, so sánh và mô hình hoá giá bán xe ô tô đã qua
sử dụng trên CarDekho.com, từ đó xác định các yếu tố ảnh hưởng đến giá và mức độ ảnh hưởng của chúng.

**Mục tiêu cụ thể:**

1. Xây dựng một bộ dữ liệu sạch, có thể tái lập, làm chuẩn chung cho mọi phân tích (tệp `cleaned_cars.csv` v1.0).
2. Mô tả phân phối của giá bán và các đặc trưng của xe; ước lượng khoảng tin cậy 95% cho giá trung bình theo phân khúc
   hộp số và loại nhiên liệu.
3. Kiểm định sự khác biệt về giá giữa xe số sàn và xe số tự động, giữa các loại nhiên liệu, giữa các mức số đời chủ;
   kiểm định tính độc lập giữa loại nhiên liệu và loại hộp số.
4. Xây dựng mô hình hồi quy tuyến tính bội cho logarit của giá bán, chẩn đoán các giả định của mô hình và đánh giá khả
   năng dự báo trên tập kiểm tra.

## 1.3. Câu hỏi nghiên cứu

Các câu hỏi nghiên cứu được nhóm thống nhất trước khi phân tích (Bảng 1.1). Giả thuyết cụ thể (H0, H1) của từng câu
hỏi được trình bày ở mục 3.2.

: Bảng 1.1. Câu hỏi nghiên cứu và phương pháp tương ứng

| Mã | Câu hỏi nghiên cứu | Phương pháp chính | Mục |
|---|---|---|---|
| CH1 | Giá xe cũ phân bố như thế nào; giá trung bình theo hộp số và nhiên liệu nằm trong khoảng nào? | Thống kê mô tả; khoảng tin cậy 95% | 3.1 |
| CH2 | Giá xe số tự động có cao hơn xe số sàn không? | Welch t-test trên log(giá); Mann-Whitney U | 3.2 |
| CH3 | Giá xe có khác nhau theo loại nhiên liệu và theo số đời chủ không? | Welch ANOVA / Kruskal-Wallis; hậu kiểm; Spearman | 3.2 |
| CH4 | Loại nhiên liệu và loại hộp số có độc lập với nhau không? | Kiểm định Chi-bình phương; Cramér's V | 3.2 |
| CH5 | Những yếu tố nào ảnh hưởng đến giá và ảnh hưởng bao nhiêu? | Hồi quy tuyến tính bội trên log(giá) | 3.3 |

*Nguồn: Nhóm nghiên cứu.*

## 1.4. Đối tượng và phạm vi nghiên cứu

* **Đối tượng nghiên cứu:** giá rao bán của xe ô tô con đã qua sử dụng và các yếu tố liên quan.
* **Đơn vị quan sát:** một tin rao bán một chiếc xe trên CarDekho.com.
* **Phạm vi không gian:** thị trường Ấn Độ; giá tính bằng rupee Ấn Độ (INR).
* **Phạm vi thời gian:** xe sản xuất từ 1994 đến 2020 (sau làm sạch), dữ liệu được thu thập khoảng năm 2020; vì vậy
  tuổi xe được tính theo năm tham chiếu 2020.
* **Giới hạn:** giá trong dữ liệu là **giá rao bán**, không phải giá giao dịch cuối cùng; các thông tin như số km và
  số đời chủ do người bán tự khai báo. Dữ liệu là dữ liệu chéo quan sát, nên các kết quả chỉ cho biết **mối liên hệ**,
  không khẳng định quan hệ nhân quả.

## 1.5. Dữ liệu nghiên cứu

Dữ liệu được lấy từ bộ *Vehicle dataset from CarDekho* đăng trên Kaggle (Birla, Verma & Kushwaha, n.d.). Bộ dữ liệu
gồm nhiều tệp; nhóm đã đối chiếu hai tệp thường được sử dụng (Bảng 1.2).

: Bảng 1.2. So sánh hai tệp dữ liệu trong bộ Vehicle dataset from CarDekho

| Tiêu chí | `car data.csv` | `Car details v3.csv` (**được chọn**) |
|---|---|---|
| Số dòng × số cột | 301 × 9 | 8.128 × 13 |
| Mức tiêu hao nhiên liệu, dung tích, công suất | Không có | Có (`mileage`, `engine`, `max_power`, `torque`) |
| Số chỗ ngồi | Không có | Có (`seats`) |
| Tên xe để tách hãng | Chỉ tên dòng xe | Có đủ hãng + dòng + phiên bản |
| Nhiên liệu | Petrol, Diesel, CNG | Petrol, Diesel, CNG, LPG |
| Giá trị khuyết | Không | Khoảng 2,7% ở các cột kỹ thuật |
| Dòng trùng lặp | — | 1.202 dòng |

*Nguồn: Nhóm tổng hợp từ Kaggle; số liệu tệp v3 lấy từ `notebooks/01_cleaning.ipynb`.*

Notebook tham khảo đi kèm đường dẫn của đề bài sử dụng tệp `car data.csv` (301 dòng). Tệp này quá nhỏ và thiếu các
biến kỹ thuật cần cho kiểm định và hồi quy, nên nhóm chọn **`Car details v3.csv`**. Sau quá trình làm sạch (mục 2.7),
bộ dữ liệu phân tích gồm **6.693 xe** với 22 biến, trong đó có các biến gốc đã chuẩn hoá đơn vị và các biến tạo mới
(`brand`, `car_age`, `log_price`, `fuel_group`, `owner_rank`, …). Toàn bộ định nghĩa biến được trình bày trong từ điển
dữ liệu (Phụ lục A, tệp `docs/tu_dien_du_lieu.md`).

## 1.6. Phương pháp nghiên cứu và công cụ

Nghiên cứu được tiến hành theo bốn giai đoạn nối tiếp nhau; mỗi giai đoạn tương ứng một notebook và một thành viên
phụ trách (Bảng 1.3).

: Bảng 1.3. Quy trình nghiên cứu

| Giai đoạn | Nội dung | Sản phẩm | Phụ trách |
|---|---|---|---|
| 1. Tiền xử lý | Xoá trùng, chuẩn hoá đơn vị, xử lý giá trị khuyết, mức hiếm, giá trị vô lý; tạo biến mới | `cleaned_cars.csv` v1.0, từ điển dữ liệu, nhật ký làm sạch | Khoa |
| 2. Thống kê mô tả và ước lượng | Đặc trưng mẫu, biểu đồ phân phối, tương quan, khoảng tin cậy 95% | Mục 3.1 | Uyên |
| 3. Kiểm định giả thuyết | Kiểm tra giả định; t-test, ANOVA, phi tham số, Chi-bình phương; hệ số ảnh hưởng | Mục 3.2 | Sang |
| 4. Hồi quy và chẩn đoán | Hồi quy tuyến tính bội, chọn biến, VIF, chẩn đoán phần dư, đánh giá trên tập kiểm tra | Mục 3.3, Chương 4 | Nguyên |

*Nguồn: Nhóm nghiên cứu.*

**Công cụ:** ngôn ngữ Python 3 với các thư viện `pandas`, `numpy` (xử lý dữ liệu), `matplotlib`, `seaborn` (trực quan
hoá), `scipy`, `statsmodels`, `pingouin`, `scikit-posthocs` (kiểm định và hồi quy), `scikit-learn` (chia tập và đánh giá
mô hình). Mã nguồn được quản lý bằng Git trên một repository GitHub chung; các notebook có thể chạy lại trên Kaggle.

**Nguyên tắc tái lập:** mọi phân tích đọc cùng một tệp `cleaned_cars.csv` v1.0 đã được "đóng băng" (có mã băm
SHA-256); mức ý nghĩa thống nhất α = 0,05; mọi thao tác ngẫu nhiên dùng `random_state = 42`; mỗi con số trong báo cáo
đều truy được về một ô mã trong notebook. Tệp `kiem_thu_quy_trinh.py` tự động kiểm tra lại toàn bộ quy trình làm sạch
bằng một cài đặt độc lập.

## 1.7. Ý nghĩa của nghiên cứu

* **Về phương pháp:** minh hoạ một quy trình phân tích thống kê đầy đủ trên dữ liệu thực — từ làm sạch có kiểm soát,
  kiểm tra giả định trước khi kiểm định, đến chẩn đoán mô hình hồi quy — và chỉ ra những sai lầm thường gặp khi áp dụng
  máy móc (cắt ngoại lai theo IQR trên biến lệch, dùng Shapiro-Wilk với mẫu rất lớn, so sánh chung hai đơn vị đo khác nhau).
* **Về thực tiễn:** cung cấp căn cứ định lượng cho người mua và người bán xe cũ khi đánh giá mức giá hợp lý, ví dụ mức
  chênh lệch giá giữa xe số tự động và số sàn hay mức giảm giá theo mỗi năm tuổi xe.

## 1.8. Cấu trúc báo cáo

Ngoài phần mở đầu, tài liệu tham khảo và phụ lục, báo cáo gồm bốn chương:

* **Chương 1 – Giới thiệu:** bối cảnh, mục tiêu, câu hỏi nghiên cứu, phạm vi, dữ liệu và phương pháp.
* **Chương 2 – Cơ sở lý thuyết và dữ liệu:** các khái niệm và phương pháp thống kê được sử dụng; mô tả dữ liệu và quy
  trình tiền xử lý.
* **Chương 3 – Kết quả phân tích:** thống kê mô tả và ước lượng (3.1), kiểm định giả thuyết (3.2), mô hình hồi quy (3.3).
* **Chương 4 – Kết luận và kiến nghị:** tổng hợp kết quả, hạn chế và hướng phát triển.
