# data/processed — dữ liệu chuẩn chung của nhóm

| File | Nội dung |
|---|---|
| `cleaned_cars.csv` | **v1.0 — đóng băng 18/11/2026**, 6.693 dòng × 22 cột. Mọi notebook 02–04 đọc file này. |
| `cleaned_cars_v1.0.json` | Siêu dữ liệu phiên bản: số dòng, SHA-256, quy tắc, tần số các mức |
| `cleaning_log.csv` | Số dòng trước/sau từng bước làm sạch |

Từ điển dữ liệu: [`docs/tu_dien_du_lieu.md`](../../docs/tu_dien_du_lieu.md) ·
Nhật ký: [`docs/nhat_ky_lam_sach.md`](../../docs/nhat_ky_lam_sach.md)

```python
import pandas as pd
df = pd.read_csv("data/processed/cleaned_cars.csv")   # trong repo
assert df.shape == (6693, 22), "Sai phiên bản cleaned_cars.csv"
```

⚠️ Không sửa file này bằng tay. Muốn thay đổi: mở Pull Request sửa notebook 01, báo cả nhóm, tăng phiên bản (v1.1).
