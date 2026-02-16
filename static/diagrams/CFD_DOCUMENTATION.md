# Control Flow Diagram (CFD) Documentation for Fintelligent System

## Overview
Control Flow Diagrams (CFD) show the flow of control through a program, illustrating the sequence of operations, decision points, loops, exception handling, and control transfers. This document describes the CFDs for the Fintelligent Financial Management System.

---

## CFD Diagrams

### 1. Main Application Flow (`cfd_main.mmd`)

**Purpose**: Shows the overall control flow of the Flask application from startup to request handling.

#### Key Components:
1. **Initialization Flow**
   - Initialize Flask App
   - Load Configuration
   - Initialize Database
   - Register Blueprints
   - Initialize Flask-Login
   - Create Database Tables
   - Start Flask Server (Port 5001)

2. **Request Handling Loop**
   - Wait for HTTP Request
   - Route Request based on URL
   - Process Request
   - Execute Route Handler
   - Return Response
   - Continue or Shutdown

#### Route Branches:
- **Auth Routes**: /register, /login, /logout
- **Main Routes**: / (Home), /api/dashboard-stats
- **Tax Routes**: /tax/*
- **Stock Routes**: /analyze-stock, /get_clusters
- **Recommendation Routes**: /upload, /upload_expenditure
- **Education Routes**: /education/*
- **Strategy Routes**: /strategies
- **Monitoring Routes**: /monitoring

#### Decision Points:
- **Route Request**: Determines which route handler to execute
- **Continue Server?**: Determines whether to keep server running

---

### 2. Authentication Flow (`cfd_authentication.mmd`)

**Purpose**: Shows the control flow for user authentication operations (registration, login, logout).

#### Registration Flow:
1. Check Request Method (GET/POST)
2. **GET**: Render registration form
3. **POST**: 
   - Get form data (username, password)
   - Check if user already exists
   - If exists: Flash error, redirect to register
   - If not exists:
     - Create User object
     - Hash password (set_password)
     - Add to database
     - Commit transaction
     - Login user
     - Redirect to home

#### Login Flow:
1. Check Request Method (GET/POST)
2. **GET**: Render login form
3. **POST**:
   - Get credentials (username, password)
   - Find user by username
   - Check if user found
   - If not found: Flash error, redirect to login
   - If found:
     - Check password validity
     - If invalid: Flash error, redirect to login
     - If valid: Login user, redirect to home

#### Logout Flow:
1. Check if user is logged in
2. If logged in: Logout user, redirect to home
3. If not logged in: End

#### Decision Points:
- **Request Method?**: GET or POST
- **User Exists?**: Username already in database
- **User Found?**: User lookup result
- **Password Valid?**: Password verification result
- **User Logged In?**: Session status

---

### 3. Tax Calculation Flow (`cfd_tax_calculation.mmd`)

**Purpose**: Shows the detailed control flow for tax calculation including error handling.

#### Main Flow:
1. Receive POST request to /tax/calculate
2. **TRY Block**:
   - Get JSON data
   - Extract income and deductions
   - Validate income (> 0)
   - Calculate New Regime Tax
   - Calculate Old Regime Tax
   - Calculate TDS
   - Calculate Advance Tax (Q1, Q2, Q3, Q4)
   - Compare regimes
   - Calculate savings
   - Calculate effective rates
   - Build result dictionary
   - Round values
   - Return JSON response

3. **CATCH Block**:
   - Handle exception
   - Return Error 500

#### Tax Calculation Sub-Flows:

**New Regime Calculation**:
1. Apply Standard Deduction (income - 75,000)
2. Check taxable income thresholds
3. Apply progressive tax slabs (5%, 10%, 15%, 20%, 25%, 30%)
4. Check if income <= 12L for rebate
5. Apply Section 87A rebate (tax - 60,000)
6. Return tax

**Old Regime Calculation**:
1. Apply Basic Exemption (income - 250,000)
2. Apply deductions (80C, 80D, etc.)
3. Apply progressive tax slabs (5%, 20%, 30%)
4. Check if income <= 5L for rebate
5. Apply Section 87A rebate (tax - 12,500)
6. Return tax

#### Decision Points:
- **Income > 0?**: Input validation
- **Compare Regimes**: Which regime has lower tax
- **Exception?**: Error handling

#### Error Handling:
- **Error 400**: Invalid income input
- **Error 500**: Exception during calculation

---

### 4. Stock Analysis Flow (`cfd_stock_analysis.mmd`)

**Purpose**: Shows the control flow for stock market data analysis and clustering.

#### Main Flow:
1. Receive GET request to /get_clusters
2. Get stock symbol parameter (default: INFY)
3. Build API URL
4. Make HTTP request to Alpha Vantage API
5. Check if API response is valid
6. Parse JSON response
7. Extract time series data
8. Convert to DataFrame
9. Rename columns
10. Convert index to datetime
11. Calculate returns (percentage change)
12. Calculate volatility (rolling std dev)
13. Prepare features array
14. Drop NaN values
15. Check data length (>= 3)
16. Normalize data (StandardScaler)
17. Initialize and fit K-Means (n_clusters=3)
18. Assign cluster labels
19. Select columns
20. Get last 30 records
21. Convert to dictionary
22. Build JSON response
23. Return JSON

#### Decision Points:
- **API Response Valid?**: Check for valid data structure
- **Data Points >= 3?**: Sufficient data for clustering

#### Error Handling:
- **Error 400**: API limit reached or invalid symbol
- **Error 400**: Not enough data for clustering

#### Data Processing Steps:
1. **Data Transformation**: JSON → DataFrame → Processed DataFrame
2. **Feature Engineering**: Returns, Volatility calculation
3. **Normalization**: StandardScaler fit and transform
4. **Clustering**: K-Means with 3 clusters
5. **Result Formatting**: DataFrame → Dictionary → JSON

---

### 5. Expenditure Processing Flow (`cfd_expenditure_processing.mmd`)

**Purpose**: Shows the complex control flow for expenditure CSV upload, processing, clustering, and recommendation generation.

#### Main Flow:

1. **File Upload**:
   - Check if file in request
   - Check if filename is empty
   - Save file to /tmp

2. **CSV Processing** (TRY Block):
   - Read CSV file
   - Check required columns (user_id, category, amount)
   - Aggregate by category
   - Aggregate by date
   - Check optional columns:
     - Payment method
     - Merchant
     - Location
     - User income
   - Create pivot table
   - Fill missing values

3. **Clustering Setup**:
   - Check pivot length
   - Determine optimal K (2 to 6)
   - Calculate inertias for each K
   - Find elbow point
   - Set optimal K

4. **K-Means Clustering**:
   - Fit K-Means with optimal K
   - Assign cluster labels

5. **PCA Visualization** (TRY Block):
   - Initialize PCA (n_components=2)
   - Fit PCA on pivot data
   - Transform pivot data
   - Transform cluster centers
   - Create PCA points array
   - Create center points array

6. **Cluster Analysis**:
   - Calculate cluster profiles
   - Build profile dictionary

7. **Recommendation Generation** (FOR Loop):
   - Loop through each user
   - Analyze spending patterns
   - Check thresholds:
     - Entertainment > 20% total?
     - Groceries < 10% total?
     - Total spend < 50% income?
   - Generate recommendations
   - Build recommendations dictionary

8. **Template Rendering**:
   - Render upload.html template
   - Pass data: recommendations, analytics, PCA points, cluster profiles

#### Decision Points:
- **File in Request?**: File upload validation
- **Filename Empty?**: File selection validation
- **Required Columns Present?**: CSV structure validation
- **Optional Columns Exist?**: Feature availability checks
- **Pivot Rows > 1?**: Data sufficiency for clustering
- **Entertainment > 20%?**: High spending threshold
- **Groceries < 10%?**: Low essential spending threshold
- **Total Spend < 50% Income?**: Savings threshold

#### Error Handling:
- **Error**: No file part
- **Error**: No selected file
- **Error**: Missing required columns
- **CATCH Block**: General exception handling
- **PCA CATCH**: Default coordinates on PCA failure

#### Loops:
- **Determine K Loop**: k = 2 to min(6, len(pivot))
- **FOR Each User**: Recommendation generation loop

#### Complex Operations:
1. **Data Aggregation**: Multiple groupby operations
2. **Optimal K Determination**: Elbow method with inertia calculation
3. **Dimensionality Reduction**: PCA for 2D visualization
4. **Pattern Analysis**: Multiple threshold checks
5. **Recommendation Logic**: Conditional recommendation generation

---

## Control Flow Patterns

### 1. **Sequential Flow**
Most operations follow sequential execution: Step 1 → Step 2 → Step 3

### 2. **Conditional Branching**
Decision points create branches:
- **If-Else**: Income > 0, User exists, etc.
- **Ternary**: New regime < Old regime

### 3. **Loop Structures**
- **For Loop**: User recommendation generation
- **While Loop**: Server request handling loop

### 4. **Exception Handling**
- **Try-Catch Blocks**: Tax calculation, Expenditure processing, PCA
- **Error Returns**: 400 (Bad Request), 500 (Server Error)

### 5. **Guard Clauses**
Early returns on validation failures:
- File validation
- Column validation
- Data length validation

---

## Key Decision Points Summary

| Diagram | Decision Points | Outcomes |
|---------|---------------|----------|
| Main | Route Request | Routes to 8 different handlers |
| Main | Continue Server? | Continue or Shutdown |
| Authentication | Request Method? | GET or POST |
| Authentication | User Exists? | Registration allowed/denied |
| Authentication | Password Valid? | Login success/failure |
| Tax Calculation | Income > 0? | Validation pass/fail |
| Tax Calculation | New < Old Regime? | Recommended regime |
| Tax Calculation | Exception? | Success or error response |
| Stock Analysis | API Response Valid? | Continue or return error |
| Stock Analysis | Data Points >= 3? | Proceed or return error |
| Expenditure | File in Request? | Continue or return error |
| Expenditure | Required Columns? | Continue or return error |
| Expenditure | Pivot Rows > 1? | Set K=1 or determine optimal K |
| Expenditure | Spending Thresholds | Generate different recommendations |

---

## Error Handling Patterns

### 1. **Input Validation Errors**
- Early return with error message
- Status code: 400 (Bad Request)
- Example: Invalid income, missing file

### 2. **Processing Errors**
- Try-Catch blocks
- Status code: 500 (Server Error)
- Example: Calculation exceptions, API failures

### 3. **Data Validation Errors**
- Check before processing
- Return appropriate error message
- Example: Missing columns, insufficient data

### 4. **External Service Errors**
- Check response validity
- Return error or retry
- Example: Stock API failures

---

## Control Flow Best Practices Used

1. **Early Returns**: Validation failures return immediately
2. **Exception Handling**: Try-Catch blocks protect critical operations
3. **Guard Clauses**: Input validation before processing
4. **Clear Decision Points**: Boolean checks with clear outcomes
5. **Error Propagation**: Errors bubble up appropriately
6. **Resource Cleanup**: Files handled appropriately

---

## Diagram Files Summary

| Diagram | Mermaid File | PNG File | Focus Area |
|---------|------------|---------|------------|
| Main Application | `cfd_main.mmd` | `cfd_main.png` | Overall application flow |
| Authentication | `cfd_authentication.mmd` | `cfd_authentication.png` | User auth operations |
| Tax Calculation | `cfd_tax_calculation.mmd` | `cfd_tax_calculation.png` | Tax computation logic |
| Stock Analysis | `cfd_stock_analysis.mmd` | `cfd_stock_analysis.png` | Stock data processing |
| Expenditure Processing | `cfd_expenditure_processing.mmd` | `cfd_expenditure_processing.png` | CSV processing & ML |

---

## Usage Notes

- **Viewing**: PNG files can be viewed in any image viewer
- **Editing**: Mermaid files can be edited and regenerated
- **Documentation**: Use in technical documentation and code reviews
- **Debugging**: Helpful for understanding control flow during debugging
- **Code Reviews**: Useful for reviewing logic and decision points

---

*Last Updated: Based on current codebase analysis*
