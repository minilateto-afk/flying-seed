# 飛行種子重新分析計算附件

## 檔案

- `seed_measurements.csv`：三十筆原始紀錄，各實驗十五筆。
- `seed_reanalysis.py`：從 CSV 計算描述統計、最小平方直線、殘差、兩種決定係數與平方和分解，並繪圖。
- `seed_summary.json`：程式輸出的完整數值。
- `seed_figures.png`：兩實驗的原始值、平均及標準差與各自的擬合直線。
- `seed_residuals.png`：兩實驗相對各自直線的殘差圖。
- `seed_report.md`：含公式的完整研究報告文字稿。

## 執行

需要 Python 3、NumPy 及 Matplotlib。將附件解壓到同一資料夾後執行：

```bash
python -m pip install numpy matplotlib
python seed_reanalysis.py
```

有 Noto Sans TC、Noto Sans CJK TC 或微軟正黑體時，圖表以繁體中文標示；其他環境自動使用英文標示，數值結果相同。

## 欄位與解讀

`experiment` 為 `wing_length` 或 `weight`。`predictor_value` 是該實驗的原表設定值，`predictor_unit` 為 `cm` 或 `g`。

`trial_within_setting` 是「第一次」至「第五次」的組內編號，並非已知的跨組時序。`model_id` 與 `global_release_order` 空白表示未記錄，不能將每列解讀為獨立製作的模型。`source_page` 是原 PDF 的實體頁碼。資料依設定值排序，不表示原實驗的操作先後。

分析保留全部紀錄，沒有刪除離群值或進行顯著性檢定。兩實驗分別分析，沒有合併成同時含翅長與重量的模型。標準差描述組內散布；圖上的誤差棒不是信賴區間。RMSE 及 R² 都是樣本內描述，並非預測準確率。
