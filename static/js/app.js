// 재무제표 시각화 웹앱 JavaScript

class FinancialApp {
    constructor() {
        this.selectedCompany = null;
        this.currentYear = '2024';
        this.charts = {};
        this.aiEnabled = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDatabaseStats();
        this.checkAIStatus();
    }

    setupEventListeners() {
        // 검색 버튼 클릭
        document.getElementById('search-btn').addEventListener('click', () => {
            this.searchCompanies();
        });

        // 엔터키로 검색
        document.getElementById('company-search').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchCompanies();
            }
        });

        // 연도 선택 변경
        document.getElementById('year-select').addEventListener('change', (e) => {
            this.currentYear = e.target.value;
            if (this.selectedCompany) {
                this.loadFinancialData(this.selectedCompany.corp_code);
            }
        });

        // AI 분석 버튼 클릭
        document.getElementById('ai-analyze-btn').addEventListener('click', () => {
            if (this.selectedCompany) {
                this.runAIAnalysis(this.selectedCompany.corp_code);
            }
        });
    }

    async loadDatabaseStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('company-count').textContent = 
                    data.stats.total_companies.toLocaleString();
            }
        } catch (error) {
            console.error('통계 로드 오류:', error);
        }
    }

    async searchCompanies() {
        const query = document.getElementById('company-search').value.trim();
        
        if (!query) {
            this.showAlert('검색어를 입력해주세요.', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=10`);
            const data = await response.json();

            if (data.success) {
                this.displaySearchResults(data.companies);
            } else {
                this.showAlert(data.error || '검색 중 오류가 발생했습니다.', 'danger');
            }
        } catch (error) {
            console.error('검색 오류:', error);
            this.showAlert('검색 중 오류가 발생했습니다.', 'danger');
        }
    }

    displaySearchResults(companies) {
        const resultsContainer = document.getElementById('search-results');
        const resultsSection = document.getElementById('search-results-section');

        if (companies.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    검색 결과가 없습니다.
                </div>
            `;
        } else {
            resultsContainer.innerHTML = companies.map((company, index) => `
                <div class="search-result-item" data-company='${JSON.stringify(company)}'>
                    <div class="company-name">
                        ${company.corp_name}
                        ${company.stock_code ? 
                            `<span class="stock-code ms-2">${company.stock_code}</span>` : 
                            `<span class="unlisted ms-2">비상장</span>`
                        }
                    </div>
                    <div class="company-details">
                        고유번호: ${company.corp_code} | 
                        최종변경: ${this.formatDate(company.modify_date)}
                        ${company.corp_eng_name ? ` | ${company.corp_eng_name}` : ''}
                    </div>
                </div>
            `).join('');

            // 검색 결과 클릭 이벤트 추가
            resultsContainer.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', () => {
                    const company = JSON.parse(item.dataset.company);
                    this.selectCompany(company);
                });
            });
        }

        resultsSection.style.display = 'block';
        resultsSection.classList.add('fade-in');
    }

    selectCompany(company) {
        this.selectedCompany = company;
        
        // 선택된 항목 하이라이트
        document.querySelectorAll('.search-result-item').forEach(item => {
            item.classList.remove('selected');
        });
        event.target.closest('.search-result-item').classList.add('selected');

        // 회사 정보 표시
        this.displayCompanyInfo(company);
        
        // 재무제표 데이터 로드
        this.loadFinancialData(company.corp_code);
    }

    displayCompanyInfo(company) {
        const companyTitle = document.getElementById('company-title');
        const companyDetails = document.getElementById('company-details');
        const companyInfoSection = document.getElementById('company-info-section');

        companyTitle.innerHTML = `
            <i class="fas fa-building me-2"></i>
            ${company.corp_name}
            ${company.stock_code ? 
                `<span class="stock-code ms-2">${company.stock_code}</span>` : 
                `<span class="unlisted ms-2">비상장</span>`
            }
        `;

        companyDetails.innerHTML = `
            <div class="row">
                <div class="col-md-3">
                    <strong>고유번호:</strong><br>
                    <span class="text-muted">${company.corp_code}</span>
                </div>
                <div class="col-md-3">
                    <strong>종목코드:</strong><br>
                    <span class="text-muted">${company.stock_code || '비상장'}</span>
                </div>
                <div class="col-md-3">
                    <strong>최종변경일:</strong><br>
                    <span class="text-muted">${this.formatDate(company.modify_date)}</span>
                </div>
                <div class="col-md-3">
                    <strong>영문명:</strong><br>
                    <span class="text-muted">${company.corp_eng_name || '-'}</span>
                </div>
            </div>
        `;

        companyInfoSection.style.display = 'block';
        companyInfoSection.classList.add('fade-in');
    }

    async loadFinancialData(corpCode) {
        console.log(`재무제표 데이터 로드 시작: ${corpCode}, 연도: ${this.currentYear}`);
        this.showLoadingModal();

        try {
            const url = `/api/financial/${corpCode}?year=${this.currentYear}`;
            console.log(`API 요청 URL: ${url}`);
            
            const response = await fetch(url);
            console.log(`응답 상태: ${response.status}`);
            
            const data = await response.json();
            console.log('응답 데이터:', data);

            if (data.success) {
                console.log('재무제표 데이터 표시 시작');
                this.displayFinancialData(data.financial_data);
                console.log('재무제표 데이터 표시 완료');
            } else {
                console.error('API 오류:', data.error);
                this.showAlert(data.error || '재무제표 데이터를 가져올 수 없습니다.', 'warning');
                this.hideDataSections();
            }
        } catch (error) {
            console.error('재무제표 로드 오류:', error);
            this.showAlert('재무제표 데이터 로드 중 오류가 발생했습니다.', 'danger');
            this.hideDataSections();
        } finally {
            console.log('로딩 모달 숨김');
            this.hideLoadingModal();
        }
    }

    displayFinancialData(financialData) {
        try {
            console.log('재무제표 데이터:', financialData);
            
            // 주요 지표 표시
            console.log('주요 지표 표시 중...');
            this.displayKeyMetrics(financialData.key_metrics);
            
            // 차트 생성
            console.log('차트 생성 중...');
            this.createCharts(financialData);
            
            // 상세 테이블 생성
            console.log('상세 테이블 생성 중...');
            this.createDetailedTables(financialData);
            
            // 섹션 표시
            console.log('섹션 표시 중...');
            this.showDataSections();
            
            console.log('재무제표 데이터 표시 완료');
        } catch (error) {
            console.error('재무제표 데이터 표시 오류:', error);
            this.showAlert('데이터 표시 중 오류가 발생했습니다.', 'danger');
        }
    }

    displayKeyMetrics(keyMetrics) {
        const metrics = {
            'revenue': 'revenue',
            'operating_profit': 'operating-profit',
            'net_income': 'net-income',
            'total_assets': 'total-assets',
            'total_liabilities': 'total-liabilities',
            'total_equity': 'total-equity'
        };

        Object.entries(metrics).forEach(([key, elementPrefix]) => {
            const metric = keyMetrics[key];
            if (metric) {
                const amountElement = document.getElementById(`${elementPrefix}-amount`);
                const changeElement = document.getElementById(`${elementPrefix}-change`);

                amountElement.textContent = this.formatAmount(metric.current);
                
                const changeRate = metric.change_rate;
                const changeText = changeRate > 0 ? `+${changeRate.toFixed(1)}%` : 
                                 changeRate < 0 ? `${changeRate.toFixed(1)}%` : '0.0%';
                
                changeElement.textContent = changeText;
                changeElement.className = `text-muted change-rate ${
                    changeRate > 0 ? 'positive' : changeRate < 0 ? 'negative' : 'neutral'
                }`;
            }
        });
    }

    createCharts(financialData) {
        // 재무상태표 차트
        this.createBalanceSheetChart(financialData.balance_sheet);
        
        // 손익계산서 차트
        this.createIncomeStatementChart(financialData.income_statement);
    }

    createBalanceSheetChart(balanceSheetData) {
        const ctx = document.getElementById('balance-sheet-chart').getContext('2d');
        
        // 주요 항목만 추출
        const keyItems = ['자산총계', '부채총계', '자본총계'];
        const chartData = balanceSheetData.filter(item => 
            keyItems.includes(item.account_name) && item.fs_div === 'CFS'
        );

        if (this.charts.balanceSheet) {
            this.charts.balanceSheet.destroy();
        }

        this.charts.balanceSheet = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.map(item => item.account_name),
                datasets: [{
                    label: '당기',
                    data: chartData.map(item => item.current_period.amount / 1000000000000), // 조 단위
                    backgroundColor: 'rgba(13, 110, 253, 0.6)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    borderWidth: 1
                }, {
                    label: '전기',
                    data: chartData.map(item => item.previous_period.amount / 1000000000000), // 조 단위
                    backgroundColor: 'rgba(108, 117, 125, 0.6)',
                    borderColor: 'rgba(108, 117, 125, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '금액 (조원)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `${this.currentYear}년 재무상태표 (연결기준)`
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    createIncomeStatementChart(incomeStatementData) {
        const ctx = document.getElementById('income-statement-chart').getContext('2d');
        
        // 주요 항목만 추출
        const keyItems = ['매출액', '영업이익', '당기순이익'];
        const chartData = incomeStatementData.filter(item => 
            keyItems.includes(item.account_name) && item.fs_div === 'CFS'
        );

        if (this.charts.incomeStatement) {
            this.charts.incomeStatement.destroy();
        }

        this.charts.incomeStatement = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.map(item => item.account_name),
                datasets: [{
                    label: '당기',
                    data: chartData.map(item => item.current_period.amount / 1000000000000), // 조 단위
                    backgroundColor: 'rgba(25, 135, 84, 0.2)',
                    borderColor: 'rgba(25, 135, 84, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }, {
                    label: '전기',
                    data: chartData.map(item => item.previous_period.amount / 1000000000000), // 조 단위
                    backgroundColor: 'rgba(255, 193, 7, 0.2)',
                    borderColor: 'rgba(255, 193, 7, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '금액 (조원)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `${this.currentYear}년 손익계산서 (연결기준)`
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    createDetailedTables(financialData) {
        // 재무상태표 테이블
        this.createTable('balance-sheet-table', financialData.balance_sheet);
        
        // 손익계산서 테이블
        this.createTable('income-statement-table', financialData.income_statement);
    }

    createTable(tableId, data) {
        const table = document.getElementById(tableId);
        const tbody = table.querySelector('tbody');
        
        // 연결재무제표 데이터만 사용
        const cfsData = data.filter(item => item.fs_div === 'CFS');
        
        tbody.innerHTML = cfsData.map(item => {
            const change = item.current_period.amount - item.previous_period.amount;
            const changeRate = item.previous_period.amount !== 0 ? 
                (change / item.previous_period.amount) * 100 : 0;
            
            return `
                <tr>
                    <td><strong>${item.account_name}</strong></td>
                    <td class="text-end amount">${this.formatAmount(item.current_period.amount)}</td>
                    <td class="text-end amount">${this.formatAmount(item.previous_period.amount)}</td>
                    <td class="text-end amount ${change >= 0 ? 'positive' : 'negative'}">
                        ${change >= 0 ? '+' : ''}${this.formatAmount(change)}
                    </td>
                    <td class="text-end change-rate ${changeRate >= 0 ? 'positive' : 'negative'}">
                        ${changeRate >= 0 ? '+' : ''}${changeRate.toFixed(1)}%
                    </td>
                </tr>
            `;
        }).join('');
    }

    showDataSections() {
        document.getElementById('metrics-section').style.display = 'block';
        document.getElementById('charts-section').style.display = 'block';
        document.getElementById('ai-analysis-section').style.display = 'block';
        document.getElementById('detailed-data-section').style.display = 'block';
        
        // 애니메이션 추가
        ['metrics-section', 'charts-section', 'ai-analysis-section', 'detailed-data-section'].forEach(id => {
            document.getElementById(id).classList.add('fade-in');
        });
    }

    hideDataSections() {
        document.getElementById('metrics-section').style.display = 'none';
        document.getElementById('charts-section').style.display = 'none';
        document.getElementById('ai-analysis-section').style.display = 'none';
        document.getElementById('detailed-data-section').style.display = 'none';
    }

    showLoadingModal() {
        // 간단한 로딩 표시
        const loadingHtml = `
            <div id="simple-loading" style="
                position: fixed; 
                top: 0; left: 0; 
                width: 100%; height: 100%; 
                background: rgba(0,0,0,0.5); 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                z-index: 9999;
            ">
                <div style="
                    background: white; 
                    padding: 2rem; 
                    border-radius: 0.5rem; 
                    text-align: center;
                ">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="mt-3 mb-0">재무제표 데이터를 가져오는 중...</p>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', loadingHtml);
    }

    hideLoadingModal() {
        const loadingElement = document.getElementById('simple-loading');
        if (loadingElement) {
            loadingElement.remove();
        }
    }

    showAlert(message, type = 'info') {
        // 기존 알림 제거
        const existingAlert = document.querySelector('.alert-dismissible');
        if (existingAlert) {
            existingAlert.remove();
        }

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.querySelector('.container').insertBefore(alert, document.querySelector('.container').firstChild);
        
        // 5초 후 자동 제거
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    formatAmount(amount) {
        if (amount === 0) return '0';
        
        const absAmount = Math.abs(amount);
        let formattedAmount;
        
        if (absAmount >= 1000000000000) { // 조 단위
            formattedAmount = (amount / 1000000000000).toFixed(1) + '조';
        } else if (absAmount >= 100000000) { // 억 단위
            formattedAmount = (amount / 100000000).toFixed(1) + '억';
        } else if (absAmount >= 10000) { // 만 단위
            formattedAmount = (amount / 10000).toFixed(0) + '만';
        } else {
            formattedAmount = amount.toLocaleString();
        }
        
        return formattedAmount;
    }

    formatDate(dateStr) {
        if (!dateStr || dateStr.length !== 8) return dateStr;
        
        const year = dateStr.substring(0, 4);
        const month = dateStr.substring(4, 6);
        const day = dateStr.substring(6, 8);
        
        return `${year}-${month}-${day}`;
    }

    // AI 관련 함수들
    async checkAIStatus() {
        try {
            const response = await fetch('/api/ai-status');
            const data = await response.json();
            this.aiEnabled = data.ai_enabled;
            
            // AI 버튼 상태 업데이트
            const aiBtn = document.getElementById('ai-analyze-btn');
            if (!this.aiEnabled) {
                aiBtn.disabled = true;
                aiBtn.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>API 키 필요';
                aiBtn.title = 'Gemini API 키를 .env 파일에 설정해주세요';
            }
        } catch (error) {
            console.error('AI 상태 확인 오류:', error);
            this.aiEnabled = false;
        }
    }

    async runAIAnalysis(corpCode) {
        if (!this.aiEnabled) {
            this.showAlert('AI 분석 기능을 사용하려면 Gemini API 키를 설정해주세요.', 'warning');
            return;
        }

        const aiBtn = document.getElementById('ai-analyze-btn');
        const aiContent = document.getElementById('ai-analysis-content');
        
        // 로딩 상태
        aiBtn.disabled = true;
        aiBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>분석 중...';
        
        aiContent.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-3 mb-0">AI가 재무제표를 분석하고 있습니다...</p>
                <small class="text-muted">잠시만 기다려주세요 (약 10-30초)</small>
            </div>
        `;

        try {
            const response = await fetch(`/api/ai-analysis/${corpCode}?year=${this.currentYear}`);
            const data = await response.json();

            if (data.success) {
                this.displayAIAnalysis(data.analysis);
            } else {
                aiContent.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        ${data.error}
                    </div>
                `;
            }
        } catch (error) {
            console.error('AI 분석 오류:', error);
            aiContent.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-times-circle me-2"></i>
                    AI 분석 중 오류가 발생했습니다: ${error.message}
                </div>
            `;
        } finally {
            // 버튼 복원
            aiBtn.disabled = false;
            aiBtn.innerHTML = '<i class="fas fa-brain me-1"></i>AI 분석 실행';
        }
    }

    displayAIAnalysis(analysis) {
        const aiContent = document.getElementById('ai-analysis-content');
        
        if (analysis.parsing_error) {
            // 파싱 오류가 있으면 원본 텍스트 표시
            aiContent.innerHTML = `
                <div class="alert alert-info">
                    <h6><i class="fas fa-info-circle me-2"></i>AI 분석 결과</h6>
                    <div class="ai-analysis-text">${analysis.raw_response.replace(/\n/g, '<br>')}</div>
                </div>
            `;
            return;
        }

        // 구조화된 분석 결과 표시
        let html = '<div class="ai-analysis-results">';

        // 종합 점수
        if (analysis.overall_score) {
            html += `
                <div class="row mb-3">
                    <div class="col-12">
                        <div class="card bg-primary text-white">
                            <div class="card-body text-center py-2">
                                <h5 class="mb-1">종합 평가</h5>
                                <h2 class="mb-0">${analysis.overall_score}/5.0</h2>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        // 재무 건전성
        if (analysis.financial_health) {
            html += '<div class="row mb-3">';
            const health = analysis.financial_health;
            const healthItems = [
                { key: 'profitability', name: '수익성', icon: 'fas fa-chart-line', color: 'success' },
                { key: 'stability', name: '안정성', icon: 'fas fa-shield-alt', color: 'info' },
                { key: 'growth', name: '성장성', icon: 'fas fa-trending-up', color: 'warning' },
                { key: 'activity', name: '활동성', icon: 'fas fa-sync', color: 'secondary' }
            ];

            healthItems.forEach(item => {
                if (health[item.key]) {
                    html += `
                        <div class="col-md-3 col-6 mb-2">
                            <div class="card border-${item.color}">
                                <div class="card-body text-center p-2">
                                    <i class="${item.icon} text-${item.color} fs-4"></i>
                                    <div class="fw-bold">${item.name}</div>
                                    <div class="fs-5 text-${item.color}">${health[item.key].score}/5</div>
                                    <small class="text-muted">${health[item.key].comment}</small>
                                </div>
                            </div>
                        </div>
                    `;
                }
            });
            html += '</div>';
        }

        // 강점과 약점
        if (analysis.strengths || analysis.weaknesses) {
            html += '<div class="row mb-3">';
            
            if (analysis.strengths) {
                html += `
                    <div class="col-md-6">
                        <div class="card border-success">
                            <div class="card-body p-2">
                                <h6 class="text-success"><i class="fas fa-thumbs-up me-2"></i>주요 강점</h6>
                                <ul class="list-unstyled mb-0">
                                    ${analysis.strengths.map(strength => `<li><i class="fas fa-check text-success me-2"></i>${strength}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            if (analysis.weaknesses) {
                html += `
                    <div class="col-md-6">
                        <div class="card border-warning">
                            <div class="card-body p-2">
                                <h6 class="text-warning"><i class="fas fa-exclamation-triangle me-2"></i>개선점</h6>
                                <ul class="list-unstyled mb-0">
                                    ${analysis.weaknesses.map(weakness => `<li><i class="fas fa-minus text-warning me-2"></i>${weakness}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
        }

        // 투자 관점
        if (analysis.investment_perspective) {
            const invest = analysis.investment_perspective;
            html += `
                <div class="row mb-3">
                    <div class="col-12">
                        <div class="card border-primary">
                            <div class="card-body p-2">
                                <h6 class="text-primary"><i class="fas fa-chart-pie me-2"></i>투자 관점</h6>
                                <div class="row">
                                    <div class="col-md-4">
                                        <strong>투자 매력도:</strong> 
                                        <span class="badge ${invest.attractiveness === '높음' ? 'bg-success' : invest.attractiveness === '보통' ? 'bg-warning' : 'bg-secondary'}">
                                            ${invest.attractiveness}
                                        </span>
                                    </div>
                                    <div class="col-md-8">
                                        <small>
                                            ${invest.risk_factors ? `<strong>리스크:</strong> ${invest.risk_factors.join(', ')}` : ''}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        // 요약
        if (analysis.summary) {
            html += `
                <div class="alert alert-light">
                    <h6><i class="fas fa-lightbulb me-2"></i>AI 분석 요약</h6>
                    <p class="mb-0">${analysis.summary}</p>
                </div>
            `;
        }

        html += '</div>';
        
        aiContent.innerHTML = html;
    }
}

// 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    new FinancialApp();
});
