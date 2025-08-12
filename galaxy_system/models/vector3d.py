from __future__ import annotations
import torch


class Vector3D:
    """三维向量类，用于表示和操作三维空间中的向量"""
    
    def __init__(self, x, y, z):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._data = torch.tensor([x, y, z], dtype=torch.float64, device=device)
    
    @property
    def x(self):
        """获取x分量"""
        return self._data[0].item()
    
    @property
    def y(self):
        """获取y分量"""
        return self._data[1].item()
    
    @property
    def z(self):
        """获取z分量"""
        return self._data[2].item()

    def __add__(self, other: Vector3D):
        """向量加法"""
        result = self._data + other._data
        return Vector3D(*result.tolist())

    def __sub__(self, other: Vector3D):
        """向量减法"""
        result = self._data - other._data
        return Vector3D(*result.tolist())

    def __mul__(self, scalar):
        """向量与标量乘法"""
        result = self._data * scalar
        return Vector3D(*result.tolist())

    def __truediv__(self, scalar):
        """向量与标量除法"""
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        result = self._data / scalar
        return Vector3D(*result.tolist())

    def magnitude(self):
        """计算向量的模长。"""
        return torch.norm(self._data).item()

    def normalize(self):
        """返回向量的单位向量。"""
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(0, 0, 0)  # 避免除以零
        result = self._data / mag
        return Vector3D(*result.tolist())

    def cross(self, other: Vector3D):
        """计算两个向量的叉积（外积）。"""
        result = torch.linalg.cross(self._data, other._data)
        return Vector3D(*result.tolist())
    
    def dot(self, other: Vector3D):
        """计算两个向量的点积（内积）。"""
        return torch.dot(self._data, other._data).item()

    def __str__(self):
        """字符串表示，保留5位小数"""
        return f"({self.x:.5f}, {self.y:.5f}, {self.z:.5f})"

    def __repr__(self):
        """对象表示"""
        return f"Vector3D({self.x}, {self.y}, {self.z})"