"""
迭代管理工具
管理多轮迭代的状态、数据持久化和报告生成
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from loguru import logger


@dataclass
class RoundState:
    """单轮迭代的状态"""
    round_num: int
    urls: List[str]
    htmls: Dict[str, str]  # {url: html}
    screenshots: Dict[str, str]  # {url: screenshot_path}
    groundtruth_jsons: Dict[str, Dict]  # {url: json}
    schema: Dict
    parser_path: str
    accuracy_per_url: Dict[str, float]  # {url: accuracy}
    overall_accuracy: float
    timestamp: str
    diff_explanation: Optional[str] = None  # 代码修改说明


class IterationManager:
    """迭代管理器"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.iteration_dir = self.output_dir / "iterations"
        self.groundtruth_dir = self.output_dir / "groundtruth"
        self.iteration_dir.mkdir(parents=True, exist_ok=True)
        self.groundtruth_dir.mkdir(parents=True, exist_ok=True)

    def save_round_state(self, round_state: RoundState) -> str:
        """
        保存单轮状态到磁盘

        Args:
            round_state: 轮次状态

        Returns:
            保存的文件路径
        """
        round_dir = self.iteration_dir / f"round_{round_state.round_num}"
        round_dir.mkdir(parents=True, exist_ok=True)

        # 保存状态JSON（不含HTML和PARSER代码，太大）
        state_data = {
            'round_num': round_state.round_num,
            'urls': round_state.urls,
            'schema': round_state.schema,
            'parser_path': round_state.parser_path,
            'accuracy_per_url': round_state.accuracy_per_url,
            'overall_accuracy': round_state.overall_accuracy,
            'timestamp': round_state.timestamp,
            'diff_explanation': round_state.diff_explanation,
        }

        state_path = round_dir / "state.json"
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2)

        logger.info(f"已保存第 {round_state.round_num} 轮状态: {state_path}")

        return str(state_path)

    def save_groundtruth_json(self, round_num: int, sample_idx: int,
                             groundtruth_json: Dict, image_path: str) -> str:
        """
        保存groundtruth JSON（每轮的视觉识别结果）

        Args:
            round_num: 轮次号
            sample_idx: 样本索引
            groundtruth_json: 图片识别的JSON
            image_path: 图片路径

        Returns:
            保存的文件路径
        """
        json_path = self.groundtruth_dir / f"round_{round_num}_sample_{sample_idx}.json"

        metadata = {
            'round_num': round_num,
            'sample_idx': sample_idx,
            'image_path': str(image_path),
            'timestamp': datetime.now().isoformat(),
            'data': groundtruth_json
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.debug(f"已保存Groundtruth JSON: {json_path}")

        return str(json_path)

    def load_previous_state(self, round_num: int) -> Optional[RoundState]:
        """
        加载上一轮状态

        Args:
            round_num: 当前轮次（会加载 round_num-1）

        Returns:
            上一轮的状态对象，如果不存在则返回None
        """
        prev_round_num = round_num - 1
        if prev_round_num < 1:
            return None

        state_path = self.iteration_dir / f"round_{prev_round_num}" / "state.json"

        if not state_path.exists():
            logger.warning(f"未找到第 {prev_round_num} 轮状态文件")
            return None

        try:
            with open(state_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

            logger.info(f"已加载第 {prev_round_num} 轮状态")
            return state_data
        except Exception as e:
            logger.error(f"加载状态失败: {str(e)}")
            return None

    def load_all_groundtruth_jsons(self, round_num: int) -> Dict[int, Dict]:
        """
        加载某一轮的所有groundtruth JSON

        Args:
            round_num: 轮次号

        Returns:
            {sample_idx: json_data}
        """
        results = {}

        for json_path in self.groundtruth_dir.glob(f"round_{round_num}_*.json"):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                sample_idx = metadata['sample_idx']
                results[sample_idx] = metadata['data']
            except Exception as e:
                logger.warning(f"加载 {json_path} 失败: {str(e)}")

        return results

    def generate_iteration_report(self) -> str:
        """
        生成迭代报告

        Returns:
            报告文本
        """
        lines = []
        lines.append("\n" + "="*70)
        lines.append("多轮迭代报告")
        lines.append("="*70)

        # 收集所有轮次的状态
        round_states = []
        for state_file in sorted(self.iteration_dir.glob("round_*/state.json")):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                round_states.append(state_data)
            except Exception as e:
                logger.warning(f"加载 {state_file} 失败: {str(e)}")

        if not round_states:
            lines.append("\n未找到任何轮次数据")
        else:
            lines.append(f"\n总轮次: {len(round_states)}")
            lines.append("\n轮次详情:")
            lines.append("-" * 70)

            for state in round_states:
                round_num = state['round_num']
                accuracy = state['overall_accuracy']
                timestamp = state['timestamp']

                lines.append(f"\n第 {round_num} 轮:")
                lines.append(f"  时间: {timestamp}")
                lines.append(f"  整体准确率: {accuracy:.1%}")
                lines.append(f"  URL数量: {len(state['urls'])}")
                lines.append(f"  字段数量: {len(state['schema'])}")

                if state['diff_explanation']:
                    lines.append(f"  代码修改: {state['diff_explanation'][:200]}...")

                # 按URL显示准确率
                if state['accuracy_per_url']:
                    lines.append("  URL准确率分布:")
                    for url, acc in state['accuracy_per_url'].items():
                        status = "✓" if acc >= 0.8 else "✗"
                        lines.append(f"    {status} {url[:50]}: {acc:.1%}")

            # 精度趋势
            accuracies = [s['overall_accuracy'] for s in round_states]
            if len(accuracies) > 1:
                trend = "↑" if accuracies[-1] > accuracies[0] else "↓" if accuracies[-1] < accuracies[0] else "→"
                lines.append(f"\n精度趋势: {accuracies[0]:.1%} → {accuracies[-1]:.1%} {trend}")

        lines.append("\n" + "="*70)

        report = "\n".join(lines)
        logger.info(report)

        return report



