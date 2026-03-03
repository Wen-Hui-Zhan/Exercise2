#!/usr/bin/env python3
"""
坐標比較測試腳本
使用模擬資料測試坐標比較功能
"""

import pandas as pd
import numpy as np
from coordinate_comparison import CoordinateComparison
import os
from datetime import datetime

def create_test_data():
    """創建測試用的模擬氣象站資料"""
    np.random.seed(42)  # 確保可重複性
    
    # 台灣主要城市的大概坐標
    taiwan_cities = [
        {"name": "台北", "lat": 25.033, "lon": 121.565},
        {"name": "新竹", "lat": 24.813, "lon": 120.967},
        {"name": "台中", "lat": 24.147, "lon": 120.673},
        {"name": "嘉義", "lat": 23.481, "lon": 120.449},
        {"name": "台南", "lat": 22.999, "lon": 120.226},
        {"name": "高雄", "lat": 22.627, "lon": 120.314},
        {"name": "花蓮", "lat": 23.752, "lon": 121.560},
        {"name": "宜蘭", "lat": 24.692, "lon": 121.770},
        {"name": "台東", "lat": 22.756, "lon": 121.144},
        {"name": "澎湖", "lat": 23.569, "lon": 119.578},
        {"name": "金門", "lat": 24.432, "lon": 118.317},
        {"name": "馬祖", "lat": 26.163, "lon": 119.950}
    ]
    
    stations = []
    for i, city in enumerate(taiwan_cities):
        # 基本坐標（坐標系統2 - WGS84）
        coord2_lat = city["lat"]
        coord2_lon = city["lon"]
        
        # 坐標系統1 - 添加隨機偏移（模擬不同坐標系統的差異）
        # 偏移範圍：緯度 ±0.001度（約±100米），經度 ±0.001度（約±100米）
        offset_lat = np.random.uniform(-0.001, 0.001)
        offset_lon = np.random.uniform(-0.001, 0.001)
        
        coord1_lat = coord2_lat + offset_lat
        coord1_lon = coord2_lon + offset_lon
        
        station = {
            'station_id': f'CWA{i+1:03d}',
            'station_name': f'{city["name"]}氣象站',
            'coord1_latitude': coord1_lat,
            'coord1_longitude': coord1_lon,
            'coord1_name': 'TWD97',
            'coord2_latitude': coord2_lat,
            'coord2_longitude': coord2_lon,
            'coord2_name': 'WGS84',
            'temperature': np.random.uniform(18, 32),  # 18-32°C
            'humidity': np.random.uniform(40, 90),     # 40-90%
            'observation_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00'),
            'location': city["name"] + "市",
            'weather': np.random.choice(['晴', '多雲', '陰', '小雨']),
            'wind_speed': np.random.uniform(0, 15),    # 0-15 m/s
            'wind_direction': np.random.uniform(0, 360), # 0-360°
            'air_pressure': np.random.uniform(990, 1020) # 990-1020 hPa
        }
        stations.append(station)
    
    return pd.DataFrame(stations)

def main():
    """主程式"""
    print("創建測試資料...")
    
    # 創建測試資料
    test_df = create_test_data()
    
    # 確保 outputs 目錄存在
    os.makedirs("outputs", exist_ok=True)
    
    # 儲存測試資料
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_csv_file = f"outputs/test_weather_stations_{timestamp}.csv"
    test_df.to_csv(test_csv_file, index=False, encoding='utf-8-sig')
    print(f"測試資料已儲存至: {test_csv_file}")
    
    # 顯示測試資料摘要
    print(f"\n=== 測試資料摘要 ===")
    print(f"測站數量: {len(test_df)}")
    print(f"坐標系統1: {test_df['coord1_name'].iloc[0]}")
    print(f"坐標系統2: {test_df['coord2_name'].iloc[0]}")
    
    # 顯示前3筆資料
    print(f"\n=== 前3筆測站資料 ===")
    for i, (_, row) in enumerate(test_df.head(3).iterrows()):
        print(f"{i+1}. {row['station_name']}")
        print(f"   坐標系統1: ({row['coord1_latitude']:.6f}, {row['coord1_longitude']:.6f})")
        print(f"   坐標系統2: ({row['coord2_latitude']:.6f}, {row['coord2_longitude']:.6f})")
        print(f"   溫度: {row['temperature']:.1f}°C")
        print()
    
    # 使用坐標比較分析器
    print("開始坐標比較分析...")
    analyzer = CoordinateComparison()
    
    # 載入並處理資料
    df = analyzer.load_and_process_data(test_csv_file)
    
    if df is not None:
        # 生成統計報告
        analyzer.generate_distance_report(df)
        
        # 創建比較地圖
        map_file = analyzer.create_comparison_map(df)
        
        # 創建距離分析圖表
        chart_file = analyzer.create_distance_analysis(df)
        
        if map_file and chart_file:
            print(f"\n=== 測試完成 ===")
            print(f"坐標比較地圖: {map_file}")
            print(f"距離分析圖表: {chart_file}")
            print(f"\n可以在瀏覽器中開啟 HTML 檔案查看地圖")
            print("這是使用模擬資料的測試結果")
    else:
        print("資料處理失敗")

if __name__ == "__main__":
    main()
