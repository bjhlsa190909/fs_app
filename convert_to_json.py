"""
회사 고유번호 데이터를 JSON 형태로 변환하는 스크립트
"""

import sys
from opendart_example import OpenDartAPI

def main():
    """JSON 변환 메인 함수"""
    try:
        api = OpenDartAPI()
        
        print("=== 회사 고유번호 JSON 변환 ===")
        print()
        
        # 기존 XML 데이터가 있는지 확인
        import os
        if not os.path.exists("corp_codes.xml"):
            print("❌ corp_codes.xml 파일이 없습니다.")
            print("먼저 'python opendart_example.py'를 실행하여 데이터를 다운로드하세요.")
            return
        
        # XML에서 데이터 로드
        print("📋 XML 파일에서 회사 고유번호 데이터 로드 중...")
        corp_df = api.parse_corp_codes("corp_codes.xml")
        
        if corp_df is None:
            print("❌ XML 파일 파싱에 실패했습니다.")
            return
        
        # JSON으로 저장
        json_path = api.save_corp_codes_to_json("corp_codes.json", corp_df)
        
        if json_path:
            print("✅ JSON 변환 완료!")
            print()
            
            # 파일 크기 비교
            import os
            xml_size = os.path.getsize("corp_codes.xml")
            json_size = os.path.getsize("corp_codes.json")
            
            print("📊 파일 크기 비교:")
            print(f"  XML 파일:  {xml_size:,} bytes ({xml_size/1024/1024:.1f} MB)")
            print(f"  JSON 파일: {json_size:,} bytes ({json_size/1024/1024:.1f} MB)")
            
            # 샘플 데이터 출력
            print()
            print("📄 JSON 파일 샘플 (상위 3개 회사):")
            print("-" * 80)
            
            for i in range(min(3, len(corp_df))):
                company = corp_df.iloc[i]
                print(f"{i+1}. {company['corp_name']}")
                print(f"   고유번호: {company['corp_code']}")
                print(f"   종목코드: {company['stock_code'] if company['stock_code'] else 'N/A'}")
                print(f"   최종변경일: {company['modify_date']}")
                print()
            
            print(f"💾 총 {len(corp_df):,}개 회사 정보가 JSON 형태로 저장되었습니다.")
            
        else:
            print("❌ JSON 변환에 실패했습니다.")
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
