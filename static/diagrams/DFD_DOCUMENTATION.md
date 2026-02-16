# Data Flow Diagram (DFD) Documentation for Fintelligent System

## Overview
This document provides detailed information about the Data Flow Diagrams (DFD) for the Fintelligent Financial Management System at three levels of abstraction: Level 1 (Context Diagram), Level 2 (System Level), and Level 3 (Detailed Process Level).

---

## DFD Level 1 - Context Diagram

### External Entities
1. **User**
   - Primary external entity interacting with the system
   - Provides input data and receives outputs
   - Initiates all major processes

2. **Stock Market API (Alpha Vantage)**
   - External service providing real-time and historical stock market data
   - Used for stock analysis and clustering

### Data Stores

1. **D1: User Database**
   - Type: SQLite Database
   - Contains: User credentials (username, password_hash), user IDs
   - Used by: Authentication system, Dashboard
   - Access: Create, Read, Update

2. **D2: Tax History (user_tax_history.csv)**
   - Type: CSV File
   - Contains: Historical tax data with 80C, 80D, home loan details
   - Used by: Tax calculation, Recommendation system
   - Access: Read

3. **D3: Tax Data New (user_tax_data_new.csv)**
   - Type: CSV File
   - Contains: New tax regime data (user_id, income, timestamp)
   - Used by: Tax planning, Strategies, Recommendations
   - Access: Create, Read

4. **D4: Expenditure Data (expenditure.csv)**
   - Type: CSV File
   - Contains: User expenditure data (user_id, category, amount, date, payment_method, merchant, location)
   - Used by: Recommendation system, Analytics, Clustering
   - Access: Create, Read, Update

5. **D5: Temporary Storage (/tmp)**
   - Type: File System
   - Contains: Temporarily uploaded CSV files for processing
   - Used by: Expenditure upload processing
   - Access: Create, Read, Delete

### Processes

1. **1.0 User Authentication & Management**
   - Handles user registration, login, logout, and session management
   - Validates credentials against user database
   - Manages user sessions

2. **2.0 Tax Calculation & Planning**
   - Calculates taxes under new and old regimes
   - Computes TDS, HRA exemptions, advance tax
   - Compares tax regimes and provides recommendations
   - Stores tax calculation results

3. **3.0 Stock Analysis & Clustering**
   - Fetches stock market data from external API
   - Performs technical analysis (returns, volatility)
   - Applies K-Means clustering algorithm
   - Generates analysis reports and visualizations

4. **4.0 Financial Recommendations & Strategies**
   - Processes expenditure CSV uploads
   - Performs spending pattern clustering
   - Generates personalized financial recommendations
   - Provides tax strategy planning based on income

5. **5.0 Education & Financial Tools**
   - SIP (Systematic Investment Plan) goal calculator
   - Budget advice generator (50-30-20 rule)
   - Educational content management
   - Financial literacy resources

6. **6.0 Financial Monitoring**
   - Collects financial data from various sources
   - Generates monitoring reports
   - Tracks financial health metrics

7. **7.0 Dashboard & Statistics**
   - Aggregates data from multiple sources
   - Generates dashboard statistics
   - Provides real-time updates on financial metrics

---

## DFD Level 2 - System Level Decomposition

### Process 1.0 - User Authentication & Management (Decomposed)

1. **1.1 Register User**
   - Input: Registration data (username, password)
   - Process: Create new user account, hash password
   - Output: User created confirmation
   - Data Store: Write to D1 (User Database)

2. **1.2 Authenticate Login**
   - Input: Login credentials (username, password)
   - Process: Verify credentials against database
   - Output: Authentication status (success/failure)
   - Data Store: Read from D1 (User Database)

3. **1.3 Manage Session**
   - Input: Session request
   - Process: Create/validate user session
   - Output: Session information
   - Data Store: Read from D1 (User Database)

4. **1.4 Logout**
   - Input: Logout request
   - Process: Terminate user session
   - Output: Logout confirmation

### Process 2.0 - Tax Calculation & Planning (Decomposed)

1. **2.1 Calculate Tax (New/Old Regime)**
   - Input: Income, deductions
   - Process: Apply tax slabs, calculate tax for both regimes
   - Output: Tax amounts for both regimes
   - Data Store: Read from D2 (Tax History)

2. **2.2 Calculate TDS**
   - Input: Income, frequency (monthly/quarterly/daily)
   - Process: Calculate annual tax, convert to period-based TDS
   - Output: TDS amount

3. **2.3 Calculate HRA Exemption**
   - Input: Basic salary, HRA received, rent paid, city type
   - Process: Apply HRA exemption formula (minimum of 3 conditions)
   - Output: HRA exemption amount, taxable HRA

4. **2.4 Calculate Advance Tax**
   - Input: Income, current quarter
   - Process: Calculate advance tax schedule (15%, 45%, 75%, 100%)
   - Output: Advance tax due amount

