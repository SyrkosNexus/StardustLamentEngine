from typing import List, Dict, Any
import numpy as np
import matplotlib.pyplot as plt
import logging
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from .models.astral_canopy import AstralCanopy
from .models.stellar_pearl import StellarPearl
from .models.celestial_plume import CelestialPlume
from .models.vector3d import Vector3D
from .modules.gravity_loom import GravityLoom
from .modules.orbital_loom import OrbitalLoom
from .modules.boundary.base import BoundaryAtrium

class StellarCourtyard:
    """星枢庭园：星系管理中心"""
    
    def __init__(self):
        """初始化星枢庭园"""
        self.galaxy_model: AstralCanopy = None
        self.gravity_module: GravityLoom = None
        self.boundary_effect: BoundaryAtrium = None
        self.simulation_module: OrbitalLoom = None
        self.constants = {
            "gravity_constant": 0.1,       # 重力常数
            "speed_of_light": 299792458.0, # 光速
            "gravity_force_min_distance": 1e-3           # 引力最小作用距离
        }
        self.time_step = 0.01
        self.disabled_gravity_timers: Dict[int, int] = {}
    
    def set_constants(self, gravity_constant: float = None, speed_of_light: float = None, gravity_force_min_distance: float = None):
        """
        调谐星律
        
        Args:
            gravity_constant: 重力常数
            speed_of_light: 光速
            gravity_force_min_distance: 引力涟漪距离
        """
        if gravity_constant is not None:
            self.constants["gravity_constant"] = gravity_constant
        if speed_of_light is not None:
            self.constants["speed_of_light"] = speed_of_light
        if gravity_force_min_distance is not None:
            self.constants["gravity_force_min_distance"] = gravity_force_min_distance
    
    def build_galaxy(self, central_mass: float, boundary_type: str):
        """
        编织星穹
        
        Args:
            central_mass: 领域核心
            boundary_type: 界域类型
        """
        # 创建星引织网
        self.gravity_module = GravityLoom(
            speed_of_light=self.constants["speed_of_light"],
            gravity_constant=self.constants["gravity_constant"],
            gravity_force_min_distance=self.constants["gravity_force_min_distance"],
        )

        # 创建星穹领域
        self.galaxy_model = AstralCanopy(
            self.gravity_module,
            central_mass=central_mass,
            boundary_type=boundary_type,
        )
        
        # 创建星轨织机
        self.simulation_module = OrbitalLoom(
            gravity_module=self.gravity_module,
            boundary_effect=self.galaxy_model.boundary_effect,
            time_step=self.time_step
        )
        
        # 将模块设置到星穹领域
        self.galaxy_model.set_gravity_module(self.gravity_module)
        self.galaxy_model.set_boundary_effect(self.boundary_effect)
    
    def add_stellar_pearl(self, name: str, mass: float, position: Vector3D, orbit_raduis: float = 1) -> StellarPearl:
        """
        抚育星核：添加星核
        
        Args:
            mass: 质量
            position: 月光坐标
            
        Returns:
            StellarPearl: 创建的星核对象
        """

        orbit_velocity, escape_velocity = self.gravity_module.calculate_orbital_escape_velocities(mass, orbit_raduis)
        stellar_pearl = StellarPearl(name, position, mass, orbit_raduis, orbit_velocity, escape_velocity)
        self.galaxy_model.add_stellar_pearl(stellar_pearl)
        return stellar_pearl
    
    def remove_stellar_pearl(self, stellar_pearl: StellarPearl):
        """
        泯灭星核：移除星核
        
        Args:
            stellar_pearl: 要移除的星核对象
        """
        self.galaxy_model.remove_stellar_pearl(stellar_pearl)
    
    def set_celestial_plume(self, mass: float, position: Vector3D, velocity: Vector3D) -> CelestialPlume:
        """
        引航星翎：添加星翎
        
        Args:
            mass: 质量
            position: 月光坐标
            velocity: 速度羽衣
            
        Returns:
            CelestialPlume: 创建的星翎对象
        """
        celestial_plume = CelestialPlume(position, velocity, mass)
        print(self.galaxy_model)
        self.galaxy_model.celestial_plume = celestial_plume
        return celestial_plume
    
    def remove_celestial_plume(self, celestial_plume: CelestialPlume):
        """
        引航星翎：移除星翎
        
        Args:
            celestial_plume: 要移除的星翎对象
        """
        self.galaxy_model.remove_celestial_plume(celestial_plume)
    
    def set_time_step(self, time_step: float):
        """
        设置时间步长
        
        Args:
            time_step: 时间步长
        """
        self.time_step = time_step
        if self.simulation_module:
            self.simulation_module.time_step = time_step
    
    def run_simulation(self, steps: int) -> List[Dict[str, Any]]:
        """
        流转星轨
        
        Args:
            steps: 运转步数
            
        Returns:
            List[Dict[str, Any]]: 每步的运行结果
        """
        if not self.galaxy_model or not self.simulation_module:
            raise RuntimeError("Galaxy not built. Please call build_galaxy() first.")
        
        logging.info(f"准备模拟，总步数={steps}")
        logging.debug(f"星系模型: {self.galaxy_model}")
        logging.debug(f"时间步长: {self.time_step}")
        
        # 检查星核和星翎
        stellar_pearls = self.galaxy_model.get_stellar_pearls()
        if not stellar_pearls or len(stellar_pearls) == 0:
            logging.warning("没有星核存在，无法进行模拟")
        if not self.galaxy_model.celestial_plume:
            raise RuntimeError("没有星翎存在，无法进行模拟")
            
        results = []
        
        try:
            for time in range(steps):
                logging.debug(f"开始步进 {time+1}/{steps}")
                
                # 运行一步模拟
                result = self.simulation_module.step(
                    stellar_pearls,
                    self.galaxy_model.celestial_plume,
                    time  # 每次只步进1步
                )
                
                logging.debug(f"步进{time}完成，结果: {result}")
                
                # 处理捕获事件
                self._handle_capture_events(result)
                
                # 更新禁用引力计时器
                self._update_gravity_timers()
                
                results.append(result)
                
                # 定期打印进度
                if (time + 1) % 10 == 0:
                    logging.info(f"已完成 {time+1}/{steps} 步 ({((time+1)/steps)*100:.1f}%)")
                    
        except Exception as e:
            logging.error(f"模拟在步进 {time} 时出错: {str(e)}")
            raise
            
        logging.info("模拟完成")
        
        return results
    
    def _handle_capture_events(self, result: Dict[str, Any]):
        """
        处理星核沉眠仪式
        
        Args:
            result: 运行结果
        """
        if result is None or "captures" not in result:
            return
            
        for capture in result["captures"]:
            stellar_pearl_id = capture["stellar_pearl_id"]
            
            # 找到对应的星核
            stellar_pearl = None
            
            for sp in self.galaxy_model.get_stellar_pearls():
                if id(sp) == stellar_pearl_id:
                    stellar_pearl = sp
                    break
            
            if stellar_pearl:
                # 星核沉眠
                stellar_pearl.perturbations = False
                # 设置恢复计时器
                self.disabled_gravity_timers[stellar_pearl_id] = 60  # 60步后恢复
    
    def _update_gravity_timers(self):
        """更新星核沉眠计时器"""
        to_remove = []
        
        for stellar_pearl_id, timer in self.disabled_gravity_timers.items():
            self.disabled_gravity_timers[stellar_pearl_id] = timer - 1
            
            if timer <= 0:
                # 找到对应的星核并恢复引力
                for stellar_pearl in self.galaxy_model.get_stellar_pearls():
                    if id(stellar_pearl) == stellar_pearl_id:
                        stellar_pearl.enable_gravity()
                        break
                
                to_remove.append(stellar_pearl_id)
        
        for stellar_pearl_id in to_remove:
            del self.disabled_gravity_timers[stellar_pearl_id]
    
    def plot_simulation(self, results: List[Dict[str, Any]], title: str = "星轨模拟结果", oort_cloud_radius: float = None):
        """
        绘制模拟轨迹图 - 增强版 (基于sample实现优化)
        
        Args:
            results: 模拟结果列表
            title: 图表标题
            oort_cloud_radius: 奥尔特云半径，用于绘制灰色球体边界
        """
        # 设置中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 提取轨迹数据（添加防御性检查）
        positions = []
        for state in results:
            if state is None or 'positions' not in state or id(self.galaxy_model.celestial_plume) not in state['positions']:
                continue
            pos = state['positions'][id(self.galaxy_model.celestial_plume)]
            positions.append([pos.x, pos.y, pos.z])
        
        
        if not positions:
            raise ValueError("没有有效的轨迹数据可用于绘图")
            
        positions = np.array(positions)
        
        # 提取warp事件索引
        warp_indices = [i for i, state in enumerate(results)
                       if state.get('boundary_collisions', [])]
        
        # 创建3D图形
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # 如果没有warp事件，按原方式绘制轨迹
        if not warp_indices:
            # 优化采样率
            step_size = max(1, len(positions) // 1000)
            sampled_positions = positions[::step_size]
            
            # 创建渐变色轨迹
            points = sampled_positions.reshape(-1, 1, 3)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)
            cmap = LinearSegmentedColormap.from_list('trajectory', ['blue', 'purple', 'red'])
            norm = plt.Normalize(0, len(segments))
            
            for i, segment in enumerate(segments):
                color = cmap(norm(i))
                ax.plot(segment[:, 0], segment[:, 1], segment[:, 2],
                       color=color, linewidth=1.2, alpha=0.8)
            
            # 添加颜色条
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, pad=0.1, shrink=0.8)
            cbar.set_label('运动方向 (起点→终点)')
        else:
            # 分段绘制轨迹
            segment_colors = ['blue', 'green', 'red', 'purple', 'orange']
            start_idx = 0
            
            for segment_idx, warp_idx in enumerate(warp_indices):
                end_idx = warp_idx
                if start_idx <= end_idx:
                    segment_positions = positions[start_idx:end_idx+1]
                    step_size = max(1, len(segment_positions) // 500)
                    sampled_segment = segment_positions[::step_size]
                    
                    color = segment_colors[segment_idx % len(segment_colors)]
                    ax.plot(sampled_segment[:, 0], sampled_segment[:, 1], sampled_segment[:, 2],
                           color=color, linewidth=1.2, alpha=0.8)
                
                start_idx = warp_idx + 1
            
            # 绘制最后一段
            if start_idx < len(positions):
                segment_positions = positions[start_idx:]
                step_size = max(1, len(segment_positions) // 500)
                sampled_segment = segment_positions[::step_size]
                
                color = segment_colors[len(warp_indices) % len(segment_colors)]
                ax.plot(sampled_segment[:, 0], sampled_segment[:, 1], sampled_segment[:, 2],
                       color=color, linewidth=1.2, alpha=0.8)
        
        # 标记起点和终点
        ax.scatter(positions[0, 0], positions[0, 1], positions[0, 2],
                  color='green', s=100, label='起点')
        ax.scatter(positions[-1, 0], positions[-1, 1], positions[-1, 2],
                  color='red', s=100, label='终点')
        
        # 绘制星核位置和轨道半径
        for pearl in self.galaxy_model.get_stellar_pearls():
            # 绘制星核
            ax.scatter(pearl.position.x, pearl.position.y, pearl.position.z,
                      color='orange', s=150, marker='*', label=pearl.name)
            
            # 绘制轨道半径
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            x = pearl.orbit_radius * np.outer(np.cos(u), np.sin(v)) + pearl.position.x
            y = pearl.orbit_radius * np.outer(np.sin(u), np.sin(v)) + pearl.position.y
            z = pearl.orbit_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + pearl.position.z
            
            for j in range(0, 20, 5):
                ax.plot(x[j, :], y[j, :], z[j, :], color='orange', alpha=0.2, linewidth=0.5)
            for j in range(0, 20, 5):
                ax.plot(x[:, j], y[:, j], z[:, j], color='orange', alpha=0.2, linewidth=0.5)
        
        # 绘制奥尔特云球体（透明度30%的灰色球体）
        if oort_cloud_radius is not None:
            u = np.linspace(0, 2 * np.pi, 50)
            v = np.linspace(0, np.pi, 50)
            x_sphere = oort_cloud_radius * np.outer(np.cos(u), np.sin(v))
            y_sphere = oort_cloud_radius * np.outer(np.sin(u), np.sin(v))
            z_sphere = oort_cloud_radius * np.outer(np.ones(np.size(u)), np.cos(v))
            
            # 绘制球体表面，透明度30%，添加光照效果增强立体感
            ax.plot_surface(x_sphere, y_sphere, z_sphere, color='gray', alpha=0.3,
                          linewidth=0, antialiased=True, shade=True)
            
            # 添加球体轮廓线增强立体感
            ax.plot_wireframe(x_sphere, y_sphere, z_sphere, color='darkgray',
                            alpha=0.2, linewidth=0.5, rstride=5, cstride=5)
        
        # 设置图表属性
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(title)
        ax.legend()
        ax.view_init(elev=30, azim=45)
        
        plt.tight_layout()
        plt.show(block=True)
        
        # 重置字体设置
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = True

    def get_galaxy_status(self) -> Dict[str, Any]:
        """
        获取星穹领域状态
        
        Returns:
            Dict[str, Any]: 星穹领域状态信息
        """
        if not self.galaxy_model:
            return {"status": "not_built"}
        
        return {
            "status": "built",
            "central_mass": self.galaxy_model.central_mass,
            "boundary_type": self.galaxy_model.boundary_type,
            "stellar_pearls_count": len(self.galaxy_model.get_stellar_pearls()),
            "disabled_gravity_count": len(self.disabled_gravity_timers),
            "constants": self.constants,
            "time_step": self.time_step
        }