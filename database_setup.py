"""
회사 고유번호 JSON 데이터를 SQLite 데이터베이스로 변환
"""

import sqlite3
import json
import os
from typing import Optional

class CompanyDatabase:
    def __init__(self, db_path: str = "companies.db"):
        """데이터베이스 초기화"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 회사 정보 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                corp_code TEXT NOT NULL UNIQUE,
                corp_name TEXT NOT NULL,
                corp_eng_name TEXT,
                stock_code TEXT,
                modify_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 인덱스 생성 (검색 성능 향상)
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_corp_name ON companies(corp_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_corp_code ON companies(corp_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_code ON companies(stock_code)')
        
        conn.commit()
        conn.close()
        print("데이터베이스 테이블이 생성되었습니다.")
    
    def load_from_json(self, json_path: str = "corp_codes.json") -> bool:
        """JSON 파일에서 데이터를 로드하여 데이터베이스에 저장"""
        if not os.path.exists(json_path):
            print(f"JSON 파일이 존재하지 않습니다: {json_path}")
            return False
        
        try:
            print(f"JSON 파일에서 데이터를 로드 중: {json_path}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            companies = data['companies']
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 기존 데이터 삭제 (새로 로드)
            cursor.execute('DELETE FROM companies')
            
            # 배치 삽입
            insert_query = '''
                INSERT INTO companies (corp_code, corp_name, corp_eng_name, stock_code, modify_date)
                VALUES (?, ?, ?, ?, ?)
            '''
            
            batch_data = []
            for company in companies:
                batch_data.append((
                    company.get('corp_code', ''),
                    company.get('corp_name', ''),
                    company.get('corp_eng_name', ''),
                    company.get('stock_code', '').strip() if company.get('stock_code', '').strip() else None,
                    company.get('modify_date', '')
                ))
            
            cursor.executemany(insert_query, batch_data)
            conn.commit()
            
            # 통계 정보
            cursor.execute('SELECT COUNT(*) FROM companies')
            total_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM companies WHERE stock_code IS NOT NULL AND stock_code != ""')
            listed_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"✅ 데이터베이스 로드 완료!")
            print(f"   총 회사 수: {total_count:,}개")
            print(f"   상장 회사 수: {listed_count:,}개")
            print(f"   비상장 회사 수: {total_count - listed_count:,}개")
            
            return True
            
        except Exception as e:
            print(f"❌ 데이터베이스 로드 중 오류: {e}")
            return False
    
    def search_company(self, query: str, limit: int = 20) -> list:
        """회사명으로 검색"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 부분 일치 검색 (대소문자 구분 없음)
        search_query = '''
            SELECT corp_code, corp_name, corp_eng_name, stock_code, modify_date
            FROM companies
            WHERE corp_name LIKE ? OR corp_eng_name LIKE ?
            ORDER BY 
                CASE 
                    WHEN corp_name = ? THEN 1  -- 완전 일치 우선
                    WHEN corp_name LIKE ? THEN 2  -- 시작 부분 일치
                    ELSE 3  -- 부분 일치
                END,
                corp_name
            LIMIT ?
        '''
        
        search_term = f"%{query}%"
        start_term = f"{query}%"
        
        cursor.execute(search_query, (search_term, search_term, query, start_term, limit))
        results = cursor.fetchall()
        
        conn.close()
        
        # 딕셔너리 형태로 변환
        companies = []
        for row in results:
            companies.append({
                'corp_code': row[0],
                'corp_name': row[1],
                'corp_eng_name': row[2],
                'stock_code': row[3],
                'modify_date': row[4]
            })
        
        return companies
    
    def get_company_by_code(self, corp_code: str) -> Optional[dict]:
        """고유번호로 회사 정보 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT corp_code, corp_name, corp_eng_name, stock_code, modify_date
            FROM companies
            WHERE corp_code = ?
        ''', (corp_code,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'corp_code': result[0],
                'corp_name': result[1],
                'corp_eng_name': result[2],
                'stock_code': result[3],
                'modify_date': result[4]
            }
        return None
    
    def get_stats(self) -> dict:
        """데이터베이스 통계 정보"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM companies')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM companies WHERE stock_code IS NOT NULL AND stock_code != ""')
        listed = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_companies': total,
            'listed_companies': listed,
            'unlisted_companies': total - listed
        }

def main():
    """메인 함수"""
    print("=== 회사 데이터베이스 설정 ===")
    print()
    
    # 데이터베이스 생성
    db = CompanyDatabase()
    
    # JSON 파일에서 데이터 로드
    success = db.load_from_json()
    
    if success:
        # 통계 정보 출력
        stats = db.get_stats()
        print()
        print("📊 데이터베이스 통계:")
        print(f"   총 회사 수: {stats['total_companies']:,}")
        print(f"   상장 회사 수: {stats['listed_companies']:,}")
        print(f"   비상장 회사 수: {stats['unlisted_companies']:,}")
        
        # 검색 테스트
        print()
        print("🔍 검색 테스트:")
        test_queries = ["삼성", "LG", "현대"]
        
        for query in test_queries:
            results = db.search_company(query, 3)
            print(f"   '{query}' 검색 결과: {len(results)}개")
            for company in results[:2]:  # 상위 2개만 출력
                stock_info = f"({company['stock_code']})" if company['stock_code'] else "(비상장)"
                print(f"     - {company['corp_name']} {stock_info}")
        
        print()
        print("✅ 데이터베이스 설정 완료!")
        print("이제 웹 애플리케이션에서 빠른 검색이 가능합니다.")
    
    else:
        print("❌ 데이터베이스 설정 실패")

if __name__ == "__main__":
    main()
