from typing import Tuple
import math
import random
from .base import BoundaryAtrium
from ...models.celestial_plume import CelestialPlume
from ...models.vector3d import Vector3D

class MirrorAbyssGate(BoundaryAtrium):
    """镜渊之门：星翎抵达边际时，将穿过星穹原点，如露滴坠入镜渊另一侧"""
    
    def __init__(self, boundary_radius: float, reflection_angle: float = 0, reflection_angle_range: float = math.pi):
        """
        初始化无限边界效果
        
        Args:
            reflection_angle: 反射角
        """
        super().__init__("infinite", boundary_radius, reflection_angle, reflection_angle_range)
    
    def handle_collision(self, point: CelestialPlume, dt: float) -> Tuple[Vector3D, Vector3D]:
        """
        处理镜渊之门边际之诗
        
        Args:
            point: 星翎对象
            dt: 时间步长
            
        Returns:
            Vector3D: 处理后的位置
        """
        origin_point = Vector3D(0, 0, 0)  # 星系原点
        # 计算从原点到当前位置的向量
        position_vector = point.position - origin_point
        
        # 计算速度方向单位向量
        velocity_direction = point.velocity.normalize()

        if self.reflection_angle == 0:
            # 镜面反射非随机位置：穿过参考原点落到另外一边
            # 将位置向量反向，并缩小距离，确保不会立即再次超出阈值
            warped_position_vector = position_vector.normalize() * (-self.boundary_radius)
            
            # 首先计算穿越后的位置，确保穿越后的位置、初始质点和穿越前的位置在一条直线上
            base_warped_position = origin_point + warped_position_vector
            
            # 然后在穿越后的位置基础上添加偏移量，偏移方向与速度方向相同
            offset = velocity_direction * (self.boundary_radius * 0.05)  # 偏移量为安全距离的5%
            warped_position = base_warped_position + offset
            new_velocity = point.velocity * 0.6
        else:
            # 随机位置：在球形边界上的任意一个点
            # 使用球面坐标生成随机方向
            theta = random.uniform(0, 2 * math.pi)  # 方位角
            phi = random.uniform(0, math.pi)  # 仰角，覆盖整个球面
            
            # 将球面坐标转换为笛卡尔坐标
            x = math.sin(phi) * math.cos(theta)
            y = math.sin(phi) * math.sin(theta)
            z = math.cos(phi)
            
            # 创建随机方向的单位向量
            random_direction = Vector3D(x, y, z)
            
            # 计算warp后的位置
            warped_position = origin_point + random_direction * self.boundary_radius
            # 计算从当前位置指向原点的单位向量
            direction_to_origin = (origin_point - warped_position).normalize()
            
            new_velocity = direction_to_origin * (point.velocity.magnitude() * 0.6)
        return warped_position, new_velocity