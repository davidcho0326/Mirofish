"""
Fashion Ontology Service
패션 도메인 온톨로지 생성 — 템플릿 모드(Quick) / LLM 모드(Full)
"""

import json
import os
from typing import Optional

from core.ontology_generator import OntologyGenerator
from core.utils.llm_client import LLMClient

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../../templates')


class FashionOntologyService:
    """패션 도메인 온톨로지 생성 서비스"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self._llm_client = llm_client
        self._template = self._load_template()

    def _load_template(self) -> dict:
        path = os.path.join(_TEMPLATES_DIR, 'fashion_entities.json')
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    def get_ontology(self, seed_text: str = "", simulation_requirement: str = "",
                     use_template: bool = True) -> dict:
        """
        온톨로지 생성.
        - use_template=True (Quick Mode): 템플릿 기반, 즉시 반환
        - use_template=False (Full Mode): LLM으로 캠페인 맞춤 온톨로지 생성
        """
        if use_template:
            return self._template_to_ontology()
        else:
            return self._generate_with_llm(seed_text, simulation_requirement)

    def _template_to_ontology(self) -> dict:
        """templates/fashion_entities.json → Zep 온톨로지 포맷 변환"""
        entity_types = []
        for et in self._template.get('entity_types', []):
            attributes = []
            for attr in et.get('attributes', []):
                if isinstance(attr, str):
                    attributes.append({
                        "name": attr,
                        "type": "text",
                        "description": attr,
                    })
                elif isinstance(attr, dict):
                    attributes.append(attr)

            entity_types.append({
                "name": et['name'],
                "description": et.get('description', ''),
                "attributes": attributes,
                "examples": et.get('examples', []),
            })

        # Zep requires exactly 10 entity types (8 specific + 2 fallback)
        existing_names = {et['name'].lower() for et in entity_types}
        if 'person' not in existing_names:
            entity_types.append({
                "name": "Person",
                "description": "기타 개인",
                "attributes": [{"name": "full_name", "type": "text", "description": "이름"}],
                "examples": [],
            })
        if 'organization' not in existing_names:
            entity_types.append({
                "name": "Organization",
                "description": "기타 조직/기관",
                "attributes": [{"name": "org_name", "type": "text", "description": "조직명"}],
                "examples": [],
            })

        # Limit to 10 entity types (Zep constraint)
        entity_types = entity_types[:10]

        edge_types = []
        for rt in self._template.get('relationship_types', []):
            edge_types.append({
                "name": rt['name'].upper(),
                "description": rt.get('description', ''),
                "source_targets": [],
                "attributes": [],
            })

        return {
            "entity_types": entity_types,
            "edge_types": edge_types,
            "analysis_summary": "패션 도메인 템플릿 기반 온톨로지 (Quick Mode)",
        }

    def _generate_with_llm(self, seed_text: str, simulation_requirement: str) -> dict:
        """LLM으로 캠페인 맞춤 온톨로지 생성 (Full Mode)"""
        if not simulation_requirement:
            simulation_requirement = (
                "한국 패션 시장에서의 캠페인 사전 테스트. "
                "소비자, 인플루언서, 경쟁사, 미디어 등의 반응을 시뮬레이션하여 "
                "캠페인 성공 가능성을 예측한다."
            )

        generator = OntologyGenerator(llm_client=self._llm_client)
        return generator.generate(
            document_texts=[seed_text],
            simulation_requirement=simulation_requirement,
            additional_context="패션/의류 브랜드 마케팅 캠페인 시뮬레이션 맥락에서 온톨로지를 생성하세요.",
        )
