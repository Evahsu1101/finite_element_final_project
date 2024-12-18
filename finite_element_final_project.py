print("==========================")

# 匯入 OpenSeesPy 模組來使用結構分析功能
from openseespy.opensees import *
# import openseespy.postprocessing.Get_Rendering as opsplt

print("Starting RCFrameGravity example")

# ------------------------------
# 1. 建立結構模型 (陳延融)
# ------------------------------
# 設定為二維模型，每個節點有3個自由度（x、y、rotation）。
model('basic', '-ndm', 2, '-ndf', 3)

# 早上那張圖看起來是淨跨距3m，柱為2m*2m，所以中心間距為5m
# 節點定義
space = 500 # cm
floor = 420 # cm
# 第一層 (底層)
for n in range(81):
    for i in range(1,10):
        node(i+9*n,(i-1)*space,n*floor)

# 設定最底層節點固定支撐，101一共打了380 支直徑1.5 公尺的群樁，所以底下都當固定端
# fix(節點ID, DX, DY, RZ) 中，1 代表固定，0 代表自由
for i in range(1,10):
    fix(i, 1, 1, 1)

print("已定義節點標籤：", getNodeTags())
# ------------------------------
# 2. 定義材料 (陳延融)
# ------------------------------
# 這裡我們使用三種材料來定義鋼骨(S)、鋼筋(R)、混凝土(C)的行為。

# 定義混凝土材料，使用 Concrete01 材料模型
# tag, f'c (混凝土抗壓強度), ec0 (混凝土初始彈性模數), f'cu(=0.85*f'c) (極限抗壓強度), ecu (混凝土破壞應變)
# 第一個材料為核心混凝土（受約束混凝土） 2m*2m方柱用
# 應用本土化New RC圍束混凝土模式於柱構件撓曲行為之研究
# Ec = (0.24S+0.83)*(8830*(f'c)^0.5+74200) (MPa)，S為矽灰比取0.1
uniaxialMaterial('Concrete01', 1, -700, -1284672.4, -595, -0.003)

# 定義鋼筋材料，使用 Steel01 材料模型
# fy 為鋼筋降伏強度，E 為鋼筋的彈性模數
fy = 4200  # 降伏強度 (kgf/cm²)
E = 2040000  # 彈性模數 (kgf/cm²)
# 使用 Steel01 來定義鋼筋材料
uniaxialMaterial('Steel01', 2, fy, E, 0.01)

# 定義 SM570M 鋼材的材料
Fy = 500.0  # 降伏強度 (MPa) 5200kgf/cm^2>=fy>=4200kgf/cm^2
E0 = 210000.0  # 彈性模數 (MPa)
b = 0.02  # 硬化係數 (二次斜率)，，控制了材料從降伏點（降伏強度）到極限強度區域的硬化速率。它表示鋼材在屈服後的硬化行為，決定了應力-應變曲線在塑性區域的斜率。
R0 = 18.0  # 鋼材圓滑參數，它決定了鋼材應力-應變曲線的起始部分的平滑度（即從降伏強度到初始硬化段的變化）
cR1 = 0.925  # 硬化調整係數，是用來調整鋼材在塑性階段硬化行為的參數，特別是在降伏後的塑性硬化速率。它影響鋼材的應力-應變曲線在塑性區域的形狀，尤其是從降伏強度到達極限強度過程中的變化。
cR2 = 0.15  # 硬化調整係數，用於控制鋼材從降伏強度到極限強度過程中的硬化行為

uniaxialMaterial('Steel02', 3, Fy, E0, b, R0, cR1, cR2)



# ------------------------------
# 3. 定義柱子斷面 (許慈忻)
# 1 200*200 SRC柱
# 2 150*150 SRC柱
# 3 H型鋼 柱
# 4 H型鋼 梁
# ------------------------------

