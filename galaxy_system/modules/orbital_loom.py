from typing import Dict, Any, List, Tuple
from ..models.stellar_pearl import StellarPearl
from ..models.celestial_plume import CelestialPlume
from ..models.vector3d import Vector3D
from .gravity_loom import GravityLoom
from .boundary.base import BoundaryAtrium
import logging

class OrbitalLoom:
    """星轨织机：通过时光步长计算星引织网的扰动，编织星翎在月光坐标中的舞姿、速度羽衣、及星核共鸣状态"""
    
    def __init__(self, gravity_module: GravityLoom, boundary_effect: BoundaryAtrium, time_step: float):
        """
        初始化运行模块
        
        Args:
            gravity_module: 引力模块
            boundary_effect: 边界效果
            time_step: 时间步长
        """
        self.gravity_module = gravity_module
        self.boundary_effect = boundary_effect
        self.time_step = time_step
        self.capture_events: List[Dict[str, Any]] = []
    
    def step(self, stellar_pearls: List[StellarPearl], celestial_plume: CelestialPlume, step: int) -> Dict[str, Any]:
        """
        通过时光步长计算星引织网的扰动，编织星翎在月光坐标中的舞姿、速度羽衣、及星核共鸣状态
        
        Args:
            stellar_pearls: 星核列表
            celestial_plume: 星翎对象
            num_steps: 步进次数
            
        Returns:
            Dict[str, Any]: 包含时间步长、位置、速度、捕获事件和边界碰撞的结果字典
        """
        result = {
            "time_step": self.time_step,
            "positions": {},
            "velocities": {},
            "captures": [],
            "boundary_collisions": []
        }

        is_captured = False
        history = [] 
        
        # 1. 计算当前最近的有效星核和它到活动点的距离
        # 注意：总是会有有效星核，因为已经处理了默认星核的情况
        logging.debug(f"步进{step}: 开始计算最近星核...")
        min_dist = float('inf')
        current_closest_anchor_obj = None 
        
        # 总是会有有效星核，因为我们已经处理了默认星核的情况
        for stellar in stellar_pearls:
            # if not stellar.perturbations:
            #     continue
            dist = (celestial_plume.position - stellar.position).magnitude()
            if dist < min_dist:
                min_dist = dist
                current_closest_anchor_obj = stellar
        
        # ----------------------------------------
        # 边界碰撞处理 (优先级最高)
        # 当活动质点触碰边界时，会触发边界处理逻辑
        # 边界处理可能包括反射、传送等效果
        logging.debug(f"步进{step}: 检查边界碰撞...")
        if self.boundary_effect.check_collision(celestial_plume):
            logging.info(f"步进{step}: 触碰边界")
            is_captured = False  # 解除捕获状态
            
            # 使用边界处理器处理边界情况
            new_position, new_velocity = self.boundary_effect.handle_collision(celestial_plume, step)
            # 更新位置和速度
            celestial_plume.position = new_position
            celestial_plume.velocity = new_velocity
            result["boundary_collisions"].append({
                "celestial_plume_id": id(celestial_plume),
                "position": new_position,
                "velocity": new_velocity
            })
            
            # 如果是warp事件，记录相关信息
            logging.info(f"步进{step}: 边界处理(warp)，活动点已传送到球体另一侧")
            
            # 确保填充positions数据
            result["positions"][id(celestial_plume)] = celestial_plume.position
            result["velocities"][id(celestial_plume)] = celestial_plume.velocity
            
            logging.info(f"步进{step}[边界处理]: 位置={celestial_plume.position}, 速度={celestial_plume.velocity.magnitude():.1f}m/s, 最近星核: {current_closest_anchor_obj.name}({min_dist:.1f}m)")
            return result  # 返回当前结果

        # ----------------------------------------
        # 捕获逻辑 (仅当未触发边界碰撞时执行)
        # 当活动点与星核的距离小于该星核的理想同步轨道高度时，会被捕获
        # 被捕获的星核会暂时失效60个步进
        logging.debug(f"步进{step}: 检查捕获条件...")
        if not is_captured:
            # 检查是否满足捕获条件：活动点与星核的距离小于该星核的理想同步轨道高度
            if min_dist < current_closest_anchor_obj.orbit_radius:
                is_captured = True
                # 无效化捕获星核
                current_closest_anchor_obj.perturbations = False
                current_closest_anchor_obj.revival_rounds = step
                logging.info(f"!!! 步进 {step}: 星翎已触碰星核 {current_closest_anchor_obj.name}  (距离 {min_dist:.5f}m < 轨道半径 {current_closest_anchor_obj.orbit_radius:.5f}m), 星核已无效化 !!!")
                logging.info(f"步进{step}: {current_closest_anchor_obj.name}沉眠 (距离{min_dist:.1f}m), 星核已无效化")
                
        # ----------------------------------------
        # 引力计算和运动更新 (仅当未触发边界碰撞且未被捕获时执行)
        # 1. 筛选有效的引力源(排除失效的星核)
        # 2. 计算总引力加速度
        # 3. 使用高级积分方法更新速度和位置
        logging.debug(f"步进{step}: 开始引力计算...")
        if not is_captured: # 未被捕获时，使用高级引力计算引擎
            # 筛选引力源，只考虑影响力最大的星核，排除无效的星核
            active_anchors = []
            for stellar in stellar_pearls:
                # 检查星核是否无效，如果是无效的，检查是否已经超过60步
                if not stellar.perturbations:
                    if step - stellar.revival_rounds >= 60:
                        # 超过60步，恢复星核有效性
                        stellar.perturbations = True
                        logging.info(f"步进{step}: 星核{stellar.name}已复苏")
                    else:
                        # 星核仍然无效，跳过
                        continue
                active_anchors.append(stellar)
            
            filtered_anchors = self.gravity_module.filter_gravity_sources_by_influence(
                celestial_plume, active_anchors, influence_threshold=1e-6, max_sources=10
            )
            
            # 计算总引力加速度
            acceleration = self.gravity_module.calculate_total_acceleration(
                celestial_plume, filtered_anchors
            )
            
            # 使用高级积分方法更新速度和位置
            new_position, new_velocity = self.gravity_module.integrate_step(
                celestial_plume, filtered_anchors, self.time_step
            )
            
            # 更新活动点的速度和位置
            celestial_plume.velocity = new_velocity
            # 注意：位置更新会在后面的代码中进行
        
        # 更新位置
        celestial_plume.position += celestial_plume.velocity * self.time_step

        history.append({
            'step': step,
            'position': celestial_plume.position,
            'velocity': celestial_plume.velocity,
            'is_captured': is_captured,
            'capturing_anchor': (current_closest_anchor_obj.name) if is_captured else None,
            'is_warp': False  # 标记这不是一个warp事件
        })

        result["positions"][id(celestial_plume)] = celestial_plume.position
        result["velocities"][id(celestial_plume)] = celestial_plume.velocity

        # 打印当前步进详细信息
        # 包括位置、速度、加速度(如果未被捕获)、最近星核信息
        logging.debug(f"步进{step}: 计算完成，更新历史记录...")
        logging.info(f"步进{step}: 位置={celestial_plume.position}, 速度={celestial_plume.velocity.magnitude():.4f}m/s, {'' if is_captured else f'加速度={acceleration}'}, 最近星核: {current_closest_anchor_obj.name}({min_dist:.4f}m) {' [已捕获]' if is_captured else '' }")

        return result
    
    def _update_position(self, celestial_plume: CelestialPlume):
        """
        更新星翎位置
        
        Args:
            celestial_plume: 星翎对象
        """
        position = celestial_plume.position
        velocity = celestial_plume.velocity
        
        new_x = position.x + velocity.x * self.time_step
        new_y = position.y + velocity.y * self.time_step
        new_z = position.z + velocity.z * self.time_step
        
        celestial_plume.position = Vector3D(new_x, new_y, new_z)
    
    def checkStellarCapture(self, stellar_pearl: StellarPearl, celestial_plume: CelestialPlume) -> bool:
        """
        检查星翎是否被星核捕获
        
        Args:
            stellar_pearl: 星核对象
            celestial_plume: 星翎对象
            
        Returns:
            bool: 是否被捕获
        """
        # 计算星翎与星核的距离
        dx = celestial_plume.position.x - stellar_pearl.position.x
        dy = celestial_plume.position.y - stellar_pearl.position.y
        dz = celestial_plume.position.z - stellar_pearl.position.z
        distance = (dx**2 + dy**2 + dz**2)**0.5
        
        # 如果距离小于星核的轨道高度，则认为被捕获
        return distance < stellar_pearl.orbit_radius
    
    def get_capture_events(self) -> List[Dict[str, Any]]:
        """
        获取捕获事件列表
        
        Returns:
            List[Dict[str, Any]]: 捕获事件列表
        """
        return self.capture_events
    
    def clear_capture_events(self):
        """清空捕获事件列表"""
        self.capture_events.clear()