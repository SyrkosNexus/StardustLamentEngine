"""
泊松盘采样算法模块
提供生成均匀分布随机点的功能
"""
import random
import math


def poisson_disk_sampling(num_points, min_distance, max_attempts=30, bounds=(-100, 100)):
    """
    泊松盘采样算法，生成均匀分布的随机点
    
    参数:
        num_points: 需要生成的点数量
        min_distance: 点之间的最小距离
        max_attempts: 每个点的最大尝试次数
        bounds: 坐标范围 (min, max)
    
    返回:
        list: 生成的点坐标列表 [(x, y, z), ...]
    """
    points = []
    active_list = []
    
    # 生成第一个点
    first_point = (
        random.uniform(bounds[0], bounds[1]),
        random.uniform(bounds[0], bounds[1]),
        random.uniform(bounds[0], bounds[1])
    )
    points.append(first_point)
    active_list.append(first_point)
    
    # 定义单元格大小，用于加速邻近点搜索
    cell_size = min_distance / math.sqrt(3)
    grid_size = int((bounds[1] - bounds[0]) / cell_size) + 1
    grid = [[[-1 for _ in range(grid_size)] for _ in range(grid_size)] for _ in range(grid_size)]
    
    # 将第一个点添加到网格中
    grid_x = int((first_point[0] - bounds[0]) / cell_size)
    grid_y = int((first_point[1] - bounds[0]) / cell_size)
    grid_z = int((first_point[2] - bounds[0]) / cell_size)
    grid[grid_x][grid_y][grid_z] = 0
    
    while active_list and len(points) < num_points:
        # 从活动列表中随机选择一个点
        idx = random.randint(0, len(active_list) - 1)
        point = active_list[idx]
        found = False
        
        # 尝试生成新点
        for _ in range(max_attempts):
            # 在以point为中心，半径为min_distance到2*min_distance的球体内随机生成一个点
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(0, math.pi)
            r = random.uniform(min_distance, 2 * min_distance)
            
            x = point[0] + r * math.sin(phi) * math.cos(theta)
            y = point[1] + r * math.sin(phi) * math.sin(theta)
            z = point[2] + r * math.cos(phi)
            
            # 检查是否在边界内
            if not (bounds[0] <= x <= bounds[1] and 
                    bounds[0] <= y <= bounds[1] and 
                    bounds[0] <= z <= bounds[1]):
                continue
            
            # 检查与现有点的距离
            new_point = (x, y, z)
            grid_x = int((x - bounds[0]) / cell_size)
            grid_y = int((y - bounds[0]) / cell_size)
            grid_z = int((z - bounds[0]) / cell_size)
            
            # 检查邻近单元格
            valid = True
            for i in range(max(0, grid_x - 2), min(grid_size, grid_x + 3)):
                for j in range(max(0, grid_y - 2), min(grid_size, grid_y + 3)):
                    for k in range(max(0, grid_z - 2), min(grid_size, grid_z + 3)):
                        if grid[i][j][k] != -1:
                            neighbor = points[grid[i][j][k]]
                            distance = math.sqrt(
                                (new_point[0] - neighbor[0])**2 +
                                (new_point[1] - neighbor[1])**2 +
                                (new_point[2] - neighbor[2])**2
                            )
                            if distance < min_distance:
                                valid = False
                                break
                    if not valid:
                        break
                if not valid:
                    break
            
            if valid:
                points.append(new_point)
                active_list.append(new_point)
                grid[grid_x][grid_y][grid_z] = len(points) - 1
                found = True
                break
        
        # 如果经过max_attempts次尝试仍未找到有效点，则从活动列表中移除该点
        if not found:
            active_list.pop(idx)
    
    # 如果生成的点数量不足，使用随机采样补充
    while len(points) < num_points:
        new_point = (
            random.uniform(bounds[0], bounds[1]),
            random.uniform(bounds[0], bounds[1]),
            random.uniform(bounds[0], bounds[1])
        )
        points.append(new_point)
    
    return points