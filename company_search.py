"""
회사 고유번호 검색 전용 스크립트
OpenDart API를 사용하여 회사 고유번호를 다운로드하고 검색하는 기능을 제공합니다.
"""

import sys
from opendart_example import OpenDartAPI, search_company_interactive

def main():
    """회사 검색 메인 함수"""
    if len(sys.argv) > 1:
        # 명령행 인수로 회사명이 제공된 경우
        company_name = ' '.join(sys.argv[1:])
        search_single_company(company_name)
    else:
        # 대화형 검색 모드
        search_company_interactive()

def search_single_company(company_name: str):
    """단일 회사 검색"""
    try:
        api = OpenDartAPI()
        
        print(f"'{company_name}' 검색 중...")
        
        # 회사 고유번호 데이터 로드
        corp_df = api.get_or_download_corp_codes()
        if corp_df is None:
            print("회사 고유번호 데이터를 가져올 수 없습니다.")
            return
        
        # 회사 검색
        search_result = api.search_company(company_name, corp_df)
        
        if search_result is not None and len(search_result) > 0:
            print(f"\n'{company_name}' 검색 결과 ({len(search_result)}개):")
            print("=" * 80)
            print(f"{'번호':<4} {'회사명':<30} {'고유번호':<10} {'종목코드':<8} {'최종변경일'}")
            print("=" * 80)
            
            for idx, (_, company) in enumerate(search_result.iterrows(), 1):
                stock_code = company['stock_code'] if company['stock_code'] else 'N/A'
                print(f"{idx:<4} {company['corp_name']:<30} {company['corp_code']:<10} {stock_code:<8} {company['modify_date']}")
        else:
            print(f"'{company_name}'와 일치하는 회사를 찾을 수 없습니다.")
            
            # 유사한 회사명 제안
            similar_companies = corp_df[corp_df['corp_name'].str.contains(company_name[:2], na=False, case=False)].head(5)
            if len(similar_companies) > 0:
                print(f"\n유사한 회사명 제안:")
                for _, company in similar_companies.iterrows():
                    print(f"  - {company['corp_name']}")
    
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
