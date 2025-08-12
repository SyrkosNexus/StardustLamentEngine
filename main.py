import argparse
from galaxy_system.stellar_courtyard import StellarCourtyard
from galaxy_system.models.vector3d import Vector3D
from poisson_disk_sampling import poisson_disk_sampling
import random
import logging
import math
from galaxy_system.logger import setup_logging

def main():
    """
    主函数：演示星系模拟系统的使用
    """
    parser = argparse.ArgumentParser(description='星系模拟系统')
    parser.add_argument('--visual', action='store_true', help='启用可视化模式')
    args = parser.parse_args()
    setup_logging(level=logging.INFO)
    # 创建星系管理终端
    terminal = StellarCourtyard()
    
    # 设定星系常数
    terminal.set_constants(
        gravity_constant=0.1,            # 引力常数
        speed_of_light=299792458.0,      # 光速
        gravity_force_min_distance=1e-10 # 最小距离
    )
    
    # 构建星系
    # 无限：镜像穿越
    terminal.build_galaxy(
        central_mass=885000,
        boundary_type="infinite",
        reflection_angle=0
    )
    # 无限：随机穿越
    # terminal.build_galaxy(
    #     central_mass=88500,
    #     boundary_type="infinite",
    #     reflection_angle=math.pi/2
    # )
    # 反射：标准反射
    # terminal.build_galaxy(
    #     central_mass=88500,
    #     boundary_type="reflective",
    #     reflection_angle=0
    # )
    # 反射：漫反射
    # terminal.build_galaxy(
    #     central_mass=88500,
    #     boundary_type="reflective",
    #     reflection_angle=math.pi/3
    # )
    
    # 获取奥尔特云半径
    oort_cloud_radius = terminal.galaxy_model.oort_cloud_radius
    logging.info(f"奥尔特云半径: {oort_cloud_radius}")
    # 使用泊松盘采样算法生成均匀分布的点位
    # 最小距离设为奥尔特云半径的10%，确保点之间有足够的间距
    min_distance = oort_cloud_radius * 0.1
    # 使用泊松盘采样生成点，并确保在奥尔特云半径的75%范围内
    sampled_points = poisson_disk_sampling(
        5,  # 增加点数
        min_distance,
        max_attempts=50,  # 增加尝试次数
        radius=oort_cloud_radius * 0.75
    )

    for i, (x, y, z) in enumerate(sampled_points):
        position = Vector3D(x, y, z)
        terminal.add_stellar_pearl(
            name=f"P{i+1}",
            mass=2000,
            position=position,
        )
    
    # 生成初始位置并验证在奥尔特云半径范围内
    moving_point_initial_pos = Vector3D(
        random.uniform(-oort_cloud_radius / 2, oort_cloud_radius / 2),
        random.uniform(-oort_cloud_radius / 2, oort_cloud_radius / 2),
        random.uniform(-oort_cloud_radius / 2, oort_cloud_radius / 2)
    )
    moving_point_initial_vel = Vector3D(
        random.uniform(-1.0, 1.0),
        random.uniform(-1.0, 1.0),
        random.uniform(-1.0, 1.0)
    )
    # 添加星翎（行星）
    terminal.set_celestial_plume(
        mass=1.0,                 # 地球质量
        position=moving_point_initial_pos, # 地球到太阳的距离
        velocity=moving_point_initial_vel   # 地球公转速度
    )
    
    # 设置时间步长
    terminal.set_time_step(10)
    
    # 运行模拟
    logging.info("开始星系模拟...")
    status = terminal.get_galaxy_status()
    logging.info(f"星系状态: {status}")
    
    # 运行365步（1年）
    results = terminal.run_simulation(5000)
    
    logging.info("模拟完成！")
    logging.info(f"运行了 {len(results)} 步")
    
    # 显示最后一步的结果
    final_result = results[-1]
    logging.info(f"最后一步的位置: {final_result['positions']}")
    logging.info(f"最后一步的速度: {final_result['velocities']}")
    logging.info(f"捕获事件: {final_result['captures']}")
    logging.info(f"边界碰撞: {final_result['boundary_collisions']}")
    
    # 如果启用了可视化模式则绘制模拟轨迹图
    if args.visual:
        terminal.plot_simulation(results, "星系模拟轨迹", oort_cloud_radius=oort_cloud_radius)

if __name__ == "__main__":
    main()