from ..models.vector3d import Vector3D

class StardustCore:
    """星尘之核"""
    
    def __init__(self, mass: float, position: Vector3D, orbital_radius: float, orbital_velocity: float, escape_velocity: float):
        """
        初始化星尘之核
        
        Args:
            mass: 物体质量
            orbital_radius: 轨道半径
            orbital_velocity: 轨道速度
            escape_velocity: 逃逸速度
        """
        self._mass = mass
        self._position = position
        self._orbital_radius = orbital_radius
        self._orbital_velocity = orbital_velocity
        self._escape_velocity = escape_velocity

    mass = property(lambda self: self._mass, doc="获取物体质量")
    position = property(lambda self: self._position, doc="获取物体位置")
    orbit_radius = property(lambda self: self._orbital_radius, doc="获取轨道半径")
    orbit_velocity = property(lambda self: self._orbital_velocity, doc="获取轨道速度")
    escape_velocity = property(lambda self: self._escape_velocity, doc="获取逃逸速度")

    def update(self, mass: float, orbital_radius: float, orbital_velocity: float, escape_velocity: float):
        """
        更新星尘之核的属性
        
        Args:
            mass: 新的物体质量
            orbital_radius: 新的轨道半径
            orbital_velocity: 新的轨道速度
            escape_velocity: 新的逃逸速度
        """
        self._mass = mass
        self._orbital_radius = orbital_radius
        self._orbital_velocity = orbital_velocity
        self._escape_velocity = escape_velocity