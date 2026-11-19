# Quy ước làm việc chung của nhóm

## 1. Câu hỏi nghiên cứu (chốt ở mốc 1)

| # | Câu hỏi | Phương pháp chính | Phụ trách |
|---|---|---|---|
| CH1 | Giá xe cũ phân bố thế nào; giá trung bình theo hộp số và nhiên liệu nằm trong khoảng nào? | Thống kê mô tả, KTC 95% trên `log_price` | Uyên |
| CH2 | Giá xe số tự động có cao hơn xe số sàn không? | Welch t-test trên `log_price` (Mann-Whitney U kiểm tra lại), Cohen's d | Sang |
| CH3 | Giá có khác nhau theo nhiên liệu và theo số đời chủ không? | Welch ANOVA + Games-Howell / Kruskal-Wallis + Dunn (Holm); Spearman với `owner_rank` | Sang |
| CH4 | Nhiên liệu và loại hộp số có độc lập không? | Chi-squared (kiểm tra tần số kỳ vọng ≥ 5), Cramér's V | Sang |
| CH5 | Những yếu tố nào ảnh hưởng đến giá và ảnh hưởng bao nhiêu? | Hồi quy tuyến tính bội trên `log_price`, stepwise AIC/BIC, VIF, HC3 | Nguyên |

## 2. Quy ước kỹ thuật

* **α = 0,05** cho mọi kiểm định; hiệu chỉnh đa kiểm định bằng **Holm** khi có nhiều so sánh.
* **random_state = 42** cho mọi thao tác ngẫu nhiên (chia train/test, bootstrap, `sample`).
* **Giá tính bằng INR.** Khi trình bày có thể đổi sang "lakh" (1 lakh = 100.000 INR) nhưng phải ghi rõ.
* **Dữ liệu:** mọi notebook đọc `data/processed/cleaned_cars.csv` **v1.0** (kiểm tra `df.shape == (6693, 22)`).
* **Biến phụ thuộc:** `log_price`; báo cáo kết quả quy đổi về thang giá gốc khi cần.
* **Nhiên liệu:** `fuel_group` (3 mức) cho kiểm định; `fuel` (4 mức) cho mô tả.
* **Hình:** 300 dpi, nhãn tiếng Việt, đơn vị trên trục, đánh số `Hình <chương>.<số>`; lưu `figures/<notebook>/`.
  (Quy chuẩn chi tiết do Uyên chốt; TV1 đã dùng font DejaVu Sans, `savefig.dpi = 300`.)
* **Bảng:** đánh số `Bảng <chương>.<số>`, tiêu đề **trên** bảng, nguồn **dưới** bảng; số dùng dấu phẩy thập phân
  và dấu chấm phân cách hàng nghìn trong báo cáo (ví dụ 6.693; 0,05).

## 3. Cấu trúc repository

```
data/raw/                 dữ liệu gốc (không sửa)
data/processed/           cleaned_cars.csv v1.0 + siêu dữ liệu
notebooks/01_cleaning     TV1 — Khoa
notebooks/02_eda          TV2 — Uyên
notebooks/03_hypothesis   TV3 — Sang
notebooks/04_regression   TV4 — Nguyên
figures/                  hình xuất từ notebook (300 dpi)
docs/                     từ điển dữ liệu, nhật ký làm sạch, quy ước
report/                   các chương báo cáo (Markdown) + script dựng file Word
kiem_thu_quy_trinh.py     kiểm thử toàn bộ quy trình (PASS/WARN/FAIL)
```

## 4. Quy trình Git

1. Mỗi người làm trên **nhánh riêng**: `tv1-khoa-cleaning`, `tv2-uyen-eda`, `tv3-sang-hypothesis`, `tv4-nguyen-regression`.
2. Commit nhỏ, thông điệp rõ ràng (ví dụ `eda: thêm KTC 95% cho giá theo hộp số`).
3. Gộp vào `main` qua **Pull Request**, có **ít nhất một người khác duyệt**:
   * Khoa ↔ Nguyên: kiểm tra chéo phần dữ liệu và mô hình;
   * Uyên ↔ Sang: kiểm tra chéo phần mô tả, ước lượng và kiểm định.
4. Trước khi mở PR: **Restart & Run All** notebook không lỗi, chạy `python kiem_thu_quy_trinh.py` không có FAIL.
5. Không commit file lớn ngoài dữ liệu đã có; không commit khoá/token.

## 5. Tiêu chí nghiệm thu (nhắc lại)

* Notebook chạy Restart & Run All không lỗi, đọc từ `cleaned_cars.csv` v1.0.
* Mỗi con số trong báo cáo truy được về một ô code.
* Mỗi kiểm định ghi đủ H0/H1, tên kiểm định và lý do chọn, giá trị thống kê, p-value, hệ số ảnh hưởng, kết luận thực tế.
* Hình và bảng theo quy chuẩn chung, có đánh số và nguồn.
* Người review chéo đã đồng ý.
* `kiem_thu_quy_trinh.py` không còn FAIL; mỗi WARN có cách xử lý ghi trong báo cáo.

## 6. Tiến độ

| Mốc | Hạn | Việc | Người phụ trách | Trạng thái |
|:-:|:-:|---|---|---|
| 1 | __/__ | Chốt dataset, câu hỏi nghiên cứu, từ điển dữ liệu, repository | Khoa (cả nhóm duyệt) | ✅ Đã có bản đề xuất — chờ nhóm duyệt |
| 2 | __/__ | `cleaned_cars.csv` v1.0 đóng băng | Khoa | ✅ 18/11/2026 — 6.693 dòng |
| 3 | __/__ | Bản nháp 3.1, 3.2, 3.3 + notebook chạy được | Uyên, Sang, Nguyên | ⏳ Đã có notebook khởi tạo |
| 4 | __/__ | Review chéo, sửa theo góp ý | Theo cặp | ⏳ |
| 5 | __/__ | Ghép báo cáo, slide, tập thuyết trình | Khoa (ghép), Uyên (slide) | ⏳ Đã có khung báo cáo + script dựng Word |