# Fiber 截面定義
section('Fiber', 1) # 200*200
# 定義鋼骨部分 (矩形鋼骨)
# (-100,100)-----------(100,100)
#     | (-93,93)-----(93,93) |
#     |    |            |    |
#     |    |            |    |
#     |    |            |    |
#     |    |            |    |
#     | (-93,-93)--(93,-93)  |
# (-100,-100)------------(100,-100)
# 定義柱子的尺寸
colWidth = 200    # 柱寬度(cm)
colDepth = 200    # 柱深度(cm)
cover = 7        # 鋼骨厚度(cm)
# patch('矩形鋼骨',鋼材材料標籤,網格劃分的密度（x, y 方向）,後面的座標對應於矩形區域的四個頂點)
patch('quad', 2, 10, 10, -colWidth/2, -colDepth/2, colWidth/2, -colDepth/2, colWidth/2, colDepth/2, -colWidth/2, colDepth/2)
# 定義混凝土核心部分
# patch('矩形',混凝土材料標籤,網格劃分的密度（x, y 方向）,後面的座標對應於矩形區域的四個頂點)
patch('quad', 1, 10, 10, -colWidth/2+cover, -colDepth/2+cover, colWidth/2-cover, -colDepth/2+cover, colWidth/2-cover, colDepth/2-cover, -colWidth/2+cover, colDepth/2-cover)

section('Fiber', 2) # 150*150
# 定義鋼骨部分 (矩形鋼骨)
# (-75,75)----------------(75,75)
#     |(-68,68)------(68,68) |
#     |    |            |    |
#     |    |            |    |
#     |    |            |    |
#     |    |            |    |
#     |(-68,-68)-----(68,-68)|
# (-75,-75)---------------(75,-75)
# 定義柱子的尺寸
colWidth = 150    # 柱寬度(cm)
colDepth = 150    # 柱深度(cm)
cover = 7        # 鋼骨厚度(cm)
# patch('矩形鋼骨',鋼材材料標籤,網格劃分的密度（x, y 方向）,後面的座標對應於矩形區域的四個頂點)
patch('quad', 3, 10, 10, -colWidth/2, -colDepth/2, colWidth/2, -colDepth/2, colWidth/2, colDepth/2, -colWidth/2, colDepth/2)
# 定義混凝土核心部分
# patch('矩形',混凝土材料標籤,網格劃分的密度（x, y 方向）,後面的座標對應於矩形區域的四個頂點)
patch('quad', 1, 10, 10, -colWidth/2+cover, -colDepth/2+cover, colWidth/2-cover, -colDepth/2+cover, colWidth/2-cover, colDepth/2-cover, -colWidth/2+cover, colDepth/2-cover)

section('Fiber', 3)  # H 510*306
flange = 30.6 # 寬度：30   cm。
flange_t = 2.9# 翼板厚度：1.8  cm。
web = 51 # 高度：44 cm。
web_t = 1.7# 腹板厚度：1.1  cm。
# 上翼緣
patch('rect', 3, 10, 1, -flange/2, web/2-flange_t, flange/2, web/2)  # 材料 3，10x1 分割 , 左下角, 右上角
# 下翼緣
patch('rect', 3, 10, 1, -flange/2, -web/2, flange/2, -web/2+flange_t)  # 材料 3，10x1 分割
# 腹板
patch('rect', 3, 1, 10, -web_t/2, -web/2+flange_t, web_t/2, web/2-flange_t)  # 材料 3，1x10 分割

section('Fiber', 4)  # H 440*300
flange = 30 # 寬度：30   cm。
flange_t = 1.8# 翼板厚度：1.8  cm。
web = 44 # 高度：44 cm。
web_t = 1.1# 腹板厚度：1.1  cm。
# 上翼緣
patch('rect', 3, 10, 1, -flange/2, web/2-flange_t, flange/2, web/2)  # 材料 3，10x1 分割 , 左下角, 右上角
# 下翼緣
patch('rect', 3, 10, 1, -flange/2, -web/2, flange/2, -web/2+flange_t)  # 材料 3，10x1 分割
# 腹板
patch('rect', 3, 1, 10, -web_t/2, -web/2+flange_t, web_t/2, web/2-flange_t)  # 材料 3，1x10 分割

