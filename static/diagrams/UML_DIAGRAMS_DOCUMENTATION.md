# UML Diagrams Documentation for Fintelligent System

## Overview
This document describes all UML (Unified Modeling Language) diagrams for the Fintelligent Financial Management System. The system is documented using 10 different UML diagram types following standard UML 2.5 specifications.

---

## 6.6.1 Use Case Diagram (`uml_use_case.mmd`)

### Purpose
Shows the interactions between actors (users, external systems) and the system's use cases.

### Actors
1. **User** - Primary actor, performs most use cases
2. **Administrator** - Manages system statistics and reports
3. **Stock Market API** - External system providing stock data

### Use Cases

#### Authentication (UC1-UC4)
- **UC1**: Register Account
- **UC2**: Login
- **UC3**: Logout
- **UC4**: Manage Session

#### Dashboard (UC5-UC6)
- **UC5**: View Dashboard
- **UC6**: View Statistics

#### Tax Management (UC7-UC13)
- **UC7**: Calculate Tax - New Regime
- **UC8**: Calculate Tax - Old Regime
- **UC9**: Compare Tax Regimes
- **UC10**: Calculate TDS
- **UC11**: Calculate HRA Exemption
- **UC12**: Calculate Advance Tax
- **UC13**: View Tax History

#### Stock Analysis (UC14-UC16)
- **UC14**: Analyze Stock
- **UC15**: View Stock Clusters
- **UC16**: Get Stock Data from API

#### Financial Recommendations (UC17-UC21)
- **UC17**: Upload Expenditure CSV
- **UC18**: View Spending Analytics
- **UC19**: Get Financial Recommendations
- **UC20**: View Clustering Results
- **UC21**: Generate Tax Strategy

#### Education & Tools (UC22-UC24)
- **UC22**: Calculate SIP Goal
- **UC23**: Get Budget Advice
- **UC24**: View Educational Content

#### Financial Monitoring (UC25-UC26)
- **UC25**: Monitor Finances
- **UC26**: Generate Reports

### Relationships
- **Includes**: Dashboard includes View Statistics
- **Extends**: Compare Tax Regimes extends both Calculate Tax use cases
- **Uses**: Stock Analysis uses Stock Market API

---

## 6.6.2 Activity Diagram (`uml_activity.mmd`)

### Purpose
Describes the workflow and business processes in the system.

### Main Activities

#### 1. Authentication Flow
- User Login → Validate Credentials → Dashboard Access

#### 2. Tax Calculation Flow
- Enter Income & Deductions
- Calculate New Regime Tax
- Calculate Old Regime Tax
- Compare Tax Regimes
- Display Results

#### 3. Stock Analysis Flow
- Enter Stock Symbol
- Fetch Stock Data from API
- Process Stock Data
- Calculate Returns & Volatility
- Perform K-Means Clustering
- Display Analysis Results

#### 4. Expenditure Analysis Flow
- Upload Expenditure CSV
- Validate CSV Format
- Process Expenditure Data
- Aggregate by Category/Date
- Perform Spending Clustering
- Generate Recommendations
- Display Analytics & Recommendations

#### 5. SIP Calculator Flow
- Enter Target Amount & Years
- Calculate Monthly SIP
- Display SIP Amount

#### 6. Budget Advice Flow
- Enter Monthly Income
- Apply 50-30-20 Rule
- Display Budget Allocation

### Decision Points
- **CheckAuth**: Validates user credentials
- **ValidateCSV**: Validates uploaded CSV format

---

## 6.6.3 Class Diagram (`uml_class.mmd`)

### Purpose
Shows the static structure of the system, including classes, attributes, methods, and relationships.

### Main Classes

#### Core Models
- **User**: User authentication and management
  - Attributes: id, username, password_hash
  - Methods: set_password(), check_password(), get(), get_by_username()

#### Tax Calculation Classes
- **TaxCalculator**: Tax computation logic
  - Methods: calculate_new_regime_tax(), calculate_old_regime_tax(), calculate_tds(), calculate_advance_tax(), calculate_hra_exemption()
- **TaxData**: Tax data model
  - Attributes: user_id, income, new_regime_tax, old_regime_tax, calculated_at

#### Stock Analysis Classes
- **StockAnalyzer**: Stock data processing
  - Methods: fetch_stock_data(), process_stock_data(), calculate_returns(), calculate_volatility(), perform_clustering()
- **StockData**: Stock data model
  - Attributes: symbol, date, open, high, low, close, volume, return_rate, volatility, cluster

#### Recommendation Classes
- **ExpenditureProcessor**: CSV processing and aggregation
  - Methods: validate_csv(), parse_csv(), aggregate_by_category(), aggregate_by_date(), create_pivot_table()