5. **2.5 Compare Tax Regimes**
   - Input: Tax amounts from both regimes
   - Process: Compare and determine better regime
   - Output: Recommended regime, savings amount
   - Data Store: Read from D3 (Tax Data New)

6. **2.6 Store Tax Data**
   - Input: Tax calculation results
   - Process: Save tax data for future analysis
   - Output: Storage confirmation
   - Data Store: Write to D3 (Tax Data New)

### Process 3.0 - Stock Analysis & Clustering (Decomposed)

1. **3.1 Fetch Stock Data**
   - Input: Stock symbol
   - Process: Request data from Alpha Vantage API
   - Output: Historical stock price data
   - External Entity: Stock Market API

2. **3.2 Process Stock Data**
   - Input: Raw stock data from API
   - Process: Parse JSON, convert to DataFrame, rename columns
   - Output: Processed stock DataFrame

3. **3.3 Perform Clustering (K-Means)**
   - Input: Stock features (returns, volatility)
   - Process: Apply K-Means algorithm (n_clusters=3), normalize data
   - Output: Cluster labels, cluster centers

4. **3.4 Calculate Returns & Volatility**
   - Input: Stock price data
   - Process: Calculate percentage returns, rolling standard deviation
   - Output: Returns and volatility features

5. **3.5 Generate Analysis**
   - Input: Clustering results, stock metrics
   - Process: Format results, create visualization data
   - Output: Analysis reports, cluster visualization

### Process 4.0 - Financial Recommendations & Strategies (Decomposed)

1. **4.1 Upload Expenditure CSV**
   - Input: CSV file
   - Process: Validate file, save to temporary storage
   - Output: File saved confirmation
   - Data Store: Write to D5 (Temporary Storage)

2. **4.2 Process Expenditure Data**
   - Input: CSV file path
   - Process: Read CSV, validate columns, aggregate by category/date/method
   - Output: Processed expenditure data
   - Data Store: Read from D5, Write to D4 (Expenditure Data)

3. **4.3 Perform Clustering on Spending**
   - Input: Processed expenditure data
   - Process: Create pivot table, normalize, determine optimal K, apply K-Means, perform PCA
   - Output: Cluster assignments, cluster profiles, PCA coordinates
   - Data Store: Read from D4 (Expenditure Data)

4. **4.4 Generate Recommendations**
   - Input: Clustering results, spending patterns
   - Process: Analyze spending vs thresholds, compare with cluster averages
   - Output: Personalized recommendations
   - Data Store: Read from D4 (Expenditure Data)

5. **4.5 Calculate Analytics**
   - Input: Expenditure data
   - Process: Calculate totals by category, time series, payment methods, merchants, locations
   - Output: Analytics dashboard data

6. **4.6 Tax Strategy Planning**
   - Input: Income, tax history
   - Process: Generate income-based recommendations, regime comparison
   - Output: Tax strategy plan
   - Data Store: Read from D3 (Tax Data New), D2 (Tax History)

### Process 5.0 - Education & Financial Tools (Decomposed)

1. **5.1 SIP Goal Calculator**
   - Input: Target amount, years, annual rate
   - Process: Calculate monthly interest rate, apply SIP future value formula
   - Output: Monthly SIP amount required

2. **5.2 Budget Advice Generator**
   - Input: Monthly income
   - Process: Apply 50-30-20 rule (Needs 50%, Wants 30%, Savings 20%)
   - Output: Budget allocation breakdown

3. **5.3 Educational Content Management**
   - Input: Content request
   - Process: Retrieve educational resources
   - Output: Educational content

### Process 6.0 - Financial Monitoring (Decomposed)

1. **6.1 Collect Financial Data**
   - Input: Monitoring request
   - Process: Gather data from various sources
   - Output: Collected financial data

2. **6.2 Generate Reports**
   - Input: Financial data
   - Process: Analyze and format data
   - Output: Monitoring reports

### Process 7.0 - Dashboard & Statistics (Decomposed)

1. **7.1 Aggregate Statistics**
   - Input: Data requests
   - Process: Collect data from multiple sources
   - Output: Aggregated statistics
   - Data Store: Read from D1, D3, D4

2. **7.2 Generate Dashboard Data**
   - Input: Aggregated statistics
   - Process: Format data for dashboard display
   - Output: Dashboard-ready data

3. **7.3 Real-time Updates**
   - Input: Dashboard data
   - Process: Provide live updates
   - Output: Real-time dashboard statistics

---

## DFD Level 3 - Detailed Process Level

### Process 2.1 - Calculate Tax (Detailed Decomposition)

1. **2.1.1 Validate Input (Income & Deductions)**
   - Validates income is positive
   - Validates deduction values
   - Error handling

