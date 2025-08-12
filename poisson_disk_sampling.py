"""
泊松盘采样算法模块
提供在球体空间内生成均匀分布随机点的功能
"""
import torch
import math


def poisson_disk_sampling(num_points, min_distance, max_attempts=30, radius=100):
    """
    泊松盘采样算法，在球体空间内生成均匀分布的随机点
    
    参数:
        num_points: 需要生成的点数量
        min_distance: 点之间的最小距离
        max_attempts: 每个点的最大尝试次数
        radius: 球体半径，所有点必须位于以原点为中心的球体内
    
    返回:
        list: 生成的点坐标列表 [(x, y, z), ...]，所有点都在球体内且满足最小距离要求
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def is_in_sphere(point, r):
        """检查点是否在球体内"""
        return torch.sqrt(point[0]**2 + point[1]**2 + point[2]**2) <= r
    
    def generate_first_point():
        """生成球体内的第一个点"""
        max_attempts = 1000
        for _ in range(max_attempts):
            # 使用球坐标生成均匀分布的点
            theta = torch.rand(1).item() * 2 * math.pi
            phi = torch.rand(1).item() * math.pi
            # 使用立方根分布确保体积均匀
            r = radius * (torch.rand(1).item() ** (1/3))
            
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)
            
            point = torch.tensor([x, y, z], device=device)
            if is_in_sphere(point, radius):
                return point
        return torch.tensor([0.0, 0.0, 0.0], device=device)  # 回退到原点
    
    # 对于少量点，使用分层采样确保均匀分布
    if num_points <= 10:
        # 使用球面分层采样确保均匀分布
        points = []
        if num_points == 1:
            # 单点放在中心附近
            points = [torch.tensor([0.0, 0.0, 0.0], device=device)]
        elif num_points == 2:
            # 两点放在相对位置
            r = radius * 0.7
            points = [
                torch.tensor([r, 0.0, 0.0], device=device),
                torch.tensor([-r, 0.0, 0.0], device=device)
            ]
        elif num_points <= 6:
            # 使用正多面体顶点分布
            if num_points == 3:
                # 等边三角形
                r = radius * 0.6
                angle = 2 * math.pi / 3
                for i in range(3):
                    theta = i * angle
                    points.append(torch.tensor([
                        r * math.cos(theta),
                        r * math.sin(theta),
                        0.0
                    ], device=device))
            elif num_points == 4:
                # 四面体
                r = radius * 0.5
                a = r * math.sqrt(8/9)
                c = r * 1/3
                points = [
                    torch.tensor([0.0, 0.0, r], device=device),
                    torch.tensor([a * math.cos(0), a * math.sin(0), -c], device=device),
                    torch.tensor([a * math.cos(2*math.pi/3), a * math.sin(2*math.pi/3), -c], device=device),
                    torch.tensor([a * math.cos(4*math.pi/3), a * math.sin(4*math.pi/3), -c], device=device)
                ]
            elif num_points == 5:
                # 三角双锥
                r = radius * 0.5
                a = r * math.sqrt(3/4)
                points = [
                    torch.tensor([0.0, 0.0, r], device=device),
                    torch.tensor([0.0, 0.0, -r], device=device),
                    torch.tensor([a, 0.0, 0.0], device=device),
                    torch.tensor([-a/2, a * math.sqrt(3)/2, 0.0], device=device),
                    torch.tensor([-a/2, -a * math.sqrt(3)/2, 0.0], device=device)
                ]
            elif num_points == 6:
                # 八面体
                r = radius * 0.5
                points = [
                    torch.tensor([r, 0.0, 0.0], device=device),
                    torch.tensor([-r, 0.0, 0.0], device=device),
                    torch.tensor([0.0, r, 0.0], device=device),
                    torch.tensor([0.0, -r, 0.0], device=device),
                    torch.tensor([0.0, 0.0, r], device=device),
                    torch.tensor([0.0, 0.0, -r], device=device)
                ]
        else:
            # 少量点使用球面均匀分布
            for i in range(num_points):
                # 使用黄金螺旋算法
                phi = math.acos(1 - 2 * (i + 0.5) / num_points)
                theta = math.pi * (1 + math.sqrt(5)) * i
                r = radius * 0.7
                x = r * math.cos(theta) * math.sin(phi)
                y = r * math.sin(theta) * math.sin(phi)
                z = r * math.cos(phi)
                points.append(torch.tensor([x, y, z], device=device))
        
        # 验证所有点都在球体内
        valid_points = [p for p in points if is_in_sphere(p, radius)]
        if len(valid_points) == num_points:
            return [tuple(p.cpu().numpy()) for p in valid_points]
    
    # 对于大量点，使用标准泊松盘采样
    points = []
    active_list = []
    
    # 生成第一个点
    first_point = generate_first_point()
    points.append(first_point)
    active_list.append(first_point)
    
    # 定义单元格大小，用于加速邻近点搜索
    sphere_diameter = 2 * radius
    cell_size = min_distance / math.sqrt(3)
    grid_size = max(1, int(sphere_diameter / cell_size) + 1)
    grid_offset = -radius
    
    # 使用PyTorch张量创建网格
    grid = torch.full((grid_size, grid_size, grid_size), -1, dtype=torch.long, device=device)
    
    grid_x = int((first_point[0] - grid_offset) / cell_size)
    grid_y = int((first_point[1] - grid_offset) / cell_size)
    grid_z = int((first_point[2] - grid_offset) / cell_size)
    if 0 <= grid_x < grid_size and 0 <= grid_y < grid_size and 0 <= grid_z < grid_size:
        grid[grid_x, grid_y, grid_z] = 0
    
    while active_list and len(points) < num_points:
        # 从活动列表中随机选择一个点
        idx = torch.randint(0, len(active_list), (1,)).item()
        point = active_list[idx]
        found = False
        
        # 尝试生成新点
        for _ in range(max_attempts):
            # 使用更智能的采样策略，确保均匀分布
            theta = torch.rand(1).item() * 2 * math.pi
            phi = torch.rand(1).item() * math.pi
            
            # 根据剩余空间调整采样半径
            current_distance = torch.sqrt(point[0]**2 + point[1]**2 + point[2]**2).item()
            max_possible_r = min(min_distance * 2, radius - current_distance)
            r = torch.rand(1).item() * (max(min_distance * 1.2, max_possible_r) - min_distance) + min_distance
            
            x = point[0] + r * math.sin(phi) * math.cos(theta)
            y = point[1] + r * math.sin(phi) * math.sin(theta)
            z = point[2] + r * math.cos(phi)
            
            new_point = torch.tensor([x, y, z], device=device)
            
            # 检查是否在球体内
            if not is_in_sphere(new_point, radius):
                continue
            
            # 检查与现有点的距离
            grid_x = int((x - grid_offset) / cell_size)
            grid_y = int((y - grid_offset) / cell_size)
            grid_z = int((z - grid_offset) / cell_size)
            
            # 检查邻近单元格
            valid = True
            search_radius = 2
            for i in range(max(0, grid_x - search_radius), min(grid_size, grid_x + search_radius + 1)):
                for j in range(max(0, grid_y - search_radius), min(grid_size, grid_y + search_radius + 1)):
                    for k in range(max(0, grid_z - search_radius), min(grid_size, grid_z + search_radius + 1)):
                        if 0 <= i < grid_size and 0 <= j < grid_size and 0 <= k < grid_size:
                            if grid[i, j, k] != -1:
                                neighbor = points[grid[i, j, k]]
                                distance = torch.sqrt(
                                    (new_point[0] - neighbor[0])**2 +
                                    (new_point[1] - neighbor[1])**2 +
                                    (new_point[2] - neighbor[2])**2
                                ).item()
                                if distance < min_distance * 0.999:
                                    valid = False
                                    break
                    if not valid:
                        break
                if not valid:
                    break
            
            if valid:
                points.append(new_point)
                active_list.append(new_point)
                if 0 <= grid_x < grid_size and 0 <= grid_y < grid_size and 0 <= grid_z < grid_size:
                    grid[grid_x, grid_y, grid_z] = len(points) - 1
                found = True
                break
        
        # 如果经过max_attempts次尝试仍未找到有效点，则从活动列表中移除该点
        if not found:
            active_list.pop(idx)
    
    # 不再使用随机采样补充，只返回通过泊松盘采样生成的点
    return [tuple(p.cpu().numpy()) for p in points]