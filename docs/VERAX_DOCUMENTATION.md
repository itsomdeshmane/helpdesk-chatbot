# VERAX APPLICATION - COMPLETE DOCUMENTATION

**Version:** 1.0  
**Last Updated:** November 2025  
**Application:** Verax Angular ERP System

---

## Table of Contents

1. [Overview](#1-overview)
2. [System Architecture](#2-system-architecture)
3. [Main Modules](#3-main-modules)
4. [Security & Permissions](#4-security--permissions)
5. [All Security Activities](#5-all-security-activities)
6. [Module Permissions Guide](#6-module-permissions-guide)
7. [Operations Summary](#7-operations-summary)
8. [Role Management](#8-role-management)
9. [Configuration Guide](#9-configuration-guide)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Overview

### What is Verax?
Verax is an enterprise resource planning (ERP) application built with Angular. It helps businesses manage:
- Customer relationships (CRM)
- Financial accounting
- Inventory and materials
- Manufacturing and production
- Purchasing and vendors
- Service operations
- Human resources
- Employee time tracking

### Technology Stack
- **Frontend:** Angular (TypeScript)
- **UI Framework:** Bootstrap (Bootswatch themes)
- **State Management:** RxJS
- **Components:** ng-bootstrap, ngx-bootstrap, ng-select
- **API:** RESTful backend (configurable URL)

---

## 2. System Architecture

### Module Structure
```
Application Root
├── Authorization Module (Login/Logout)
├── Core Module (Services, Guards, Interceptors)
├── Shared Module (Reusable Components)
└── Application Module
    ├── Dashboard
    ├── CRM
    ├── Accounting
    ├── Purchasing
    ├── Inventory
    ├── Workflow
    ├── Service
    ├── HRM
    ├── Attendance
    ├── Scheduling
    ├── Setup
    ├── Administration
    ├── Account
    ├── Tenants
    └── Errors
```

### Key Concepts

#### Multi-Tenancy
- Users can switch between different company databases (tenants)
- Each tenant has separate data and settings
- Access controlled at tenant level

#### Page Settings
- Each user can customize table columns and layouts
- Settings stored per user per page
- Managed through `PageSettingsService`

#### Search Filters
- Pre-defined search filters for each list page
- Users can save custom filter preferences
- Managed through search filter components

---

## 3. Main Modules

### 3.1 Dashboard Module 📊
**Purpose:** Personal workspace and task management

#### Submodules

##### Tasks
- **My Tasks:** View your assigned tasks
- **Others' Tasks:** View tasks assigned to team members
- **Grouped Tasks:** Tasks organized by status/type
- **Manage Tasks:** Create, edit, delete, and copy tasks

**Operations:**
- ✅ Create tasks
- ✅ Edit tasks
- ✅ Delete tasks
- ✅ Copy tasks
- ✅ Assign tasks to users
- ✅ Set due dates and priorities

##### Calendar
- **Microsoft Calendar Integration:** Sync with Outlook/Office 365
- **Event Management:** Create meetings and appointments
- **Calendar Assets:** Book meeting rooms and equipment
- **Attendee Management:** Invite and track participants

**Operations:**
- ✅ Create events
- ✅ Edit events
- ✅ Delete events
- ✅ Create calendars
- ✅ Manage calendar assets
- ✅ Validate event conflicts

##### Other Features
- **Profile:** Manage your personal information and settings
- **Signature:** Digital signature management
- **Organization Chart:** View company hierarchy
- **What's New:** See recent system updates

---

### 3.2 CRM Module 👥
**Purpose:** Customer relationship management and sales

#### Submodules

##### Companies (Customers & Facilities)
Manage customer information and facility locations.

**Features:**
- Customer details (name, contact info, payment terms)
- Multiple facilities per customer
- Facility addresses and contact information
- Advanced payment processing
- Customer notes and attachments

**Operations:**
- ✅ Add new customers
- ✅ Edit customer details
- ✅ Delete customers
- ✅ Add facilities
- ✅ Edit facilities
- ✅ Accept advance payments

**Where to Find:**
- Navigate to: **CRM → Companies → Customers**

##### Contacts
Manage individual contacts at customer companies.

**Features:**
- Contact details (name, email, phone)
- Contact types and relationships
- Multiple contacts per facility
- Contact notes

**Operations:**
- ✅ Create contacts
- ✅ Edit contacts
- ✅ Delete contacts
- ✅ Link to facilities

**Where to Find:**
- Navigate to: **CRM → Contacts**

##### Leads
Track potential customers before they become opportunities.

**Features:**
- Lead source tracking
- Lead status management
- Lead assignment to sales reps
- Convert lead to opportunity

**Operations:**
- ✅ Add leads
- ✅ Edit leads
- ✅ Delete leads
- ✅ Convert to opportunity

**Where to Find:**
- Navigate to: **CRM → Leads**

##### Opportunities
Track sales opportunities through the sales pipeline.

**Features:**
- Opportunity stages
- Win probability tracking
- Expected close date
- Opportunity value
- Link to contacts
- Sales process steps
- Convert to job when won

**Operations:**
- ✅ Create opportunities
- ✅ Edit opportunities
- ✅ Delete opportunities
- ✅ Link contacts
- ✅ Convert to job
- ✅ Mark as won/lost

**Where to Find:**
- Navigate to: **CRM → Opportunities**

##### Quotes (Sales)
Create and manage sales quotations.

**Features:**
- Quote lines (items, services)
- Quote inputs (specifications)
- Pricing and discounts
- Quote acknowledgment workflow
- Convert to job
- Reopen closed quotes
- Link to existing jobs

**Operations:**
- ✅ Create quotes
- ✅ Edit quotes
- ✅ Delete quotes
- ✅ Copy quotes
- ✅ Add quote lines
- ✅ Add quote inputs
- ✅ Acknowledge quotes
- ✅ Convert to job
- ✅ Link to job

**Where to Find:**
- Navigate to: **CRM → Quotes**

##### CRM Reports
Generate sales analytics and reports.

**Available Reports:**
- Quote Lines Report
- Quotes by Fiscal Period
- Sales pipeline analysis

**Where to Find:**
- Navigate to: **CRM → CRM Reports**

---

### 3.3 Accounting Module 💰
**Purpose:** Financial management and bookkeeping

#### Submodules

##### Chart of Accounts
Define and manage the accounting account structure.

**Features:**
- Account hierarchy
- Account types (Asset, Liability, Equity, Revenue, Expense)
- Account classifications
- Sub-accounts
- Recent transactions view

**Operations:**
- ✅ Create accounts
- ✅ Edit accounts
- ✅ Delete accounts
- ✅ View sub-accounts

**Where to Find:**
- Navigate to: **Accounting → Accounts**

##### Accounts Payable (AP)
Manage vendor bills and payments.

**Features:**
- Vendor invoices
- Bill payments
- Vendor returns
- Accrual adjustments
- Purchasing accrual clearing
- Bank reconciliation

**Operations:**
- ✅ Create AP invoices
- ✅ Edit AP invoices
- ✅ Delete AP invoices
- ✅ Process payments
- ✅ Adjust accruals
- ✅ Reconcile accounts

**Where to Find:**
- Navigate to: **Accounting → Accounts Payable**

##### Accounts Receivable (AR)
Manage customer invoices and payments.

**Features:**
- Customer invoices
- Payment processing
- Customer returns
- AR aging
- Invoice generation from jobs

**Operations:**
- ✅ Create AR invoices
- ✅ Edit AR invoices
- ✅ Delete AR invoices
- ✅ Process payments
- ✅ Generate from jobs

**Where to Find:**
- Navigate to: **Accounting → Accounts Receivable**

##### General Ledger
Post journal entries and view ledger activity.

**Features:**
- Journal entries
- Trial balance
- Account activity
- Period management

**Operations:**
- ✅ Create journal entries
- ✅ Edit journal entries
- ✅ Delete journal entries
- ✅ View trial balance

**Where to Find:**
- Navigate to: **Accounting → General Ledger**

##### Billing Types
Configure different billing methods.

**Operations:**
- ✅ Create billing types
- ✅ Edit billing types
- ✅ Delete billing types

**Where to Find:**
- Navigate to: **Accounting → Settings → Billing Types**

##### Periods
Define and manage accounting periods.

**Features:**
- Period open/close status
- Period date ranges
- Fiscal year management

**Operations:**
- ✅ Create periods
- ✅ Edit periods
- ✅ Close periods
- ✅ Reopen periods

**Where to Find:**
- Navigate to: **Accounting → Periods**

##### Year End
Perform year-end closing procedures.

**Features:**
- Year-end closing wizard
- Close income/expense accounts
- Transfer to retained earnings

**Operations:**
- ✅ Perform year-end close

**Where to Find:**
- Navigate to: **Accounting → Year End**

##### Reports
Generate financial statements and reports.

**Available Reports:**
- Balance Sheet
- Income Statement (P&L)
- AR Aging Report
- AP Aging Report
- Accrual Aging Report
- Account Activity Report
- WIP Report
- Billing by Location
- Closed Job Labor Hours
- Closed Sales Job Cost Report
- Closed Service Issue Cost Report
- Closed Service Job Cost Report

**Where to Find:**
- Navigate to: **Accounting → Reports**

##### Manage Settings
Configure accounting system settings.

**Features:**
- Default AP accounts
- Default AR accounts
- Accounting preferences

**Where to Find:**
- Navigate to: **Accounting → Settings → Manage Settings**

---

### 3.4 Purchasing Module 🛒
**Purpose:** Vendor management and procurement

#### Submodules

##### Vendors
Manage supplier information.

**Features:**
- Vendor details
- Payment terms
- Vendor contacts
- Items sold by vendor
- Purchase order history
- AP invoice history

**Operations:**
- ✅ Create vendors
- ✅ Edit vendors
- ✅ Delete vendors
- ✅ View vendor details

**Where to Find:**
- Navigate to: **Purchasing → Vendors**

##### Manufacturers
Track product manufacturers.

**Features:**
- Manufacturer details
- Manufacturer items

**Operations:**
- ✅ Create manufacturers
- ✅ Edit manufacturers
- ✅ Delete manufacturers

**Where to Find:**
- Navigate to: **Purchasing → Manufacturers**

##### Purchase Orders
Create and manage purchase orders.

**Features:**
- PO lines (items and quantities)
- PO receiving
- PO status tracking
- Vendor selection
- Expected delivery dates
- PO notes and attachments

**Operations:**
- ✅ Create POs
- ✅ Edit POs
- ✅ Delete POs
- ✅ Copy POs
- ✅ Receive items
- ✅ Close POs

**Where to Find:**
- Navigate to: **Purchasing → Purchase Orders**

##### Requisitions
Request items for purchase.

**Features:**
- Requisition approval workflow
- Convert to purchase order
- Requisition status tracking
- Multi-item requisitions

**Operations:**
- ✅ Create requisitions
- ✅ Edit requisitions
- ✅ Delete requisitions
- ✅ Approve requisitions
- ✅ Convert to PO

**Where to Find:**
- Navigate to: **Purchasing → Requisitions**

##### Request for Quote (RFQ)
Request quotes from vendors.

**Features:**
- RFQ to multiple vendors
- Response tracking
- Convert to PO

**Operations:**
- ✅ Create RFQs
- ✅ Edit RFQs
- ✅ Delete RFQs
- ✅ Track responses

**Where to Find:**
- Navigate to: **Purchasing → Requests for Quote**

##### Current Demand
View material requirements.

**Features:**
- Current demand view
- Material needs by job
- Safety stock levels
- Reorder suggestions

**Where to Find:**
- Navigate to: **Purchasing → Current Demand**

##### Purchasing Reports
Generate purchasing analytics.

**Where to Find:**
- Navigate to: **Purchasing → Reports**

---

### 3.5 Inventory Module 📦
**Purpose:** Stock and materials management

#### Submodules

##### Items
Manage inventory items and materials.

**Features:**
- Item details (description, specs)
- Item costs and pricing
- Item locations
- Item history
- Item tags
- Item links (related items)
- Used-on relationships

**Operations:**
- ✅ Create items
- ✅ Edit items
- ✅ Delete items
- ✅ Add stock
- ✅ Move items between locations
- ✅ Scrap items
- ✅ Use inventory
- ✅ Adjust costs
- ✅ Set sell prices
- ✅ Manage tags

**Where to Find:**
- Navigate to: **Inventory → Items**

##### Inventory Items
Purchased inventory tracking.

**Operations:**
- ✅ View inventory levels
- ✅ Manage inventory items

**Where to Find:**
- Navigate to: **Inventory → Inventory Items**

##### Inventory Routers
Define manufacturing routings.

**Features:**
- Router steps and operations
- Operation sequence
- Time estimates
- Material requirements
- Add jobs from routers

**Operations:**
- ✅ Create routers
- ✅ Edit routers
- ✅ Delete routers
- ✅ Add router steps
- ✅ Create jobs from router

**Where to Find:**
- Navigate to: **Inventory → Routers**

##### Issue Material
Issue materials to jobs or work orders.

**Operations:**
- ✅ Issue materials to work orders
- ✅ Issue materials to service jobs

**Where to Find:**
- Navigate to: **Inventory → Issue Material**

##### Receive PO
Receive purchased items.

**Operations:**
- ✅ Receive items from PO
- ✅ Partial receives
- ✅ Over-receive handling

**Where to Find:**
- Navigate to: **Inventory → Receive PO**

##### Close Work Order
Close completed work orders.

**Operations:**
- ✅ Close work orders
- ✅ Close individual operations

**Where to Find:**
- Navigate to: **Inventory → Close Work Order**

##### Inventory Reports
Generate inventory reports.

**Available Reports:**
- Inventory Report
- Inventory by Storage Area
- Router Tree Report

**Where to Find:**
- Navigate to: **Inventory → Reports**

##### Inventory History
View all inventory transactions.

**Features:**
- Transaction history
- Movement tracking
- Stock adjustments log

**Where to Find:**
- Navigate to: **Inventory → Reports → Inventory History**

##### Raw Materials
Manage raw material definitions.

**Operations:**
- ✅ View raw materials
- ✅ Create raw materials
- ✅ Edit raw materials

**Where to Find:**
- Navigate to: **Setup → Raw Materials**

---

### 3.6 Workflow Module ⚙️
**Purpose:** Manufacturing and production management

#### Submodules

##### Jobs
Manage production and sales jobs.

**Features:**
- Job details and status
- Job contacts
- Job shippers
- Job costing (Actual, Fixed Rates, Hours Only)
- Job operations
- Material requirements
- Job notes and attachments
- Estimated completion dates

**Operations:**
- ✅ Create jobs
- ✅ Edit jobs
- ✅ Delete jobs
- ✅ Copy jobs
- ✅ Close jobs
- ✅ Reopen jobs
- ✅ Add contacts
- ✅ Add shippers
- ✅ Add notes
- ✅ Manage expenses
- ✅ Set completion dates

**Where to Find:**
- Navigate to: **Workflow → Jobs**

##### Work Orders
Manage manufacturing work orders.

**Features:**
- Work order operations
- Operation status
- Material requirements
- Labor tracking
- Outside operations
- Work order holds
- Print work orders

**Operations:**
- ✅ Create work orders
- ✅ Edit work orders
- ✅ Delete work orders
- ✅ Issue materials
- ✅ Close work orders
- ✅ Release to production
- ✅ Move supply/demand
- ✅ Request outside operations
- ✅ Print work orders
- ✅ Print labor tickets

**Where to Find:**
- Navigate to: **Workflow → Jobs** (work orders are under jobs)

##### Designs
Manage product design workflow.

**Features:**
- Design steps
- Design approval
- Design tasks

**Operations:**
- ✅ Create designs
- ✅ Edit designs
- ✅ Approve designs
- ✅ Clock into design tasks

**Where to Find:**
- Navigate to: **Workflow → Designs**

##### Change Requests
Engineering change request management.

**Features:**
- Change request tracking
- Root cause analysis
- Approval workflow
- Operation holds

**Operations:**
- ✅ Create change requests
- ✅ Edit change requests
- ✅ Delete change requests
- ✅ Root cause analysis
- ✅ Override holds

**Where to Find:**
- Navigate to: **Workflow → Change Requests**

##### Release Work
Release work orders to production floor.

**Operations:**
- ✅ Release work to production

**Where to Find:**
- Navigate to: **Workflow → Release Work**

##### WIP Tracking
Track work in process.

**Features:**
- Item movements
- WIP locations
- Operation completion

**Operations:**
- ✅ View item movements
- ✅ Manage item movements

**Where to Find:**
- Navigate to: **Workflow → WIP Tracking**

##### MPR
Material planning requirements.

**Where to Find:**
- Navigate to: **Workflow → MPR**

##### Customers & Facilities
Manage workflow customer and facility data.

**Operations:**
- ✅ View facilities
- ✅ Create facilities
- ✅ Edit facilities
- ✅ Accept advance payments

**Where to Find:**
- Navigate to: **Workflow → Customers**

##### Active Work
View current production activity.

**Where to Find:**
- Navigate to: **Workflow → Active Work**

##### Work Centers
View production work centers.

**Where to Find:**
- Navigate to: **Workflow → Work Centers**

##### Manage Estimates
Review operation time estimates.

**Operations:**
- ✅ Review all estimates
- ✅ Reopen designs

**Where to Find:**
- Navigate to: **Workflow → Manage Estimates**

##### Review MPT Jobs
Review make-to-print jobs.

**Operations:**
- ✅ Review MPT process

**Where to Find:**
- Navigate to: **Workflow → Review MPT Jobs**

##### Vault
Document storage.

**Where to Find:**
- Navigate to: **Workflow → Vault**

##### Workflow Reports
Generate workflow reports.

**Where to Find:**
- Navigate to: **Workflow → Reports**

---

### 3.7 Service Module 🔧
**Purpose:** Service and repair operations

#### Submodules

##### Service Jobs
Manage service work for customers.

**Features:**
- Service job details
- Service job contacts
- Service issues linked to job
- Service shippers
- Service job notes

**Operations:**
- ✅ Create service jobs
- ✅ Edit service jobs
- ✅ Delete service jobs
- ✅ Add contacts
- ✅ Add issues
- ✅ Add shippers
- ✅ Manage notes
- ✅ Set completion dates

**Where to Find:**
- Navigate to: **Service → Service Jobs**

##### Service Issues
Track service tickets and issues.

**Features:**
- Issue details and status
- Issue operations
- Labor tracking
- Material requirements
- Issue scheduling
- Facility contacts
- Outside operations
- Status flow management
- Cost breakdown
- Mobile view

**Operations:**
- ✅ Create issues
- ✅ Edit issues
- ✅ Delete issues
- ✅ Add operations
- ✅ Add items/materials
- ✅ Add labor
- ✅ Schedule issues
- ✅ Link facility contacts
- ✅ Request outside operations
- ✅ Approve for billing
- ✅ Override status
- ✅ Clock into service

**Where to Find:**
- Navigate to: **Service → Issues**

##### Service Quotes
Create quotes for service work.

**Features:**
- Service quote lines
- Service quote inputs
- Quote acknowledgment
- Convert to service job

**Operations:**
- ✅ Create service quotes
- ✅ Edit service quotes
- ✅ Delete service quotes
- ✅ Copy service quotes
- ✅ Acknowledge quotes
- ✅ Convert to job

**Where to Find:**
- Navigate to: **Service → Quotes**

##### Machines
Track customer equipment and machines.

**Features:**
- Machine details
- Machine owners
- Machine history

**Operations:**
- ✅ Create machines
- ✅ Edit machines
- ✅ Delete machines
- ✅ Add machine owners

**Where to Find:**
- Navigate to: **Service → Machines**

##### Schedule Feed
Service scheduling feed view.

**Where to Find:**
- Navigate to: **Service → Schedule Feed**

##### Other Service Pages
- **Calibration:** Equipment calibration tracking
- **Subscriptions:** Service subscription management
- **Service Wallboard:** Visual dashboard
- **Service and Attendance:** Combined view

---

### 3.8 HRM Module 👨‍💼
**Purpose:** Human resources management

#### Submodules

##### Employees
Manage employee information.

**Features:**
- Employee details
- Contact information
- Emergency contacts
- Direct reports hierarchy
- Employee contacts panel
- Sensitive information (SSN, salary)

**Operations:**
- ✅ Create employees
- ✅ Edit employees
- ✅ Delete employees
- ✅ Manage sensitive info
- ✅ Manage direct reports

**Where to Find:**
- Navigate to: **HRM → Employees**

##### HRM Contacts
Manage HR-related contacts.

**Features:**
- Contact details
- Contact types

**Operations:**
- ✅ Create contacts
- ✅ Edit contacts
- ✅ Delete contacts

**Where to Find:**
- Navigate to: **HRM → Contacts**

##### HRM Reports
Generate HR reports.

**Available Reports:**
- Attendance Report
- Labor Report

**Where to Find:**
- Navigate to: **HRM → Reports**

---

### 3.9 Attendance Module ⏰
**Purpose:** Employee time tracking

#### Submodules

##### Attendance (Clock In/Out)
Time clock functionality.

**Features:**
- Web-based clock in/out
- Clock into work orders
- Clock into service issues
- Clock into design tasks
- Active work orders view
- Service issue notes

**Operations:**
- ✅ Clock in
- ✅ Clock out
- ✅ Select work order
- ✅ Select service issue
- ✅ Override location
- ✅ Override next operation

**Where to Find:**
- Navigate to: **Attendance → Attendance**

##### Employee Time
View employee time records.

**Features:**
- Time details by employee
- Attendance by week
- Direct vs indirect hours
- Current work
- Recent work
- Time details

**Operations:**
- ✅ View time records
- ✅ View employee details

**Where to Find:**
- Navigate to: **Attendance → Employee Time**

##### Balance
Balance and adjust employee time.

**Features:**
- Balance log
- Work in process time
- Service labor time
- Add/edit attendance
- Add/edit job time
- Add/edit indirect time
- Adjust clock-in times
- Move time between jobs
- Remove lunch
- Change indirect type

**Operations:**
- ✅ Add attendance
- ✅ Edit attendance
- ✅ Add job time
- ✅ Edit job time
- ✅ Add indirect time
- ✅ Adjust clock-in
- ✅ Move time
- ✅ Remove lunch
- ✅ Change indirect type
- ✅ Override balance checks

**Where to Find:**
- Navigate to: **Attendance → Balance**

##### Indirect Notifications
Manage indirect time notifications.

**Operations:**
- ✅ Create notifications
- ✅ Edit notifications
- ✅ Delete notifications

**Where to Find:**
- Navigate to: **Attendance → Indirect Notifications**

---

### 3.10 Scheduling Module 📅
**Purpose:** Production scheduling

#### Features
- Job scheduling
- Work center scheduling
- Visual chip maker
- Drag and drop scheduling
- Scheduling buckets
- Similar items view
- Work by area scheduling
- User personal buckets

**Operations:**
- ✅ View schedules
- ✅ Create schedules
- ✅ Edit schedules
- ✅ Create buckets
- ✅ Edit chips (scheduled items)
- ✅ Update work center assignments
- ✅ Drag and drop items

**Where to Find:**
- Navigate to: **Scheduling → Job Schedule**
- Navigate to: **Scheduling → Work Center Schedule**
- Navigate to: **Scheduling → Chip Maker**
- Navigate to: **Scheduling → Work by Area Chip Maker**
- Navigate to: **Scheduling → User Buckets**

---

### 3.11 Setup Module ⚙️
**Purpose:** System configuration

#### Submodules

##### Security Settings
Configure roles and permissions.

**Features:**
- Security roles
- Security activities
- User activity assignments
- Role activity assignments
- Available users for activities
- Available roles for activities

**Operations:**
- ✅ Create roles
- ✅ Edit roles
- ✅ Delete roles
- ✅ Assign activities to roles
- ✅ Assign roles to users
- ✅ Assign activities to users

**Where to Find:**
- Navigate to: **Setup → Security**
- Navigate to: **Setup → Restricted Security** (limited view)

##### Departments
Manage company departments.

**Operations:**
- ✅ Create departments
- ✅ Edit departments
- ✅ Delete departments

**Where to Find:**
- Navigate to: **Setup → Departments**

##### Product Lines
Manage product lines.

**Operations:**
- ✅ Create product lines
- ✅ Edit product lines
- ✅ Delete product lines

**Where to Find:**
- Navigate to: **Setup → Product Lines**

##### Storage Areas (Inventory Locations)
Define warehouse locations.

**Operations:**
- ✅ Create storage areas
- ✅ Edit storage areas
- ✅ Delete storage areas

**Where to Find:**
- Navigate to: **Setup → Storage Areas**

##### Work Centers
Define production work centers.

**Operations:**
- ✅ Create work centers
- ✅ Edit work centers
- ✅ Delete work centers

**Where to Find:**
- Navigate to: **Setup → Work Centers**

##### Operations
Define manufacturing operations.

**Operations:**
- ✅ Create operations
- ✅ Edit operations
- ✅ Delete operations

**Where to Find:**
- Navigate to: **Setup → Operations**

##### Currencies
Manage currency types.

**Operations:**
- ✅ Create currencies
- ✅ Edit currencies
- ✅ Delete currencies

**Where to Find:**
- Navigate to: **Setup → Currencies**

##### Shifts
Define work shifts.

**Operations:**
- ✅ Create shifts
- ✅ Edit shifts
- ✅ Delete shifts

**Where to Find:**
- Navigate to: **Setup → Shifts**

##### List Options
Manage dropdown list options.

**Operations:**
- ✅ Create list options
- ✅ Edit list options
- ✅ Delete list options

**Where to Find:**
- Navigate to: **Setup → List Options**

##### Payment Terms
Define payment terms.

**Operations:**
- ✅ Create payment terms
- ✅ Edit payment terms
- ✅ Delete payment terms

**Where to Find:**
- Navigate to: **Setup → Payment Terms**

##### Sales Process
Define sales workflow steps.

**Operations:**
- ✅ Create process steps
- ✅ Edit process steps
- ✅ Delete process steps

**Where to Find:**
- Navigate to: **Setup → Sales Process**

##### Units of Measure
Define measurement units.

**Operations:**
- ✅ Create units
- ✅ Edit units
- ✅ Delete units

**Where to Find:**
- Navigate to: **Setup → Settings → Units of Measure**

##### Days Closed
Define company holidays.

**Operations:**
- ✅ Create closed days
- ✅ Edit closed days
- ✅ Delete closed days

**Where to Find:**
- Navigate to: **Setup → Settings → Days Closed**

##### Item Types
Define inventory item types.

**Operations:**
- ✅ Create item types
- ✅ Edit item types
- ✅ Delete item types

**Where to Find:**
- Navigate to: **Setup → Item Types**

##### Job Types
Define job types.

**Operations:**
- ✅ Create job types
- ✅ Edit job types
- ✅ Delete job types

**Where to Find:**
- Navigate to: **Setup → Job Types**

##### vScan Stations
Configure barcode scanning stations.

**Operations:**
- ✅ Create stations
- ✅ Edit stations
- ✅ Delete stations

**Where to Find:**
- Navigate to: **Setup → vScan Stations**

##### Site-Wide Settings
Configure system-wide settings.

**Settings:**
- Service enabled/disabled
- Buyer users
- Sales representative users
- Company name
- Accounting year start
- Router combining rules
- Labor report settings

**Where to Find:**
- Navigate to: **Setup → Setup (Site Wide Settings)**

##### Non-Accounting Site Wide Settings
General system settings.

**Where to Find:**
- Navigate to: **Setup → Settings → Non-Accounting**

##### User Interface
Customize UI appearance.

**Operations:**
- ✅ View UI settings
- ✅ Modify UI settings

**Where to Find:**
- Navigate to: **Setup → User Interface**

##### Manage Licenses
Software license management.

**Operations:**
- ✅ View licenses
- ✅ Manage licenses

**Where to Find:**
- Navigate to: **Setup → Manage Licenses**

##### Raw Materials
Raw material definitions.

**Operations:**
- ✅ View raw materials
- ✅ Create raw materials
- ✅ Manage raw materials

**Where to Find:**
- Navigate to: **Setup → Raw Materials**

---

### 3.12 Administration Module 🏢
**Purpose:** System administration

#### Features
- Customer management (admin level)
- Customer licenses
- License types
- Tenant management

**Operations:**
- ✅ Create customers
- ✅ Edit customers
- ✅ Delete customers
- ✅ Create licenses
- ✅ Edit licenses
- ✅ Create license types
- ✅ Create tenants

**Where to Find:**
- Navigate to: **Admin → Customers**
- Navigate to: **Admin → Licensing**

---

### 3.13 Account Module 👤
**Purpose:** Personal account management

#### Features
- Profile management
- Personal settings
- User management
- Facility access
- Localization settings

**Where to Find:**
- Navigate to: **Account → Profile**
- Navigate to: **Account → Settings**
- Navigate to: **Account → Users**
- Navigate to: **Account → Facilities**
- Navigate to: **Account → Localizations**

---

### 3.14 Tenants Module 🏢
**Purpose:** Switch between company databases

#### Features
- Tenant selection
- Multi-tenant support

**Where to Find:**
- Navigate to: **Tenants**

---

### 3.15 Errors Module ⚠️
**Purpose:** Error page handling

#### Features
- 404 Page Not Found
- Error messages

---

### 3.16 Facility Module 🏭
**Purpose:** Facility-specific features

**Note:** Limited functionality, mostly integrated into other modules.

---

## 4. Security & Permissions

### Security System Overview

The Verax application uses a **Role-Based Access Control (RBAC)** system:

1. **Activities (Permissions)** - Specific actions users can perform
2. **Roles** - Collections of activities bundled together
3. **Users** - Assigned roles which give them specific activities
4. **Guards** - Check permissions before allowing access

### Security Architecture

```
User
 ├── Role 1 (Sales Manager)
 │    ├── Activity: view all quotes
 │    ├── Activity: manage quotes
 │    └── Activity: view all opportunities
 ├── Role 2 (Customer Service)
 │    ├── Activity: view companies
 │    └── Activity: add contacts
 └── Individual Activities
      └── Activity: upload my own documents
```

### Activity Categories

| Category | Purpose |
|----------|---------|
| **Accounting** | Financial operations |
| **CRM** | Customer relationship management |
| **Inventory System** | Stock and materials |
| **Purchasing** | Vendor and procurement |
| **Workflow** | Manufacturing and production |
| **Service** | Service and repair operations |
| **HRM** | Employee management |
| **Attendance System** | Time tracking |
| **Dashboard** | Personal workspace |
| **Scheduling** | Production scheduling |
| **Facility** | System-wide settings |
| **Processes** | Business process management |

### Activity Subcategories

- Accounts Receivable
- Accounts Payable
- Chart of Accounts
- General Ledger
- Companies
- Contacts
- Leads
- Opportunities
- Quotes
- Jobs
- Work Orders
- Employees
- Time & Attendance
- And many more...

---

## 5. All Security Activities

### Complete Activity List (180 Activities)

#### Accounting Activities (25)

1. **account receivable payments** - Process customer payments
2. **adjust purchasing accrual** - Adjust accrual entries
3. **bank reconciliation** - Reconcile bank accounts
4. **inventory reports with cost** - View inventory with cost data
5. **manage account receivable invoice** - Create/edit AR invoices
6. **manage account receivable invoice - service** - AR invoices for service
7. **manage bill payments** - Process vendor payments
8. **manage chart of accounts** - Create/edit accounts
9. **manage financial reports settings** - Configure report templates
10. **manage payable invoice** - Create/edit AP invoices
11. **manage periods** - Define accounting periods
12. **mange accounting payment terms** - Define payment terms
13. **override balancing check for labor report** - Skip balance validation
14. **record general journal entries** - Post journal entries
15. **view account receivable invoice** - View AR invoices
16. **view account receivable reports** - Access AR reports
17. **view accrual aging report** - Access AP aging reports
18. **view all payables** - See all AP invoices
19. **view chart of accounts &trial balance & reports** - View accounting structure
20. **view financial reports** - Access financial statements
21. **view own payables** - See your own AP invoices
22. **view payable aging report** - View payment aging
23. **view purchasing reports for accounting** - Purchasing data for accounting
24. **view wip reports** - Work in progress reports
25. **year end** - Perform year-end closing

#### CRM Activities (15)

26. **add contacts** - Create new contacts
27. **add opportunities** - Create sales opportunities
28. **manage companies** - Add/edit customer companies
29. **manage contacts** - Edit contact information
30. **manage leads** - Create/edit/convert leads
31. **manage quotes** - Create/edit sales quotes
32. **view all contacts** - See all contacts in system
33. **view all leads** - See all sales leads
34. **view all opportunities** - See all opportunities
35. **view all quotes** - See all quotes in system
36. **view companies** - View customer list
37. **view own contacts** - See contacts you created
38. **view own leads** - See your own leads
39. **view own opportunities** - See your opportunities
40. **view own quotes** - See quotes you created

#### Purchasing Activities (10)

41. **manage purchase orders** - Create/edit POs
42. **manage purchase requisitions** - Handle material requests
43. **manage requests for quote** - Create/manage RFQs
44. **manage vendors and manufacturers** - Add/edit vendor records
45. **view all purchase orders** - See all POs
46. **view current demand** - See material requirements
47. **view purchase requisitions** - View requisition list
48. **view purchasing reports** - Access purchasing analytics
49. **view requests for quote** - View RFQ list
50. **view vendors and manufacturers** - View vendor list

#### Inventory System Activities (17)

51. **Add Job From Router** - Create jobs from routers
52. **adjust inventory stock** - Adjust quantities
53. **adjust material cost** - Modify item costs
54. **close work orders** - Complete work orders
55. **Create Raw Materials** - Add new raw materials
56. **inventory reports** - Basic inventory reports
57. **issue material to work order** - Issue materials to production
58. **issue to service demand** - Issue materials to service jobs
59. **manage inventory items** - Add/edit inventory items
60. **manage item tags** - Tag items for organization
61. **Manage Raw Materials** - Handle raw material definitions
62. **manage routers** - Create/edit manufacturing routings
63. **manage sell prices** - Set selling prices
64. **Receive Purchased Items** - Receive items from POs
65. **view inventory items** - View item list
66. **view routers** - View router list
67. **view sell prices** - View pricing information

#### Workflow Activities (41)

68. **actual Job Cost** - View actual job costs (special permission)
69. **add job notes** - Add notes to jobs
70. **clocking into Design Tasks** - Clock into design work
71. **create crs** - Create change requests
72. **Job Cost: Actual** - View actual job costs
73. **Job Cost: Fixed Rates** - View fixed-rate costing
74. **Job Cost: Hours Only** - View hour-based costing
75. **manage crs** - Edit change requests
76. **manage customers & facilities** - Add/edit facility data
77. **manage distributors** - Add/edit distributors
78. **Manage design Tasks** - Manage design workflow
79. **manage estimated completion of job** - Set completion dates
80. **manage item movements** - Track material movements
81. **manage jobs** - Create/edit production jobs
82. **manage all attachments** - Manage all order attachments
83. **manage all demand** - Manage all material demands
84. **manage all expenses** - Manage all order expenses
85. **manage all notes** - Manage all order notes
86. **manage own expenses** - Manage your own expenses
87. **manage root cause analysis** - Handle RCA documentation
88. **manage sales orders** - Handle order processing
89. **manage shippers** - Create/edit shipments
90. **modify work orders** - Edit work order details
91. **move supply and demand work orders** - Transfer materials
92. **override operation holds** - Override production holds
93. **print labor operations** - Print labor tickets
94. **print work order** - Print work documentation
95. **release work** - Release work to production
96. **request outside operations** - Request vendor services
97. **review all operation estimates** - Review time estimates
98. **Review MPT Process** - Review make-to-print jobs
99. **send work orders to production** - Release to floor
100. **view crs** - View change request list
101. **view customers & facilities** - View facility list
102. **view distributors** - View distributor list
103. **view item movements** - View movement history
104. **view jobs** - View job list
105. **view sales orders** - View order list
106. **view shippers** - View shipment list
107. **view work flow reports** - Access workflow reports
108. **view work orders** - View work order list

#### Service Activities (22)

109. **approve service order for billing** - Approve for invoicing
110. **clocking into service** - Clock into service work
111. **manage all service job notes** - Manage job notes
112. **manage all service order attachments** - Manage attachments
113. **manage all service order demands** - Manage material needs
114. **manage all service order expenses** - Manage all expenses
115. **manage all service order notes** - Manage order notes
116. **manage estimated completion of service job** - Set completion dates
117. **manage machines** - Add/edit equipment records
118. **manage own service order expenses** - Manage your expenses
119. **manage service jobs** - Create/edit service jobs
120. **manage service order shippers** - Handle service shipments
121. **manage service orders** - Handle service orders
122. **manage service quotes** - Create/edit service quotes
123. **override service order status** - Override status rules
124. **view all service quotes** - See all service quotes
125. **view machines** - View equipment list
126. **view own service quotes** - See your service quotes
127. **view service jobs** - View service job list
128. **view service orders** - View order list
129. **view service reports** - Access service analytics
130. **view service shippers** - View shipment list

#### HRM Activities (4)

131. **manage direct report employees** - Manage your direct reports
132. **manage employees** - Add/edit employee records
133. **manage employees sensitive information** - Access sensitive data
134. **view employees** - View employee list

#### Attendance System Activities (10)

135. **clocking into work orders** - Clock into production work
136. **edit attendance** - Edit time entries
137. **edit previous attendance** - Edit past time records
138. **manage employee times balancing access** - Balance time records
139. **override location checks** - Clock in from any location
140. **override next operation** - Skip operation sequence
141. **restricted web clock in** - Limited web clock access
142. **view all employee time records** - Access all time data
143. **view employee times balancing access** - View balance tools
144. **web clock in** - Use web-based time clock

#### Dashboard Activities (3)

145. **manage open tasks** - Create/edit tasks
146. **switch between desktop and mobile view** - Toggle views
147. **upload my own documents** - Upload personal files

#### Scheduling Activities (2)

148. **manage scheduling** - Access scheduling tools
149. **view scheduling** - View production schedules

#### Facility (System Settings) Activities (31)

150. **accept advance payment** - Accept customer advance payments
151. **manage all list options** - Manage dropdown options
152. **manage attachment categories** - Define attachment types
153. **manage departments** - Add/edit departments
154. **manage operations** - Add/edit operations
155. **manage product lines** - Add/edit product lines
156. **manage security roles and activities** - Configure permissions
157. **manage shifts** - Define work shifts
158. **manage shop locations** - Facility locations
159. **manage site settings** - Configure system-wide settings
160. **manage storage areas** - Add/edit storage locations
161. **manage taxes** - Configure tax settings
162. **manage time clock machines** - Configure time clocks
163. **manage work centers** - Add/edit work centers
164. **Manage Licenses** - Manage software licenses
165. **modify user interface** - Customize UI
166. **register fingerprints in tpiclock** - Enroll biometrics
167. **Restricted access to Security Activities** - Limited security view
168. **view all attachments** - View all document attachments
169. **view currencies** - View currency list
170. **view departments** - View department list
171. **view operations** - View operation list
172. **view product lines** - View product line list
173. **view security roles and activities** - View security setup
174. **view shifts** - View shift list
175. **view shop locations** - View shop locations
176. **view storage areas** - View storage locations
177. **view taxes** - View tax configuration
178. **view time clock machines** - View clock setup
179. **view user interface** - View UI settings
180. **view work centers** - View work center list

---

## 6. Module Permissions Guide

### 6.1 Dashboard Module

| **Feature** | **View** | **Create** | **Edit** | **Delete** |
|------------|----------|-----------|----------|-----------|
| **My Tasks** | No permission | `manage open tasks` | `manage open tasks` | `manage open tasks` |
| **Others' Tasks** | `manage open tasks` | `manage open tasks` | `manage open tasks` | `manage open tasks` |
| **Calendar Events** | No permission | No permission | Owner/Admin | Owner/Admin |
| **Profile** | No permission | N/A | No permission | N/A |
| **Upload Documents** | N/A | `upload my own documents` | N/A | N/A |
| **Org Chart** | `view employees` | N/A | N/A | N/A |

---

### 6.2 CRM Module

| **Feature** | **View All** | **View Own** | **Create** | **Edit** | **Delete** |
|------------|-------------|-------------|-----------|----------|-----------|
| **Companies** | `view companies` | N/A | `manage companies` | `manage companies` | `manage companies` |
| **Contacts** | `view all contacts` | `view own contacts` | `add contacts` OR `manage contacts` | `manage contacts` | `manage contacts` |
| **Leads** | `view all leads` | `view own leads` | `manage leads` | `manage leads` | `manage leads` |
| **Opportunities** | `view all opportunities` | `view own opportunities` | `add opportunities` | View permission + edit | View permission + delete |
| **Quotes** | `view all quotes` | `view own quotes` | `manage quotes` | `manage quotes` | `manage quotes` |

**Special Operations:**
- **Convert Lead to Opportunity:** `manage leads`
- **Convert Opportunity to Job:** `view all opportunities` (or own) + `manage jobs`
- **Convert Quote to Job:** `manage quotes` + `manage jobs`
- **Copy Quote:** `manage quotes`
- **Accept Advance Payment:** `accept advance payment`

---

### 6.3 Accounting Module

| **Feature** | **View** | **Create** | **Edit** | **Delete** |
|------------|----------|-----------|----------|-----------|
| **Chart of Accounts** | `view chart of accounts &trial balance & reports` | `manage chart of accounts` | `manage chart of accounts` | `manage chart of accounts` |
| **AP Invoices (All)** | `view all payables` | `manage payable invoice` | `manage payable invoice` | `manage payable invoice` |
| **AP Invoices (Own)** | `view own payables` | `manage payable invoice` | `manage payable invoice` | `manage payable invoice` |
| **AR Invoices** | `view account receivable invoice` | `manage account receivable invoice` | `manage account receivable invoice` | `manage account receivable invoice` |
| **AR Service Invoices** | `view account receivable invoice` | `manage account receivable invoice - service` | `manage account receivable invoice - service` | `manage account receivable invoice - service` |
| **Journal Entries** | `record general journal entries` | `record general journal entries` | `record general journal entries` | `record general journal entries` |
| **Periods** | `manage periods` | `manage periods` | `manage periods` | `manage periods` |
| **Billing Types** | `manage site settings` | `manage site settings` | `manage site settings` | `manage site settings` |

**Special Operations:**
- **Process AR Payments:** `account receivable payments`
- **Process AP Payments:** `manage bill payments`
- **Adjust Accruals:** `adjust purchasing accrual`
- **Bank Reconciliation:** `bank reconciliation`
- **Year End Close:** `year end`
- **View Financial Reports:** `view financial reports`
- **Configure Reports:** `manage financial reports settings`
- **View AR Reports:** `view account receivable reports`
- **View AP Aging:** `view accrual aging report` or `view payable aging report`
- **View WIP Reports:** `view wip reports`

---

### 6.4 Purchasing Module

| **Feature** | **View** | **Create** | **Edit** | **Delete** |
|------------|----------|-----------|----------|-----------|
| **Vendors** | `view vendors and manufacturers` | `manage vendors and manufacturers` | `manage vendors and manufacturers` | `manage vendors and manufacturers` |
| **Manufacturers** | `view vendors and manufacturers` | `manage vendors and manufacturers` | `manage vendors and manufacturers` | `manage vendors and manufacturers` |
| **Purchase Orders** | `view all purchase orders` | `manage purchase orders` | `manage purchase orders` | `manage purchase orders` |
| **Requisitions** | `view purchase requisitions` | `manage purchase requisitions` | `manage purchase requisitions` | `manage purchase requisitions` |
| **RFQs** | `view requests for quote` | `manage requests for quote` | `manage requests for quote` | `manage requests for quote` |
| **Current Demand** | `view current demand` | N/A | N/A | N/A |

**Special Operations:**
- **Copy PO:** `manage purchase orders`
- **Receive Items:** `Receive Purchased Items`
- **Convert Requisition to PO:** `manage purchase requisitions` + `manage purchase orders`
- **View Purchasing Reports:** `view purchasing reports`
- **View Reports for Accounting:** `view purchasing reports for accounting`

---

### 6.5 Inventory Module

| **Feature** | **View** | **Create** | **Edit** | **Delete** |
|------------|----------|-----------|----------|-----------|
| **Items** | `view inventory items` | `manage inventory items` | `manage inventory items` | `manage inventory items` |
| **Inventory Items** | `view inventory items` | `manage inventory items` | `manage inventory items` | `manage inventory items` |
| **Routers** | `view routers` | `manage routers` | `manage routers` | `manage routers` |
| **Raw Materials** | `Manage Raw Materials` | `Create Raw Materials` | `Manage Raw Materials` | `Manage Raw Materials` |

**Special Operations:**
- **Add Stock:** `adjust inventory stock`
- **Move Items:** `manage inventory items`
- **Scrap Items:** `manage inventory items`
- **Adjust Costs:** `adjust material cost`
- **Manage Sell Prices:** `manage sell prices`
- **View Sell Prices:** `view sell prices`
- **Manage Tags:** `manage item tags`
- **Issue to Work Order:** `issue material to work order`
- **Issue to Service:** `issue to service demand`
- **Receive PO:** `Receive Purchased Items`
- **Close Work Order:** `close work orders`
- **Add Job from Router:** `Add Job From Router`
- **View Reports:** `inventory reports`
- **View Reports with Cost:** `inventory reports with cost`

---

### 6.6 Workflow Module

| **Feature** | **View** | **Create** | **Edit** | **Delete** |
|------------|----------|-----------|----------|-----------|
| **Jobs** | `view jobs` | `manage jobs` | `manage jobs` | `manage jobs` |
| **Work Orders** | `view work orders` | `modify work orders` | `modify work orders` | `modify work orders` |
| **Designs** | (Part of jobs) | `Manage design Tasks` | `Manage design Tasks` | `Manage design Tasks` |
| **Change Requests** | `view crs` | `create crs` | `manage crs` | `manage crs` |
| **Facilities** | `view customers & facilities` | `manage customers & facilities` | `manage customers & facilities` | `manage customers & facilities` |

**Special Operations:**
- **Copy Job:** `manage jobs`
- **Close/Reopen Job:** `manage jobs`
- **Add Job Notes:** `add job notes` OR `manage all notes`
- **Manage All Expenses:** `manage all expenses`
- **Manage Own Expenses:** `manage own expenses`
- **View Job Costs:** `Job Cost: Actual` OR `Job Cost: Fixed Rates` OR `Job Cost: Hours Only`
- **Set Completion Date:** `manage estimated completion of job`
- **Issue Materials:** `issue material to work order`
- **Close Work Orders:** `close work orders`
- **Move Supply/Demand:** `move supply and demand work orders`
- **Release to Production:** `send work orders to production` OR `release work`
- **Print Work Order:** `print work order`
- **Print Labor:** `print labor operations`
- **Request Outside Operations:** `request outside operations`
- **Root Cause Analysis:** `manage root cause analysis`
- **Override Holds:** `override operation holds`
- **View Movements:** `view item movements`
- **Manage Movements:** `manage item movements`
- **Review Estimates:** `review all operation estimates`
- **Review MPT:** `Review MPT Process`
- **Clock into Designs:** `clocking into Design Tasks`
- **View Reports:** `view work flow reports`

---

### 6.7 Service Module

| **Feature** | **View** | **Create** | **Edit** | **Delete** |
|------------|----------|-----------|----------|-----------|
| **Service Jobs** | `view service jobs` | `manage service jobs` | `manage service jobs` | `manage service jobs` |
| **Service Issues** | `view service orders` | `manage service orders` | `manage service orders` | `manage service orders` |
| **Service Quotes (All)** | `view all service quotes` | `manage service quotes` | `manage service quotes` | `manage service quotes` |
| **Service Quotes (Own)** | `view own service quotes` | `manage service quotes` | `manage service quotes` | `manage service quotes` |
| **Machines** | `view machines` | `manage machines` | `manage machines` | `manage machines` |

**Special Operations:**
- **Add Job Notes:** `manage all service job notes`
- **Set Completion:** `manage estimated completion of service job`
- **Approve for Billing:** `approve service order for billing`
- **Override Status:** `override service order status`
- **Manage All Attachments:** `manage all service order attachments`
- **Manage All Demands:** `manage all service order demands`
- **Manage All Expenses:** `manage all service order expenses`
- **Manage Own Expenses:** `manage own service order expenses`
- **Manage All Notes:** `manage all service order notes`
- **Clock into Service:** `clocking into service`
- **Manage Shippers:** `manage service order shippers`
- **View Shippers:** `view service shippers`
- **View Reports:** `view service reports`

---

### 6.8 HRM Module

| **Feature** | **View** | **Create** | **Edit** | **Delete** |
|------------|----------|-----------|----------|-----------|
| **Employees** | `view employees` | `manage employees` | `manage employees` | `manage employees` |
| **Employee Sensitive Info** | `manage employees sensitive information` | N/A | `manage employees sensitive information` | N/A |
| **Direct Reports Only** | `manage direct report employees` | `manage direct report employees` | `manage direct report employees` | `manage direct report employees` |

---

### 6.9 Attendance Module

| **Feature** | **Permission Required** |
|------------|----------------------|
| **Web Clock In** | `web clock in` |
| **Restricted Clock In** | `restricted web clock in` |
| **Clock into Work Orders** | `clocking into work orders` |
| **Clock into Service** | `clocking into service` |
| **Clock into Designs** | `clocking into Design Tasks` |
| **Override Location** | `override location checks` |
| **Override Next Operation** | `override next operation` |
| **View All Time Records** | `view all employee time records` |
| **Edit Attendance** | `edit attendance` |
| **Edit Previous Attendance** | `edit previous attendance` |
| **Access Balance Tools** | `manage employee times balancing access` |
| **View Balance Tools** | `view employee times balancing access` |
| **Override Balance Checks** | `override balancing check for labor report` |

---

### 6.10 Scheduling Module

| **Feature** | **View** | **Manage** |
|------------|----------|-----------|
| **All Scheduling Features** | `view scheduling` | `manage scheduling` |

---

### 6.11 Setup Module

| **Feature** | **View** | **Create/Edit/Delete** |
|------------|----------|----------------------|
| **Security Settings** | `view security roles and activities` | `manage security roles and activities` |
| **Restricted Security** | `Restricted access to Security Activities` | (Limited access) |
| **Departments** | `view departments` | `manage departments` |
| **Product Lines** | `view product lines` | `manage product lines` |
| **Storage Areas** | `view storage areas` | `manage storage areas` |
| **Work Centers** | `view work centers` | `manage work centers` |
| **Operations** | `view operations` | `manage operations` |
| **Currencies** | `view currencies` | (Implied through facility settings) |
| **Shifts** | `view shifts` | `manage shifts` |
| **List Options** | N/A | `manage all list options` |
| **Payment Terms** | N/A | `mange accounting payment terms` |
| **Site Settings** | N/A | `manage site settings` |
| **User Interface** | `view user interface` | `modify user interface` |
| **Licenses** | `Manage Licenses` | `Manage Licenses` |

---

## 7. Operations Summary

### 7.1 CREATE Operations

| **Module** | **Entity** | **Required Permission** |
|-----------|-----------|------------------------|
| **CRM** | Contact | `add contacts` OR `manage contacts` |
| | Lead | `manage leads` |
| | Opportunity | `add opportunities` |
| | Quote | `manage quotes` |
| | Customer/Company | `manage companies` |
| **Accounting** | Account | `manage chart of accounts` |
| | AP Invoice | `manage payable invoice` |
| | AR Invoice | `manage account receivable invoice` |
| | AR Service Invoice | `manage account receivable invoice - service` |
| | Journal Entry | `record general journal entries` |
| | Period | `manage periods` |
| **Purchasing** | Vendor | `manage vendors and manufacturers` |
| | Manufacturer | `manage vendors and manufacturers` |
| | Purchase Order | `manage purchase orders` |
| | Requisition | `manage purchase requisitions` |
| | RFQ | `manage requests for quote` |
| **Inventory** | Item | `manage inventory items` |
| | Router | `manage routers` |
| | Raw Material | `Create Raw Materials` |
| **Workflow** | Job | `manage jobs` |
| | Work Order | `modify work orders` |
| | Change Request | `create crs` |
| | Facility | `manage customers & facilities` |
| **Service** | Service Job | `manage service jobs` |
| | Service Issue | `manage service orders` |
| | Service Quote | `manage service quotes` |
| | Machine | `manage machines` |
| **HRM** | Employee | `manage employees` |
| **Attendance** | Time Entry | `edit attendance` |
| **Setup** | Department | `manage departments` |
| | Product Line | `manage product lines` |
| | Work Center | `manage work centers` |
| | Operation | `manage operations` |
| | Storage Area | `manage storage areas` |
| | Shift | `manage shifts` |

---

### 7.2 EDIT Operations

| **Module** | **Entity** | **Required Permission** |
|-----------|-----------|------------------------|
| **CRM** | Contact | `manage contacts` |
| | Lead | `manage leads` |
| | Opportunity | `view all opportunities` OR `view own opportunities` |
| | Quote | `manage quotes` |
| | Company | `manage companies` |
| **Accounting** | Account | `manage chart of accounts` |
| | AP Invoice | `manage payable invoice` |
| | AR Invoice | `manage account receivable invoice` |
| | Journal Entry | `record general journal entries` |
| **Purchasing** | Vendor | `manage vendors and manufacturers` |
| | Purchase Order | `manage purchase orders` |
| | Requisition | `manage purchase requisitions` |
| **Inventory** | Item | `manage inventory items` |
| | Router | `manage routers` |
| | Item Price | `manage sell prices` |
| | Item Cost | `adjust material cost` |
| | Stock Quantity | `adjust inventory stock` |
| **Workflow** | Job | `manage jobs` |
| | Work Order | `modify work orders` |
| | Change Request | `manage crs` |
| | Facility | `manage customers & facilities` |
| **Service** | Service Job | `manage service jobs` |
| | Service Issue | `manage service orders` |
| | Machine | `manage machines` |
| **HRM** | Employee | `manage employees` |
| | Employee Sensitive Info | `manage employees sensitive information` |
| **Attendance** | Time Entry | `edit attendance` |
| | Previous Time Entry | `edit previous attendance` |
| **Setup** | Site Settings | `manage site settings` |
| | Security Role | `manage security roles and activities` |
| | List Options | `manage all list options` |

---

### 7.3 DELETE Operations

| **Module** | **Entity** | **Required Permission** |
|-----------|-----------|------------------------|
| **CRM** | Contact | `manage contacts` |
| | Lead | `manage leads` |
| | Opportunity | `view all opportunities` OR `view own opportunities` |
| | Quote | `manage quotes` |
| | Company | `manage companies` |
| **Accounting** | Account | `manage chart of accounts` |
| | Invoice | `manage payable invoice` OR `manage account receivable invoice` |
| **Purchasing** | Vendor | `manage vendors and manufacturers` |
| | Purchase Order | `manage purchase orders` |
| | Requisition | `manage purchase requisitions` |
| | RFQ | `manage requests for quote` |
| **Inventory** | Item | `manage inventory items` |
| | Router | `manage routers` |
| **Workflow** | Job | `manage jobs` |
| | Work Order | `modify work orders` |
| | Change Request | `manage crs` |
| **Service** | Service Job | `manage service jobs` |
| | Service Issue | `manage service orders` |
| | Service Quote | `manage service quotes` |
| | Machine | `manage machines` |
| **HRM** | Employee | `manage employees` |
| **Attendance** | Time Entry | `edit attendance` |
| **Setup** | Department | `manage departments` |
| | Product Line | `manage product lines` |
| | Work Center | `manage work centers` |
| | Operation | `manage operations` |
| | Storage Area | `manage storage areas` |

---

### 7.4 VIEW Operations

| **Entity** | **View All Permission** | **View Own Permission** |
|-----------|----------------------|----------------------|
| **Contacts** | `view all contacts` | `view own contacts` |
| **Leads** | `view all leads` | `view own leads` |
| **Opportunities** | `view all opportunities` | `view own opportunities` |
| **Quotes** | `view all quotes` | `view own quotes` |
| **Service Quotes** | `view all service quotes` | `view own service quotes` |
| **Purchase Orders** | `view all purchase orders` | N/A |
| **Payables** | `view all payables` | `view own payables` |
| **Employee Time** | `view all employee time records` | (Own by default) |

---

### 7.5 Special Operations

| **Operation** | **Required Permission** |
|--------------|------------------------|
| **Convert Lead to Opportunity** | `manage leads` |
| **Convert Opportunity to Job** | View opportunity permission + `manage jobs` |
| **Convert Quote to Job** | `manage quotes` + `manage jobs` |
| **Copy Quote** | `manage quotes` |
| **Copy Job** | `manage jobs` |
| **Accept Advance Payment** | `accept advance payment` |
| **Process AR Payment** | `account receivable payments` |
| **Process AP Payment** | `manage bill payments` |
| **Adjust Accrual** | `adjust purchasing accrual` |
| **Bank Reconciliation** | `bank reconciliation` |
| **Year End Close** | `year end` |
| **Issue Material to Work Order** | `issue material to work order` |
| **Issue Material to Service** | `issue to service demand` |
| **Receive PO Items** | `Receive Purchased Items` |
| **Close Work Order** | `close work orders` |
| **Release Work** | `release work` OR `send work orders to production` |
| **Print Work Order** | `print work order` |
| **Print Labor Operations** | `print labor operations` |
| **Request Outside Operations** | `request outside operations` |
| **Move Supply/Demand** | `move supply and demand work orders` |
| **Override Operation Holds** | `override operation holds` |
| **Approve Service for Billing** | `approve service order for billing` |
| **Override Service Status** | `override service order status` |
| **Clock In (Web)** | `web clock in` |
| **Clock In (Restricted)** | `restricted web clock in` |
| **Clock into Work Order** | `clocking into work orders` |
| **Clock into Service** | `clocking into service` |
| **Clock into Design** | `clocking into Design Tasks` |
| **Override Location Check** | `override location checks` |
| **Override Next Operation** | `override next operation` |
| **Balance Employee Time** | `manage employee times balancing access` |
| **Override Balance Check** | `override balancing check for labor report` |
| **Add Job from Router** | `Add Job From Router` |
| **Review Operation Estimates** | `review all operation estimates` |
| **Review MPT Process** | `Review MPT Process` |
| **Upload Own Documents** | `upload my own documents` |
| **Switch Desktop/Mobile** | `switch between desktop and mobile view` |
| **Root Cause Analysis** | `manage root cause analysis` |
| **Register Fingerprints** | `register fingerprints in tpiclock` |

---

## 8. Role Management

### 8.1 How to Access Security Settings

**Location:** Setup → Security Settings

**Required Permission:**
- `manage security roles and activities` - Full access
- `view security roles and activities` - View only
- `Restricted access to Security Activities` - Limited view

---

### 8.2 Managing Roles

#### View Existing Roles
1. Navigate to **Setup → Security**
2. Click on **Roles** tab
3. View list of all defined roles

#### Create New Role
1. Click **"+ Add Role"** or **"Create Role"**
2. Enter role name (e.g., "Production Manager")
3. Enter description
4. Click **Save**

#### Edit Role
1. Find role in list
2. Click **edit icon** (pencil)
3. Modify name/description
4. Click **Save**

#### Delete Role
1. Find role in list
2. Click **delete icon** (trash)
3. Confirm deletion
   - **Note:** Can only delete if no users are assigned

---

### 8.3 Assigning Activities to Roles

1. Select a role from the list
2. View **"Role Activities"** panel
3. Browse available activities (organized by category)
4. **Check boxes** next to activities to assign
5. **Uncheck boxes** to remove activities
6. Click **Save changes**

**Tip:** Use category filters to find activities quickly.

---

### 8.4 Assigning Roles/Activities to Users

#### Assign Roles
1. Go to **User management**
2. Select a user
3. View **"User Roles"** panel
4. Select roles to assign
5. User inherits all activities from all assigned roles
6. Click **Save**

#### Assign Individual Activities
1. Go to **User management**
2. Select a user
3. View **"User Activities"** panel
4. Check activities to assign directly
5. These are in addition to role-based activities
6. Click **Save**

---

### 8.5 Typical Role Examples

#### Sales Manager Role
**Suggested Activities:**
- `view all leads`
- `manage leads`
- `view all opportunities`
- `add opportunities`
- `view all quotes`
- `manage quotes`
- `view all contacts`
- `manage contacts`
- `view companies`
- `manage companies`
- `view jobs`

---

#### Accountant Role
**Suggested Activities:**
- `manage chart of accounts`
- `manage payable invoice`
- `view all payables`
- `manage bill payments`
- `manage account receivable invoice`
- `account receivable payments`
- `record general journal entries`
- `view financial reports`
- `manage periods`
- `view chart of accounts &trial balance & reports`

---

#### Production Manager Role
**Suggested Activities:**
- `view jobs`
- `manage jobs`
- `view work orders`
- `modify work orders`
- `release work`
- `send work orders to production`
- `view scheduling`
- `manage scheduling`
- `view inventory items`
- `issue material to work order`
- `close work orders`
- `print work order`
- `print labor operations`

---

#### Shop Floor Operator Role
**Suggested Activities:**
- `view jobs`
- `view work orders`
- `clocking into work orders`
- `web clock in`

---

#### Purchasing Agent Role
**Suggested Activities:**
- `view vendors and manufacturers`
- `manage vendors and manufacturers`
- `view all purchase orders`
- `manage purchase orders`
- `view purchase requisitions`
- `manage purchase requisitions`
- `view requests for quote`
- `manage requests for quote`
- `view current demand`
- `Receive Purchased Items`

---

#### Service Technician Role
**Suggested Activities:**
- `view service orders`
- `manage service orders`
- `clocking into service`
- `view machines`
- `manage own service order expenses`
- `view service jobs`

---

#### HR Manager Role
**Suggested Activities:**
- `view employees`
- `manage employees`
- `manage employees sensitive information`
- `view all employee time records`
- `edit attendance`
- `manage employee times balancing access`

---

#### System Administrator Role
**Suggested Activities:**
- `manage security roles and activities`
- `manage site settings`
- `manage all list options`
- `manage departments`
- `manage work centers`
- `manage operations`
- `manage product lines`
- `manage storage areas`
- `manage shifts`
- `modify user interface`
- `Manage Licenses`
- `view currencies`
- (Plus many more as needed)

---

## 9. Configuration Guide

### 9.1 Environment Configuration

**Files:**
- `src/environments/environment.ts` (Development)
- `src/environments/environment.prod.ts` (Production)
- `src/environments/environment.qa.ts` (QA)
- `src/environments/environment.stage.ts` (Staging)

**Purpose:** Configure API connection

**Example:**
```typescript
export const environment = {
  production: false,
  api: {
    baseUrl: 'https://localhost:5001'
  }
};
```

**Who Configures:** IT/DevOps team

---

### 9.2 Site-Wide Settings

**Location:** Setup → Setup (Site Wide Settings)

**Required Permission:** `manage site settings`

**Settings Include:**
- **Service Enabled:** Enable/disable service module
- **Buyer Users:** Users who can purchase
- **Sales Representative Users:** Sales team members
- **Company Name:** Organization name
- **Accounting Year Start:** Fiscal year start month
- **Combine Routers Only Within Jobs:** Router combining rules
- **Labor Report Download for Payroll:** Payroll export settings

---

### 9.3 Non-Accounting Site Wide Settings

**Location:** Setup → Settings → Non-Accounting

**Purpose:** General business rules and behaviors

---

### 9.4 Accounting Settings

**Location:** Accounting → Settings → Manage Settings

**Configuration:**
- **AP (Accounts Payable) Accounts:** Default payable accounts
- **AR (Accounts Receivable) Accounts:** Default receivable accounts
- **Year-End Settings:** Year-end closing configuration
- **Billing Settings:** Billing defaults

---

### 9.5 Page Display Settings

**What:** Customize how tables and lists appear

**Where:** Each page with tables has customization icon (gear or settings)

**Stored:** Database per user per page

**Service:** `PageSettingsService`

**User Can Customize:**
- Visible columns
- Column order
- Column width
- Pinned columns
- Sort order
- Filters

---

### 9.6 Security Settings

**Location:** Setup → Security Settings

**Required Permission:** `manage security roles and activities`

**Configuration:**
- Define roles
- Assign activities to roles
- Assign roles to users
- Assign individual activities to users

---

### 9.7 User Interface Settings

**Location:** Setup → User Interface

**Required Permission:**
- View: `view user interface`
- Edit: `modify user interface`

**Controls:**
- Theme selection (Lux, Pulse, Tarus, Tarus-Alt)
- Color scheme
- Default behaviors

---

### 9.8 License Management

**Location:** Administration → Licensing

**Required Permission:** `Manage Licenses`

**Controls:**
- Which modules are enabled
- Feature availability
- User limits

---

### 9.9 Application Module Settings

**File:** `src/app/app.module.ts`

**Configuration:**
- **Toast Notifications:**
  - Position: 'toast-bottom-right'
  - Timeout: 2000ms
  - Tap to dismiss: true

- **Confirmation Popovers:**
  - Append to body: true
  - Default message: "Are you sure?"
  - Button styles

- **Date Picker:**
  - Format settings
  - Locale settings

---

## 10. Troubleshooting

### 10.1 Common Access Issues

#### Issue: User Can't Access a Page

**Possible Causes & Solutions:**

1. **Not logged in**
   - Solution: Log in with valid credentials

2. **No tenant selected**
   - Solution: Select a company from tenant dropdown

3. **Missing permission**
   - Check: User's roles and activities
   - Solution: Assign appropriate role or activity

4. **License doesn't include feature**
   - Check: License management
   - Solution: Enable feature in license

5. **Page requires specific security activity**
   - Check: Page's route configuration for required activities
   - Solution: Assign required activity to user

**How to Check User Permissions:**
1. Go to **Setup → Security**
2. Find the user
3. View **"User Activities"** tab
4. Check assigned roles
5. Check individual activities

---

#### Issue: User Can See Page But Can't Edit

**Cause:** User has "view" permission but not "manage" permission

**Example:**
- `view quotes` allows viewing quotes
- `manage quotes` allows creating/editing/deleting quotes

**Solution:** Assign the "manage" permission in addition to "view"

---

#### Issue: User Says "Access Denied"

**Cause:** Missing required security activity

**Solution:**
1. Identify which page they're trying to access
2. Check route configuration for required activities
3. Assign appropriate role or individual activity
4. User may need to log out and back in

---

### 10.2 Security Check Operations

**"All" Operation:**
- User must have ALL listed activities
- Example: Page requires activities A, B, and C
- User must have all three

**"Any" Operation:**
- User must have AT LEAST ONE of the listed activities
- Example: Page requires activities A, B, or C
- User needs only one of them

---

### 10.3 Data-Level Security

#### View All vs View Own

Some permissions are scoped:

| **Permission** | **Scope** | **Example** |
|---------------|-----------|-------------|
| `view all quotes` | All quotes in system | See everyone's quotes |
| `view own quotes` | Only user's quotes | See only quotes you created |
| `view all opportunities` | All opportunities | See entire sales pipeline |
| `view own opportunities` | Only user's opportunities | See only your opportunities |
| `view all contacts` | All contacts | See all customer contacts |
| `view own contacts` | Only user's contacts | See only contacts you added |

**Troubleshooting:**
- If user can't see records they expect to see, check if they have "all" vs "own" permission
- Users with "own" permission can only see records they created

---

### 10.4 Route Guards

The application uses several guards to protect routes:

1. **HasActivitiesGuard**
   - Checks if user has required security activities
   - Redirects to error page if check fails

2. **TenantSelectedGuard**
   - Ensures a company (tenant) is selected
   - Redirects to tenant selection if needed

3. **UsersSettingsLoadedGuard**
   - Loads user settings before page access
   - Ensures user preferences are available

4. **PageSettingsLoadedGuard**
   - Loads page-specific settings
   - Ensures table configurations are loaded

5. **SearchFiltersLoadedGuard**
   - Loads search filter configurations
   - Ensures filters are available

---

### 10.5 Best Practices

#### Role Design
- ✅ Create roles based on job functions
- ✅ Use descriptive role names
- ❌ Don't create a role for each individual person
- ✅ Group related activities together

#### Security Principles
- ✅ **Principle of Least Privilege:** Give only necessary permissions
- ✅ **Regular Audits:** Review user access quarterly
- ✅ **Test New Roles:** Test with test accounts before assigning
- ✅ **Document:** Keep records of who has admin access

#### User Management
- ✅ Remove access for terminated employees immediately
- ✅ Update permissions when roles change
- ✅ Use roles instead of individual activity assignments when possible
- ✅ Document any custom permission assignments

---

### 10.6 Testing Security

#### Test New Roles
1. Create test user account
2. Assign new role
3. Log in as test user
4. Verify access to expected pages
5. Verify restriction from unauthorized pages
6. Test CRUD operations

#### Verify Permissions
1. Document what role should access
2. Test each major function
3. Verify data visibility (all vs own)
4. Test special operations (convert, approve, etc.)

---

## Appendix A: Quick Reference

### Module Access Summary

| **Module** | **Main Permission Pattern** |
|-----------|-----------------------------|
| **Dashboard** | Mostly open access |
| **CRM** | `view/manage` + entity name |
| **Accounting** | `view/manage` + entity name |
| **Purchasing** | `view/manage` + entity name |
| **Inventory** | `view/manage` + entity name |
| **Workflow** | `view/manage` + entity name |
| **Service** | `view/manage service` + entity |
| **HRM** | `view/manage employees` |
| **Attendance** | `web clock in`, `edit attendance` |
| **Scheduling** | `view/manage scheduling` |
| **Setup** | `view/manage` + setting type |

---

### Permission Naming Patterns

| **Pattern** | **Example** | **Meaning** |
|------------|-------------|-------------|
| **view [entity]** | `view jobs` | Can see list and details |
| **manage [entity]** | `manage jobs` | Can create, edit, delete |
| **view all [entity]** | `view all quotes` | Can see everyone's records |
| **view own [entity]** | `view own quotes` | Can see only own records |
| **add [entity]** | `add contacts` | Can create new records |
| **[action] [entity]** | `close work orders` | Specific operation |

---

## Appendix B: Configuration File Locations

### Key Files

| **Configuration** | **File Path** |
|------------------|---------------|
| **Environment** | `src/environments/environment*.ts` |
| **App Module** | `src/app/app.module.ts` |
| **Routing** | `src/app/app-routing.module.ts` |
| **Security Activities** | `src/app/modules/shared/modules/security/models/security-activities.defaults.ts` |
| **Page Settings** | `src/app/modules/core/constants/page-settings/` |
| **Search Filters** | `src/app/modules/core/constants/search-filters/` |
| **Navigation Menus** | `src/app/modules/application/constants/navigation-menus/` |
| **Styles** | `src/assets/scss/` |

---

## Appendix C: Contact & Support

For questions about this documentation or the Verax application:

- **Setup Issues:** Contact System Administrator
- **Permission Issues:** Contact System Administrator or HR
- **Technical Issues:** Contact IT Support
- **Feature Requests:** Contact Product Manager

---

## Document Information

**Document Version:** 1.0  
**Created:** November 2025  
**Format:** Markdown  
**For:** Verax Angular ERP System  
**File:** `VERAX_DOCUMENTATION.md`

---

**End of Documentation**

