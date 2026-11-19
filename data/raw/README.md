# data/raw — dữ liệu gốc (KHÔNG SỬA)

| File | Nguồn | Kích thước | SHA-256 |
|---|---|---|---|
| `Car details v3.csv` | [Kaggle — nehalbirla/vehicle-dataset-from-cardekho](https://www.kaggle.com/datasets/nehalbirla/vehicle-dataset-from-cardekho) | 8.128 dòng × 13 cột | `788e7f7a5be161011789a0d4b64ea0879570348c943a414f4f99953f58d74048` |

* Nhóm **không dùng** `car data.csv` (301 dòng, 9 cột) vì thiếu `mileage`, `engine`, `max_power`, hãng xe và LPG.
* Mọi xử lý thực hiện trong `notebooks/01_cleaning.ipynb`; kết quả nằm ở `data/processed/`.
* Kiểm tra tính toàn vẹn: `sha256sum "data/raw/Car details v3.csv"` hoặc `python kiem_thu_quy_trinh.py`.
