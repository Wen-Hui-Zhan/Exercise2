#!/usr/bin/env python3
"""
坐標比較分析腳本
分析氣象站兩種坐標系統的差異，並生成視覺化圖表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from haversine import haversine
import seaborn as sns
from datetime import datetime
import os

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

class CoordinateComparison:
    def __init__(self):
        self.data = None
        
    def load_and_process_data(self, csv_file):
        """載入並處理氣象站資料"""
        try:
            self.data = pd.read_csv(csv_file)
            print(f"成功載入 {len(self.data)} 筆測站資料")
            
            # 計算兩坐標系統之間的距離
            self.data['distance_meters'] = self.data.apply(
                self.calculate_distance, axis=1
            )
            
            return self.data
            
        except Exception as e:
            print(f"載入資料失敗: {e}")
            return None
    
    def calculate_distance(self, row):
        """計算兩坐標系統之間的距離（米）"""
        coord1 = (row['coord1_latitude'], row['coord1_longitude'])
        coord2 = (row['coord2_latitude'], row['coord2_longitude'])
        
        return haversine(coord1, coord2) * 1000  # 轉換為米
    
    def generate_distance_report(self, df):
        """生成距離統計報告"""
        print("\n=== 坐標差異統計報告 ===")
        
        distances = df['distance_meters']
        
        print(f"測站總數: {len(df)}")
        print(f"平均距離: {distances.mean():.2f} 米")
        print(f"最大距離: {distances.max():.2f} 米")
        print(f"最小距離: {distances.min():.2f} 米")
        print(f"標準差: {distances.std():.2f} 米")
        
        # 找出距離最大的測站
        max_dist_idx = distances.idxmax()
        max_dist_station = df.loc[max_dist_idx]
        
        print(f"\n距離最大的測站: {max_dist_station['station_name']}")
        print(f"距離: {max_dist_station['distance_meters']:.2f} 米")
        print(f"坐標系統1 ({max_dist_station['coord1_name']}): "
              f"({max_dist_station['coord1_latitude']:.6f}, {max_dist_station['coord1_longitude']:.6f})")
        print(f"坐標系統2 ({max_dist_station['coord2_name']}): "
              f"({max_dist_station['coord2_latitude']:.6f}, {max_dist_station['coord2_longitude']:.6f})")
        
        # 距離分佈統計
        print(f"\n=== 距離分佈 ===")
        print(f"< 10米: {len(distances[distances < 10])} 個測站 ({len(distances[distances < 10])/len(distances)*100:.1f}%)")
        print(f"10-50米: {len(distances[(distances >= 10) & (distances < 50)])} 個測站")
        print(f"50-100米: {len(distances[(distances >= 50) & (distances < 100)])} 個測站")
        print(f"> 100米: {len(distances[distances >= 100])} 個測站")
        
        return distances
    
    def create_comparison_map(self, df):
        """創建坐標比較地圖"""
        # 計算台灣中心點
        center_lat = df['coord1_latitude'].mean()
        center_lon = df['coord1_longitude'].mean()
        
        # 創建地圖
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # 添加測站坐標
        for idx, row in df.iterrows():
            # 坐標系統1 (紅色)
            folium.CircleMarker(
                location=[row['coord1_latitude'], row['coord1_longitude']],
                radius=5,
                popup=f"{row['station_name']}<br>"
                      f"{row['coord1_name']}<br>"
                      f"({row['coord1_latitude']:.6f}, {row['coord1_longitude']:.6f})<br>"
                      f"距離差異: {row['distance_meters']:.1f}米",
                color='red',
                fill=True,
                fillColor='red',
                fillOpacity=0.7
            ).add_to(m)
            
            # 坐標系統2 (藍色)
            folium.CircleMarker(
                location=[row['coord2_latitude'], row['coord2_longitude']],
                radius=5,
                popup=f"{row['station_name']}<br>"
                      f"{row['coord2_name']}<br>"
                      f"({row['coord2_latitude']:.6f}, {row['coord2_longitude']:.6f})<br>"
                      f"距離差異: {row['distance_meters']:.1f}米",
                color='blue',
                fill=True,
                fillColor='blue',
                fillOpacity=0.7
            ).add_to(m)
            
            # 連接線 (如果距離 > 10米)
            if row['distance_meters'] > 10:
                folium.PolyLine(
                    locations=[
                        [row['coord1_latitude'], row['coord1_longitude']],
                        [row['coord2_latitude'], row['coord2_longitude']]
                    ],
                    color='green',
                    weight=1,
                    opacity=0.5,
                    popup=f"距離: {row['distance_meters']:.1f}米"
                ).add_to(m)
        
        # 添加圖例
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>坐標系統</h4>
        <p><i class="fa fa-circle" style="color:red"></i> TWD67</p>
        <p><i class="fa fa-circle" style="color:blue"></i> WGS84</p>
        <p><i class="fa fa-minus" style="color:green"></i> 連接線</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 儲存地圖
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_file = f"outputs/coordinate_comparison_map_{timestamp}.html"
        m.save(map_file)
        
        return map_file
    
    def create_distance_analysis(self, df):
        """創建距離分析圖表"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Weather Station Coordinate System Difference Analysis', fontsize=16, fontweight='bold')
        
        # 1. 距離分佈直方圖
        axes[0, 0].hist(df['distance_meters'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Distance Distribution')
        axes[0, 0].set_xlabel('Distance (meters)')
        axes[0, 0].set_ylabel('Number of Stations')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 距離箱型圖
        axes[0, 1].boxplot(df['distance_meters'])
        axes[0, 1].set_title('Distance Box Plot')
        axes[0, 1].set_ylabel('Distance (meters)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 距離 vs 緯度散布圖
        axes[1, 0].scatter(df['coord1_latitude'], df['distance_meters'], 
                          alpha=0.6, color='red', label='TWD67')
        axes[1, 0].scatter(df['coord2_latitude'], df['distance_meters'], 
                          alpha=0.6, color='blue', label='WGS84')
        axes[1, 0].set_title('Distance vs Latitude')
        axes[1, 0].set_xlabel('Latitude')
        axes[1, 0].set_ylabel('Distance (meters)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 距離 vs 經度散布圖
        axes[1, 1].scatter(df['coord1_longitude'], df['distance_meters'], 
                          alpha=0.6, color='red', label='TWD67')
        axes[1, 1].scatter(df['coord2_longitude'], df['distance_meters'], 
                          alpha=0.6, color='blue', label='WGS84')
        axes[1, 1].set_title('Distance vs Longitude')
        axes[1, 1].set_xlabel('Longitude')
        axes[1, 1].set_ylabel('Distance (meters)')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        # 添加統計信息
        stats_text = f'Mean: {df["distance_meters"].mean():.1f}m\n'
        stats_text += f'Max: {df["distance_meters"].max():.1f}m\n'
        stats_text += f'Min: {df["distance_meters"].min():.1f}m\n'
        stats_text += f'Std: {df["distance_meters"].std():.1f}m'
        
        fig.text(0.02, 0.02, stats_text, fontsize=12, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
        
        plt.tight_layout()
        
        # 儲存圖表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_file = f"outputs/distance_analysis_{timestamp}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_file
    
    def export_detailed_results(self, df, output_file):
        """匯出詳細分析結果"""
        # 按距離排序
        df_sorted = df.sort_values('distance_meters', ascending=False)
        
        # 創建詳細報告
        report = []
        report.append("# 氣象站坐標系統差異詳細報告")
        report.append(f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析測站數: {len(df)}")
        report.append(f"\n## 統計摘要")
        report.append(f"- 平均距離: {df['distance_meters'].mean():.2f} 米")
        report.append(f"- 最大距離: {df['distance_meters'].max():.2f} 米")
        report.append(f"- 最小距離: {df['distance_meters'].min():.2f} 米")
        report.append(f"- 標準差: {df['distance_meters'].std():.2f} 米")
        
        report.append(f"\n## 距離最大的前10個測站")
        for i, (_, row) in enumerate(df_sorted.head(10).iterrows()):
            report.append(f"\n{i+1}. **{row['station_name']}**")
            report.append(f"   - 距離差異: {row['distance_meters']:.2f} 米")
            report.append(f"   - {row['coord1_name']}: ({row['coord1_latitude']:.6f}, {row['coord1_longitude']:.6f})")
            report.append(f"   - {row['coord2_name']}: ({row['coord2_latitude']:.6f}, {row['coord2_longitude']:.6f})")
        
        # 寫入檔案
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        return output_file

def main():
    """主程式"""
    print("開始坐標比較分析...")
    
    # 確保 outputs 目錄存在
    os.makedirs("outputs", exist_ok=True)
    
    # 找到最新的氣象資料檔案
    import glob
    csv_files = glob.glob("outputs/weather_stations_*.csv")
    
    if not csv_files:
        print("找不到氣象資料檔案，請先執行 cwa_weather_api.py")
        return
    
    # 使用最新的檔案
    latest_csv = max(csv_files, key=os.path.getctime)
    print(f"使用資料檔案: {latest_csv}")
    
    # 初始化分析器
    analyzer = CoordinateComparison()
    
    # 載入並處理資料
    df = analyzer.load_and_process_data(latest_csv)
    
    if df is not None:
        # 生成統計報告
        distances = analyzer.generate_distance_report(df)
        
        # 創建比較地圖
        map_file = analyzer.create_comparison_map(df)
        print(f"\n坐標比較地圖已儲存: {map_file}")
        
        # 創建距離分析圖表
        chart_file = analyzer.create_distance_analysis(df)
        print(f"距離分析圖表已儲存: {chart_file}")
        
        # 匯出詳細結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"outputs/coordinate_analysis_report_{timestamp}.md"
        analyzer.export_detailed_results(df, report_file)
        print(f"詳細報告已儲存: {report_file}")
        
        print(f"\n=== 分析完成 ===")
        print(f"請在瀏覽器中開啟 {map_file} 查看地圖")
        print(f"查看 {chart_file} 查看統計圖表")
        print(f"查看 {report_file} 查看詳細報告")
        
    else:
        print("資料處理失敗")

if __name__ == "__main__":
    main()
