# 氣象站坐標系統比較分析

這個專案分析中央氣象署 API 中每個測站的兩個坐標系統，並將它們都視為 WGS84 EPSG:4326 進行比較。

## 功能特色

1. **雙坐標系統支援**: 解析 API 回應中的兩組坐標資料
2. **距離計算**: 計算兩個坐標系統之間的實際距離差異
3. **視覺化分析**: 
   - 互動式地圖顯示兩個坐標位置
   - 連接線顯示坐標差異
   - 距離分佈統計圖表
4. **統計報告**: 詳細的距離統計分析

## 檔案結構

```
Exercise2/
├── scripts/
│   ├── cwa_weather_api.py          # 修改後的 API 腳本（支援雙坐標）
│   ├── coordinate_comparison.py    # 新增的坐標比較分析腳本
│   ├── weather_map_visualization.py # 原有的地圖視覺化
│   └── debug_api.py               # API 調試工具
├── outputs/                       # 輸出目錄
└── requirements.txt               # 更新後的依賴套件
```

## 使用方法

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. 設定 API 金鑰

在專案根目錄建立 `.env` 檔案：

```
CWA_API_KEY=你的API金鑰
```

### 3. 獲取氣象站資料

```bash
python scripts/cwa_weather_api.py
```

這會：
- 從 CWA API 獲取氣象站資料
- 解析兩個坐標系統
- 儲存 CSV 檔案到 `outputs/` 目錄

### 4. 執行坐標比較分析

```bash
python scripts/coordinate_comparison.py
```

這會生成：
- **互動式地圖** (`coordinate_comparison_map_*.html`): 顯示兩個坐標系統的位置
- **統計圖表** (`distance_analysis_*.png`): 距離分佈分析
- **統計報告**: 在終端機顯示詳細統計資訊

## 輸出說明

### 地圖視覺化
- **紅色圓點**: 坐標系統1的位置
- **藍色圓點**: 坐標系統2的位置  
- **綠色連接線**: 顯示兩個坐標之間的距離差異
- **點擊標記**: 可查看詳細資訊和距離

### 統計分析
- **距離分佈直方圖**: 顯示所有測站的距離分佈
- **箱型圖**: 距離的統計分佈
- **散佈圖**: 距離與溫度的關係
- **統計摘要**: 詳細的數值統計

### 統計報告包含：
- 平均距離、標準差、最大/最小距離
- 距離分類統計（<10m, 10-50m, 50-100m, 100-500m, >500m）
- 極值測站資訊
- 坐標系統名稱

## 技術細節

### 坐標處理
- API 回應中的 `Coordinates[0]` 和 `Coordinates[1]` 分別對應兩個坐標系統
- 兩組坐標都被視為 WGS84 EPSG:4326 處理
- 使用 `geopy.distance.geodesic` 計算實際地面距離

### 距離計算
```python
from geopy.distance import geodesic

def calculate_distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).meters
```

### 視覺化工具
- **Folium**: 互動式地圖
- **Matplotlib + Seaborn**: 統計圖表
- **Pandas**: 資料處理

## 預期結果

根據氣象站坐標系統的特性，預期會發現：

1. **大部分測站距離很小**: 通常在幾米到幾十米之間
2. **部分測站距離較大**: 可能由於坐標轉換或測站位置變更
3. **系統性差異**: 某些地區可能顯示特定的坐標偏移模式

## 注意事項

1. 確保有網路連線以存取 CWA API
2. API 金鑰需要有效授權
3. 輸出檔案會儲存在 `outputs/` 目錄中
4. 地圖檔案需要在瀏覽器中開啟查看

## 故障排除

- **API 授權錯誤**: 檢查 `.env` 檔案中的 API 金鑰
- **無坐標資料**: 確認 API 回應格式是否正確
- **距離計算錯誤**: 檢查坐標格式和數值範圍
