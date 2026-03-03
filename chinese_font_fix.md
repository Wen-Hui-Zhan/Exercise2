# 中文字體修復說明

## 問題描述
原本輸出的 PNG 圖表中，中文字元無法正確顯示，出現方塊字符。

## 解決方案

### 1. 新增字體檢測函數
創建了 `setup_chinese_font()` 函數，自動檢測系統中可用的中文字體：

```python
def setup_chinese_font():
    """設置中文字體"""
    # 嘗試不同的中文字體
    chinese_fonts = [
        'Microsoft JhengHei',  # Windows 微軟正黑體
        'Microsoft YaHei',     # Windows 微軟雅黑
        'SimHei',             # Windows 黑體
        'SimSun',             # Windows 宋體
        'PingFang SC',        # macOS 蘋方
        'Hiragino Sans GB',   # macOS 冬青黑體
        'WenQuanYi Zen Hei', # Linux 文泉驛正黑
        'Arial Unicode MS',    # 跨平台
        'DejaVu Sans'         # 備用
    ]
    
    # 檢查系統中可用的字體
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 找到第一個可用的中文字體
    for font in chinese_fonts:
        if font in available_fonts:
            plt.rcParams['font.sans-serif'] = [font] + plt.rcParams['font.sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            print(f"使用字體: {font}")
            return font
    
    # 如果沒有找到中文字體，使用預設字體並警告
    print("警告: 未找到合適的中文字體，圖表中文字可能無法正確顯示")
    return None
```

### 2. 修改圖表生成函數
在 `create_distance_analysis()` 函數中調用字體設置：

```python
def create_distance_analysis(self, df):
    # 設置中文字體
    setup_chinese_font()
    
    # 設置圖表樣式
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('氣象站坐標系統距離分析', fontsize=16, fontweight='bold')
```

### 3. 字體優先順序
按照作業系統和可用性設置字體優先順序：

1. **Windows**: Microsoft JhengHei → Microsoft YaHei → SimHei → SimSun
2. **macOS**: PingFang SC → Hiragino Sans GB
3. **Linux**: WenQuanYi Zen Hei
4. **跨平台**: Arial Unicode MS → DejaVu Sans

## 測試結果

### 系統檢測
- ✅ 成功檢測到系統字體
- ✅ 自動選擇最佳中文字體
- ✅ 在 Windows 系統上選擇了 "Microsoft JhengHei"

### 圖表輸出
- ✅ 所有中文字元正確顯示
- ✅ 圖表標題、軸標籤、統計文字都正常
- ✅ PNG 檔案中的中文完全可讀

### 生成檔案
- `distance_analysis_*.png` - 修復後的統計圖表
- `chinese_font_test.png` - 字體測試圖表

## 使用方法

### 自動修復
運行坐標比較分析時，字體會自動設置：

```bash
python scripts/coordinate_comparison.py
```

### 手動測試
測試中文字體設置：

```bash
python scripts/test_chinese_font.py
```

## 技術細節

### 字體檢測機制
- 使用 `matplotlib.font_manager.fontManager.ttflist` 獲取系統字體列表
- 按優先順序檢查中文字體可用性
- 動態設置 matplotlib 字體參數

### 相容性處理
- 設置 `axes.unicode_minus = False` 避免負號顯示問題
- 使用 `plt.style.use('default')` 確保樣式一致性
- 支援跨平台字體檢測

### 錯誤處理
- 如果沒有找到中文字體會顯示警告
- 仍然會生成圖表，但中文可能顯示為方塊
- 提供明確的錯誤訊息

## 注意事項

1. **系統字體**: 確保系統安裝了中文字體
2. **matplotlib 版本**: 建議使用較新版本的 matplotlib
3. **字體快取**: 首次運行可能需要重建字體快取
4. **跨平台**: 不同作業系統會自動選擇合適的字體

## 驗證方法

1. 查看控制台輸出的字體名稱
2. 檢查生成的 PNG 檔案中的中文顯示
3. 使用測試腳本驗證所有中文字元

---

**修復完成**: 所有輸出的 PNG 圖表現在都能正確顯示中文字元。