- **ClusteringEngine**: Machine learning clustering
  - Methods: determine_optimal_k(), perform_kmeans_clustering(), perform_pca(), calculate_cluster_profiles()
- **RecommendationGenerator**: Recommendation generation
  - Methods: analyze_spending_patterns(), check_category_thresholds(), compare_with_cluster_average(), generate_budget_suggestions()

#### Financial Tools Classes
- **SIPCalculator**: SIP calculations
  - Methods: validate_inputs(), calculate_monthly_rate(), calculate_sip_amount()
- **BudgetPlanner**: Budget planning
  - Methods: apply_50_30_20_rule(), calculate_needs(), calculate_wants(), calculate_savings()

#### Data Access Classes
- **Database**: SQLAlchemy database wrapper
- **CSVManager**: CSV file operations

#### Route Classes (Blueprints)
- **AuthRoutes**, **TaxRoutes**, **StockRoutes**, **RecommendationRoutes**, **EducationRoutes**, **MainRoutes**

#### Application Class
- **FlaskApp**: Main Flask application

### Relationships
- Composition: FlaskApp contains Route Blueprints
- Association: Routes use Business Logic Classes
- Dependency: Business Logic Classes use Data Access Classes

---

## 6.6.4 Object Diagram (`uml_object.mmd`)

### Purpose
Shows specific instances of classes at a particular point in time with actual attribute values.

### Scenarios Documented

#### 1. Tax Calculation Scenario
- **user1**: User instance with id=1, username='john_doe'
- **tc1**: TaxCalculator instance
- **taxData1**: TaxData instance with income=800000, calculated taxes
- **csvMgr1**: CSVManager instance managing tax data file

#### 2. Stock Analysis Scenario
- **user2**: User instance with id=2
- **stockAnalyzer1**: StockAnalyzer instance with API credentials
- **stockData1, stockData2**: StockData instances with INFY stock data, calculated metrics, cluster assignments

#### 3. Expenditure Analysis Scenario
- **user3**: User instance with id=3
- **expProcessor1**: ExpenditureProcessor instance
- **clusterEngine1**: ClusteringEngine instance with n_clusters=3
- **recGen1**: RecommendationGenerator instance
- **exp1, exp2**: ExpenditureData instances with category, amount, date

#### 4. SIP Calculator Scenario
- **user4**: User instance with id=4
- **sipCalc1**: SIPCalculator instance
- **sipResult1**: SIPResult with target_amount=1000000, calculated monthly_sip

### Object Relationships
Shows actual runtime connections between objects with specific attribute values.

---

## 6.6.5 State Machine Diagram (`uml_state_machine.mmd`)

### Purpose
Shows the different states of objects and state transitions triggered by events.

### Main States

#### Authentication States
- **LoggedOut**: Initial state
- **Registering**: User registration in progress
- **LoggingIn**: User login in progress
- **LoggedIn**: Authenticated user state
- **RegistrationError**: Registration failure
- **AuthenticationError**: Login failure

#### Feature States

#### Tax Calculation States
- **CalculatingTax**: Tax feature accessed
- **EnteringTaxData**: User entering tax information
- **ProcessingTax**: System calculating taxes
- **DisplayingTaxResults**: Results shown
- **TaxError**: Error state

#### Stock Analysis States
- **AnalyzingStock**: Stock feature accessed
- **EnteringStockSymbol**: User entering symbol
- **FetchingStockData**: API request in progress
- **ProcessingStockData**: Data processing
- **ClusteringStocks**: ML clustering
- **DisplayingStockResults**: Results shown
- **StockAPIError**: API error

#### Expenditure Analysis States
- **UploadingExpenditure**: CSV upload
- **ValidatingCSV**: File validation
- **ProcessingExpenditure**: Data processing
- **ClusteringExpenditure**: Spending clustering
- **GeneratingRecommendations**: Recommendation generation
- **DisplayingExpResults**: Results shown
- **CSVError**: Validation error

#### Financial Tools States
- **UsingCalculator**: Calculator accessed
- **EnteringSIPData**: SIP input
- **EnteringBudgetData**: Budget input
- **CalculatingSIP**: SIP calculation
- **CalculatingBudget**: Budget calculation
- **DisplayingSIPResult**: SIP results
- **DisplayingBudgetResult**: Budget results

### State Transitions
All states eventually return to **LoggedIn** state after completion or error handling.

---

## 6.6.6 Sequence Diagram (`uml_sequence.mmd`)

### Purpose
Shows the sequence of interactions between objects over time.

