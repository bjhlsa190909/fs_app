"""
Google Gemini AI를 사용한 재무제표 분석 모듈
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import pandas as pd
from typing import Dict, Any, List, Optional

# .env 파일 로드
load_dotenv()

class AIFinancialAnalyzer:
    def __init__(self):
        """AI 분석기 초기화"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        
        # Gemini AI 설정
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_financial_data(self, company_info: Dict[str, Any], financial_data: Dict[str, Any], year: str) -> Dict[str, Any]:
        """
        재무제표 데이터를 AI로 분석
        
        Args:
            company_info: 회사 정보
            financial_data: 재무제표 데이터
            year: 분석 연도
            
        Returns:
            AI 분석 결과
        """
        try:
            # 분석용 프롬프트 생성
            prompt = self._create_analysis_prompt(company_info, financial_data, year)
            
            # AI 분석 실행
            response = self.model.generate_content(prompt)
            
            # 응답 파싱
            analysis_result = self._parse_ai_response(response.text)
            
            return {
                'success': True,
                'company': company_info['corp_name'],
                'year': year,
                'analysis': analysis_result,
                'generated_at': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'AI 분석 중 오류 발생: {str(e)}',
                'company': company_info.get('corp_name', '알 수 없음'),
                'year': year
            }
    
    def _create_analysis_prompt(self, company_info: Dict[str, Any], financial_data: Dict[str, Any], year: str) -> str:
        """AI 분석용 프롬프트 생성"""
        
        # 주요 재무지표 추출
        key_metrics = financial_data.get('key_metrics', {})
        
        prompt = f"""
다음은 {company_info['corp_name']}의 {year}년 재무제표 데이터입니다. 전문적인 재무분석가 관점에서 상세하게 분석해주세요.

## 회사 정보
- 회사명: {company_info['corp_name']}
- 고유번호: {company_info['corp_code']}
- 종목코드: {company_info.get('stock_code', '비상장')}
- 분석연도: {year}년

## 주요 재무지표
"""
        
        # 주요 지표 정보 추가
        metrics_info = [
            ('매출액', 'revenue'),
            ('영업이익', 'operating_profit'),
            ('당기순이익', 'net_income'),
            ('총자산', 'total_assets'),
            ('총부채', 'total_liabilities'),
            ('자본총계', 'total_equity')
        ]
        
        for metric_name, metric_key in metrics_info:
            if metric_key in key_metrics:
                metric = key_metrics[metric_key]
                current = self._format_amount(metric['current'])
                previous = self._format_amount(metric['previous'])
                change_rate = metric['change_rate']
                
                prompt += f"- {metric_name}: {current} (전년대비 {change_rate:+.1f}%, 전년: {previous})\n"
        
        # 재무비율 정보 추가
        if 'ratios' in key_metrics:
            ratios = key_metrics['ratios']
            prompt += "\n## 주요 재무비율\n"
            
            if 'debt_ratio' in ratios:
                prompt += f"- 부채비율: {ratios['debt_ratio']:.1f}%\n"
            if 'operating_margin' in ratios:
                prompt += f"- 영업이익률: {ratios['operating_margin']:.1f}%\n"
            if 'net_margin' in ratios:
                prompt += f"- 순이익률: {ratios['net_margin']:.1f}%\n"
        
        prompt += f"""

## 분석 요청사항
다음 항목들을 포함하여 전문적이고 실용적인 분석을 제공해주세요:

1. **재무 건전성 평가** (5점 만점)
   - 수익성, 안정성, 성장성, 활동성 관점에서 평가
   - 각 항목별 점수와 근거 제시

2. **주요 강점과 약점**
   - 재무적 강점 3가지
   - 개선이 필요한 약점 3가지

3. **전년 대비 변화 분석**
   - 주요 지표 변화의 원인 분석
   - 긍정적/부정적 변화 요인

4. **투자 관점 분석**
   - 투자 매력도 평가
   - 리스크 요인 식별
   - 투자 시 고려사항

5. **향후 전망 및 권고사항**
   - 단기/중기 전망
   - 경영진에게 권고할 사항

응답은 다음 JSON 형식으로 구조화해서 제공해주세요:

```json
{{
    "overall_score": 4.2,
    "financial_health": {{
        "profitability": {{ "score": 4.5, "comment": "..." }},
        "stability": {{ "score": 4.0, "comment": "..." }},
        "growth": {{ "score": 4.0, "comment": "..." }},
        "activity": {{ "score": 4.2, "comment": "..." }}
    }},
    "strengths": ["강점1", "강점2", "강점3"],
    "weaknesses": ["약점1", "약점2", "약점3"],
    "year_over_year": {{
        "positive_changes": ["긍정적 변화1", "긍정적 변화2"],
        "negative_changes": ["부정적 변화1", "부정적 변화2"],
        "analysis": "전년 대비 변화 종합 분석"
    }},
    "investment_perspective": {{
        "attractiveness": "높음/보통/낮음",
        "risk_factors": ["리스크1", "리스크2"],
        "considerations": ["고려사항1", "고려사항2"]
    }},
    "outlook_and_recommendations": {{
        "short_term_outlook": "단기 전망",
        "medium_term_outlook": "중기 전망",
        "recommendations": ["권고사항1", "권고사항2", "권고사항3"]
    }},
    "summary": "3-4줄 요약"
}}
```

분석은 객관적이고 균형잡힌 관점에서 작성해주세요.
"""
        
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """AI 응답을 파싱하여 구조화된 데이터로 변환"""
        try:
            # JSON 부분 추출
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                parsed_data = json.loads(json_str)
                
                # 원본 텍스트도 포함
                parsed_data['raw_response'] = response_text
                
                return parsed_data
            else:
                # JSON 형식이 없으면 텍스트 그대로 반환
                return {
                    'raw_response': response_text,
                    'summary': response_text[:500] + "..." if len(response_text) > 500 else response_text,
                    'parsing_error': 'JSON 형식을 찾을 수 없습니다.'
                }
                
        except json.JSONDecodeError as e:
            return {
                'raw_response': response_text,
                'summary': response_text[:500] + "..." if len(response_text) > 500 else response_text,
                'parsing_error': f'JSON 파싱 오류: {str(e)}'
            }
        except Exception as e:
            return {
                'raw_response': response_text,
                'summary': 'AI 응답 파싱 중 오류가 발생했습니다.',
                'parsing_error': str(e)
            }
    
    def _format_amount(self, amount: int) -> str:
        """금액을 읽기 쉬운 형태로 포맷"""
        if amount == 0:
            return '0원'
        
        abs_amount = abs(amount)
        
        if abs_amount >= 1000000000000:  # 조 단위
            formatted = f"{amount / 1000000000000:.1f}조원"
        elif abs_amount >= 100000000:  # 억 단위
            formatted = f"{amount / 100000000:.1f}억원"
        elif abs_amount >= 10000:  # 만 단위
            formatted = f"{amount / 10000:.0f}만원"
        else:
            formatted = f"{amount:,}원"
        
        return formatted
    
    def generate_comparison_analysis(self, companies_data: List[Dict[str, Any]], year: str) -> Dict[str, Any]:
        """
        여러 회사의 비교 분석
        
        Args:
            companies_data: 여러 회사의 재무데이터 리스트
            year: 분석 연도
            
        Returns:
            비교 분석 결과
        """
        try:
            if len(companies_data) < 2:
                return {
                    'success': False,
                    'error': '비교 분석을 위해서는 최소 2개 회사의 데이터가 필요합니다.'
                }
            
            # 비교 분석 프롬프트 생성
            prompt = self._create_comparison_prompt(companies_data, year)
            
            # AI 분석 실행
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'year': year,
                'companies': [data['company']['corp_name'] for data in companies_data],
                'comparison_analysis': response.text,
                'generated_at': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'비교 분석 중 오류 발생: {str(e)}',
                'year': year
            }
    
    def _create_comparison_prompt(self, companies_data: List[Dict[str, Any]], year: str) -> str:
        """비교 분석용 프롬프트 생성"""
        
        prompt = f"다음은 {year}년 주요 기업들의 재무제표 데이터입니다. 이들 기업을 비교 분석해주세요.\n\n"
        
        for i, data in enumerate(companies_data, 1):
            company = data['company']
            key_metrics = data['financial_data']['key_metrics']
            
            prompt += f"## {i}. {company['corp_name']}\n"
            prompt += f"- 종목코드: {company.get('stock_code', '비상장')}\n"
            
            # 주요 지표
            metrics_info = [
                ('매출액', 'revenue'),
                ('영업이익', 'operating_profit'),
                ('당기순이익', 'net_income'),
                ('총자산', 'total_assets')
            ]
            
            for metric_name, metric_key in metrics_info:
                if metric_key in key_metrics:
                    current = self._format_amount(key_metrics[metric_key]['current'])
                    change_rate = key_metrics[metric_key]['change_rate']
                    prompt += f"- {metric_name}: {current} (전년대비 {change_rate:+.1f}%)\n"
            
            prompt += "\n"
        
        prompt += """
## 비교 분석 요청사항
1. **규모별 비교**: 매출액, 자산 규모 기준 순위
2. **수익성 비교**: 영업이익률, 순이익률 비교
3. **성장성 비교**: 전년 대비 성장률 비교
4. **각 기업의 특징**: 업종별 특성과 경쟁력
5. **투자 관점**: 각 기업의 투자 매력도 순위

간결하고 명확하게 비교 분석해주세요.
"""
        
        return prompt

# 사용 예제
def test_ai_analyzer():
    """AI 분석기 테스트"""
    try:
        analyzer = AIFinancialAnalyzer()
        print("✅ AI 분석기 초기화 성공")
        
        # 테스트용 더미 데이터
        company_info = {
            'corp_name': '테스트 회사',
            'corp_code': '00000000',
            'stock_code': '000000'
        }
        
        financial_data = {
            'key_metrics': {
                'revenue': {'current': 1000000000000, 'previous': 900000000000, 'change_rate': 11.1},
                'operating_profit': {'current': 100000000000, 'previous': 80000000000, 'change_rate': 25.0}
            }
        }
        
        print("AI 분석 테스트는 실제 API 키 설정 후 가능합니다.")
        
    except ValueError as e:
        print(f"⚠️ {e}")
        print("Google AI Studio에서 API 키를 발급받아 .env 파일에 설정해주세요.")
        print("URL: https://aistudio.google.com/app/apikey")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    test_ai_analyzer()
