#!/usr/bin/env python3
"""
氣象站坐標系統比較視覺化腳本
比較兩個坐標系統的差異並繪製在同一張圖上
"""

import pandas as pd
import folium
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic
import os
from datetime import datetime
import matplotlib.font_manager as fm

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
            # 強制設置字體參數
            plt.rcParams.update({
                'font.family': ['sans-serif'],
                'font.sans-serif': [font] + [f for f in plt.rcParams.get('font.sans-serif', []) if f != font],
                'axes.unicode_minus': False
            })
            
            print(f"使用字體: {font}")
            print(f"字體設置: {plt.rcParams['font.sans-serif'][:3]}")
            return font
    
    # 如果沒有找到中文字體，使用預設字體並警告
    print("警告: 未找到合適的中文字體，圖表中文字可能無法正確顯示")
    return None

class CoordinateComparison:
    def __init__(self):
        self.colors = {
            'coord1': '#FF0000',  # 紅色 - 坐標系統1
            'coord2': '#0000FF',  # 藍色 - 坐標系統2
            'connection': '#00FF00'  # 綠色 - 連接線
        }
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """計算兩個坐標之間的距離（米）"""
        try:
            point1 = (lat1, lon1)
            point2 = (lat2, lon2)
            return geodesic(point1, point2).meters
        except:
            return None
    
    def load_and_process_data(self, csv_file):
        """載入並處理坐標資料"""
        try:
            df = pd.read_csv(csv_file)
            print(f"成功載入 {len(df)} 筆測站資料")
            
            # 過濾有效坐標資料
            valid_df = df.dropna(subset=[
                'coord1_latitude', 'coord1_longitude', 
                'coord2_latitude', 'coord2_longitude'
            ])
            
            print(f"有效坐標資料: {len(valid_df)} 筆")
            
            # 計算距離
            valid_df['distance_meters'] = valid_df.apply(
                lambda row: self.calculate_distance(
                    row['coord1_latitude'], row['coord1_longitude'],
                    row['coord2_latitude'], row['coord2_longitude']
                ), axis=1
            )
            
            # 移除距離計算失敗的記錄
            valid_df = valid_df.dropna(subset=['distance_meters'])
            print(f"成功計算距離的資料: {len(valid_df)} 筆")
            
            return valid_df
            
        except Exception as e:
            print(f"載入資料失敗: {e}")
            return None
    
    def create_comparison_map(self, df, output_file=None):
        """創建坐標比較地圖"""
        if df is None or len(df) == 0:
            print("沒有資料可繪製")
            return None
        
        # 計算地圖中心點（使用坐標系統2的平均位置）
        center_lat = df['coord2_latitude'].mean()
        center_lon = df['coord2_longitude'].mean()
        
        # 創建地圖
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # 添加圖例
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4 style="margin: 0 0 10px 0;">坐標系統圖例</h4>
        <p style="margin: 5px 0;"><span style="color: #FF0000;">●</span> 坐標系統1</p>
        <p style="margin: 5px 0;"><span style="color: #0000FF;">●</span> 坐標系統2</p>
        <p style="margin: 5px 0;"><span style="color: #00FF00;">—</span> 連接線</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 為每個測站添加標記和連接線
        for idx, row in df.iterrows():
            station_name = row['station_name']
            
            # 坐標系統1標記（紅色）
            folium.CircleMarker(
                location=[row['coord1_latitude'], row['coord1_longitude']],
                radius=6,
                popup=f"{station_name}<br>坐標系統1 ({row['coord1_name']})<br>"
                      f"({row['coord1_latitude']:.6f}, {row['coord1_longitude']:.6f})",
                color='black',
                weight=1,
                fillColor=self.colors['coord1'],
                fillOpacity=0.8
            ).add_to(m)
            
            # 坐標系統2標記（藍色）
            folium.CircleMarker(
                location=[row['coord2_latitude'], row['coord2_longitude']],
                radius=6,
                popup=f"{station_name}<br>坐標系統2 ({row['coord2_name']})<br>"
                      f"({row['coord2_latitude']:.6f}, {row['coord2_longitude']:.6f})<br>"
                      f"距離: {row['distance_meters']:.2f}m",
                color='black',
                weight=1,
                fillColor=self.colors['coord2'],
                fillOpacity=0.8
            ).add_to(m)
            
            # 連接線（綠色）
            folium.PolyLine(
                locations=[
                    [row['coord1_latitude'], row['coord1_longitude']],
                    [row['coord2_latitude'], row['coord2_longitude']]
                ],
                color=self.colors['connection'],
                weight=2,
                opacity=0.6
            ).add_to(m)
        
        # 儲存地圖
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"outputs/coordinate_comparison_map_{timestamp}.html"
        
        m.save(output_file)
        print(f"坐標比較地圖已儲存至: {output_file}")
        
        return output_file
    
    def create_distance_analysis(self, df):
        """創建距離分析圖表"""
        if df is None or len(df) == 0:
            print("沒有資料可分析")
            return
        
        # 設置中文字體
        setup_chinese_font()
        
        # 設置圖表樣式
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('氣象站坐標系統距離分析', fontsize=16, fontweight='bold')
        
        # 1. 距離分佈直方圖
        axes[0, 0].hist(df['distance_meters'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_xlabel('距離 (米)')
        axes[0, 0].set_ylabel('測站數量')
        axes[0, 0].set_title('坐標系統間距離分佈')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 距離統計箱型圖
        axes[0, 1].boxplot(df['distance_meters'], vert=True)
        axes[0, 1].set_ylabel('距離 (米)')
        axes[0, 1].set_title('距離分佈箱型圖')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 距離與溫度關係散佈圖
        valid_temp_df = df.dropna(subset=['temperature'])
        if len(valid_temp_df) > 0:
            axes[1, 0].scatter(valid_temp_df['temperature'], valid_temp_df['distance_meters'], 
                            alpha=0.6, color='coral')
            axes[1, 0].set_xlabel('溫度 (°C)')
            axes[1, 0].set_ylabel('距離 (米)')
            axes[1, 0].set_title('距離與溫度關係')
            axes[1, 0].grid(True, alpha=0.3)
        else:
            axes[1, 0].text(0.5, 0.5, '無有效溫度資料', ha='center', va='center', 
                          transform=axes[1, 0].transAxes)
        
        # 4. 距離統計摘要
        distance_stats = df['distance_meters'].describe()
        stats_text = f"""
        距離統計摘要 (米)
        =================
        測站數量: {len(df)}
        平均距離: {distance_stats['mean']:.2f}
        標準差: {distance_stats['std']:.2f}
        最小距離: {distance_stats['min']:.2f}
        最大距離: {distance_stats['max']:.2f}
        中位數: {distance_stats['50%']:.2f}
        第25百分位: {distance_stats['25%']:.2f}
        第75百分位: {distance_stats['75%']:.2f}
        """
        
        axes[1, 1].text(0.1, 0.9, stats_text, transform=axes[1, 1].transAxes, 
                       fontsize=10, verticalalignment='top')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        # 儲存圖表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_file = f"outputs/distance_analysis_{timestamp}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        print(f"距離分析圖表已儲存至: {chart_file}")
        
        plt.show()
        return chart_file
    
    def generate_distance_report(self, df):
        """生成距離統計報告"""
        if df is None or len(df) == 0:
            print("沒有資料可分析")
            return
        
        # 基本統計
        distance_stats = df['distance_meters'].describe()
        
        # 距離分類
        distance_categories = {
            '很小 (<10m)': len(df[df['distance_meters'] < 10]),
            '小 (10-50m)': len(df[(df['distance_meters'] >= 10) & (df['distance_meters'] < 50)]),
            '中等 (50-100m)': len(df[(df['distance_meters'] >= 50) & (df['distance_meters'] < 100)]),
            '大 (100-500m)': len(df[(df['distance_meters'] >= 100) & (df['distance_meters'] < 500)]),
            '很大 (>500m)': len(df[df['distance_meters'] >= 500])
        }
        
        # 找出最大和最小距離的測站
        max_distance_idx = df['distance_meters'].idxmax()
        min_distance_idx = df['distance_meters'].idxmin()
        
        max_distance_station = df.loc[max_distance_idx]
        min_distance_station = df.loc[min_distance_idx]
        
        print("\n" + "="*60)
        print("氣象站坐標系統距離分析報告")
        print("="*60)
        
        print(f"\n基本統計:")
        print(f"  總測站數量: {len(df)}")
        print(f"  平均距離: {distance_stats['mean']:.2f} 米")
        print(f"  標準差: {distance_stats['std']:.2f} 米")
        print(f"  最小距離: {distance_stats['min']:.2f} 米")
        print(f"  最大距離: {distance_stats['max']:.2f} 米")
        print(f"  中位數: {distance_stats['50%']:.2f} 米")
        
        print(f"\n距離分佈:")
        for category, count in distance_categories.items():
            percentage = (count / len(df)) * 100
            print(f"  {category}: {count} 站 ({percentage:.1f}%)")
        
        print(f"\n極值測站:")
        print(f"  最大距離: {max_distance_station['station_name']} - {max_distance_station['distance_meters']:.2f} 米")
        print(f"  最小距離: {min_distance_station['station_name']} - {min_distance_station['distance_meters']:.2f} 米")
        
        print(f"\n坐標系統資訊:")
        coord1_names = df['coord1_name'].unique()
        coord2_names = df['coord2_name'].unique()
        print(f"  坐標系統1: {', '.join(coord1_names)}")
        print(f"  坐標系統2: {', '.join(coord2_names)}")
        
        print("="*60)

def main():
    """主程式"""
    # 查找最新的 CSV 檔案
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        print("找不到 outputs 目錄，請先執行 cwa_weather_api.py")
        return
    
    csv_files = [f for f in os.listdir(output_dir) if f.startswith('weather_stations_') and f.endswith('.csv')]
    
    if not csv_files:
        print("找不到氣象站 CSV 資料檔，請先執行 cwa_weather_api.py")
        return
    
    # 使用最新的檔案
    latest_csv = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(output_dir, x)))
    csv_path = os.path.join(output_dir, latest_csv)
    print(f"使用資料檔案: {csv_path}")
    
    # 創建比較分析器
    analyzer = CoordinateComparison()
    
    # 載入並處理資料
    print("\n正在載入並處理資料...")
    df = analyzer.load_and_process_data(csv_path)
    
    if df is not None:
        # 生成統計報告
        print("\n正在生成統計報告...")
        analyzer.generate_distance_report(df)
        
        # 創建比較地圖
        print("\n正在創建坐標比較地圖...")
        map_file = analyzer.create_comparison_map(df)
        
        # 創建距離分析圖表
        print("\n正在創建距離分析圖表...")
        chart_file = analyzer.create_distance_analysis(df)
        
        if map_file and chart_file:
            print(f"\n=== 輸出檔案 ===")
            print(f"坐標比較地圖: {map_file}")
            print(f"距離分析圖表: {chart_file}")
            print("\n可以在瀏覽器中開啟 HTML 檔案查看地圖")

if __name__ == "__main__":
    main()