2. **2.1.2 Apply Standard Deduction**
   - New Regime: ₹75,000 standard deduction
   - Old Regime: ₹25,000 basic exemption

3. **2.1.3 Calculate Tax - New Regime Slabs**
   - Slabs: 4L-8L (5%), 8L-12L (10%), 12L-16L (15%), 16L-20L (20%), 20L-24L (25%), 24L+ (30%)
   - Apply progressive tax calculation

4. **2.1.4 Apply Tax Rebates (Section 87A)**
   - New Regime: ₹60,000 rebate for income ≤ ₹12L
   - Reduce tax accordingly

5. **2.1.5 Calculate Tax - Old Regime Slabs**
   - Slabs: 2.5L-5L (5%), 5L-10L (20%), 10L+ (30%)
   - Apply progressive tax calculation

6. **2.1.6 Apply Old Regime Deductions**
   - Apply 80C, 80D deductions if provided
   - Reduce taxable income

7. **2.1.7 Compare Results**
   - Compare tax amounts from both regimes
   - Calculate savings difference
   - Determine recommended regime

8. **2.1.8 Format Output**
   - Format results with currency symbols
   - Calculate effective tax rates
   - Prepare JSON response

### Process 4.2 - Process Expenditure Data (Detailed Decomposition)

1. **4.2.1 Validate CSV Format**
   - Check file exists
   - Validate file extension
   - Check for required columns (user_id, category, amount)

2. **4.2.2 Parse CSV Columns**
   - Read CSV using pandas
   - Identify available columns
   - Handle missing columns gracefully

3. **4.2.3 Aggregate by Category**
   - Group by category and user_id
   - Sum amounts per category
   - Create category totals dictionary

4. **4.2.4 Aggregate by Date**
   - Group by date
   - Sum amounts per date
   - Create time series data

5. **4.2.5 Aggregate by Payment Method**
   - Group by payment_method (if available)
   - Sum amounts per payment method
   - Create payment method totals

6. **4.2.6 Calculate Totals & Percentages**
   - Calculate total spending
   - Calculate category percentages
   - Calculate spend vs income ratios

7. **4.2.7 Create Pivot Table**
   - Pivot: user_id (index) × category (columns) × amount (values)
   - Fill missing values with 0
   - Prepare for clustering

8. **4.2.8 Prepare Data for Clustering**
   - Normalize pivot table
   - Handle missing values
   - Prepare feature matrix

### Process 4.3 - Perform Clustering on Spending (Detailed Decomposition)

1. **4.3.1 Normalize Data (StandardScaler)**
   - Standardize features (mean=0, std=1)
   - Prepare for distance-based clustering

2. **4.3.2 Determine Optimal Clusters (K)**
   - Elbow method: test K from 2 to 6
   - Calculate inertia for each K
   - Find optimal K based on elbow point

3. **4.3.3 Apply K-Means Algorithm**
   - Initialize K-Means with chosen K
   - Fit on normalized pivot data
   - Assign cluster labels to users

4. **4.3.4 Perform PCA for Visualization**
   - Reduce dimensions to 2D using PCA
   - Transform data points and cluster centers
   - Prepare for scatter plot visualization

5. **4.3.5 Calculate Cluster Profiles**
   - Group users by cluster
   - Calculate mean spending per category per cluster
   - Create cluster profile dictionary

6. **4.3.6 Generate Elbow Curve Data**
   - Store K values and inertias
   - Prepare data for elbow curve visualization

### Process 4.4 - Generate Recommendations (Detailed Decomposition)

1. **4.4.1 Analyze Spending Patterns**
   - Read user spending data
   - Identify spending categories
   - Calculate spending ratios

2. **4.4.2 Check Category Thresholds**
   - Entertainment > 20% of total: flag high spending
   - Groceries < 10% of total: flag low essentials
   - Total spending < 50% of income: flag good savings

3. **4.4.3 Compare with Cluster Average**
   - Get user's cluster assignment
   - Compare user spending with cluster average
   - Identify deviations

4. **4.4.4 Generate Budget Suggestions**
   - Provide category-specific limits
   - Suggest reallocation strategies
   - Recommend savings targets

5. **4.4.5 Create Personalized Messages**
   - Generate context-aware recommendations
   - Use friendly, actionable language
   - Provide specific examples

6. **4.4.6 Format Recommendations**
   - Structure as list of recommendations
   - Format for display
   - Prepare JSON response

### Process 3.3 - Perform Clustering on Stock Data (Detailed Decomposition)

1. **3.3.1 Calculate Returns (Percentage Change)**
   - Calculate daily percentage returns: (Close_today - Close_yesterday) / Close_yesterday
   - Handle first value (NaN)

2. **3.3.2 Calculate Volatility (Rolling Std Dev)**
   - Calculate 20-day rolling standard deviation of returns
   - Measure price volatility

