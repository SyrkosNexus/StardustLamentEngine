import math
from typing import List, Tuple
from ..models.vector3d import Vector3D
from ..models.stardust_core import StardustCore
from ..models.celestial_plume import CelestialPlume

class GravityLoom:
    """星引织网：根据光速竖琴、引力涟漪距离、星律等条件，计算星核与星翎在时光步长中的引力共舞"""
    GRAVITY_CONSTANT: float = 0.1  # 引力常数 (N·m²/kg²)
    STARDUST_LIGHT_SPEED = 299792458.0  # 光速 (m/s)
    GRAVITY_FORCE_MIN_DISTANCE: float = 1e-3
    
    def __init__(self, gravity_constant: float = GRAVITY_CONSTANT, speed_of_light: float = STARDUST_LIGHT_SPEED, gravity_force_min_distance: float = GRAVITY_FORCE_MIN_DISTANCE,
                 enable_perturbations=True,
                 enable_relativistic_corrections=False,
                 integration_method="rk4"):
        """
        初始化引力模块
        
        Args:
            gravity_constant: 引力常数
            speed_of_light: 光速常量
            gravity_force_min_distance: 引力作用最小距离
            enable_perturbations: 是否启用引力扰动
            enable_relativistic_corrections: 是否启用相对论修正
            integration_method: 数值积分方法 ("euler", "rk2", "rk4")
        """
        if gravity_constant <= 0:
            self._gravity_constant = GravityLoom.GRAVITY_CONSTANT
        else:
            self._gravity_constant = gravity_constant
        if speed_of_light <= 0:
            self._speed_of_light = GravityLoom.STARDUST_LIGHT_SPEED
        else:
            self._speed_of_light = speed_of_light
        if gravity_force_min_distance <= 0:
            self._gravity_force_min_distance = GravityLoom.GRAVITY_FORCE_MIN_DISTANCE
        else:
            self._gravity_force_min_distance = gravity_force_min_distance

        self._enable_perturbations = enable_perturbations
        self._enable_relativistic_corrections = enable_relativistic_corrections
        self._integration_method = integration_method
        # 根据项目参数调整物理效应的强度
        self._perturbation_scale = 1.0  # 扰动效应缩放因子
    
    @property
    def gravity_constant(self) -> float:
        """获取引力常数"""
        return self._gravity_constant
    
    @property
    def speed_of_light(self) -> float:
        """获取光速常量"""
        return self._speed_of_light
    
    @property
    def gravity_force_min_distance(self) -> float:
        """获取引力作用最小距离"""
        return self._gravity_force_min_distance
    
    def calculate_oort_cloud_radius(self, central_mass: float = 88500):
        """
        计算奥尔特云半径，用于生成世界的边界大小。
        
        该方法基于太阳系奥尔特云的参考半径和引力关系，计算给定中心质点质量
        和引力常数下的奥尔特云半径。计算结果可以用于确定模拟世界的边界大小。
        
        参数:
            G: 引力常数，默认值为 0.1 N·m²/kg²
            central_mass: 中心质点质量，默认值为 88,500 吨
                
        返回:
            float: 计算出的奥尔特云半径
            
        计算公式:
            R_hypo (米) = (7.5 × 10^15 * G_hypo * M_hypo) / (6.674 × 10^-11 * 1.989 × 10^30)
            
        参考值:
            - 太阳系奥尔特云的参考半径: 约 50,000 天文单位 (AU)
            - 1 AU ≈ 1.5 × 10^11 米
            - 太阳质量: 1.989 × 10^30 kg
            - 标准引力常数: 6.674 × 10^-11 N·m²/kg²
            
        示例:
            使用默认参数值:
            >>> service = SeikaiService()
            >>> radius = service.calculate_oort_cloud_radius()
            >>> print(radius)  # 输出应接近 500.0
        """
        # 常量定义
        R_SUN_OORT_REF = 7.5e15  # 太阳系奥尔特云的参考半径，单位为米
        G_STANDARD = 6.674e-11   # 标准引力常数，单位为 N·m²/kg²
        M_SUN = 1.989e30         # 太阳质量，单位为 kg
        
        # 计算奥尔特云半径（单位：米）
        radius_meters = R_SUN_OORT_REF * (self._gravity_constant * central_mass * 1000) / (G_STANDARD * M_SUN)
        return radius_meters

    def calculate_orbital_escape_velocities(self, mass: float, orbit_raduis: float=1.0):
        """
        计算圆形轨道速度和逃逸速度。
        
        参数:
            mass: 物体质量
            orbit_raduis: 轨道半径
            
        返回:
            tuple: (轨道速度, 逃逸速度)
        """
        if orbit_raduis <= 0:
            # 实际物理中距离不能为0，这里返回无穷大或抛出错误
            return float('inf'), float('inf') 
        
        # 轨道速度 (圆形轨道)
        orbital_velocity = math.sqrt(self._gravity_constant * mass / orbit_raduis)
        
        # 逃逸速度
        escape_velocity = math.sqrt(2 * self._gravity_constant * mass / orbit_raduis)
        
        return orbital_velocity, escape_velocity
    
    def calculate_gravity_force(self, stellar: StardustCore, plume: StardustCore) -> Vector3D:
        """
        计算星核对星翎的基本引力作用，包含相对论修正
        
        参数:
            stellar: 星核
            plume: 星翎
            
        返回:
            Vector3D: 作用在星翎上的引力向量
        """
        # 从 星核 到 星翎 的位移矢量
        r_vec = plume.position - stellar.position
        distance = r_vec.magnitude()
        
        if distance < self.gravity_force_min_distance:
            return Vector3D(0, 0, 0)
        
        # 基本牛顿引力
        force_magnitude = (self.gravity_constant * stellar.mass * plume.mass) / (distance**2)
        
        # 相对论修正（后牛顿近似）
        if self._enable_relativistic_corrections:
            # 简化的相对论修正因子
            v_squared = 0  # 这里需要速度信息，暂时简化处理
            relativistic_factor = 1 + (3 * self.gravity_constant * stellar.mass) / (distance * self.speed_of_light**2) - v_squared / self.speed_of_light**2
            force_magnitude *= relativistic_factor
        
        # 引力方向是从星翎指向星核
        return r_vec.normalize() * (-force_magnitude)
    
    def calculate_perturbation_force(self, primary: StardustCore,
                                   plume: StardustCore,
                                   perturber: StardustCore) -> Vector3D:
        """
        计算星核对星翎的扰动引力
        
        参数:
            primary: 主星核
            plume: 星翎
            perturber: 扰动星核
            
        返回:
            Vector3D: 作用在星翎上的扰动引力向量
        """
        if not self._enable_perturbations:
            return Vector3D(0, 0, 0)
            
        try:
            # 计算扰动星核对星翎的直接引力
            direct_force = self.calculate_gravity_force(perturber, plume)
            if direct_force is None:
                return Vector3D(0, 0, 0)
            
            # 计算扰动星核对主星核的扰动引力
            primary_force = self.calculate_gravity_force(perturber, primary)
            if primary_force is None:
                return Vector3D(0, 0, 0)
            
            # 安全计算质量比
            mass_ratio = 0.0
            if primary.mass > 1e-10:  # 避免除零和小数精度问题
                mass_ratio = plume.mass / primary.mass
            
            # 计算扰动力，确保数值稳定
            scaled_primary_force = primary_force * mass_ratio
            perturbation = direct_force - scaled_primary_force
            
            # 应用扰动效应缩放因子，确保在小质量系统中合理但可见
            perturbation = perturbation * self._perturbation_scale
            
            return perturbation
            
        except Exception as e:
            import logging
            logging.error(f"计算扰动引力时出错: {str(e)}")
            return Vector3D(0, 0, 0)
    
    def calculate_total_acceleration(self, point: CelestialPlume, gravity_sources: List[StardustCore]) -> Vector3D:
        """
        计算一个点受到所有引力源的总加速度，包含所有高级效应
        
        参数:
            point: 要计算加速度的点
            gravity_sources: 引力源列表
            
        返回:
            Vector3D: 总加速度向量
        """
        total_force = Vector3D(0, 0, 0)
        
        # 计算基本引力
        for source in gravity_sources:
            force = self.calculate_gravity_force(source, point)
            total_force += force
        
        # 计算扰动引力（三体或多体效应）
        if self._enable_perturbations and len(gravity_sources) >= 2:
            for i, primary_source in enumerate(gravity_sources):
                for j, perturber_source in enumerate(gravity_sources):
                    if i != j:  # 确保不是同一个引力源
                        perturbation_force = self.calculate_perturbation_force(primary_source, point, perturber_source)
                        total_force += perturbation_force
        
        # F = ma, 所以 a = F/m
        return total_force / point.mass
    
    def runge_kutta_4_step(self, point: CelestialPlume, gravity_sources: List[StardustCore],
                         time_step: float) -> Tuple[Vector3D, Vector3D]:
        """
        使用四阶Runge-Kutta方法进行一步积分
        
        参数:
            point: 要积分的点
            gravity_sources: 引力源列表
            time_step: 时间步长
            
        返回:
            Tuple[Vector3D, Vector3D]: (新位置, 新速度)
        """
        # RK4方法需要计算四个中间状态
        # k1
        a1 = self.calculate_total_acceleration(point, gravity_sources)
        v1 = point.velocity
        r1 = point.position
        
        # k2
        temp_point = CelestialPlume(r1 + v1 * (time_step/2), v1 + a1 * (time_step/2), mass=point.mass)
        a2 = self.calculate_total_acceleration(temp_point, gravity_sources)
        v2 = temp_point.velocity
        r2 = temp_point.position
        
        # k3
        temp_point = CelestialPlume(r1 + v2 * (time_step/2), v1 + a2 * (time_step/2), mass=point.mass)
        a3 = self.calculate_total_acceleration(temp_point, gravity_sources)
        v3 = temp_point.velocity
        r3 = temp_point.position
        
        # k4
        temp_point = CelestialPlume(r1 + v3 * time_step, v1 + a3 * time_step, mass=point.mass)
        a4 = self.calculate_total_acceleration(temp_point, gravity_sources)
        v4 = temp_point.velocity
        r4 = temp_point.position
        
        # 计算新位置和新速度
        new_position = r1 + (v1 + v2*2 + v3*2 + v4) * (time_step/6)
        new_velocity = v1 + (a1 + a2*2 + a3*2 + a4) * (time_step/6)
        
        return new_position, new_velocity
    
    def runge_kutta_2_step(self, point: CelestialPlume, gravity_sources: List[StardustCore],
                         time_step: float) -> Tuple[Vector3D, Vector3D]:
        """
        使用二阶Runge-Kutta方法进行一步积分
        
        参数:
            point: 要积分的点
            gravity_sources: 引力源列表
            time_step: 时间步长
            
        返回:
            Tuple[Vector3D, Vector3D]: (新位置, 新速度)
        """
        # RK2方法（中点法）
        # k1
        a1 = self.calculate_total_acceleration(point, gravity_sources)
        v1 = point.velocity
        r1 = point.position
        
        # k2
        temp_point = CelestialPlume(r1 + v1 * (time_step/2), v1 + a1 * (time_step/2), mass=point.mass)
        a2 = self.calculate_total_acceleration(temp_point, gravity_sources)
        v2 = temp_point.velocity
        
        # 计算新位置和新速度
        new_position = r1 + v2 * time_step
        new_velocity = v1 + a2 * time_step
        
        return new_position, new_velocity
    
    def euler_step(self, point: CelestialPlume, gravity_sources: List[StardustCore],
                 time_step: float) -> Tuple[Vector3D, Vector3D]:
        """
        使用欧拉方法进行一步积分
        
        参数:
            point: 要积分的点
            gravity_sources: 引力源列表
            G: 引力常数
            time_step: 时间步长
            
        返回:
            Tuple[Vector3D, Vector3D]: (新位置, 新速度)
        """
        # 计算加速度
        acceleration = self.calculate_total_acceleration(point, gravity_sources)
        
        # 更新速度和位置
        new_velocity = point.velocity + acceleration * time_step
        new_position = point.position + point.velocity * time_step
        
        return new_position, new_velocity
    
    def integrate_step(self, point: CelestialPlume, gravity_sources: List[StardustCore],
                      time_step: float) -> Tuple[Vector3D, Vector3D]:
        """
        根据选择的积分方法进行一步积分
        
        参数:
            point: 要积分的点
            gravity_sources: 引力源列表
            time_step: 时间步长
            
        返回:
            Tuple[Vector3D, Vector3D]: (新位置, 新速度)
        """
        if self._integration_method == "rk4":
            return self.runge_kutta_4_step(point, gravity_sources, time_step)
        elif self._integration_method == "rk2":
            return self.runge_kutta_2_step(point, gravity_sources, time_step)
        else:  # 默认使用欧拉方法
            return self.euler_step(point, gravity_sources, time_step)
    
    def filter_gravity_sources_by_influence(self, point: CelestialPlume, gravity_sources: List[StardustCore],
                                          influence_threshold: float = 1e-6,
                                          max_sources: int = 10) -> List[StardustCore]:
        """
        根据影响力筛选引力源，只保留影响力最大的引力源
        
        参数:
            point: 要计算的星翎
            gravity_sources: 所有引力源列表
            influence_threshold: 影响力阈值，低于此值的引力源将被忽略
            max_sources: 最大保留的引力源数量
            
        返回:
            List[StardustCore]: 筛选后的引力源列表
        """
        # 计算每个引力源的影响力
        source_influences = []
        for source in gravity_sources:
            distance = (point.position - source.position).magnitude()
            if distance < 1e-10:  # 避免除零
                continue
                
            # 影响力定义为 G*M/r^2
            influence = (self.gravity_constant * source.mass) / (distance**2)
            if influence >= influence_threshold:
                source_influences.append((source, influence))
        
        # 按影响力降序排序
        source_influences.sort(key=lambda x: x[1], reverse=True)
        
        # 只保留影响力最大的max_sources个引力源
        filtered_sources = [item[0] for item in source_influences[:max_sources]]
        
        return filtered_sources