import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle
import matplotlib.patches as patches

def draw_pitch(ax=None, color='black', lw= 2):
    """
    Hàm vẽ sân bóng đá tiêu chuẩn dựa trên bộ dữ liệu có kích thước (105m x 68m)
    """
    if ax is  None:
        fig, ax = plt.subplots(figsize=(14, 9))

    pitch = Rectangle([0, 0], 105, 68, fill=False, color=color, lw=lw)
    ax.add_patch(pitch)

    #Khu vuc 16m50
    ax.add_patch(Rectangle([0, (68-40.3)/2], 16.5, 40.3, fill=False, lw=lw, color=color))
    ax.add_patch(Rectangle([105-16.5, (68-40.3)/2], 16.5, 40.3, fill=False, lw=lw, color=color))

    #Khu vuc 5m50
    ax.add_patch(Rectangle([0, (68-18.32)/2], 5.5, 18.32, fill=False, lw=lw, color=color))
    ax.add_patch(Rectangle([105-5.5, (68-18.32)/2], 5.5, 18.32, fill=False, lw=lw, color=color))

    #Diem cham phat den
    ax.plot(11, 68/2, 'o', color=color)
    ax.plot(105-11, 68/2, 'o', color=color)
    ax.add_patch(Arc((11, 68/2), height=18.3, width=18.3, angle=0, theta1=308, theta2=52, lw=lw, color=color))
    ax.add_patch(Arc((105-11, 68/2), height=18.3, width=18.3, angle=0, theta1=128, theta2=232, lw=lw, color=color))

    #Vong tron giua san
    ax.add_patch(Arc((105/2, 68/2), height=18.3, width=18.3, angle=0, theta1=0, theta2=360, lw=lw, color=color))
    ax.plot(105/2, 68/2, 'o', color=color)

    #Duong giua san
    ax.plot([105/2, 105/2], [0, 68], color=color, lw=lw)
    
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 68)
    ax.set_aspect('equal')
    ax.axis('off')
    return ax


def plot_formation(player_positions, title='None'):
    ax = draw_pitch()

    home = player_positions[player_positions['side'] == 'home'].copy()
    away = player_positions[player_positions['side'] == 'away'].copy()

    # Đội nhà (xanh)
    ax.scatter(home['x'], home['y'], color='blue', s=80, label='Home')
    for _, row in home.iterrows():
        ax.text(row['x'], row['y'], str(row['playerId']), color='white',
                fontsize=7, ha='center', va='center')

    # Đội khách (đỏ, lật chiều)
    away['x'] = 100 - away['x']
    away['y'] = 100 - away['y']

    ax.scatter(away['x'], away['y'], color='red', s=80, label='Away')
    for _, row in away.iterrows():
        ax.text(100 - row['x'], 100 - row['y'], str(row['playerId']), color='white',
                fontsize=7, ha='center', va='center')

    ax.legend()
    ax.set_title(title)
    plt.show()

