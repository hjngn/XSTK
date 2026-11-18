# Nhật ký làm sạch dữ liệu — `cleaned_cars.csv` v1.0

Người thực hiện: **Khoa (TV1)** · Ngày đóng băng: **18/11/2026** · Notebook: `notebooks/01_cleaning.ipynb`
· Bảng máy đọc được: `data/processed/cleaning_log.csv`

## 1. Số dòng sau từng bước

| Bước | Nội dung | Trước | Bị loại | Còn lại | Lý do |
|---:|---|---:|---:|---:|---|
| 0 | Đọc `Car details v3.csv` | 8.128 | 0 | 8.128 | 13 cột, đúng cấu trúc |
| 1 | Xoá dòng trùng lặp hoàn toàn | 8.128 | **1.202** | 6.926 | Trùng cả 13 cột (625 nhóm); giữ lần đầu |
| 2 | Tách đơn vị `mileage`, `engine`, `max_power`, `torque` | 6.926 | 0 | 6.926 | 15 ô `mileage = 0`, 4 ô `max_power` rỗng/0, 3 ô `torque` vô lý → NA |
| 3 | Loại dòng thiếu `mileage`/`engine`/`max_power`/`seats` | 6.926 | **224** | 6.702 | 208 tin không có thông số kỹ thuật + 16 dòng có ô vô nghĩa |
| 4a | Loại `owner = Test Drive Car` | 6.702 | **5** | 6.697 | Không thuộc thang số đời chủ; nhóm quá nhỏ |
| 4b | Gộp `Trustmark Dealer` → `Dealer` | 6.697 | 0 | 6.697 | 27 xe; vẫn là đại lý; giữ cờ `is_trustmark` |
| 5a | Loại `km_driven > 500.000` | 6.697 | **3** | 6.694 | 2.360.457; 1.500.000; 577.414 km |
| 5b | Loại `km_driven < 1.000` với xe ≥ 2 tuổi | 6.694 | **1** | 6.693 | Maruti Eeco 2011, chủ thứ 4, ghi 1 km |
| 7 | Xuất `cleaned_cars.csv` v1.0 | 6.693 | 0 | **6.693** | Đóng băng |

Tổng cộng loại **1.435 dòng (17,7%)**, trong đó 1.202 dòng (83,8% số bị loại) là trùng lặp.

## 2. Quyết định và lý do

### 2.1. Xoá trùng trước mọi bước khác
Dòng trùng là cùng một tin rao bị thu thập nhiều lần. Nếu không xoá, các xe đó được tính nhiều lần, làm hẹp
khoảng tin cậy giả tạo và vi phạm giả định độc lập của các kiểm định. Xoá trùng trước giúp mọi con số đếm sau
(NA, mức hiếm) phản ánh số xe thật. Ví dụ: `Trustmark Dealer` có **236** dòng trong dữ liệu gốc nhưng chỉ còn
**27** xe sau xoá trùng — tức phần lớn tin của nhóm này là bản lặp.

### 2.2. `mileage` có hai đơn vị
Đơn vị khớp tuyệt đối với nhiên liệu: `kmpl` (km/lít) cho toàn bộ Petrol, Diesel; `km/kg` cho toàn bộ CNG, LPG.
Hai đơn vị đo hai đại lượng khác nhau nên **không so sánh chung**. File sạch giữ `mileage` dạng số và cột
`mileage_unit`; khi phân tích tiêu hao nhiên liệu phải tách theo đơn vị (hoặc chỉ dùng nhóm `kmpl`, 6.608 xe).
15 ô `0.0 kmpl` (không thể có) được coi là thiếu.

### 2.3. Giá trị khuyết — loại dòng, không điền
Thiếu tập trung ở cùng một nhóm dòng (thiếu đồng thời cả 5 cột thông số kỹ thuật). Tỷ lệ nhỏ (3,2% sau xoá trùng)
nên loại dòng. Không điền trung vị vì sẽ tạo ra nhiều xe "trung bình" giả và làm giảm phương sai.
**Hạn chế:** nhóm thiếu có giá trung vị thấp hơn (175.000 so với 420.000 INR) và cũ hơn (đời 2008 so với 2014),
nên dữ liệu thiếu **không hoàn toàn ngẫu nhiên** (không phải MCAR). Việc loại có thể làm mẫu nghiêng nhẹ về xe
mới hơn — cần ghi vào phần hạn chế ở Chương 4.