# ------------------------------
# 4. 定義梁柱元素 (許慈忻) 
# ------------------------------
# 使用 forceBeamColumn 元素來建立柱子，並指定其材料與纖維模型。
###################################################################
# 設定柱子的彎矩與剪力模型
# 1. Linear Transformation（'Linear'）
# 用途：處理線性幾何變形的情況，忽略幾何非線性效應。
# 適用場景：用於小變形理論假設下的框架結構。
#-------------------------------------------#
# 2. P-Delta Transformation（'PDelta'）
# 用途：處理結構的二階效應（P-Delta 效應）。
# 適用場景：用於考慮重力效應和側向變形的框架結構分析。
#-------------------------------------------#
# 3. Corotational Transformation（'Corotational'）
# 用途：針對幾何高度非線性（大變形）問題，適合分析非線性框架結構。
# 適用場景：大變形理論。高柔性結構。需要精確描述幾何行為的情況。
#-------------------------------------------#
# 4. Initial State Transformation（'Initial'）
# 用途：考慮初始幾何狀態對結構行為的影響。
# 適用場景：需要包含初始變形或應力狀態的分析。
#-------------------------------------------#
# geomTransf('PDelta'\'Linear'\'Corotational'\'Initial', tag)
geomTransf('PDelta', 1)  # 使用 P-Delta 方法

# 設定數值積分方法（Lobatto積分）
# beamIntegration('Lobatto', tag, secTag, numPts)
beamIntegration('Lobatto', 1, 1, 10)

# 創建柱子元素
# element('forceBeamColumn', tag, nodeI, nodeJ, 數值積分點數量, 截面標籤, 幾何變換標籤)
for n in range(80):
    element('nonlinearBeamColumn', 4+(17*n), 3+(9*n), 3+(9*(n+1)), 5, 1, 1)  # 主柱 200*200
    element('nonlinearBeamColumn', 12+(17*n), 7+(9*n), 7+(9*(n+1)), 5, 1, 1)  # 主柱 200*200

    element('nonlinearBeamColumn', 1+(17*n), 1+(9*n), 1+(9*(n+1)), 5, 2, 1)  # 柱 150*150
    element('nonlinearBeamColumn', 8+(17*n), 5+(9*n), 5+(9*(n+1)), 5, 2, 1)  # 柱 150*150
    element('nonlinearBeamColumn', 16+(17*n), 9+(9*n), 9+(9*(n+1)), 5, 2, 1)  # 柱 150*150

    element('nonlinearBeamColumn', 2+(17*n), 2+(9*n), 2+(9*(n+1)), 5, 3, 1)  # 柱子 H 
    element('nonlinearBeamColumn', 6+(17*n), 4+(9*n), 4+(9*(n+1)), 5, 3, 1)  # 柱子 H 
    element('nonlinearBeamColumn', 10+(17*n), 6+(9*n), 6+(9*(n+1)), 5, 3, 1)  # 柱子 H 
    element('nonlinearBeamColumn', 14+(17*n), 8+(9*n), 8+(9*(n+1)), 5, 3, 1)  # 柱子 H 

# 創建梁元素
    element('nonlinearBeamColumn', 3+(17*n), 1+(9*(n+1)), 1+(9*(n+1))+1, 5, 4, 1)  # 梁 H 
    element('nonlinearBeamColumn', 5+(17*n), 2+(9*(n+1)), 2+(9*(n+1))+1, 5, 4, 1)  # 梁 H 
    element('nonlinearBeamColumn', 7+(17*n), 3+(9*(n+1)), 3+(9*(n+1))+1, 5, 4, 1)  # 梁 H 
    element('nonlinearBeamColumn', 9+(17*n), 4+(9*(n+1)), 4+(9*(n+1))+1, 5, 4, 1)  # 梁 H 
    element('nonlinearBeamColumn', 11+(17*n), 5+(9*(n+1)), 5+(9*(n+1))+1, 5, 4, 1)  # 梁 H 
    element('nonlinearBeamColumn', 13+(17*n), 6+(9*(n+1)), 6+(9*(n+1))+1, 5, 4, 1)  # 梁 H 
    element('nonlinearBeamColumn', 15+(17*n), 7+(9*(n+1)), 7+(9*(n+1))+1, 5, 4, 1)  # 梁 H 
    element('nonlinearBeamColumn', 17+(17*n), 8+(9*(n+1)), 8+(9*(n+1))+1, 5, 4, 1)  # 梁 H 


