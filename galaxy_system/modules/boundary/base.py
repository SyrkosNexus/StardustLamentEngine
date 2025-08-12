from abc import ABC, abstractmethod
import math
from typing import Tuple
from ...models.celestial_plume import CelestialPlume
from ...models.vector3d import Vector3D

class BoundaryAtrium(ABC):
    """界域回廊：根据不同的星穹边际法则，计算星翎是否轻触界域，在减速60%后触发边际之诗"""
    
    def __init__(self, type: str, boundary_radius: float, reflection_angle: float, reflection_angle_range: float = math.pi/3):
        """
        初始化边界效果
        
        Args:
            reflection_angle: 边界半径
        """
        self.type = type
        self.boundary_radius = boundary_radius
        self.reflection_angle = reflection_angle
        self.reflection_angle_range = reflection_angle_range
    
    def check_collision(self, point: CelestialPlume) -> bool:
        """
        检查星翎是否与界域碰撞
        
        Args:
            point: 星翎对象
            astral_canopy: 星穹领域对象
            
        Returns:
            bool: 是否碰撞
        """
        # 如果位置在边界外，先修正到边界内95%处
        position_magnitude = point.position.magnitude()
        if position_magnitude > self.boundary_radius:
            correction_factor = 0.95 * self.boundary_radius / position_magnitude
            point.position = point.position * correction_factor
            return True
            
        return position_magnitude >= self.boundary_radius
    
    @abstractmethod
    def handle_collision(self, point: CelestialPlume) -> Tuple[Vector3D, Vector3D]:
        """
        处理边际之诗
        
        Args:
            point: 星翎对象
            
        Returns:
            Vector3D: 处理后的位置
        """
        pass