### 2.4. `torque` — tách thành biến phụ `torque_nm`
Cột ghi khoảng 20 định dạng khác nhau, lẫn N·m và kgf·m. Quy tắc: lấy số đầu tiên; `kgm` → × 9,80665;
không ghi đơn vị thì số ≥ 60 coi là N·m. Phát hiện lỗi nhập liệu: một số dòng ghi `(kgm@ rpm)` nhưng số là N·m
(Maruti SX4 `145@ 4,100(kgm@ rpm)` → 145 kgf·m ≈ 1.422 N·m là không thể với động cơ 1,6 lít) → giá trị "kgm" > 60
coi là N·m. Sau quy đổi, giá trị > 700 N·m vẫn vô lý (Maruti Zen D `789Nm`; xe hợp lệ lớn nhất là Volvo XC90 T8
640 N·m) → NA (3 ô). Bỏ chuỗi gốc và vòng tua. Không khuyến nghị đưa vào mô hình chính vì tương quan mạnh với
`max_power` (r = 0,85) và `engine` (r = 0,75).

### 2.5. Mức hiếm
* **`Test Drive Car` (5 xe, loại):** xe lái thử của đại lý, đời 2019, chưa qua tay chủ nào, giá gần xe mới
  (gồm 3 chiếc Audi A6 khoảng 6 triệu INR). Không nằm trên thang thứ bậc số đời chủ mà TV3 kiểm định; 5 quan sát
  không đủ làm một nhóm.
* **`Trustmark Dealer` (27 xe, gộp):** là đại lý được CarDekho chứng nhận, bản chất vẫn là đại lý. Giữ cờ
  `is_trustmark` để có thể tách lại.

### 2.6. Ngoại lai — chỉ loại giá trị vô lý, không cắt IQR trên giá
Nếu cắt IQR trên `selling_price` (ngưỡng trên 1.250.000 INR) sẽ mất 298 xe (4,4%), trong đó **63,1% là xe số
tự động**, tức mất **33,2% toàn bộ xe số tự động** (tỷ lệ xe số tự động trong mẫu giảm từ 8,5% xuống 5,9%), và mất
gần hết xe hạng sang (Audi 83%, BMW 69%, Mercedes-Benz 75%, Jeep, Jaguar 100%). Như vậy kiểm định Manual vs
Automatic (TV3) và hệ số hồi quy (TV4) sẽ bị lệch nghiêm trọng. Giá cao là **thật**, không phải lỗi → giữ lại và
dùng `log_price` (độ lệch giảm từ 5,46 xuống −0,17). Chỉ loại `km_driven` vô lý (4 dòng).

### 2.7. Biến tạo mới
`brand`, `model`, `car_age = 2020 − year`, `log_price`, `fuel_group`, `owner_rank`, `is_trustmark`, `torque_nm`.

## 3. Quản lý phiên bản

| Phiên bản | Ngày | Số dòng | SHA-256 (16 ký tự đầu) | Thay đổi |
|---|---|---:|---|---|
| v1.0 | 18/11/2026 | 6.693 | xem `cleaned_cars_v1.0.json` | Bản đóng băng đầu tiên (mốc 2) |

**Quy tắc sau mốc đóng băng:** không sửa `cleaned_cars.csv` v1.0. Nếu cần thay đổi → mở Issue/PR, báo cả nhóm,
tạo bản v1.1 kèm dòng mới trong bảng trên, chạy lại `kiem_thu_quy_trinh.py`, và mọi notebook 02–04 chạy lại.

## 4. Ghi chú về nguồn file

Môi trường làm việc không truy cập trực tiếp được Kaggle API, nên file `data/raw/Car details v3.csv` được lấy từ một
bản sao công khai của đúng bộ dữ liệu này. Đã đối chiếu: 8.128 dòng × 13 cột, 95 xe CNG + LPG, 236 Trustmark Dealer,
giá 29.999 – 10.000.000 INR, `km_driven` lớn nhất 2.360.457 — khớp mô tả của bộ dữ liệu Kaggle.
SHA-256: `788e7f7a5be161011789a0d4b64ea0879570348c943a414f4f99953f58d74048`. Khi chạy trên Kaggle, notebook đọc
trực tiếp file Kaggle; `kiem_thu_quy_trinh.py` sẽ báo WARN nếu SHA-256 khác (ví dụ do ký tự xuống dòng) và vẫn
đối chiếu toàn bộ nội dung.
