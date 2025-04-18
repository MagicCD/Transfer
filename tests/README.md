# 测试目录

本目录包含项目的测试代码，分为以下几个子目录：

## 目录结构

- `unit/`: 单元测试，测试单个函数或类的功能
- `integration/`: 集成测试，测试多个组件之间的交互
- `fixtures/`: 测试数据和测试工具

## 运行测试

在项目根目录下运行以下命令来执行所有测试：

```bash
python -m pytest
```

运行特定的测试文件：

```bash
python -m pytest tests/unit/test_config.py
```

运行特定的测试类或测试方法：

```bash
python -m pytest tests/unit/test_config.py::TestConfigManager
python -m pytest tests/unit/test_config.py::TestConfigManager::test_load_config
```

## 编写测试

编写测试时，请遵循以下规则：

1. 测试文件名应以 `test_` 开头
2. 测试类名应以 `Test` 开头
3. 测试方法名应以 `test_` 开头
4. 使用 `pytest.fixture` 创建测试夹具
5. 使用 `assert` 语句验证测试结果

示例：

```python
import pytest
from app.core.config import ConfigManager

@pytest.fixture
def config_manager():
    return ConfigManager(env='test')

class TestConfigManager:
    def test_load_config(self, config_manager):
        assert config_manager.get('DEBUG') is True
        assert config_manager.get('LOG_LEVEL') == 'DEBUG'
```