3. **3.3.3 Normalize Features (StandardScaler)**
   - Standardize returns and volatility
   - Prepare for clustering

4. **3.3.4 Apply K-Means (n_clusters=3)**
   - Initialize with 3 clusters
   - Fit on normalized features
   - Random state=42 for reproducibility

5. **3.3.5 Assign Cluster Labels**
   - Assign cluster number to each date
   - Add cluster column to DataFrame

6. **3.3.6 Prepare Clustering Results**
   - Select relevant columns (Close, Return, Volatility, Cluster)
   - Get last 30 days
   - Format as JSON for frontend

### Process 5.1 - SIP Goal Calculator (Detailed Decomposition)

1. **5.1.1 Validate Input (Target & Years)**
   - Ensure target amount > 0
   - Ensure years > 0
   - Validate annual rate (default 12%)

2. **5.1.2 Calculate Monthly Interest Rate**
   - Convert annual rate to monthly: (1 + annual_rate)^(1/12) - 1
   - Handle edge case (rate = 0)

3. **5.1.3 Apply SIP Formula (Future Value)**
   - Formula: FV = SIP × [((1+r)^n - 1) / r] × (1+r)
   - Where: r = monthly rate, n = number of months

4. **5.1.4 Calculate Monthly SIP Amount**
   - Rearrange formula: SIP = FV × r / [((1+r)^n - 1) × (1+r)]
   - Calculate required monthly investment

5. **5.1.5 Format Result**
   - Round to 2 decimal places
   - Format as JSON response

### Process 5.2 - Budget Advice Generator (Detailed Decomposition)

1. **5.2.1 Validate Income Input**
   - Ensure income > 0
   - Handle invalid inputs

2. **5.2.2 Calculate Needs (50% Rule)**
   - Needs = Income × 0.5
   - Essential expenses only

3. **5.2.3 Calculate Wants (30% Rule)**
   - Wants = Income × 0.3
   - Discretionary spending

4. **5.2.4 Calculate Savings (20% Rule)**
   - Savings = Income × 0.2
   - Investments and emergency fund

5. **5.2.5 Format Budget Allocation**
   - Round to 2 decimal places
   - Format as JSON with all three categories

---

## Data Flow Summary

### Input Flows (User → System)
- Login credentials
- Registration data
- Income and deduction data
- Stock symbols
- Expenditure CSV files
- SIP parameters
- Budget queries
- Dashboard requests

### Output Flows (System → User)
- Authentication status
- Tax calculations
- Stock analysis results
- Financial recommendations
- Budget plans
- SIP calculations
- Dashboard statistics
- Educational content

### External Data Flows
- Stock data requests (System → Stock API)
- Stock data responses (Stock API → System)

### Data Store Access Patterns
- **D1 (User Database)**: Frequent reads (authentication), occasional writes (registration)
- **D2 (Tax History)**: Read-only for historical analysis
- **D3 (Tax Data New)**: Write after calculations, read for recommendations
- **D4 (Expenditure Data)**: Write after upload, frequent reads for analytics
- **D5 (Temporary Storage)**: Write on upload, read during processing, delete after processing

---

## Notes for Diagram Generation

1. **Diagram Notation**:
   - External entities: Rectangles with rounded corners
   - Processes: Rounded rectangles with process numbers
   - Data stores: Open rectangles with "D" notation
   - Data flows: Arrows labeled with data names

2. **Color Coding** (for visual diagrams):
   - External Entities: Blue
   - Processes: Orange/Yellow
   - Data Stores: Purple
   - Critical paths: Red

3. **Level 3 Focus Areas**:
   - Most detailed breakdown shown for:
    - Tax calculation (critical business logic)
    - Expenditure processing (complex data transformation)
    - Clustering algorithms (ML/AI operations)
    - Financial calculators (user-facing tools)

4. **For Other Processes**:
   - Similar detailed decomposition can be done following the same pattern
   - Focus on processes with multiple transformation steps
   - Simple processes may not need Level 3 breakdown

---

## Additional Information

### Technology Stack Used
- **Backend**: Flask (Python)
- **Database**: SQLite (via SQLAlchemy)
- **Data Processing**: Pandas
- **Machine Learning**: scikit-learn (KMeans, PCA, StandardScaler)
- **External APIs**: Alpha Vantage (Stock data)

### Key Algorithms
- **K-Means Clustering**: For user segmentation and stock pattern analysis
- **PCA (Principal Component Analysis)**: For dimensionality reduction and visualization
- **Linear Regression**: For tax allocation recommendations (if implemented)

### File Locations
- DFD Diagrams: `/static/diagrams/dfd_level1.mmd`, `dfd_level2.mmd`, `dfd_level3.mmd`
- Can be rendered using Mermaid.js or converted to PNG/SVG using Mermaid CLI

---

*Last Updated: Based on current codebase analysis*
