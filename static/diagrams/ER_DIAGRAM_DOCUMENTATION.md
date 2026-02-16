# Entity Relationship (ER) Diagram Documentation for Fintelligent System

## Overview
This document describes the Entity Relationship Diagram for the Fintelligent Financial Management System. The system uses a hybrid approach with SQLite database for core entities and CSV files for transactional/logical data storage.

---

## Database Schema

### Core Database Entity

#### USER
The primary database table stored in SQLite (`fintelligent.db`).

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier for each user |
| username | VARCHAR(150) | UNIQUE, NOT NULL | User's login username |
| password_hash | VARCHAR(256) | NOT NULL | Hashed password for authentication |

**Relationships:**
- One-to-Many with TAX_HISTORY
- One-to-Many with TAX_DATA_NEW
- One-to-Many with EXPENDITURE
- One-to-Many with STOCK_ANALYSIS
- One-to-Many with FINANCIAL_RECOMMENDATIONS
- One-to-Many with USER_CLUSTER
- One-to-One with DASHBOARD_STATS
- One-to-Many with SIP_GOAL
- One-to-Many with BUDGET_PLAN

---

## Logical Entities (CSV Files)

These entities are stored in CSV files but represent logical database entities. They maintain relationships with the USER entity through `user_id` foreign keys.

### TAX_HISTORY
Stored in `user_tax_history.csv` - Historical tax data under old regime.

| Attribute | Type | Description |
|-----------|------|-------------|
| user_id | INTEGER | Foreign Key to USER.id |
| income | DECIMAL | Annual income |
| invested_80c | DECIMAL | Investments under Section 80C |
| premium_80d | DECIMAL | Premium payments under Section 80D |
| home_principal | DECIMAL | Home loan principal repayment |
| home_interest | DECIMAL | Home loan interest payment |

**Storage Format:** CSV file
**Relationship:** Many-to-One with USER (multiple tax records per user)

---

### TAX_DATA_NEW
Stored in `user_tax_data_new.csv` - Tax calculations under new regime.

| Attribute | Type | Description |
|-----------|------|-------------|
| user_id | INTEGER | Foreign Key to USER.id |
| income | DECIMAL | Annual income for tax calculation |
| timestamp | TIMESTAMP | When the calculation was performed |

**Storage Format:** CSV file
**Relationship:** Many-to-One with USER (users can calculate taxes multiple times)

---

### EXPENDITURE
Stored in `expenditure.csv` or uploaded CSV files - User spending data.

| Attribute | Type | Description |
|-----------|------|-------------|
| user_id | INTEGER | Foreign Key to USER.id |
| category | STRING | Expense category (e.g., groceries, entertainment) |
| amount | DECIMAL | Expense amount |
| date | DATE | Date of expense |
| payment_method | STRING | Payment method used (optional) |
| merchant | STRING | Merchant name (optional) |
| location | STRING | Location of expense (optional) |

**Storage Format:** CSV file
**Relationship:** 
- Many-to-One with USER
- Many-to-One with USER_CLUSTER (for clustering analysis)

---

## Conceptual Entities (Derived/Logical)

These entities represent conceptual data structures used in the application but may not be stored as separate database tables. They are included for completeness of the data model.

### STOCK_ANALYSIS
Represents stock market analysis performed for users.

| Attribute | Type | Description |
|-----------|------|-------------|
| analysis_id | INTEGER | Primary Key (conceptual) |
| user_id | INTEGER | Foreign Key to USER.id |
| stock_symbol | STRING | Stock symbol analyzed (e.g., INFY) |
| analysis_date | DATE | Date of analysis |
| close_price | DECIMAL | Closing price on analysis date |
| return_rate | DECIMAL | Calculated return percentage |
| volatility | DECIMAL | Calculated volatility (rolling std dev) |
| cluster_label | INTEGER | K-Means cluster assignment |

**Storage:** Currently generated on-demand, not persisted
**Relationship:** Many-to-One with USER

---

### FINANCIAL_RECOMMENDATIONS
Personalized financial recommendations generated for users.

| Attribute | Type | Description |
|-----------|------|-------------|
| recommendation_id | INTEGER | Primary Key (conceptual) |
| user_id | INTEGER | Foreign Key to USER.id |
| recommendation_type | STRING | Type: Budget/Tax/Investment |
| recommendation_text | TEXT | Recommendation content |
| created_at | TIMESTAMP | When recommendation was generated |
| cluster_id | INTEGER | Related cluster from spending analysis |

**Storage:** Currently returned to user, not persisted
**Relationship:** 
- Many-to-One with USER
- Many-to-One with USER_CLUSTER

---

### USER_CLUSTER
User clustering assignments based on spending patterns.

| Attribute | Type | Description |
|-----------|------|-------------|
| user_id | INTEGER | Foreign Key to USER.id |
| cluster_id | INTEGER | K-Means cluster assignment |
| category_spending | DECIMAL | Spending breakdown by category |
| cluster_date | DATE | When clustering was performed |

**Storage:** Currently calculated on-demand, not persisted
**Relationship:**
- Many-to-One with USER
- Many-to-One with EXPENDITURE
- One-to-Many with FINANCIAL_RECOMMENDATIONS

---

### DASHBOARD_STATS
Aggregated dashboard statistics for users.

