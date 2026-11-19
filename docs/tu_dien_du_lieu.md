# Từ điển dữ liệu — `cleaned_cars.csv` v1.0

* **Nguồn:** `Car details v3.csv`, bộ *Vehicle dataset from CarDekho* (Nehal Birla và cộng sự, Kaggle):
  <https://www.kaggle.com/datasets/nehalbirla/vehicle-dataset-from-cardekho>.
  Dữ liệu là tin rao bán xe đã qua sử dụng trên CarDekho.com (Ấn Độ), thu thập khoảng năm 2020.
* **Đơn vị quan sát:** một tin rao bán một chiếc xe.
* **Kích thước:** gốc 8.128 dòng × 13 cột → sạch **6.693 dòng × 22 cột**.
* **Sinh ra bởi:** `notebooks/01_cleaning.ipynb` · **Kiểm thử:** `kiem_thu_quy_trinh.py`.
* **Ngày đóng băng:** 18/11/2026 · SHA-256 ghi trong `data/processed/cleaned_cars_v1.0.json`.

## 1. Dữ liệu gốc (13 cột)

| Cột gốc | Kiểu gốc | Ví dụ | Ý nghĩa | Vấn đề phát hiện | Cách xử lý |
|---|---|---|---|---|---|
| `name` | chuỗi | `Maruti Swift Dzire VDI` | Hãng + dòng xe + phiên bản | Không có cột hãng riêng | Tách `brand`, `model` |
| `year` | số nguyên | `2014` | Năm sản xuất | Năm từ 1983 đến 2020 | Tạo `car_age = 2020 − year` |
| `selling_price` | số nguyên | `450000` | Giá rao bán (INR) | Lệch phải mạnh (29.999 – 10.000.000) | **Giữ nguyên**, thêm `log_price` |
| `km_driven` | số nguyên | `145500` | Số km đã chạy | Giá trị vô lý: 2.360.457; 1 km với xe 2011 | Loại > 500.000 và < 1.000 khi xe ≥ 2 tuổi |
| `fuel` | phân loại | `Diesel` | Nhiên liệu | CNG, LPG rất ít | Giữ 4 mức + thêm `fuel_group` |
| `seller_type` | phân loại | `Individual` | Loại người bán | `Trustmark Dealer` hiếm (27 sau xoá trùng) | Gộp vào `Dealer`, cờ `is_trustmark` |
| `transmission` | phân loại | `Manual` | Hộp số | — | Giữ nguyên |
| `owner` | phân loại thứ bậc | `First Owner` | Số đời chủ | `Test Drive Car` (5 xe) | Loại; thêm `owner_rank` |
| `mileage` | chuỗi | `23.4 kmpl`, `26.6 km/kg` | Mức tiêu hao nhiên liệu | 2 đơn vị; 208 NA; 15 ô `0.0` | Tách số + `mileage_unit`; 0 → NA |
| `engine` | chuỗi | `1248 CC` | Dung tích xi-lanh | 208 NA | Tách số (cc) |
| `max_power` | chuỗi | `74 bhp` | Công suất cực đại | 205 NA; 3 ô `0`, 1 ô chỉ `bhp` | Tách số (bhp); rỗng/0 → NA |
| `torque` | chuỗi | `190Nm@ 2000rpm`, `12.7@ 2,700(kgm@ rpm)` | Mô-men xoắn cực đại @ vòng tua | ~20 định dạng; lẫn Nm/kgm; ghi nhầm đơn vị | Tách `torque_nm` (biến phụ), bỏ chuỗi gốc và rpm |
| `seats` | số thực | `5.0` | Số chỗ ngồi | 208 NA | Đổi sang số nguyên |

(Số NA trong bảng là sau khi xoá trùng; trước xoá trùng: mileage/engine/seats 221, max_power 215, torque 222.)

## 2. File sạch (22 cột)

