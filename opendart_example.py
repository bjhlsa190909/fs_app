"""
OpenDart API를 사용하여 재무제표 데이터를 가져오는 예제
.env 파일을 사용하여 API 키를 안전하게 관리합니다.
"""

import os
import requests
from dotenv import load_dotenv
import json
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from io import BytesIO
import pandas as pd

# .env 파일 로드
load_dotenv()

class OpenDartAPI:
    def __init__(self):
        """OpenDart API 클래스 초기화"""
        self.api_key = os.getenv('OPENDART_API_KEY')
        if not self.api_key:
            raise ValueError("OPENDART_API_KEY가 .env 파일에 설정되지 않았습니다.")
        
        self.base_url = "https://opendart.fss.or.kr/api"
    
    def get_corp_code(self, corp_name: str) -> Optional[str]:
        """기업명으로 고유번호 조회"""
        url = f"{self.base_url}/company.json"
        params = {
            'crtfc_key': self.api_key,
            'corp_name': corp_name
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == '000':
                return data['corp_code']
            else:
                print(f"API 오류: {data['message']}")
                return None
                
        except requests.RequestException as e:
            print(f"요청 오류: {e}")
            return None
    
    def get_financial_statement(self, corp_code: str, bsns_year: str, reprt_code: str = '11011') -> Optional[Dict[str, Any]]:
        """재무제표 조회
        
        Args:
            corp_code: 고유번호
            bsns_year: 사업연도 (YYYY)
            reprt_code: 보고서 코드 (11011: 사업보고서, 11012: 반기보고서, 11013: 1분기보고서, 11014: 3분기보고서)
        """
        url = f"{self.base_url}/fnlttSinglAcnt.json"
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code,
            'bsns_year': bsns_year,
            'reprt_code': reprt_code,
            'fs_div': 'CFS'  # CFS: 연결재무제표, OFS: 별도재무제표
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == '000':
                return data['list']
            else:
                print(f"API 오류: {data['message']}")
                return None
                
        except requests.RequestException as e:
            print(f"요청 오류: {e}")
            return None
    
    def get_company_overview(self, corp_code: str) -> Optional[Dict[str, Any]]:
        """기업개요 조회"""
        url = f"{self.base_url}/company.json"
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == '000':
                return data
            else:
                print(f"API 오류: {data['message']}")
                return None
                
        except requests.RequestException as e:
            print(f"요청 오류: {e}")
            return None
    
    def download_corp_codes(self, save_path: str = "corp_codes.xml") -> Optional[str]:
        """
        회사 고유번호 다운로드
        
        Args:
            save_path: XML 파일을 저장할 경로
            
        Returns:
            성공시 저장된 파일 경로, 실패시 None
        """
        url = "https://opendart.fss.or.kr/api/corpCode.xml"
        params = {
            'crtfc_key': self.api_key
        }
        
        try:
            print("회사 고유번호 데이터를 다운로드 중...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # ZIP 파일 처리
            with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
                # ZIP 파일 내의 첫 번째 파일을 추출 (보통 CORPCODE.xml)
                file_names = zip_file.namelist()
                if not file_names:
                    print("ZIP 파일이 비어있습니다.")
                    return None
                
                # XML 파일 추출
                xml_content = zip_file.read(file_names[0])
                
                # 파일 저장
                with open(save_path, 'wb') as f:
                    f.write(xml_content)
                
                print(f"회사 고유번호 데이터가 {save_path}에 저장되었습니다.")
                return save_path
                
        except zipfile.BadZipFile:
            print("다운로드된 파일이 올바른 ZIP 형식이 아닙니다.")
            return None
        except requests.RequestException as e:
            print(f"다운로드 오류: {e}")
            return None
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return None
    
    def parse_corp_codes(self, xml_path: str = "corp_codes.xml") -> Optional[pd.DataFrame]:
        """
        다운로드된 XML 파일에서 회사 정보를 파싱
        
        Args:
            xml_path: 파싱할 XML 파일 경로
            
        Returns:
            회사 정보가 담긴 DataFrame, 실패시 None
        """
        try:
            print("회사 고유번호 데이터를 파싱 중...")
            
            # XML 파일 파싱
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            companies = []
            for company in root.findall('list'):
                corp_data = {
                    'corp_code': company.find('corp_code').text if company.find('corp_code') is not None else '',
                    'corp_name': company.find('corp_name').text if company.find('corp_name') is not None else '',
                    'corp_eng_name': company.find('corp_eng_name').text if company.find('corp_eng_name') is not None else '',
                    'stock_code': company.find('stock_code').text if company.find('stock_code') is not None else '',
                    'modify_date': company.find('modify_date').text if company.find('modify_date') is not None else ''
                }
                companies.append(corp_data)
            
            df = pd.DataFrame(companies)
            print(f"총 {len(df)}개 회사의 정보를 파싱했습니다.")
            return df
            
        except ET.ParseError as e:
            print(f"XML 파싱 오류: {e}")
            return None
        except FileNotFoundError:
            print(f"파일을 찾을 수 없습니다: {xml_path}")
            return None
        except Exception as e:
            print(f"파싱 중 오류 발생: {e}")
            return None
    
    def search_company(self, company_name: str, df: pd.DataFrame = None) -> Optional[pd.DataFrame]:
        """
        회사명으로 회사 정보 검색
        
        Args:
            company_name: 검색할 회사명
            df: 회사 정보 DataFrame (None이면 XML 파일에서 로드)
            
        Returns:
            검색 결과 DataFrame, 실패시 None
        """
        if df is None:
            # XML 파일에서 데이터 로드
            if not os.path.exists("corp_codes.xml"):
                print("회사 고유번호 파일이 없습니다. 먼저 다운로드해주세요.")
                return None
            df = self.parse_corp_codes()
            if df is None:
                return None
        
        # 회사명으로 검색 (부분 일치)
        result = df[df['corp_name'].str.contains(company_name, na=False, case=False)]
        
        if len(result) == 0:
            print(f"'{company_name}'와 일치하는 회사를 찾을 수 없습니다.")
            return None
        
        print(f"'{company_name}'로 검색한 결과: {len(result)}개 회사")
        return result
    
    def get_or_download_corp_codes(self) -> Optional[pd.DataFrame]:
        """
        회사 고유번호 데이터를 가져오거나 다운로드
        로컬에 파일이 있으면 사용하고, 없으면 다운로드
        """
        xml_path = "corp_codes.xml"
        
        if os.path.exists(xml_path):
            print("기존 회사 고유번호 파일을 사용합니다.")
            return self.parse_corp_codes(xml_path)
        else:
            print("회사 고유번호 파일이 없습니다. 다운로드를 시작합니다.")
            downloaded_path = self.download_corp_codes(xml_path)
            if downloaded_path:
                return self.parse_corp_codes(downloaded_path)
            return None
    
    def save_corp_codes_to_json(self, json_path: str = "corp_codes.json", df: pd.DataFrame = None) -> Optional[str]:
        """
        회사 고유번호 데이터를 JSON 형태로 저장
        
        Args:
            json_path: JSON 파일을 저장할 경로
            df: 회사 정보 DataFrame (None이면 자동 로드)
            
        Returns:
            성공시 저장된 파일 경로, 실패시 None
        """
        try:
            if df is None:
                df = self.get_or_download_corp_codes()
                if df is None:
                    print("회사 고유번호 데이터를 가져올 수 없습니다.")
                    return None
            
            print(f"회사 고유번호 데이터를 JSON 형태로 저장 중... ({len(df)}개 회사)")
            
            # DataFrame을 JSON으로 변환
            corp_data = {
                "metadata": {
                    "total_count": len(df),
                    "download_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "OpenDart API"
                },
                "companies": df.to_dict('records')
            }
            
            # JSON 파일로 저장
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(corp_data, f, ensure_ascii=False, indent=2)
            
            print(f"회사 고유번호 데이터가 {json_path}에 JSON 형태로 저장되었습니다.")
            return json_path
            
        except Exception as e:
            print(f"JSON 저장 중 오류 발생: {e}")
            return None
    
    def load_corp_codes_from_json(self, json_path: str = "corp_codes.json") -> Optional[pd.DataFrame]:
        """
        JSON 파일에서 회사 고유번호 데이터 로드
        
        Args:
            json_path: 로드할 JSON 파일 경로
            
        Returns:
            회사 정보 DataFrame, 실패시 None
        """
        try:
            if not os.path.exists(json_path):
                print(f"JSON 파일이 존재하지 않습니다: {json_path}")
                return None
            
            print(f"JSON 파일에서 회사 고유번호 데이터를 로드 중...")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                corp_data = json.load(f)
            
            df = pd.DataFrame(corp_data['companies'])
            
            print(f"총 {len(df)}개 회사 정보를 JSON에서 로드했습니다.")
            print(f"다운로드 일시: {corp_data['metadata']['download_date']}")
            
            return df
            
        except Exception as e:
            print(f"JSON 로드 중 오류 발생: {e}")
            return None

def main():
    """메인 함수 - 사용 예제"""
    try:
        # OpenDart API 인스턴스 생성
        api = OpenDartAPI()
        
        print("=== OpenDart API 사용 예제 ===")
        print("1. 회사 고유번호 다운로드 및 검색")
        print("2. 재무제표 조회")
        print()
        
        # 1. 회사 고유번호 데이터 다운로드 또는 로드
        print("📋 회사 고유번호 데이터 준비 중...")
        corp_df = api.get_or_download_corp_codes()
        if corp_df is None:
            print("회사 고유번호 데이터를 가져올 수 없습니다.")
            return
        
        print(f"총 {len(corp_df)}개 회사 정보를 로드했습니다.")
        print()
        
        # 2. 회사 검색 예제
        search_companies = ["삼성전자", "LG전자", "현대자동차"]
        
        for company_name in search_companies:
            print(f"🔍 '{company_name}' 검색 결과:")
            search_result = api.search_company(company_name, corp_df)
            
            if search_result is not None and len(search_result) > 0:
                # 가장 정확한 매치 찾기 (완전 일치 우선)
                exact_match = search_result[search_result['corp_name'] == company_name]
                if len(exact_match) > 0:
                    company_info = exact_match.iloc[0]
                else:
                    company_info = search_result.iloc[0]  # 첫 번째 결과 사용
                
                print(f"  회사명: {company_info['corp_name']}")
                print(f"  고유번호: {company_info['corp_code']}")
                print(f"  종목코드: {company_info['stock_code'] if company_info['stock_code'] else 'N/A'}")
                print(f"  최종변경일: {company_info['modify_date']}")
                
                # 3. 재무제표 조회 (첫 번째 회사만)
                if company_name == search_companies[0]:
                    print(f"\n📊 {company_info['corp_name']}의 2023년 재무제표 조회:")
                    print("-" * 60)
                    
                    financial_data = api.get_financial_statement(company_info['corp_code'], "2023")
                    if financial_data:
                        # 주요 계정과목 출력
                        key_accounts = ['매출액', '영업이익', '당기순이익', '총자산', '총부채', '자본총계']
                        
                        for item in financial_data:
                            if item['account_nm'] in key_accounts:
                                amount = item['thstrm_amount'] if item['thstrm_amount'] != '-' else '0'
                                try:
                                    # 숫자 형식 변환 시도
                                    if amount.replace(',', '').isdigit():
                                        formatted_amount = f"{int(amount.replace(',', '')):,}"
                                    else:
                                        formatted_amount = amount
                                    print(f"  {item['account_nm']}: {formatted_amount:>20} 원")
                                except:
                                    print(f"  {item['account_nm']}: {amount:>20} 원")
                    else:
                        print("  재무제표 데이터를 가져올 수 없습니다.")
                
            print()
        
        # 4. 상위 10개 회사 정보 출력 (종목코드가 있는 상장회사)
        print("📈 상장회사 상위 10개 목록:")
        print("-" * 80)
        listed_companies = corp_df[corp_df['stock_code'] != ''].head(10)
        
        print(f"{'회사명':<20} {'고유번호':<10} {'종목코드':<8} {'최종변경일'}")
        print("-" * 80)
        for _, company in listed_companies.iterrows():
            print(f"{company['corp_name']:<20} {company['corp_code']:<10} {company['stock_code']:<8} {company['modify_date']}")
        
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
        print("\n📝 .env 파일 설정 방법:")
        print("1. 프로젝트 루트에 .env 파일을 생성하세요")
        print("2. 다음 내용을 추가하세요:")
        print("   OPENDART_API_KEY=your_actual_api_key_here")
        print("3. OpenDart 홈페이지(https://opendart.fss.or.kr/)에서 API 키를 발급받으세요")
    
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")

def search_company_interactive():
    """대화형 회사 검색 함수"""
    try:
        api = OpenDartAPI()
        
        # 회사 고유번호 데이터 로드
        print("회사 고유번호 데이터를 로드 중...")
        corp_df = api.get_or_download_corp_codes()
        if corp_df is None:
            print("회사 고유번호 데이터를 가져올 수 없습니다.")
            return
        
        while True:
            company_name = input("\n검색할 회사명을 입력하세요 (종료: 'quit'): ").strip()
            
            if company_name.lower() == 'quit':
                print("검색을 종료합니다.")
                break
            
            if not company_name:
                print("회사명을 입력해주세요.")
                continue
            
            # 회사 검색
            search_result = api.search_company(company_name, corp_df)
            
            if search_result is not None and len(search_result) > 0:
                print(f"\n검색 결과 ({len(search_result)}개):")
                print("-" * 80)
                print(f"{'번호':<4} {'회사명':<25} {'고유번호':<10} {'종목코드':<8} {'최종변경일'}")
                print("-" * 80)
                
                for idx, (_, company) in enumerate(search_result.iterrows(), 1):
                    stock_code = company['stock_code'] if company['stock_code'] else 'N/A'
                    print(f"{idx:<4} {company['corp_name']:<25} {company['corp_code']:<10} {stock_code:<8} {company['modify_date']}")
            else:
                print(f"'{company_name}'와 일치하는 회사를 찾을 수 없습니다.")
    
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
