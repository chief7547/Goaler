"""Utilities for loading template data from CONFIG.yaml."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class TemplateLibrary:
    """Loads quest and metric templates from the project configuration."""

    def __init__(self, config_path: str | os.PathLike[str] | None = None) -> None:
        default_path: Path = Path(os.getenv("GOALER_CONFIG_PATH", "CONFIG.yaml"))
        resolved_path = Path(config_path) if config_path is not None else default_path
        if not resolved_path.exists():
            raise FileNotFoundError(f"CONFIG file not found: {resolved_path}")
        data = yaml.safe_load(resolved_path.read_text(encoding="utf-8")) or {}
        templates_section = data.get("templates", {})
        optional_metrics = data.get("optional_metrics", {})

        self.quest_categories: List[Dict[str, Any]] = templates_section.get(
            "quest_categories", []
        )
        self.metric_categories: List[Dict[str, Any]] = optional_metrics.get(
            "metric_categories", []
        )
        self.validation_rules: Dict[str, Dict[str, Any]] = optional_metrics.get(
            "validation_rules", {}
        )

        self._quest_lookup: Dict[str, Dict[str, Any]] = {}
        for category in self.quest_categories:
            for quest in category.get("quests", []):
                title = quest.get("title")
                if title:
                    self._quest_lookup[title] = quest

        self._metric_lookup: Dict[str, Dict[str, Any]] = {}
        for category in self.metric_categories:
            for metric in category.get("examples", []):
                name = metric.get("name")
                if name:
                    self._metric_lookup[name] = metric

        self.auto_recommend_metrics: List[Dict[str, Any]] = []
        for category in self.metric_categories:
            if not category.get("auto_recommend"):
                continue
            for metric in category.get("examples", []):
                enriched = dict(metric)
                enriched["category"] = category.get("category")
                self.auto_recommend_metrics.append(enriched)

    def quest_template(self, title: str) -> Optional[Dict[str, Any]]:
        return self._quest_lookup.get(title)

    def metric_template(self, name: str) -> Optional[Dict[str, Any]]:
        return self._metric_lookup.get(name)


@lru_cache(maxsize=1)
def load_templates(config_path: str | None = None) -> TemplateLibrary:
    """Cache the template library so repeated callers share the data."""

    return TemplateLibrary(config_path=config_path)


__all__ = ["TemplateLibrary", "load_templates"]
