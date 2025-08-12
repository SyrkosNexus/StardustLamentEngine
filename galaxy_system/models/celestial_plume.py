import logging
from ..models.vector3d import Vector3D
from ..models.stardust_core import StardustCore

class CelestialPlume(StardustCore):
    """星翎"""
    DEFAULT_MASS = 1.0
    
    def __init__(self, position: Vector3D, velocity: Vector3D, mass: float):
        """
        初始化星翎
        
        Args:
            position: 三维空间座标 (x, y, z)
            velocity: 三维速度矢量 (vx, vy, vz)
            mass: 质量
        """
        super().__init__(mass, position, 1.0, 1.0, 1.0)
        if mass <= 0:
            mass = CelestialPlume.DEFAULT_MASS
            logging.warning("质量必须为正数，已重置为默认值 1.0")
        
        self._position = position
        self._velocity = velocity
    
    @property
    def position(self) -> Vector3D:
        """获取星翎位置"""
        return self._position
    
    @position.setter
    def position(self, value: Vector3D) -> None:
        """设置星翎位置"""
        self._position = value
    
    @property
    def velocity(self) -> Vector3D:
        """获取星翎速度"""
        return self._velocity
    
    @velocity.setter
    def velocity(self, value: Vector3D) -> None:
        """设置星翎速度"""
        self._velocity = value
    
    def __str__(self) -> str:
        return f"CelestialPlume(position={self._position}, velocity={self._velocity}, mass={self.mass})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> dict:
        """
        将星翎对象转换为字典
        
        Returns:
            dict: 星翎属性字典
        """
        return {
            "position": (self._position.x, self._position.y, self._position.z),
            "velocity": (self._velocity.x, self._velocity.y, self._velocity.z),
            "mass": self.mass
        }