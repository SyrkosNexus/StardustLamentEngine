from typing import Tuple
import math
import random
from .base import BoundaryAtrium
from ...models.celestial_plume import CelestialPlume
from ...models.vector3d import Vector3D

class PrismicEchoWall(BoundaryAtrium):
    """虹光回音壁：根据晨雾折射角奏响回音"""
    
    def __init__(self, boundary_radius: float, reflection_angle: float = 0, reflection_angle_range: float = math.pi/3):
        """
        初始化反射边界效果
        
        Args:
            reflection_angle: 反射角
        """
        super().__init__("reflective", boundary_radius, reflection_angle, reflection_angle_range)
    
    def handle_collision(self, point: CelestialPlume, dt: float) -> Tuple[Vector3D, Vector3D]:
        """
        处理虹光回音壁边际之诗
        
        Args:
            point: 星翎对象
            dt: 时间步长
            
        Returns:
            Vector3D: 处理后的位置
        """
        origin_point = Vector3D(0, 0, 0)  # 星系原点
        # 计算当前速度大小
        current_speed = point.velocity.magnitude()
        # 计算回音
        if self.reflection_angle == 0:
            # 镜面反射：直接指向规则参考原点
            new_direction = (origin_point - point.position).normalize()
        else:
           # 漫反射：在指定角度范围内随机反射
           # 计算从原点到当前位置的向量
           position_vector = point.position - Vector3D(0,0,0)
           position_direction = position_vector.normalize()

           # 生成随机的反射方向
           # 使用球面坐标生成随机方向
           theta = random.uniform(0, 2 * math.pi)  # 方位角
           phi = random.uniform(0, self.reflection_angle_range)  # 仰角，限制在反射角度范围内
           
           # 将球面坐标转换为笛卡尔坐标
           # 首先创建一个相对于位置向量的局部坐标系
           # 需要两个正交向量来构建坐标系
           
           # 选择一个不与position_direction平行的参考向量
           if abs(position_direction.x) < 0.9:
               ref_vector = Vector3D(1, 0, 0)
           else:
               ref_vector = Vector3D(0, 1, 0)
           
           # 计算第一个正交向量
           ortho1 = position_direction.cross(ref_vector).normalize()
           
           # 计算第二个正交向量
           ortho2 = position_direction.cross(ortho1).normalize()
           
           # 在局部坐标系中计算随机方向
           new_direction = (
               position_direction * math.cos(phi) +
               ortho1 * (math.sin(phi) * math.cos(theta)) +
               ortho2 * (math.sin(phi) * math.sin(theta))
           )
           
           # 确保方向指向内部（与位置向量相反）
           if new_direction.dot(position_direction) > 0:
               new_direction = new_direction * -1
        
        # 应用速度减速
        new_velocity = new_direction * (current_speed * 0.6)

        # 计算新位置
        new_position = point.position + new_velocity * dt
        
        return new_position, new_velocity