| # | Cột | Kiểu | Đơn vị / Mức | Ý nghĩa | Nguồn / công thức |
|---|---|---|---|---|---|
| 1 | `raw_index` | int | 0 – 8127 | Chỉ số dòng trong file gốc (đếm từ 0, không tính tiêu đề) | Truy vết |
| 2 | `name` | str | — | Tên xe gốc | `name` |
| 3 | `brand` | str | 31 hãng | Hãng xe | Từ đầu của `name`; `Land` → `Land Rover`, `Ashok` → `Ashok Leyland` |
| 4 | `model` | str | — | Dòng xe | Từ đầu tiên sau tên hãng |
| 5 | `year` | int | 1994 – 2020 | Năm sản xuất | `year` |
| 6 | `car_age` | int | năm, 0 – 26 | Tuổi xe tại năm thu thập | `2020 − year` |
| 7 | `selling_price` | int | INR, 29.999 – 10.000.000 | Giá rao bán | `selling_price` |
| 8 | `log_price` | float | ln(INR), 10,31 – 16,12 | Log tự nhiên của giá | `ln(selling_price)` |
| 9 | `km_driven` | int | km, 1.000 – 500.000 | Số km đã chạy | `km_driven` |
| 10 | `fuel` | str | Diesel, Petrol, CNG, LPG | Nhiên liệu (dùng cho mô tả) | `fuel` |
| 11 | `fuel_group` | str | Diesel, Petrol, CNG/LPG | Nhiên liệu đã gộp nhóm nhỏ (dùng cho kiểm định) | CNG, LPG → `CNG/LPG` |
| 12 | `seller_type` | str | Individual, Dealer | Loại người bán | `Trustmark Dealer` → `Dealer` |
| 13 | `is_trustmark` | int | 0/1 | 1 nếu là đại lý Trustmark của CarDekho | `seller_type` gốc |
| 14 | `transmission` | str | Manual, Automatic | Hộp số | `transmission` |
| 15 | `owner` | str | First, Second, Third, Fourth & Above Owner | Số đời chủ | `owner` (đã bỏ Test Drive Car) |
| 16 | `owner_rank` | int | 1 – 4 | Mã thứ bậc của `owner` | First = 1, …, Fourth & Above = 4 |
| 17 | `mileage` | float | kmpl **hoặc** km/kg | Mức tiêu hao nhiên liệu (số) | Tách số từ `mileage` |
| 18 | `mileage_unit` | str | kmpl, km/kg | Đơn vị của `mileage` | `kmpl` ↔ Petrol/Diesel; `km/kg` ↔ CNG/LPG |
| 19 | `engine` | int | cc, 624 – 3.604 | Dung tích động cơ | Tách số từ `engine` |
| 20 | `max_power` | float | bhp, 32,8 – 400 | Công suất cực đại | Tách số từ `max_power` |
| 21 | `torque_nm` | float | N·m, 47,1 – 640; **3 NA** | Mô-men xoắn cực đại (biến phụ) | Số đầu của `torque`; kgm × 9,80665 |
| 22 | `seats` | int | chỗ, 4 – 14 | Số chỗ ngồi | `seats` |

## 3. Tần số các biến phân loại sau làm sạch

| Biến | Mức (số xe) |
|---|---|
| `fuel` | Diesel 3.651 · Petrol 2.957 · CNG 50 · LPG 35 |
| `fuel_group` | Diesel 3.651 · Petrol 2.957 · CNG/LPG 85 |
| `transmission` | Manual 6.127 · Automatic 566 |
| `seller_type` | Individual 6.009 · Dealer 684 (trong đó Trustmark 27) |
| `owner` | First 4.165 · Second 1.883 · Third 492 · Fourth & Above 153 |
| `mileage_unit` | kmpl 6.608 · km/kg 85 |
| `brand` (10 hãng nhiều xe nhất) | Maruti 2.087 · Hyundai 1.206 · Mahindra 706 · Tata 632 · Honda 360 · Ford 353 · Toyota 324 · Chevrolet 216 · Renault 206 · Volkswagen 170 |

## 4. Lưu ý khi dùng

1. **Biến phụ thuộc** nên dùng `log_price` (độ lệch 5,46 → −0,17). Hệ số β trong mô hình log-tuyến tính:
   giá thay đổi khoảng `100·(e^β − 1)%` khi biến tăng 1 đơn vị (hoặc khi chuyển sang mức dummy).
2. **`mileage` có hai đơn vị**: không tính trung bình chung, không đưa thẳng vào mô hình cùng xe CNG/LPG
   mà không xử lý (ví dụ chỉ dùng nhóm `kmpl`, hoặc thêm tương tác với `mileage_unit`).
3. **`fuel_group`** dùng cho kiểm định (ANOVA/Kruskal-Wallis, Chi-squared) để tránh nhóm quá nhỏ.
4. **`owner_rank`** dùng cho tương quan Spearman / kiểm định xu hướng (Jonckheere-Terpstra).
5. **`torque_nm`** có 3 NA và tương quan mạnh với `max_power` (r ≈ 0,85) và `engine` (r ≈ 0,75):
   không khuyến nghị đưa vào mô hình chính; **không** `dropna()` toàn bảng.
6. **`brand`** có 31 mức, 12 hãng dưới 10 xe → gộp nhóm trước khi tạo dummy (việc của TV4).
7. Một số cột là **dữ liệu khai báo của người bán** (km, giá rao) — giá rao không phải giá giao dịch thực.
