import logging
from ..models.vector3d import Vector3D
from ..models.stardust_core import StardustCore

class StellarPearl(StardustCore):
    """星核类：没有体积，只有引力的珍珠"""
    DEFAULT_ANCHOR_MASS = 50
    DEFAULT_ORBITAL_VELOCITY=1.0
    
    def __init__(self, name: str, position: Vector3D, mass: float, orbit_raduis: float, orbit_velocity: float, escape_velocity: float, perturbations: bool = True):
        """
        初始化星核
        
        Args:
            gravity_loom: 星引织网
            name: 星核名称
            position: 空间坐标 (x, y, z)
            mass: 质量
            orbital_radius: 轨道半径
            orbital_velocity: 轨道速度
            escape_velocity: 逃逸速度
            perturbations: 是否产生引力扰动
        """
        super().__init__(mass, position, orbit_raduis, orbit_velocity, escape_velocity)

        self._is_valid = True # 是否有效的锚点
        if mass <= 0:
            logging.info(f"星核({name})的质量必须为正值")
            self._is_valid = False

        if orbit_velocity <= 0:
            logging.info(f"星核({name})的轨道速度必须为正值")
            self._is_valid = False

        self._name = name
        self._position = position
        self._perturbations = perturbations
        self.revival_rounds = -1

    def __str__(self) -> str:
        return f"StellarPearl(name={self._name}, mass={self._mass}, position={self._position}, orbit_velocity={self._orbit_velocity}, orbit_altitude={self._orbit_altitude}, escape_velocity={self._escape_velocity}, perturbations={self._perturbations}, is_valid={self._is_valid})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @property
    def is_valid(self) -> bool:
        """获取星核是否有效"""
        return self._is_valid
    
    @property
    def name(self) -> str:
        """获取星核名称"""
        return self._name
    
    @property
    def position(self) -> Vector3D:
        """获取星核位置"""
        return self._position
    
    @property
    def perturbations(self) -> bool:
        """获取是否产生引力扰动"""
        return self._perturbations
    
    @perturbations.setter
    def perturbations(self, value: bool) -> None:
        """设置是否产生引力扰动"""
        self._perturbations = value

    def to_dict(self) -> dict:
        """
        将星核对象转换为字典
        
        Returns:
            dict: 星核属性字典
        """
        return {
            "name": self._name,
            "position": (self._position.x, self._position.y, self._position.z),
            "mass": self.mass,
            "orbit_radius": self.orbit_radius,
            "orbit_velocity": self.orbit_velocity,
            "escape_velocity": self.escape_velocity,
            "perturbations": self._perturbations,
            "is_valid": self._is_valid
        }