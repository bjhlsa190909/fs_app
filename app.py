"""
재무제표 시각화 웹 애플리케이션 - Flask 백엔드
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from database_setup import CompanyDatabase
from opendart_example import OpenDartAPI
from ai_financial_analyzer import AIFinancialAnalyzer
import json
from typing import Dict, Any, List

app = Flask(__name__)
CORS(app)  # CORS 설정

# 전역 객체들
db = CompanyDatabase()
dart_api = OpenDartAPI()

# AI 분석기 초기화 (선택적)
try:
    ai_analyzer = AIFinancialAnalyzer()
    ai_enabled = True
    print("✅ AI 분석 기능이 활성화되었습니다.")
except Exception as e:
    ai_analyzer = None
    ai_enabled = False
    print(f"⚠️ AI 분석 기능을 사용할 수 없습니다: {e}")

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search_companies():
    """회사 검색 API"""
    query = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({'error': '검색어를 입력해주세요.'}), 400
    
    try:
        companies = db.search_company(query, limit)
        return jsonify({
            'success': True,
            'query': query,
            'count': len(companies),
            'companies': companies
        })
    
    except Exception as e:
        return jsonify({'error': f'검색 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/company/<corp_code>')
def get_company_info(corp_code):
    """회사 정보 조회 API"""
    try:
        company = db.get_company_by_code(corp_code)
        if not company:
            return jsonify({'error': '회사를 찾을 수 없습니다.'}), 404
        
        return jsonify({
            'success': True,
            'company': company
        })
    
    except Exception as e:
        return jsonify({'error': f'회사 정보 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/financial/<corp_code>')
def get_financial_data(corp_code):
    """재무제표 데이터 조회 API"""
    year = request.args.get('year', '2023')
    report_code = request.args.get('report_code', '11011')  # 기본값: 사업보고서
    
    try:
        # 회사 정보 먼저 확인
        company = db.get_company_by_code(corp_code)
        if not company:
            return jsonify({'error': '회사를 찾을 수 없습니다.'}), 404
        
        # 재무제표 데이터 조회
        financial_data = dart_api.get_financial_statement(corp_code, year, report_code)
        
        if not financial_data:
            return jsonify({
                'error': f'{company["corp_name"]}의 {year}년 재무제표 데이터를 찾을 수 없습니다.',
                'company': company
            }), 404
        
        # 데이터 처리 및 분류
        processed_data = process_financial_data(financial_data)
        
        return jsonify({
            'success': True,
            'company': company,
            'year': year,
            'report_code': report_code,
            'financial_data': processed_data
        })
    
    except Exception as e:
        return jsonify({'error': f'재무제표 조회 중 오류가 발생했습니다: {str(e)}'}), 500

def process_financial_data(raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """재무제표 데이터를 처리하여 시각화에 적합한 형태로 변환"""
    
    # 재무제표 구분
    balance_sheet = []  # 재무상태표 (BS)
    income_statement = []  # 손익계산서 (IS)
    
    # 주요 계정과목들
    key_accounts = {
        'assets': ['자산총계', '유동자산', '비유동자산'],
        'liabilities': ['부채총계', '유동부채', '비유동부채'],
        'equity': ['자본총계', '자본금', '이익잉여금'],
        'revenue': ['매출액'],
        'profit': ['영업이익', '당기순이익', '법인세차감전 순이익']
    }
    
    # 데이터 분류 및 처리
    for item in raw_data:
        # 숫자 형태로 변환
        try:
            current_amount = int(item.get('thstrm_amount', '0').replace(',', '')) if item.get('thstrm_amount', '0') != '-' else 0
            previous_amount = int(item.get('frmtrm_amount', '0').replace(',', '')) if item.get('frmtrm_amount', '0') != '-' else 0
        except (ValueError, AttributeError):
            current_amount = 0
            previous_amount = 0
        
        processed_item = {
            'account_name': item.get('account_nm', ''),
            'fs_div': item.get('fs_div', ''),  # CFS: 연결, OFS: 별도
            'fs_name': item.get('fs_nm', ''),
            'sj_div': item.get('sj_div', ''),  # BS: 재무상태표, IS: 손익계산서
            'sj_name': item.get('sj_nm', ''),
            'current_period': {
                'name': item.get('thstrm_nm', ''),
                'date': item.get('thstrm_dt', ''),
                'amount': current_amount
            },
            'previous_period': {
                'name': item.get('frmtrm_nm', ''),
                'date': item.get('frmtrm_dt', ''),
                'amount': previous_amount
            },
            'currency': item.get('currency', 'KRW'),
            'order': int(item.get('ord', 0))
        }
        
        # 재무제표 구분에 따라 분류
        if item.get('sj_div') == 'BS':
            balance_sheet.append(processed_item)
        elif item.get('sj_div') == 'IS':
            income_statement.append(processed_item)
    
    # 정렬 (ord 기준)
    balance_sheet.sort(key=lambda x: x['order'])
    income_statement.sort(key=lambda x: x['order'])
    
    # 주요 지표 추출
    key_metrics = extract_key_metrics(balance_sheet + income_statement)
    
    return {
        'balance_sheet': balance_sheet,
        'income_statement': income_statement,
        'key_metrics': key_metrics,
        'summary': {
            'total_items': len(raw_data),
            'balance_sheet_items': len(balance_sheet),
            'income_statement_items': len(income_statement)
        }
    }

def extract_key_metrics(financial_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """주요 재무 지표 추출"""
    metrics = {}
    
    # 주요 계정과목 매핑
    key_accounts = {
        '자산총계': 'total_assets',
        '부채총계': 'total_liabilities', 
        '자본총계': 'total_equity',
        '매출액': 'revenue',
        '영업이익': 'operating_profit',
        '당기순이익': 'net_income'
    }
    
    for item in financial_data:
        account_name = item['account_name']
        if account_name in key_accounts:
            key = key_accounts[account_name]
            metrics[key] = {
                'name': account_name,
                'current': item['current_period']['amount'],
                'previous': item['previous_period']['amount'],
                'change': item['current_period']['amount'] - item['previous_period']['amount'],
                'change_rate': 0
            }
            
            # 증감률 계산
            if item['previous_period']['amount'] != 0:
                metrics[key]['change_rate'] = (metrics[key]['change'] / item['previous_period']['amount']) * 100
    
    # 재무비율 계산
    ratios = {}
    if 'total_assets' in metrics and 'total_liabilities' in metrics:
        if metrics['total_assets']['current'] != 0:
            ratios['debt_ratio'] = (metrics['total_liabilities']['current'] / metrics['total_assets']['current']) * 100
    
    if 'revenue' in metrics and 'operating_profit' in metrics:
        if metrics['revenue']['current'] != 0:
            ratios['operating_margin'] = (metrics['operating_profit']['current'] / metrics['revenue']['current']) * 100
    
    if 'revenue' in metrics and 'net_income' in metrics:
        if metrics['revenue']['current'] != 0:
            ratios['net_margin'] = (metrics['net_income']['current'] / metrics['revenue']['current']) * 100
    
    metrics['ratios'] = ratios
    
    return metrics

@app.route('/api/stats')
def get_database_stats():
    """데이터베이스 통계 API"""
    try:
        stats = db.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({'error': f'통계 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/test/<corp_code>')
def test_financial_data(corp_code):
    """재무제표 데이터 테스트 API"""
    year = request.args.get('year', '2023')
    
    try:
        # 회사 정보 확인
        company = db.get_company_by_code(corp_code)
        if not company:
            return jsonify({'error': '회사를 찾을 수 없습니다.'}), 404
        
        # 원시 재무제표 데이터 조회
        raw_data = dart_api.get_financial_statement(corp_code, year, '11011')
        
        return jsonify({
            'success': True,
            'company': company,
            'raw_data_count': len(raw_data) if raw_data else 0,
            'raw_data_sample': raw_data[:3] if raw_data else [],
            'year': year
        })
    
    except Exception as e:
        return jsonify({'error': f'테스트 중 오류: {str(e)}'}), 500

@app.route('/api/ai-analysis/<corp_code>')
def get_ai_analysis(corp_code):
    """AI 재무분석 API"""
    year = request.args.get('year', '2024')
    
    if not ai_enabled:
        return jsonify({
            'error': 'AI 분석 기능이 비활성화되어 있습니다. Gemini API 키를 설정해주세요.',
            'ai_enabled': False
        }), 503
    
    try:
        # 회사 정보 확인
        company = db.get_company_by_code(corp_code)
        if not company:
            return jsonify({'error': '회사를 찾을 수 없습니다.'}), 404
        
        # 재무제표 데이터 조회
        financial_data = dart_api.get_financial_statement(corp_code, year, '11011')
        
        if not financial_data:
            return jsonify({
                'error': f'{company["corp_name"]}의 {year}년 재무제표 데이터를 찾을 수 없습니다.',
                'company': company
            }), 404
        
        # 데이터 처리
        processed_data = process_financial_data(financial_data)
        
        # AI 분석 실행
        analysis_result = ai_analyzer.analyze_financial_data(company, processed_data, year)
        
        return jsonify(analysis_result)
    
    except Exception as e:
        return jsonify({'error': f'AI 분석 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/ai-status')
def get_ai_status():
    """AI 기능 상태 확인 API"""
    return jsonify({
        'ai_enabled': ai_enabled,
        'gemini_configured': ai_analyzer is not None,
        'message': 'AI 분석 기능이 사용 가능합니다.' if ai_enabled else 'Gemini API 키를 설정해주세요.'
    })

if __name__ == '__main__':
    # 템플릿 폴더가 없으면 생성
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 정적 파일 폴더가 없으면 생성
    if not os.path.exists('static'):
        os.makedirs('static')
        os.makedirs('static/css')
        os.makedirs('static/js')
    
    print("🚀 재무제표 시각화 웹 애플리케이션 시작")
    
    # 환경에 따른 설정
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    if not debug:
        print(f"   프로덕션 모드로 실행 중 (포트: {port})")
    else:
        print("   URL: http://localhost:5000")
        print("   데이터베이스: companies.db")
        try:
            print("   회사 수:", db.get_stats()['total_companies'])
        except Exception as e:
            print(f"   데이터베이스 연결 오류: {e}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