### Documented Sequences

#### 1. User Registration Sequence
1. User accesses registration page
2. Flask app routes to AuthRoutes
3. User submits registration data
4. System checks if username exists
5. Creates new User object
6. Hashes password
7. Saves to database
8. Logs in user
9. Redirects to dashboard

#### 2. Tax Calculation Sequence
1. User enters tax data
2. Flask routes to TaxRoutes
3. TaxCalculator calculates new regime tax
4. TaxCalculator calculates old regime tax
5. System compares regimes
6. CSVManager saves tax data
7. Results returned to user

#### 3. Stock Analysis Sequence
1. User enters stock symbol
2. StockAnalyzer fetches data from API
3. StockAnalyzer processes data
4. Calculates returns and volatility
5. ClusteringEngine performs K-Means clustering
6. Results returned to user

#### 4. Expenditure Upload Sequence
1. User uploads CSV file
2. ExpenditureProcessor validates CSV
3. If valid: parses and aggregates data
4. ClusteringEngine performs clustering
5. RecommendationGenerator generates recommendations
6. Results displayed to user
7. If invalid: error shown

### Message Flow
Shows synchronous calls with return messages and error handling paths.

---

## 6.6.7 Communication Diagram (`uml_communication.mmd`)

### Purpose
Shows object interactions in a different format than sequence diagrams, emphasizing object relationships.

### Documented Interactions

#### 1. Tax Calculation Communication
- User → Web Browser → Flask App → TaxRoutes → TaxCalculator
- TaxRoutes → CSVManager → Database
- Results flow back through the chain

#### 2. Stock Analysis Communication
- User → Web Browser → Flask App → StockRoutes → StockAnalyzer
- StockAnalyzer → Stock API (external)
- StockAnalyzer → ClusteringEngine
- Results flow back to user

#### 3. Expenditure Analysis Communication
- User → Web Browser → Flask App → RecommendationRoutes
- RecommendationRoutes → ExpenditureProcessor → ClusteringEngine
- ClusteringEngine → RecommendationGenerator
- RecommendationGenerator → CSVManager
- Results flow back to user

#### 4. Authentication Communication
- User → Web Browser → Flask App → AuthRoutes
- AuthRoutes → User Model → Database
- AuthRoutes → Session Manager
- Session created and user redirected

### Object Links
Shows numbered message sequences between objects, emphasizing collaboration.

---

## 6.6.8 Component Diagram (`uml_component.mmd`)

### Purpose
Shows the physical components of the system and their dependencies.

### Component Layers

#### Web Layer
- **Web Browser**: Client interface
- **HTML Templates**: View templates
- **Static Files**: CSS, JavaScript, images

#### Application Layer
- **Flask Application**: Main app container
- **Flask Blueprints**: Modular route handlers

#### Route Layer
- **Auth Routes**: Authentication endpoints
- **Tax Routes**: Tax calculation endpoints
- **Stock Routes**: Stock analysis endpoints
- **Recommendation Routes**: Recommendation endpoints
- **Education Routes**: Financial tools endpoints
- **Main Routes**: Dashboard endpoints
- **Monitoring Routes**: Monitoring endpoints
- **Strategy Routes**: Tax planning endpoints

#### Business Logic Layer
- **Tax Calculator**: Tax computation logic
- **Stock Analyzer**: Stock data processing
- **Clustering Engine**: ML clustering
- **Recommendation Engine**: Recommendation generation
- **Financial Tools**: Calculators (SIP, Budget)

#### Data Access Layer
- **SQLAlchemy ORM**: Database interface
- **CSV Manager**: CSV file operations
- **File System**: Temporary storage

#### External Services
- **Stock Market API**: Alpha Vantage API

#### Data Storage
- **SQLite Database**: User database
- **CSV Files**: Tax and expenditure data
- **Temporary Storage**: File uploads

### Component Dependencies
Shows how components depend on each other from web layer down to storage.

---

## 6.6.9 Package Diagram (`uml_package.mmd`)

### Purpose
Shows the organization of packages and their dependencies.

### Package Structure

#### fintelligent Package
- **fintelligent.auth**: Authentication module
  - auth.models: User model
  - auth.routes: Authentication routes
- **fintelligent.main**: Main application module
- **fintelligent.tax**: Tax calculation module
- **fintelligent.stocks**: Stock analysis module
- **fintelligent.recommendation**: Recommendation module
- **fintelligent.education**: Education module
- **fintelligent.strategies**: Strategy module
- **fintelligent.monitoring**: Monitoring module
- **fintelligent.extensions**: Extensions (database)

