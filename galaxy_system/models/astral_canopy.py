from typing import List, Tuple
from .stellar_pearl import StellarPearl
from .celestial_plume import CelestialPlume
from ..modules.gravity_loom import GravityLoom
from ..modules.boundary.base import BoundaryAtrium
from ..modules.boundary.infinite import MirrorAbyssGate
from ..modules.boundary.reflective import PrismicEchoWall

class AstralCanopy:
    """星穹领域：封闭的宇宙庭园，根据星律、领域核心（无引力）计算奥尔特云边界半径，根据界域特性生成星穹边际，以记录万物位置"""
    
    def __init__(self, gravity_loom: GravityLoom, central_mass: float = 88500, boundary_type: str = "infinite"):
        """
        初始化星穹领域
        
        Args:
            gravity_loom: 星引织网
            central_mass: 领域核心质量(必须>0)
            boundary_type: 界域类型("infinite"或"reflective")
        
        Raises:
            ValueError: 如果central_mass<=0或boundary_type无效
        """
        import logging
        
        # 验证中央质量
        if central_mass <= 0:
            raise ValueError(f"Central mass must be positive, got {central_mass}")
            
        self.central_mass = central_mass
        logging.debug(f"计算奥尔特云半径，中央质量={central_mass}")
        
        try:
            self._oort_cloud_radius = gravity_loom.calculate_oort_cloud_radius(central_mass)
            logging.debug(f"奥尔特云半径计算结果: {self._oort_cloud_radius}")
        except Exception as e:
            logging.error(f"计算奥尔特云半径失败: {str(e)}")
            raise
            
        self._celestial_plume = None
        self.boundary_type = boundary_type.lower()
        
        # 创建界域回廊
        try:
            logging.debug(f"创建边界条件，类型={boundary_type}")
            if self.boundary_type == "infinite":
                self.boundary_effect = MirrorAbyssGate(self._oort_cloud_radius)
            elif self.boundary_type == "reflective":
                self.boundary_effect = PrismicEchoWall(self._oort_cloud_radius)
            else:
                raise ValueError(f"未知边界类型: {boundary_type}")
                
            logging.debug("边界条件创建成功")
        except Exception as e:
            logging.error(f"创建边界条件失败: {str(e)}")
            raise
        self.stellar_pearls: List[StellarPearl] = []
        self.gravity_module: GravityLoom = None
        self.simulation_module = None
    
    @property
    def oort_cloud_radius(self) -> float:
        """
        计算奥尔特云边界半径
        
        Returns:
            float: 奥尔特云边界半径
        """
        return self._oort_cloud_radius
    
    @property
    def celestial_plume(self) -> CelestialPlume:
        """
        获取星翎
        
        Args:
            celestial_plume: 星翎对象
        """
        return self._celestial_plume

    @celestial_plume.setter
    def celestial_plume(self, value: CelestialPlume):
        """
        映射星翎到星穹领域
        """
        self._celestial_plume = value
    
    def add_stellar_pearl(self, stellar_pearl: StellarPearl):
        """
        添加星核到星穹领域
        
        Args:
            stellar_pearl: 星核对象
        """
        self.stellar_pearls.append(stellar_pearl)
    
    def remove_stellar_pearl(self, stellar_pearl: StellarPearl):
        """
        从星穹领域中移除星核
        
        Args:
            stellar_pearl: 星核对象
        """
        if stellar_pearl in self.stellar_pearls:
            self.stellar_pearls.remove(stellar_pearl)

    def remove_celestial_plume(self):
        """
        从星穹领域中移除星翎
        
        Args:
            celestial_plume: 星翎对象
        """
        self.celestial_plume = None
    
    def get_stellar_pearls(self) -> List[StellarPearl]:
        """
        获取所有星核
        
        Returns:
            List[StellarPearl]: 星核列表
        """
        return self.stellar_pearls
    
    def get_stellar_pearl_by_name(self, name: str) -> StellarPearl:
        """
        根据名称获取星核
        
        Args:
            name: 星核名称
            
        Returns:
            StellarPearl: 星核对象，如果找不到则返回None
        """
        for stellar_pearl in self.stellar_pearls:
            if stellar_pearl.name == name:
                return stellar_pearl
        return None
    
    def set_gravity_module(self, gravity_module: GravityLoom):
        """
        设置星引织网
        
        Args:
            gravity_module: 星引织网
        """
        self.gravity_module = gravity_module
    
    def set_boundary_effect(self, boundary_effect: BoundaryAtrium):
        """
        设置界域回廊
        
        Args:
            boundary_effect: 界域回廊
        """
        self.boundary_effect = boundary_effect
    
    def __str__(self) -> str:
        return f"AstralCanopy(central_mass={self.central_mass}, boundary_type='{self.boundary_type}', stellar_pearls={len(self.stellar_pearls)}, celestial_plume={self._celestial_plume})"
    
    def __repr__(self) -> str:
        return self.__str__()