print("已定義的元素標籤：", eleNodes(1360))

sectionStiffness(1, 5, 3)
print("非線性元素剛度矩陣：", sectionStiffness(1, 5, 3))




# ------------------------------
# 6. 定義重力負載
# ------------------------------
# 在節點 3 和 4 上施加垂直重力負載。

P = 25108  # 設定垂直負載 (kgf)

# 設定負載時間歷程
timeSeries('Linear', 1)  # 線性負載
pattern('Plain', 1, 1)  # 使用平面負載模式

# 設定節點上的重力負載
load(3, 0.0, -P, 0.0)  # 節點 3 上施加負載
load(4, 0.0, -P, 0.0)  # 節點 4 上施加負載

# ------------------------------
# 7. 分析設定
# ------------------------------
# 設定數值分析方法，包括解算系統、約束條件、收斂判斷、解法器等。

# 設定系統解算方法（帶狀矩陣解法）
# BandGeneral: 對一般的非對稱稀疏矩陣進行求解。
# UmfPack: 基於稀疏矩陣的 LU 分解，適合大型結構分析。
# ProfileSPD: 用於對稱正定矩陣（如彈性結構）。
# SparseSYM: 用於稀疏且對稱的矩陣。
# Mumps: 高效處理大型稀疏系統。
system('BandGeneral')

# 設定約束條件處理方法
# Transformation	使用轉換矩陣處理主從節點的自由度關係，準確且適用於多數情況。
# Plain	從節點直接拷貝主節點的自由度，適用於簡單情況。
# Lagrange	通過增加拉格朗日乘子的方式處理約束，適用於剛性較高的約束，但可能導致矩陣尺寸變大。
# Penalty	使用懲罰法處理約束，適合於不完全剛性約束的情況。
# MP (Multi-Point)	將多點約束直接內嵌於矩陣中，用於定義多點約束的特定情況（如剛性板連接）。
constraints('Transformation')

# 設定自由度編號方法
# Plain	使用原始順序進行編號，無特別優化，適合小型模型或測試用。
# RCM	使用反 Cuthill-McKee 演算法，適合大型模型，能有效減少矩陣帶寬，提高計算效率和節省記憶體。
numberer('RCM')

# 設定收斂測試方法，判斷殘差的範數，並設定最大迭代次數為 10
# tol	收斂容許誤差（tolerance），如 1.0e-12。範數小於此值時即視為收斂。
# iter	最大迭代次數。如果超過此次數仍未收斂，則分析失敗。
# pFlag	顯示控制。0 表示不輸出，1 表示輸出簡單收斂資訊，2 表示每次迭代輸出詳細資訊，3 表示每次迭代顯示和分析失敗報告。
# test('NormDispIncr', tol, iter, pFlag)
test('NormDispIncr', 1.0e-12, 10, 3)

# 設定求解演算法，使用 Newton-Raphson 法
# Newton	標準牛頓法，使用完整剛度矩陣更新。
# ModifiedNewton	修正牛頓法，剛度矩陣在分析過程中不更新，計算量較低，但可能收斂較慢。
# Broyden	使用擬牛頓法，不需要計算完整剛度矩陣，適用於大規模模型的快速收斂。
# KrylovNewton	使用 Krylov 子空間技術來近似剛度矩陣更新，適合大規模問題。
# NewtonLineSearch	牛頓法加線搜索，用於避免收斂困難。
# AcceleratedNewton	加速牛頓法，結合過去的迭代資訊以提高收斂速度。
# FixedNewton	固定牛頓法，不考慮剛度矩陣的更新，與修正牛頓法類似但更簡單。
algorithm('Newton')