#### Root Package
- **app.py**: Main application entry point
- **requirements.txt**: Dependencies
- **static**: Static files package
- **templates**: HTML templates package
- **instance**: Database instance package

#### External Packages
- **flask**: Web framework
- **pandas**: Data processing
- **sklearn**: Machine learning
- **sqlalchemy**: ORM framework

### Package Dependencies
- App module depends on all fintelligent subpackages
- All route modules depend on Flask
- Data processing modules depend on pandas and sklearn
- Extensions depend on SQLAlchemy

---

## 6.6.10 Deployment Diagram (`uml_deployment.mmd`)

### Purpose
Shows the physical deployment architecture of the system.

### Deployment Architecture

#### Client Layer
- **Web Browser**: Desktop browsers (Chrome, Firefox, Safari)
- **Mobile Browser**: Mobile browsers (iOS, Android)

#### Network Layer
- **Internet/Intranet**: Network connectivity
- **HTTPS Protocol**: Secure communication on port 5001

#### Application Server
- **Flask Development Server**: Development mode (app.py)
- **WSGI Server**: Production server (Gunicorn/uWSGI)

#### Application Components
- **Flask Application**: Main application
- **Flask Blueprints**: Application modules
- **Python Runtime**: Python 3.x interpreter

#### Business Logic Services
- **Tax Calculation Service**
- **Stock Analysis Service**
- **Clustering Service**
- **Recommendation Service**
- **Financial Tools Service**

#### Data Storage Layer
- **SQLite Database**: Local database file (instance/fintelligent.db)
- **CSV Files**: Tax and expenditure data (root directory)
- **Temporary Storage**: File uploads (/tmp)

#### External Services
- **Stock Market API**: Alpha Vantage (https://alphavantage.co)

#### Development Environment
- **Development Machine**: Developer's local machine
- **Code Editor**: VS Code/PyCharm
- **Git Repository**: Version control

#### Production Environment (Optional)
- **Production Server**: Linux/Cloud deployment
- **Load Balancer**: nginx/Apache (optional)
- **Production Database**: PostgreSQL/MySQL (optional)
- **Cache Layer**: Redis (optional)
- **File Storage**: S3/Cloud Storage (optional)

### Deployment Notes
- **Current**: Single-server deployment with SQLite
- **Scalability**: Can scale to multi-server with production database
- **Security**: HTTPS for secure communication
- **Storage**: Local file system, can migrate to cloud storage

---

## Diagram Files Summary

| Diagram Type | Mermaid File | PNG File | Description |
|-------------|-------------|---------|-------------|
| Use Case | `uml_use_case.mmd` | `uml_use_case.png` | System use cases and actors |
| Activity | `uml_activity.mmd` | `uml_activity.png` | Business process workflows |
| Class | `uml_class.mmd` | `uml_class.png` | System class structure |
| Object | `uml_object.mmd` | `uml_object.png` | Object instances and values |
| State Machine | `uml_state_machine.mmd` | `uml_state_machine.png` | State transitions |
| Sequence | `uml_sequence.mmd` | `uml_sequence.png` | Interaction sequences |
| Communication | `uml_communication.mmd` | `uml_communication.png` | Object collaborations |
| Component | `uml_component.mmd` | `uml_component.png` | System components |
| Package | `uml_package.mmd` | `uml_package.png` | Package organization |
| Deployment | `uml_deployment.mmd` | `uml_deployment.png` | Deployment architecture |

---

## Usage Guidelines

### Viewing Diagrams
1. **Mermaid Files**: Edit in any text editor, view in Mermaid-compatible viewers
2. **PNG Files**: View in any image viewer or embed in documentation

### Generating PNG from Mermaid
```bash
cd static/diagrams
npx mmdc -i uml_use_case.mmd -o uml_use_case.png -b transparent
```

### Embedding in Documentation
- Use PNG files for static documentation
- Use Mermaid files for interactive documentation (GitHub, GitLab, etc.)

---

## Standards Compliance

All diagrams follow UML 2.5 specifications:
- ✅ Use Case Diagram - UML 2.5 Use Case
- ✅ Activity Diagram - UML 2.5 Activity
- ✅ Class Diagram - UML 2.5 Class
- ✅ Object Diagram - UML 2.5 Object
- ✅ State Machine Diagram - UML 2.5 State Machine
- ✅ Sequence Diagram - UML 2.5 Interaction Sequence
- ✅ Communication Diagram - UML 2.5 Interaction Communication
- ✅ Component Diagram - UML 2.5 Component
- ✅ Package Diagram - UML 2.5 Package
- ✅ Deployment Diagram - UML 2.5 Deployment

---

*Last Updated: Based on current codebase analysis*
