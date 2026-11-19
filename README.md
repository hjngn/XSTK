# XSTK — Phân tích giá xe ô tô đã qua sử dụng (dữ liệu CarDekho)

Bài tập lớn môn **Xác suất – Thống kê**. Nhóm: **Khoa** (TV1) · **Uyên** (TV2) · **Sang** (TV3) · **Nguyên** (TV4).

Dữ liệu: `Car details v3.csv` (8.128 dòng × 13 cột) trong bộ
[Vehicle dataset from CarDekho](https://www.kaggle.com/datasets/nehalbirla/vehicle-dataset-from-cardekho).
Sau làm sạch: **`data/processed/cleaned_cars.csv` v1.0 — 6.693 dòng × 22 cột, đóng băng 18/11/2026.**

## Bắt đầu nhanh

```bash
pip install -r requirements.txt
python kiem_thu_quy_trinh.py                 # kiểm thử toàn bộ quy trình: PASS / WARN / FAIL
jupyter nbconvert --to notebook --execute --inplace notebooks/01_cleaning.ipynb   # tái tạo file sạch
python report/build_report.py                # dựng báo cáo Word -> report/output/BaoCao_XSTK.docx
```

```python
import pandas as pd
df = pd.read_csv("data/processed/cleaned_cars.csv")
assert df.shape == (6693, 22)
```

**Trên Kaggle:** tạo notebook mới → *Add Input* dataset `nehalbirla/vehicle-dataset-from-cardekho` → *File → Import
Notebook* `notebooks/01_cleaning.ipynb` → *Restart & Run All*. Notebook tự nhận đường dẫn `/kaggle/input` và ghi kết quả
vào `/kaggle/working`. Các notebook 02–04 cần thêm `cleaned_cars.csv` làm Input.

## Cấu trúc repository

```
data/
  raw/Car details v3.csv           dữ liệu gốc — không sửa (SHA-256 trong data/raw/README.md)
  processed/cleaned_cars.csv       dữ liệu chuẩn chung v1.0
  processed/cleaned_cars_v1.0.json siêu dữ liệu phiên bản (số dòng, SHA-256, tần số các mức)
  processed/cleaning_log.csv       số dòng trước/sau từng bước
notebooks/
  01_cleaning.ipynb                TV1 Khoa  — tiền xử lý (đã chạy, có output)
  02_eda.ipynb                     TV2 Uyên  — thống kê mô tả & ước lượng (khung sẵn)
  03_hypothesis.ipynb              TV3 Sang  — kiểm định giả thuyết (khung sẵn)
  04_regression.ipynb              TV4 Nguyên — hồi quy & chẩn đoán (khung sẵn)
figures/                           hình 300 dpi xuất từ từng notebook
docs/
  tu_dien_du_lieu.md               từ điển dữ liệu (cột gốc + cột sạch)
  nhat_ky_lam_sach.md              nhật ký làm sạch, quyết định và lý do
  quy_uoc_nhom.md                  câu hỏi nghiên cứu, quy ước, quy trình Git, tiến độ
report/
  chapters/*.md                    các chương báo cáo (Markdown)
  build_report.py                  dựng file Word đúng định dạng (A4, TNR 13, giãn dòng 1,5, lề 3-2-2-2 cm)
  output/                          BaoCao_XSTK.docx (toàn bộ), BaoCao_Chuong_1_2.docx
kiem_thu_quy_trinh.py              kiểm thử quy trình, cài đặt lại độc lập các quy tắc làm sạch
requirements.txt
```

## Tóm tắt làm sạch (chi tiết: [`docs/nhat_ky_lam_sach.md`](docs/nhat_ky_lam_sach.md))

| Bước | Nội dung | Còn lại |
|---:|---|---:|
| 0 | Dữ liệu gốc | 8.128 |
| 1 | Xoá 1.202 dòng trùng lặp (làm đầu tiên) | 6.926 |
| 2 | Tách đơn vị `mileage` (kmpl / km/kg), `engine` (cc), `max_power` (bhp), `torque` → N·m | 6.926 |
| 3 | Loại 224 dòng thiếu thông số kỹ thuật (gồm `mileage = 0`, `max_power` rỗng) | 6.702 |
| 4 | Loại 5 xe `Test Drive Car`; gộp 27 xe `Trustmark Dealer` vào `Dealer` | 6.697 |
| 5 | Loại 4 dòng `km_driven` vô lý (> 500.000 hoặc 1 km với xe 2011) — **không** cắt IQR trên giá | **6.693** |

Biến mới: `brand`, `model`, `car_age = 2020 − year`, `log_price`, `fuel_group` (CNG+LPG), `owner_rank`, `is_trustmark`,
`torque_nm`.

## Quy ước chung

α = 0,05 · `random_state = 42` · giá tính bằng INR · biến phụ thuộc `log_price` · mọi notebook đọc `cleaned_cars.csv`
v1.0 · mỗi người làm trên nhánh riêng, gộp vào `main` qua Pull Request có ít nhất một người duyệt.
Xem [`docs/quy_uoc_nhom.md`](docs/quy_uoc_nhom.md).