# 設定負載控制的積分方案，步長為 0.1
# 設定載荷控制增量器的指令。這個指令常用於靜態分析中，特別是進行非線性靜力分析時，它用來控制載荷的增量並確保結構的位移逐步增長。
# integrator('LoadControl', 0.1)

# 設定靜力分析
# 靜態分析 (Static) 用於靜態載荷情況，忽略動態效應。適用於靜態載荷問題（如重力、土壤壓力等）。
# 動態分析 (Transient) 用於非平衡的動態問題，考慮結構在時間域內的動態反應。適用於時變載荷（如地震、風荷載等）。
# 穩定性分析 (Eigen) 用於計算結構的固有頻率、模態分析等。適用於研究結構的動態特性，尤其是模態分析。
# 屈曲分析 (Ritz) 用於計算結構的屈曲模式和臨界載荷。適用於模擬結構在不同載荷下的屈曲行為。
# 非線性靜態分析 (Static with Nonlinear Effects) 處理非線性材料和幾何的靜態分析。用於材料塑性、裂縫擴展等非線性行為。
# 大變形動態分析 (Corotational) 考慮結構的大變形問題，適用於幾何非線性。用於描述結構經歷顯著變形時的行為。
# 伽馬分析 (Gamma) 用於非線性逐步積分分析，適用於復雜載荷情況。用於結構在外部載荷作用下的非線性行為。
analysis('Static')

# ------------------------------
# 8. 執行靜力分析
# ------------------------------
# 開始進行靜力分析，並將負載分為 10 步進行逐步施加
analyze(10)

# ------------------------------
# 9. 查詢與輸出結果
# ------------------------------
# 查詢節點 3 和 4 的位移與旋轉，並查詢各個元素的內力反應。

u3_x, u3_y, u3_rot = nodeDisp(3, 1), nodeDisp(3, 2), nodeDisp(3, 3)  # 節點 3 的位移與旋轉
u4_x, u4_y, u4_rot = nodeDisp(4, 1), nodeDisp(4, 2), nodeDisp(4, 3)  # 節點 4 的位移與旋轉

# 查詢柱子 1、2 和梁 3 的內力
force_element_1 = eleResponse(1, 'force')
force_element_2 = eleResponse(2, 'force')
force_element_3 = eleResponse(3, 'force')

# 顯示結果
print("節點 3 在 X 方向的位移:", u3_x)
print("節點 3 在 Y 方向的位移:", u3_y)
print("節點 3 的旋轉:", u3_rot)
print("節點 4 在 X 方向的位移:", u4_x)
print("節點 4 在 Y 方向的位移:", u4_y)
print("節點 4 的旋轉:", u4_rot)
print("柱 1 的內力:", force_element_1)
print("柱 2 的內力:", force_element_2)
print("梁 3 的內力:", force_element_3)

# ------------------------------
# 10. 輸出結果到檔案
# ------------------------------
# 輸出結果到檔案，並檢查分析結果是否符合預期。

with open('results.out', 'a+') as results:
    # 輸出節點位移與旋轉的數值
    results.write(f"節點 3 的位移: X方向={u3_x}, Y方向={u3_y}, 旋轉={u3_rot}\n")
    results.write(f"節點 4 的位移: X方向={u4_x}, Y方向={u4_y}, 旋轉={u4_rot}\n")
    results.write(f"柱 1 的內力: {force_element_1}\n")
    results.write(f"柱 2 的內力: {force_element_2}\n")
    results.write(f"梁 3 的內力: {force_element_3}\n")
    
    # 根據位移判斷分析是否通過
    if abs(u3_y + 0.0183736) < 1e-6 and abs(u4_y + 0.0183736) < 1e-6:
        results.write('PASSED : RCFrameGravity.py\n')
        print("Passed!")
    else:
        results.write('FAILED : RCFrameGravity.py\n')
        print("Failed!")

print("==========================")