| Attribute | Type | Description |
|-----------|------|-------------|
| user_id | INTEGER | Foreign Key to USER.id |
| total_savings | DECIMAL | Total savings amount |
| tax_saved | DECIMAL | Tax savings achieved |
| investments | DECIMAL | Total investments |
| financial_score | INTEGER | Financial health score (0-100) |
| monthly_income | DECIMAL | Monthly income |
| expenses | DECIMAL | Monthly expenses |
| savings_rate | INTEGER | Savings rate percentage |
| last_updated | TIMESTAMP | Last update timestamp |

**Storage:** Currently generated on-demand (random data for demo)
**Relationship:** One-to-One with USER

---

### SIP_GOAL
Systematic Investment Plan (SIP) goals created by users.

| Attribute | Type | Description |
|-----------|------|-------------|
| goal_id | INTEGER | Primary Key (conceptual) |
| user_id | INTEGER | Foreign Key to USER.id |
| target_amount | DECIMAL | Target corpus amount |
| years | INTEGER | Time period in years |
| annual_rate | DECIMAL | Expected annual return rate |
| monthly_sip | DECIMAL | Calculated monthly SIP amount |
| created_at | TIMESTAMP | When goal was created |

**Storage:** Currently calculated on-demand, not persisted
**Relationship:** Many-to-One with USER

---

### BUDGET_PLAN
Budget plans created using 50-30-20 rule.

| Attribute | Type | Description |
|-----------|------|-------------|
| plan_id | INTEGER | Primary Key (conceptual) |
| user_id | INTEGER | Foreign Key to USER.id |
| monthly_income | DECIMAL | Monthly income |
| needs_allocation | DECIMAL | 50% for needs |
| wants_allocation | DECIMAL | 30% for wants |
| savings_allocation | DECIMAL | 20% for savings |
| created_at | TIMESTAMP | When plan was created |

**Storage:** Currently calculated on-demand, not persisted
**Relationship:** Many-to-One with USER

---

## Relationships Summary

### One-to-Many Relationships (USER → Other Entities)
- USER to TAX_HISTORY: One user can have multiple tax history records
- USER to TAX_DATA_NEW: One user can perform multiple tax calculations
- USER to EXPENDITURE: One user can have many expenditure records
- USER to STOCK_ANALYSIS: One user can analyze multiple stocks
- USER to FINANCIAL_RECOMMENDATIONS: One user can receive many recommendations
- USER to USER_CLUSTER: One user can belong to different clusters over time
- USER to SIP_GOAL: One user can create multiple SIP goals
- USER to BUDGET_PLAN: One user can create multiple budget plans

### One-to-One Relationship
- USER to DASHBOARD_STATS: Each user has one dashboard statistics record

### Many-to-One Relationships
- EXPENDITURE to USER_CLUSTER: Multiple expenses contribute to cluster assignment
- USER_CLUSTER to FINANCIAL_RECOMMENDATIONS: Clusters generate recommendations

---

## Data Storage Strategy

### Database (SQLite)
- **USER table**: Persistent storage in `instance/fintelligent.db`
- Managed via SQLAlchemy ORM

### CSV Files
- **TAX_HISTORY**: `user_tax_history.csv` (append mode)
- **TAX_DATA_NEW**: `user_tax_data_new.csv` (append mode)
- **EXPENDITURE**: `expenditure.csv` or uploaded files in `/tmp`

### In-Memory / On-Demand
- **STOCK_ANALYSIS**: Calculated on-demand, not persisted
- **FINANCIAL_RECOMMENDATIONS**: Generated on-demand
- **USER_CLUSTER**: Calculated during expenditure analysis
- **DASHBOARD_STATS**: Generated on-demand (currently random for demo)
- **SIP_GOAL**: Calculated on-demand
- **BUDGET_PLAN**: Calculated on-demand

---

## Future Database Normalization Opportunities

For production, consider migrating CSV entities to proper database tables:

1. **TAX_HISTORY** → `tax_history` table
2. **TAX_DATA_NEW** → `tax_calculations` table
3. **EXPENDITURE** → `expenditures` table with proper indexing
4. **STOCK_ANALYSIS** → `stock_analyses` table for historical tracking
5. **FINANCIAL_RECOMMENDATIONS** → `recommendations` table
6. **USER_CLUSTER** → `user_clusters` table
7. **DASHBOARD_STATS** → `dashboard_statistics` table
8. **SIP_GOAL** → `sip_goals` table
9. **BUDGET_PLAN** → `budget_plans` table

### Additional Normalization Considerations

- Add indexes on `user_id` foreign keys
- Add indexes on `date` fields for time-series queries
- Consider partitioning large tables (expenditures) by date
- Add constraints for data integrity (check constraints, foreign keys)
- Implement soft deletes with `deleted_at` timestamps
- Add audit fields (`created_at`, `updated_at`) to all entities

---

## Cardinality Notation

- `||--o{` : One-to-Many (one user to many records)
- `||--||` : One-to-One (one user to one dashboard)
- `o{--o{` : Many-to-Many (not currently used)

---

## Key Constraints

### Primary Keys (PK)
- USER.id
- STOCK_ANALYSIS.analysis_id (conceptual)
- FINANCIAL_RECOMMENDATIONS.recommendation_id (conceptual)
- SIP_GOAL.goal_id (conceptual)
- BUDGET_PLAN.plan_id (conceptual)

### Foreign Keys (FK)
- All entities reference USER.id via `user_id`

### Unique Constraints (UK)
- USER.username (must be unique)

### Not Null Constraints
- USER.username
- USER.password_hash
- All foreign key references

---

*Last Updated: Based on current codebase analysis*
