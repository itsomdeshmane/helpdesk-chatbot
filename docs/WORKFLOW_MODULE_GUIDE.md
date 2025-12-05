# WORKFLOW MODULE - Complete User Guide

**Version:** 1.0  
**Last Updated:** November 2025  
**Application:** Verax ERP System

---

## Table of Contents

1. [What is the Workflow Module?](#what-is-the-workflow-module)
2. [Getting Started](#getting-started)
3. [Customer & Facility Management](#customer--facility-management)
4. [Jobs Management](#jobs-management)
5. [Work Orders](#work-orders)
6. [Designs](#designs)
7. [Change Requests](#change-requests)
8. [Release Work](#release-work)
9. [WIP Tracking](#wip-tracking)
10. [MPT (Make-to-Print)](#mpt-make-to-print)
11. [Active Work](#active-work)
12. [Manage Estimates](#manage-estimates)
13. [Reports](#reports)
14. [Vault](#vault)
15. [Common Tasks & Workflows](#common-tasks--workflows)
16. [Tips & Best Practices](#tips--best-practices)
17. [Troubleshooting](#troubleshooting)

---

## What is the Workflow Module?

The Workflow module is your command center for managing production and manufacturing operations. Think of it as the heart of your shop floor operations - from the moment a customer order comes in, through design and production, all the way to shipping.

### What You Can Do

- **Track Customer Orders** - Manage sales jobs from start to finish
- **Control Production** - Create and manage work orders for manufacturing
- **Design Management** - Track product design and approval processes  
- **Handle Changes** - Manage engineering change requests
- **Monitor Progress** - See what's happening on the shop floor in real-time
- **Schedule Work** - Release work to production when ready
- **Track Materials** - Follow work-in-process through your facility
- **Generate Reports** - Get insights into your manufacturing operations

### Who Uses This Module?

- **Production Managers** - Oversee manufacturing operations
- **Shop Floor Supervisors** - Manage daily production activities
- **Schedulers** - Plan and schedule work
- **Engineers** - Manage designs and change requests
- **Customer Service** - Check order status and completion dates
- **Management** - Review performance and costs

---

## Getting Started

### Accessing the Workflow Module

1. Log into Verax
2. Look for **"Workflow"** in the main navigation menu (left sidebar)
3. Click to expand and see all available options

### Navigation Structure

The Workflow module contains these main sections:

```
Workflow
├── Active Work (see what's being worked on now)
├── Change Requests (manage design changes)
├── Customers & Facilities (manage facility information)
├── Designs (product design workflow)
├── Manage Estimates (review operation time estimates)
├── Manage Jobs (create and track production jobs)
├── MPT (make-to-print job review)
├── Release Work (send work orders to production)
├── Shippers (track shipments)
├── WIP Tracking (track work-in-process)
├── Work Orders (detailed work order management)
├── Vault (document storage)
└── Workflow Reports (analytics and reporting)
```

### Required Permissions

Different features require different permissions. If you can't see or access something, contact your system administrator. Common permissions include:

- **View Jobs** - See job information
- **Manage Jobs** - Create and edit jobs
- **View Work Orders** - See work order details
- **Modify Work Orders** - Edit work orders
- **Release Work** - Send work to production
- **Clock into Work** - Track time on production tasks

---

## Customer & Facility Management

### Overview

In Workflow, you manage facility-level information for your customers. This is where you keep track of where to ship products, who to contact, and payment details.

### Viewing Facilities

**To See Your Facility List:**

1. Go to **Workflow → Customers & Facilities**
2. You'll see a searchable list of all facilities
3. Use the search box to find specific customers
4. Click on any facility name to see detailed information

### Facility Details

When you open a facility, you'll see multiple tabs with information:

#### Details Tab
- Company name and contact information
- Billing address
- Phone numbers and email
- Payment terms
- Account status

#### Addresses Tab
- All shipping and billing addresses for this facility
- Add new addresses as needed
- Edit existing addresses

#### Opportunities Tab
- Sales opportunities in progress
- Potential orders you're working on
- Win probability and expected value

#### Quotes Tab
- All quotes you've provided to this customer
- Quote status (pending, accepted, rejected)
- Quick access to convert quotes to jobs

#### Jobs Tab
- All production jobs for this facility
- Current status and completion dates
- Quick access to job details

#### Machines Tab
- Equipment owned by this customer
- Service history
- Maintenance records

#### Account History Tab
- Payment history
- Invoices and receipts
- Account balance

### Creating a New Facility

**Step-by-Step:**

1. Go to **Workflow → Customers & Facilities**
2. Click the **"+ Add"** or **"Create"** button
3. Fill in required information:
   - **Company Name** (required)
   - **Status** (Active, Inactive, etc.)
   - **Ownership Type** (if applicable)
   - **Industry Type**
4. Add contact information:
   - Phone number
   - Email address
   - Website
5. Set up billing information:
   - Payment terms (Net 30, Net 60, etc.)
   - Credit limit (if applicable)
   - Tax information
6. Click **"Save"**

**What Happens Next:**
- The facility is now in your system
- You can add addresses
- You can create jobs for this customer
- The facility appears in searches and dropdown lists

### Editing Facility Information

1. Find the facility in your list
2. Click to open facility details
3. Click the **"Edit"** button or icon (usually a pencil)
4. Make your changes
5. Click **"Save"**

### Adding Addresses

Facilities can have multiple addresses (shipping, billing, warehouse locations).

**To Add an Address:**

1. Open the facility details
2. Go to the **Addresses** tab
3. Click **"+ Add Address"**
4. Choose address type:
   - Shipping
   - Billing  
   - Both
5. Enter the address details:
   - Street address
   - City, State, ZIP
   - Country
   - Contact person (optional)
6. Click **"Save"**

### Accepting Advance Payments

Some customers pay in advance for orders.

**To Record an Advance Payment:**

1. Open the facility details
2. Look for **"Accept Advance Payment"** button or option
3. Enter payment details:
   - Payment amount
   - Payment method
   - Check number or reference
   - Date received
4. Select what the payment is for (if known)
5. Click **"Save"**

**What This Does:**
- Records the payment in accounting
- Creates a credit on the customer account
- Can be applied to future invoices

### Tips for Facility Management

✅ **Keep Information Current** - Update contact info when it changes  
✅ **Use Consistent Naming** - Makes searching easier  
✅ **Add Notes** - Document special instructions or requirements  
✅ **Verify Addresses** - Double-check before shipping  
✅ **Set Proper Payment Terms** - Avoid billing issues later

---

## Jobs Management

### What is a Job?

A **Job** is a customer order that you're working on. It's the container that holds everything about that order:
- What the customer ordered
- When they need it
- How much it costs
- What work needs to be done
- Who's working on it
- Current status

Think of a job as a project folder - everything related to that customer order goes in that job.

### Types of Jobs

There are typically two main types:

1. **Sales Jobs** - Customer orders for products or manufacturing
2. **Service Jobs** - Repair or service work (managed in Service module)

### Job Lifecycle

A typical job moves through these stages:

```
Quote → Job Created → Design (if needed) → Work Orders Created → 
Production → Quality Check → Shipping → Invoicing → Job Closed
```

### Viewing Jobs

**To See Your Job List:**

1. Go to **Workflow → Manage Jobs**
2. You'll see all jobs you have access to
3. Jobs are color-coded by status (varies by configuration)
4. Use filters to find specific jobs:
   - By customer name
   - By job number
   - By status (Open, In Progress, Shipped, etc.)
   - By date range
   - By job type

### Job Details Screen

When you click on a job, you see comprehensive information organized in sections:

#### Header Information
- Job number (unique identifier)
- Customer name
- Job description
- Current status
- Due date
- Total value

#### Main Information Panel
- Customer details and contact
- Job type
- Description of work
- Special instructions
- Priority level

#### Work Orders Tab
- All work orders for this job
- Operations to be performed
- Materials needed
- Current status of each operation
- Time tracking

#### Contacts Tab
- Key contacts for this job
- Customer contacts
- Internal team members
- Email and phone numbers

#### Sales Order Tab
- Line items ordered
- Quantities
- Pricing
- Shipping information
- Terms and conditions

#### Shippers Tab
- Shipping information
- Tracking numbers
- Ship dates
- Delivery status

#### Notes Tab
- Internal notes about the job
- Customer communications
- Special instructions
- Problem documentation

#### Attachments Tab
- Drawings and specifications
- Purchase orders
- Emails
- Photos
- Any related documents

#### Expenses Tab
- Outside costs (outside operations, freight, etc.)
- Special materials
- Subcontractor charges

#### Cost Information
- Actual costs to date
- Estimated total cost
- Labor hours
- Material costs
- Overhead

### Creating a New Job

**Step-by-Step Process:**

1. Go to **Workflow → Manage Jobs**
2. Click **"+ Add Job"** or **"Create Job"**
3. **Select Customer:**
   - Choose from existing facilities
   - Or create a new facility if needed
4. **Enter Job Information:**
   - **Job Type** - What kind of work (Manufacturing, Assembly, etc.)
   - **Description** - What you're making or doing
   - **Quantity** - How many
   - **Due Date** - When customer needs it
   - **Priority** - Normal, Rush, Hot, etc.
5. **Add Details:**
   - Customer PO number
   - Special instructions
   - Shipping method
   - Delivery address
6. Click **"Save"**

**What Happens Next:**
- System assigns a job number
- Job appears in your job list
- You can now add work orders
- You can upload drawings and specifications
- You can add contacts

### Adding Contacts to a Job

Contacts are the people involved with this job - customer contacts, sales reps, project managers.

**To Add a Contact:**

1. Open the job
2. Go to the **Contacts** tab
3. Click **"+ Add Contact"**
4. Choose an existing contact or create new
5. Select their role (Decision Maker, Technical Contact, etc.)
6. Click **"Save"**

**Why This Matters:**
- Know who to call with questions
- Route emails to the right people
- Track who's involved in the project

### Editing Jobs

**To Make Changes:**

1. Find and open the job
2. Click the **"Edit"** button
3. Modify any information
4. Click **"Save"**

**Common Things to Edit:**
- Due date changes
- Customer PO number updates
- Description clarifications
- Priority changes
- Shipping address changes

### Job Status

Jobs move through different statuses. Your system may be configured differently, but typical statuses include:

- **Open** - Job created, planning stage
- **In Design** - Engineering is working on designs
- **Released** - Work orders sent to production
- **In Production** - Being manufactured
- **Quality Hold** - Waiting for quality approval
- **Ready to Ship** - Complete and ready
- **Shipped** - Sent to customer
- **Closed** - Complete and invoiced

**Changing Job Status:**

Some statuses change automatically (when you release work, ship, etc.). You can manually change status:

1. Open the job
2. Look for **Status** field or **Edit Status** button
3. Select new status
4. Add notes explaining why (if required)
5. Click **"Save"**

### Setting Completion Dates

Help your team and customers know when work will be done.

**To Set or Update Completion Date:**

1. Open the job
2. Find **"Estimated Completion"** or **"Manage Completion Date"**
3. Enter or update the date
4. The system may calculate based on:
   - Current workload
   - Operation times
   - Material availability
5. Click **"Save"**

**Best Practices:**
- Be realistic with dates
- Build in buffer time
- Update if things change
- Communicate changes to customer

### Managing Job Expenses

Sometimes you have special costs for a job (outside services, freight, special materials).

**To Add an Expense:**

1. Open the job
2. Go to **Expenses** tab
3. Click **"+ Add Expense"**
4. Enter details:
   - Description
   - Amount
   - Vendor
   - Date
   - Expense type
5. Attach receipt if needed
6. Click **"Save"**

**Why Track Expenses:**
- Accurate job costing
- Proper invoicing
- Profitability analysis
- Budget tracking

### Adding Notes to Jobs

Document important information, decisions, or communications.

**To Add a Note:**

1. Open the job
2. Go to **Notes** tab
3. Click **"+ Add Note"**
4. Type your note
5. The system timestamps and adds your name
6. Click **"Save"**

**When to Add Notes:**
- Customer phone calls
- Design decisions
- Quality issues
- Shipping instructions
- Problem resolution

### Uploading Drawings and Documents

**To Attach Files:**

1. Open the job
2. Go to **Attachments** tab
3. Click **"+ Upload"** or **"Add Attachment"**
4. Select file from your computer
5. Choose category (Drawing, Specification, PO, etc.)
6. Add description (optional)
7. Click **"Upload"**

**Supported File Types:**
- PDF documents
- CAD files (DWG, DXF)
- Images (JPG, PNG)
- Excel spreadsheets
- Word documents

### Creating Shippers (Shipping Orders)

When you're ready to ship a job, create a shipper.

**To Create a Shipper:**

1. Open the job
2. Go to **Shippers** tab
3. Click **"+ Add Shipper"**
4. Enter shipping information:
   - Ship to address
   - Carrier
   - Shipping method
   - Tracking number
   - Ship date
5. Select what items are being shipped
6. Click **"Save"**

**What This Does:**
- Documents what was shipped
- Tracks shipping information
- Updates job status
- Triggers invoicing (if configured)

### Copying Jobs

If you need to make a similar job, copy an existing one.

**To Copy a Job:**

1. Find the job to copy
2. Look for **"Copy"** button or action
3. System creates duplicate with new job number
4. Update as needed:
   - Customer
   - Due date
   - Quantity
   - Description
5. Click **"Save"**

**What Gets Copied:**
- Job structure
- Work order templates
- Materials list
- Operations

**What Doesn't Copy:**
- Actual work completed
- Time entries
- Costs incurred
- Status (new job starts fresh)

### Closing Jobs

When a job is complete and invoiced, close it.

**To Close a Job:**

1. **Verify Everything is Complete:**
   - All work orders closed
   - Everything shipped
   - Customer invoiced
   - No open issues
2. Open the job
3. Click **"Close Job"** button
4. System may ask for confirmation
5. Job moves to closed status

**Why Close Jobs:**
- Clean up active job list
- Accurate reporting
- System performance
- Clear status tracking

### Reopening Jobs

Sometimes you need to reopen a closed job (rework, additional work, corrections).

**To Reopen a Job:**

1. Find the closed job
2. Click **"Reopen Job"** button or option
3. Add reason for reopening
4. Click **"Confirm"**
5. Job returns to active status

---

## Work Orders

### What is a Work Order?

A **Work Order** is the actual work that needs to be done for a job. While a Job represents the customer order, Work Orders represent the manufacturing steps.

**Example:**  
- **Job:** Customer orders 100 brackets
- **Work Order 1:** Cut raw material
- **Work Order 2:** Bend brackets
- **Work Order 3:** Weld assembly
- **Work Order 4:** Paint
- **Work Order 5:** Final inspection

### Work Order Components

Each work order contains:

#### Operations
- Individual manufacturing steps
- Operation sequence (order of work)
- Which work center performs each operation
- Estimated time for each operation

#### Materials
- What materials are needed
- Quantities required
- When materials are needed (start vs. specific operations)
- Material issue tracking

#### Labor
- Who worked on it
- How long they worked
- Which operation they performed
- Clock in/out times

### Viewing Work Orders

**From the Main Work Orders Screen:**

1. Go to **Workflow → Work Orders**
2. See list of all work orders
3. Filter by:
   - Job number
   - Customer
   - Status
   - Work center
   - Due date
4. Click any work order to see details

**From Within a Job:**

1. Open the job
2. Go to **Work Orders** tab
3. See all work orders for that job
4. Click to open work order details

### Work Order Status

Work orders progress through statuses:

- **Planning** - Being created/planned
- **Ready to Release** - Waiting to go to production
- **Released** - Sent to shop floor
- **In Progress** - Being worked on
- **On Hold** - Stopped for some reason
- **Complete** - Finished
- **Closed** - Officially closed out

### Creating Work Orders

Work orders are usually created automatically from:
- Jobs with routers
- Standard templates
- Previous orders

**Manual Creation:**

1. Open the job
2. Go to **Work Orders** tab
3. Click **"+ Add Work Order"**
4. Select what you're making
5. System generates operations from router (if available)
6. Review and adjust:
   - Operations
   - Materials
   - Due dates
7. Click **"Save"**

### Modifying Work Orders

Sometimes you need to change a work order after it's created.

**To Modify:**

1. Find and open the work order
2. Click **"Modify"** button
3. You can change:
   - **Add Operations** - Insert additional work steps
   - **Remove Operations** - Delete unnecessary steps
   - **Add Materials** - Add more materials needed
   - **Change Quantities** - Adjust material amounts
   - **Reorder Operations** - Change sequence
   - **Add Comments** - Document special instructions
4. Click **"Save Changes"**

**Important:**  
- Some changes may require supervisor approval
- Changes may affect job cost estimates
- Material changes may trigger new purchase orders

### Adding Operations to Work Orders

**Step-by-Step:**

1. Open work order in modify mode
2. Click **"+ Add Operation"**
3. Select the operation type:
   - Choose from list of standard operations
   - Or create custom operation
4. Enter details:
   - Operation description
   - Work center assignment
   - Estimated time
   - Sequence position
5. Click **"Save"**

### Adding Materials to Work Orders

**To Add Materials:**

1. Open work order in modify mode
2. Go to materials section
3. Click **"+ Add Material"**
4. Search for and select the material:
   - From inventory items
   - Or enter description for purchased items
5. Enter quantity needed
6. Select when needed:
   - At start of work order
   - For specific operation
7. Click **"Save"**

**What Happens:**
- Material shows as required
- Appears on pick lists
- System checks inventory
- Creates demand for purchasing

### Issuing Materials

Before production can start, materials must be issued to the work order.

**To Issue Materials:**

1. Go to **Workflow → Issue Material** or from work order
2. Find the work order
3. See list of required materials
4. Check off materials being issued
5. Enter actual quantities
6. Enter lot/serial numbers if tracked
7. Click **"Issue Materials"**

**What This Does:**
- Removes materials from inventory
- Assigns them to the work order
- Updates material availability
- Tracks what was used

### Releasing Work to Production

Before shop floor can work on something, it must be "released."

**To Release Work Orders:**

1. Go to **Workflow → Release Work** or **Work Orders → Send to Production**
2. See list of work orders ready to release
3. Select which ones to release
4. Optionally print work orders and labor tickets
5. Click **"Release Selected"**

**What This Does:**
- Changes status to "Released"
- Makes work visible to shop floor
- Allows workers to clock in
- Generates paperwork

**Before Releasing, Verify:**
- ✅ All materials are available
- ✅ Drawings are uploaded
- ✅ Work center is available
- ✅ Due date is realistic
- ✅ Special tooling is ready

### Work Order Holds

Sometimes work must be stopped.

**Common Hold Reasons:**
- Customer requested change
- Quality issue found
- Awaiting materials
- Engineering change required
- Missing information

**To Place a Hold:**

1. Open the work order
2. Click **"Hold"** or **"Place on Hold"**
3. Select hold reason
4. Enter explanation
5. Click **"Confirm"**

**Work stops immediately** - operators cannot continue.

**To Release a Hold:**

1. Open the work order
2. Click **"Release Hold"**
3. Enter notes about resolution
4. Click **"Confirm"**

Work can resume.

### Outside Operations

Some operations are done by outside vendors (heat treating, plating, special processes).

**To Request Outside Operation:**

1. Open work order
2. Find the outside operation
3. Click **"Request Outside Operation"** or **"Create PO"**
4. Select vendor
5. Enter details:
   - Quantity to send out
   - Required completion date
   - Special instructions
6. System creates purchase order
7. Click **"Submit"**

**Tracking:**
- PO created automatically
- Operation marked as "Out for Processing"
- Due date tracked
- Reminder notifications

### Printing Work Orders

Production needs printed documentation.

**To Print Work Orders:**

1. Go to **Workflow → Work Orders → Print Work Orders**
2. Select which work orders to print:
   - Individual selection
   - By job
   - By work center
   - By date range
3. Click **"Print"** or **"Generate PDF"**
4. System creates printable work order packet

**What's Included:**
- Work order header information
- Operation list with sequence
- Material requirements
- Drawings (if included)
- Special instructions
- Space for labor entry

### Printing Labor Tickets

Labor tickets are given to operators for time tracking.

**To Print Labor Tickets:**

1. Go to **Workflow → Work Orders → Print Labor Operations**
2. Filter to find operations needed
3. Select operations to print
4. Choose print options:
   - Include barcode
   - Number of copies
   - Ticket size
5. Click **"Print"**

**Workers Use These To:**
- Know what operation to perform
- Record start and end times
- Note quantity completed
- Document any issues

### Closing Work Orders

When all work is complete, close the work order.

**To Close a Work Order:**

1. **Verify Everything is Done:**
   - All operations complete
   - All material issued and used
   - All labor time recorded
   - Quality approved
2. Go to **Inventory → Close Work Order** or from work order details
3. Select work order to close
4. Enter actual quantity completed
5. Handle any scrapped quantity
6. Click **"Close Work Order"**

**What This Does:**
- Finalizes costs
- Receives finished goods into inventory
- Prevents further time or material entries
- Updates job status

### Adjusting Due Dates

If work orders need different due dates, adjust them.

**To Adjust Due Dates:**

1. Open the job
2. Click **"Adjust Due Dates"** or similar option
3. See all work orders with current due dates
4. Select adjustment method:
   - Move all by X days
   - Set new end date (system back-schedules)
   - Manually adjust each
5. Review new dates
6. Click **"Apply Changes"**

**When to Adjust:**
- Customer changes delivery date
- Production delays occur
- Rush jobs need expediting
- Capacity constraints

---

## Designs

### What is the Design Feature?

The Designs feature helps you manage product design work before production begins. It tracks the engineering process - creating designs, getting approvals, and completing design tasks.

**Think of it as:** Your project management tool for engineering work.

### When to Use Designs

Use the Design module when:
- Creating new product designs
- Engineering custom parts for customers
- Developing new manufacturing processes
- Making significant product modifications
- Requiring multi-step design approval

### Design Workflow

```
Design Request → Designer Assigned → Design Work → Review → 
Revisions (if needed) → Final Approval → Ready for Production
```

### Viewing Designs

**To See Design Jobs:**

1. Go to **Workflow → Designs**
2. See list of all design projects
3. Filter by:
   - Designer assigned
   - Status
   - Customer
   - Due date
   - Job number
4. Click any design to see details

### Design Status Tree

Designs are organized in a tree structure showing:

- **Job Level** - The overall job
  - **Router Level** - What's being designed
    - **Design Steps** - Individual design tasks
      - **Tasks** - Specific activities

**Example Structure:**
```
Job #12345 - Custom Bracket
  └── Router: Bracket Assembly
      ├── Step 1: Concept Design (Complete)
      ├── Step 2: Detailed Design (In Progress)
      │   ├── Task: Create 3D model
      │   └── Task: Generate drawings
      └── Step 3: Design Review (Waiting)
```

### Design Steps

Each design step is a phase in the design process. Common steps:

1. **Concept Design** - Initial ideas and sketches
2. **Detailed Design** - Full engineering drawings
3. **Design Review** - Engineering review
4. **Customer Review** - Customer approval
5. **Final Approval** - Management sign-off
6. **Release to Production** - Design complete

### Managing Design Steps

**To Update a Design Step:**

1. Open the design project
2. Find the design step in the tree
3. Click to open step details
4. You can:
   - Mark as complete
   - Add notes
   - Upload files
   - Assign to designer
   - Set due date
5. Click **"Save"**

### Design Tasks

Within design steps, there are specific tasks to complete.

**To Manage Tasks:**

1. Open design step
2. See list of tasks
3. For each task:
   - Check off when complete
   - Add notes about completion
   - Upload completed work
4. When all tasks complete, step is done

### Clocking Into Design Work

Designers track their time on design tasks.

**To Clock Into a Design Task:**

1. Go to **Attendance → Attendance** or **Workflow → Active Work**
2. Select **"Clock into Design"**
3. Search for and select your design task
4. Click **"Clock In"**

**While Clocked In:**
- Your time is tracked
- Shows as "busy" on that task
- Appears in active work reports

**To Clock Out:**
1. Return to attendance screen
2. Click **"Clock Out"**
3. Enter any notes about work completed
4. Time is recorded to design task

### Reopening Design Steps

If a design needs changes after approval, you can reopen it.

**To Reopen a Design Step:**

1. Find the completed design step
2. Click **"Reopen"** or similar option
3. Enter reason for reopening
4. Step returns to "In Progress"
5. Designer can make changes

**When to Reopen:**
- Customer requests changes
- Error found in design
- Engineering change needed
- Additional review required

### Design Approvals

Design steps often require approval before moving forward.

**Approval Process:**

1. Designer completes work
2. Marks step as "Ready for Review"
3. Reviewer is notified
4. Reviewer examines design:
   - Reviews drawings
   - Checks calculations
   - Verifies requirements
5. Reviewer either:
   - **Approves** - design moves forward
   - **Rejects** - design returns for changes
6. Process continues through all required approvals

### Adding Design Notes

Document design decisions and changes.

**To Add Notes:**

1. Open design step or task
2. Find notes section
3. Click **"+ Add Note"**
4. Type your note:
   - Design decisions
   - Calculation references
   - Customer feedback
   - Change reasons
5. Click **"Save"**

### Uploading Design Files

Keep all design files with the design record.

**To Upload Files:**

1. Open the design project
2. Go to attachments area
3. Click **"Upload"**
4. Select files:
   - CAD files
   - PDF drawings
   - Specifications
   - Calculations
5. Add description
6. Click **"Upload"**

### Tips for Design Management

✅ **Update Status Regularly** - Keep everyone informed  
✅ **Document Decisions** - Add notes explaining why  
✅ **Track Time Accurately** - Clock in and out properly  
✅ **Get Approvals** - Don't skip review steps  
✅ **Organize Files** - Use clear file names  
✅ **Communicate Changes** - Notify affected parties

---

## Change Requests

### What is a Change Request?

A **Change Request (CR)** is a formal way to request and track changes to products, designs, or processes. It ensures changes are:
- Documented
- Reviewed
- Approved
- Implemented correctly
- Tracked for quality purposes

**Think of it as:** Your quality control system for managing changes.

### When to Create a Change Request

Create a change request when you need to:
- Fix a quality issue
- Modify an existing design
- Change manufacturing process
- Correct recurring problems
- Implement customer-requested changes
- Address safety concerns

**Example Scenarios:**
- Customer says parts don't fit properly
- Discover better manufacturing method
- Supplier changed material specifications
- Quality finds defects in production
- Engineering wants to improve design

### Viewing Change Requests

**To See Change Request List:**

1. Go to **Workflow → Change Requests**
2. See all change requests
3. Filter by:
   - Status (Open, In Review, Approved, Implemented)
   - Assigned to
   - Item/part affected
   - Date submitted
   - Priority
4. Click any CR to see details

### Change Request Status

CRs move through a lifecycle:

```
Submitted → Under Review → Approved/Rejected → 
Implementation → Verification → Closed
```

**Status Meanings:**

- **Submitted** - CR has been created, waiting for review
- **Under Review** - Team is evaluating the change
- **Approved** - Change has been approved, ready to implement
- **Rejected** - Change was not approved
- **Implementation** - Change is being made
- **Verification** - Checking that change worked
- **Closed** - Change complete and verified

### Creating a Change Request

**Step-by-Step:**

1. Go to **Workflow → Change Requests**
2. Click **"+ Add Change Request"**
3. **Find the Item:**
   - Search for the part or product affected
   - Select from list
4. **Describe the Problem:**
   - What's wrong or what needs to change
   - How it was discovered
   - Impact on quality/production
5. **Describe Proposed Solution:**
   - What change do you want to make
   - How will it fix the problem
   - Any alternative solutions considered
6. **Set Priority:**
   - Critical - Stop production
   - High - Fix soon
   - Medium - Plan and implement
   - Low - Improve when convenient
7. **Assign Responsible Person:**
   - Who will investigate
   - Who will implement
8. **Add Supporting Documentation:**
   - Photos of problem
   - Customer complaints
   - Quality reports
   - Drawings
9. Click **"Submit"**

**What Happens Next:**
- CR is assigned a number
- Responsible person is notified
- Review process begins
- Tracks through to completion

### Change Request Details

When you open a CR, you see several sections:

#### CR Information
- CR number
- Status
- Item affected
- Description of issue
- Proposed solution
- Priority
- Dates (submitted, due, completed)

#### Assignment Information
- Who reported it
- Who's responsible
- Who needs to approve
- Current assigned person

#### Root Cause Analysis
- What caused the problem
- Why it wasn't caught earlier
- Contributing factors
- Corrective actions

#### Linked Items
- Related jobs affected
- Work orders on hold
- Other related CRs
- Items that use this part

#### Activity Stream
- Timeline of all actions
- Who did what and when
- Status changes
- Comments and decisions

#### Attachments
- Photos
- Documents
- Drawings (before and after)
- Test results

### Editing Change Requests

**To Update a CR:**

1. Open the change request
2. Click **"Edit"**
3. Modify information:
   - Update description
   - Refine solution
   - Change priority
   - Reassign
   - Add new information
4. Click **"Save"**

**Note:** Some fields may lock based on status.

### Root Cause Analysis

For quality issues, document the root cause.

**To Complete Root Cause Analysis:**

1. Open the change request
2. Click **"Root Cause Analysis"** or go to that tab
3. Answer the questions:
   - **What happened?** (The problem)
   - **Why did it happen?** (Immediate cause)
   - **Why did that happen?** (Keep asking why)
   - **Root cause identified**
4. Document corrective actions:
   - What will prevent it happening again
   - Who is responsible
   - When will it be complete
5. Document preventive actions:
   - How to catch similar issues
   - Process improvements
   - Training needs
6. Click **"Save"**

**Why This Matters:**
- Fix problems permanently
- Learn from mistakes
- Improve processes
- Quality system requirements
- Customer satisfaction

### Linking Items to Change Requests

Show which parts or products are affected.

**To Link Items:**

1. Open the change request
2. Go to **Linked Items** section
3. Click **"+ Link Item"**
4. Search for and select items
5. Specify relationship:
   - This item is affected
   - This item uses affected part
   - This item is related
6. Click **"Save"**

**What This Does:**
- Shows full impact
- Helps identify affected jobs
- Tracks which items need updating
- Supports traceability

### Operation Holds

When a CR affects production, you can hold operations.

**What's an Operation Hold?**
Work orders with the affected part are automatically stopped until the CR is resolved.

**How It Works:**

1. CR is created for a part
2. System identifies all work orders using that part
3. Operations are placed on hold
4. Shop floor cannot continue work
5. When CR is resolved and approved:
   - Holds are released (automatically or manually)
   - Work can resume

**To Override a Hold:**

(Requires special permission)

1. Open work order with hold
2. Click **"Override Hold"**
3. Enter justification
4. Enter your password/approval
5. Hold is temporarily lifted
6. Work can proceed

**When to Override:**
- Using up old inventory before change
- Rework will be done later
- Customer accepts non-conforming parts
- Hold applied in error

### Attaching Files to CRs

Document problems and solutions visually.

**To Add Files:**

1. Open change request
2. Go to **Attachments**
3. Click **"Upload"**
4. Select files:
   - Photos of defects
   - Before/after drawings
   - Test reports
   - Customer letters
5. Add description
6. Click **"Upload"**

### Adding Notes to CRs

Track the conversation and decisions.

**To Add Notes:**

1. Open change request
2. Go to **Notes** or **Activity** section
3. Click **"+ Add Note"**
4. Type your note:
   - Investigation findings
   - Meeting decisions
   - Test results
   - Implementation updates
5. Click **"Save"**

**Best Practices:**
- Note all significant actions
- Document decisions made
- Reference supporting information
- Keep stakeholders informed

### CR Notifications

Notify people about CR status or needs.

**To Send Notifications:**

1. Open change request
2. Go to **Notify** section
3. Select who to notify:
   - Engineering
   - Quality
   - Production
   - Management
   - Customer (if appropriate)
4. Add message
5. Click **"Send"**

### Vault Files for CRs

Store related documents in the vault.

**To Link Vault Files:**

1. Open change request
2. Go to **Vault Files** section
3. Browse vault
4. Select relevant files
5. Link to this CR

### Closing Change Requests

When everything is complete, close the CR.

**To Close:**

1. **Verify Everything is Done:**
   - Solution implemented
   - Verified working
   - Documentation complete
   - All affected items updated
2. Open change request
3. Click **"Close CR"**
4. Add final comments
5. Click **"Confirm"**

**CR is now closed** and available for historical reference.

### Tips for Change Requests

✅ **Document Thoroughly** - More information is better  
✅ **Act Quickly on Quality Issues** - Don't wait  
✅ **Complete Root Cause** - Find real problem  
✅ **Communicate Changes** - Keep everyone informed  
✅ **Verify Solutions** - Make sure fix works  
✅ **Update Drawings** - Keep documentation current  
✅ **Learn from Issues** - Improve processes

---

## Release Work

### What Does "Release Work" Mean?

Releasing work means giving the shop floor permission to start working on something. Until work is released, operators cannot clock into it or begin production.

**Think of it as:** The green light for production to start.

### Why Control Work Release?

- **Ensure Materials Ready** - Don't start if materials aren't available
- **Manage Workload** - Control what's on the shop floor
- **Schedule Effectively** - Release in the right order
- **Prevent Confusion** - Only release what should be worked on now
- **Quality Control** - Verify everything is ready before starting

### Viewing Work Ready to Release

**To See What's Ready:**

1. Go to **Workflow → Release Work**
2. See list of work orders ready for release
3. Filter by:
   - Job
   - Customer
   - Due date
   - Work center
   - Priority
4. See status indicators:
   - Materials available
   - Drawings attached
   - Previous operations complete

### Releasing Work Orders

**To Release Work:**

1. Go to **Workflow → Release Work**
2. Review list of work orders
3. For each work order, check:
   - ✅ Materials are available or issued
   - ✅ Drawings are uploaded
   - ✅ Work center has capacity
   - ✅ Previous operations complete (if sequenced)
   - ✅ No quality holds
4. Select work orders to release:
   - Check boxes next to each
   - Or click "Select All"
5. Click **"Release Selected"**
6. Confirm the action

**What Happens:**
- Status changes to "Released"
- Appears on shop floor work lists
- Operators can clock in
- Shows in active work screens

### Release Options

When releasing, you may have options:

#### Print Work Orders
- Generate work order packets
- Include drawings
- Print labels

#### Print Labor Tickets
- Print tickets for operators
- Include barcodes
- Multiple copies if needed

#### Set Priority
- Mark as rush/hot
- Normal priority
- Fill-in work

#### Assign Work Center
- Confirm work center assignment
- Override if needed
- Balance workload

### Releasing Individual Work Orders

You can also release from within a work order or job.

**From Work Order Details:**

1. Open the work order
2. Click **"Release to Production"**
3. Verify readiness
4. Click **"Confirm"**

**From Job Details:**

1. Open the job
2. Go to **Work Orders** tab
3. Find work order
4. Click release icon or button
5. Confirm

### What to Check Before Releasing

**Material Availability:**
- All required materials in stock
- Materials issued to work order
- Special materials ordered and received

**Documentation:**
- Engineering drawings uploaded
- Specifications available
- Work instructions attached
- Quality requirements documented

**Prerequisites:**
- Previous operations complete
- Fixtures and tooling available
- Work center available
- Setup complete

**Quality:**
- No quality holds
- No pending change requests
- First article approved (if required)
- Special processes scheduled (if needed)

### Handling Not-Ready Work Orders

If a work order shouldn't be released yet:

**Add to Watch List:**
- Monitor for readiness
- Get notified when ready

**Add Notes:**
- Document what's missing
- Set reminder date

**Communicate:**
- Notify purchasing if materials needed
- Alert engineering if drawings missing
- Inform scheduling of delays

### Releasing Rework Orders

Rework orders (fixing defects) follow same process but pay attention to:

- What caused the rework
- Special instructions
- Whether change request exists
- Customer awareness
- Additional inspection needs

### Tips for Releasing Work

✅ **Release in Priority Order** - Important jobs first  
✅ **Don't Over-Release** - Keep shop floor manageable  
✅ **Check Materials First** - Avoid shop floor waiting  
✅ **Print Documentation** - Operators need instructions  
✅ **Balance Workload** - Spread work across work centers  
✅ **Communicate Hot Jobs** - Make sure everyone knows priorities  
✅ **Release Early Enough** - Give shop time to complete

---

## WIP Tracking

### What is WIP?

**WIP = Work In Process**

This is material and products that are currently being manufactured. They're not raw materials anymore, but not finished products yet - they're somewhere in between.

### Why Track WIP?

- **Know Where Things Are** - Locate any job instantly
- **Track Progress** - See how far along work is
- **Manage Inventory** - WIP ties up money
- **Accountability** - Know who has what
- **Quality Control** - Trace materials through process
- **Accurate Costing** - Value of work in process

### Viewing WIP

**To See Work In Process:**

1. Go to **Workflow → WIP Tracking**
2. Choose what to view:
   - WIP History
   - Receive Items
   - Current WIP Status

### Receiving Items

When operations are complete, "receive" items to move them forward.

**What is Receiving?**
Recording that an operation is complete and parts are moving to:
- Next operation
- Finished goods inventory
- Quality inspection
- Customer

**To Receive Items:**

1. Go to **Workflow → WIP Tracking → Receive Items**
2. Select work order and operation
3. Enter quantity completed
4. Enter quantity scrapped (if any)
5. Select destination:
   - Next operation
   - Finished goods
   - Quality hold
   - Stock location
6. Click **"Receive"**

**What This Does:**
- Marks operation as complete
- Moves parts to next location
- Updates WIP status
- Triggers next operation (if ready)
- Updates inventory quantities

### WIP History

See the complete movement history of any job.

**To View WIP History:**

1. Go to **Workflow → WIP Tracking → History**
2. Search for job, work order, or part
3. See complete timeline:
   - When materials were issued
   - Each operation completion
   - Movements between work centers
   - Quantity at each step
   - Who performed each operation
   - Timestamps for everything

**Why This Matters:**
- Track where parts are
- Troubleshoot problems
- Verify operations performed
- Quality traceability
- Process analysis

### Tracking Scrapped Items

When parts are scrapped during production:

**To Record Scrap:**

1. During receive process, enter scrap quantity
2. Select scrap reason:
   - Machine error
   - Operator error
   - Material defect
   - Design issue
   - Other
3. Add notes explaining what happened
4. Click **"Save"**

**What This Does:**
- Reduces good quantity
- Records scrap for costing
- Identifies quality issues
- Tracks loss trends
- May trigger material reorder

### Lot and Serial Tracking

If you track lot or serial numbers:

**During Receiving:**

1. System prompts for lot/serial numbers
2. Enter or scan numbers
3. System tracks which specific items:
   - Went into which work order
   - Moved through which operations
   - Where they are now
   - Where they went (if shipped)

**Benefits:**
- Complete traceability
- Quick recalls if needed
- Warranty tracking
- Quality investigation

### Moving Items Between Locations

Sometimes parts need to move without completing an operation.

**To Move Items:**

1. Go to WIP tracking
2. Find the work order/items
3. Select **"Move Items"** or **"Transfer"**
4. Enter:
   - From location
   - To location
   - Quantity
   - Reason for move
5. Click **"Confirm"**

**Common Reasons:**
- Move to quality inspection
- Return from outside operation
- Stage for shipping
- Move to rework area
- Consolidate at work center

---

## MPT (Make-to-Print)

### What is MPT?

**MPT = Make-to-Print** or **Make Per Print**

These are jobs where you manufacture parts exactly to customer-provided drawings and specifications. You're not designing anything - just making what the customer designed.

### Review MPT Process

The MPT review helps ensure jobs are set up correctly before production starts.

**To Access MPT Review:**

1. Go to **Workflow → MPT**
2. See list of jobs needing MPT review

### What to Review

For each MPT job, verify:

#### Part Information
- Part number correct
- Description accurate
- Quantity matches order

#### Manufacturing Router
- Operations are correct
- Operation sequence makes sense
- Work centers assigned properly
- Time estimates reasonable

#### Materials
- Materials correctly identified
- Quantities calculated correctly
- Materials available or ordered

#### Drawings and Specifications
- Customer drawings uploaded
- Drawings are current revision
- Special processes noted
- Quality requirements clear

### Approving MPT Jobs

**To Approve:**

1. Open the MPT job
2. Review all information
3. If everything looks good:
   - Click **"Approve"**
   - Job moves forward to production
4. If issues found:
   - Add notes about problems
   - Assign back to planner
   - Request corrections

### Managing Manufacturing Parts

For MPT jobs, you can manage the manufacturing part setup.

**To Manage Manufacturing Part:**

1. Find the MPT job
2. Click **"Manage Manufacturing Part"**
3. Review or update:
   - Part details
   - Router operations
   - Material requirements
   - Work center assignments
4. Click **"Save"**

### Tips for MPT

✅ **Verify Drawings First** - Make sure they're complete  
✅ **Check Revisions** - Use latest version  
✅ **Question Unclear Specs** - Ask customer before starting  
✅ **Accurate Time Estimates** - Bid correctly  
✅ **Material Selection** - Match customer specs exactly  
✅ **Note Special Processes** - Heat treat, plating, etc.

---

## Active Work

### What is Active Work?

The Active Work screen shows what's currently being worked on right now across your facility. It's your real-time view of production activity.

### Viewing Active Work

**To See Current Activity:**

1. Go to **Workflow → Active Work**
2. See everyone who is clocked into work
3. View by:
   - By work center
   - By employee
   - By job
   - By customer

### Information Shown

For each active work session:

- **Who** is working
- **What** they're working on (job, work order, operation)
- **When** they started
- **How long** they've been working
- **Where** they're working (work center)
- **Status** of the work

### Clocking Out Employees

Supervisors can clock out employees if needed.

**To Clock Someone Out:**

1. Find their active work session
2. Click **"Clock Out"** button
3. Enter reason (if required)
4. Enter quantity completed (if known)
5. Click **"Confirm"**

**When to Do This:**
- End of shift and they forgot
- Emergency situation
- Person unavailable
- Correcting errors

### Monitoring Production

Use Active Work to:

- **Check Status** - See if important jobs are being worked on
- **Balance Workload** - Move work if centers overloaded
- **Answer Questions** - "Who's working on job #123?"
- **Track Progress** - Estimate completion times
- **Identify Problems** - Jobs taking too long

### Tips for Active Work

✅ **Check Regularly** - Monitor throughout day  
✅ **Look for Bottlenecks** - Too much work at one center  
✅ **Verify Priority Jobs** - Make sure they're being worked  
✅ **Follow Up Long Sessions** - Check on jobs taking unusually long  
✅ **Communicate** - Talk to operators about progress

---

## Manage Estimates

### What Are Operation Estimates?

Operation estimates are the expected time it should take to perform each operation. These estimates are used for:

- Job quoting
- Scheduling
- Capacity planning
- Performance tracking
- Labor standards

### Reviewing Estimates

**To Review Operation Estimates:**

1. Go to **Workflow → Manage Estimates**
2. See list of operations needing estimate review
3. Filter by:
   - Job
   - Operation
   - Work center
   - Date range

### Estimate Information

For each operation, you see:

- **Operation** - What's being done
- **Estimated Time** - Current estimate
- **Actual Time** - What it actually took
- **Variance** - Difference between estimate and actual
- **Status** - Needs review, approved, etc.

### Reviewing and Approving Estimates

**To Review:**

1. Open the operation estimate
2. Compare estimated vs. actual time
3. Consider:
   - Was estimate reasonable?
   - Were there special circumstances?
   - Should standard time be updated?
   - First time vs. repeat job?
4. Make decision:
   - **Approve as-is** - Estimate was good
   - **Revise Estimate** - Update for future
   - **Note Exception** - Explain variance
5. Add comments
6. Click **"Approve"** or **"Save"**

### When Estimates Are Off

**If Actual Time Much Higher:**
- Was there a problem?
- Learning curve on new part?
- Machine issues?
- Poor estimate initially?

**If Actual Time Much Lower:**
- Worker very experienced?
- Estimate too conservative?
- Better method found?
- Short run setup advantage?

### Updating Standard Times

Based on actual data, update standard operation times.

**To Update:**

1. Review multiple instances of same operation
2. Determine realistic time
3. Update operation master
4. Future jobs will use new estimate

---

## Reports

### Workflow Reports Overview

The Workflow Reports section provides insights into your manufacturing operations.

**To Access Reports:**

1. Go to **Workflow → Workflow Reports**
2. Select the report you need

### Work by Area Report

See work organized by area or department.

**What It Shows:**
- Work allocated to each work center
- Scheduled start and end dates
- Priority of work
- Load by time period

**How to Use It:**
- Balance workload
- Identify overloaded centers
- Plan staffing
- Schedule deliveries

**To Generate:**

1. Go to **Workflow → Work by Area**
2. Set filters:
   - Date range
   - Department
   - Work center
   - Job type
3. Click **"Run Report"** or **"View"**
4. Export or print as needed

### Other Common Workflow Reports

Your system may include:

- **Job Status Report** - Where all jobs stand
- **Late Jobs Report** - Jobs past due
- **Work Center Load** - Capacity vs. demand
- **Job Cost Report** - Costs by job
- **Labor Hours Report** - Hours by job or center
- **Material Usage Report** - Materials consumed
- **Scrap Report** - Scrap by reason/center
- **Completion Report** - Jobs completed in period

---

## Vault

### What is the Vault?

The Vault is central document storage for important files. Instead of scattering files across individual jobs, store them centrally and link as needed.

### Using the Vault

**To Access:**

1. Go to **Workflow → Vault**
2. Browse or search for documents

### Searching the Vault

Find documents quickly:

**Search By:**
- Document name
- Category
- Date uploaded
- Uploaded by
- Keywords
- Customer
- Part number

### Categories

Organize documents into categories:

- Engineering Drawings
- Specifications
- Quality Documents
- Customer Contracts
- Certifications
- Test Reports
- Photos
- Meeting Notes

### Uploading to Vault

**To Upload:**

1. Go to Vault
2. Click **"Upload"** or **"+ Add"**
3. Select file from computer
4. Enter information:
   - Document name
   - Category
   - Description
   - Keywords
   - Related customer/part
5. Click **"Upload"**

### Linking Vault Files

Link vault documents to jobs, work orders, or other records.

**Why Link:**
- No need to upload same drawing multiple times
- Everyone sees same version
- Update once, updates everywhere
- Saves storage space

---

## Common Tasks & Workflows

### Complete Workflow: From Quote to Shipped Job

**1. Quote Phase** (in CRM)
- Customer requests quote
- Create quote
- Price and estimate time
- Send to customer

**2. Job Creation** (Customer accepts)
- Convert quote to job
- Create job in Workflow
- Upload customer drawings
- Add customer contacts

**3. Engineering** (if needed)
- Create design project
- Designer works on design
- Reviews and approvals
- Release to production

**4. Planning**
- Create work orders
- Define operations
- Calculate materials
- Assign work centers

**5. Material Procurement**
- Review material requirements
- Create purchase orders
- Receive materials
- Stage for production

**6. Release to Production**
- Verify materials available
- Check drawings attached
- Release work orders
- Print work orders and tickets

**7. Manufacturing**
- Operators clock into work
- Perform operations
- Record completions
- Move to next operation

**8. Quality Check**
- Inspect completed work
- Record results
- Approve or reject
- Handle any rework

**9. Completion**
- Receive into finished goods
- Close work orders
- Update job status

**10. Shipping**
- Create shipper
- Pick and pack
- Ship to customer
- Track shipment

**11. Invoicing & Closure**
- Generate invoice
- Send to customer
- Receive payment
- Close job

### Handling Rush Jobs

**When a Rush Job Comes In:**

1. **Assess Impact**
   - Can we meet customer need?
   - What gets delayed?
   - Additional costs?

2. **Create Job**
   - Mark as "Hot" or "Rush"
   - Set realistic due date
   - Add rush notes

3. **Expedite Materials**
   - Check inventory immediately
   - Expedite any purchases
   - Consider alternates if needed

4. **Fast-Track Design**
   - Assign immediately
   - Prioritize reviews
   - Compress timeline if possible

5. **Priority Release**
   - Release to production ASAP
   - Alert shop floor of priority
   - Consider working overtime

6. **Monitor Closely**
   - Check active work frequently
   - Remove bottlenecks
   - Ensure staying on schedule

7. **Expedite Shipping**
   - Use faster carrier
   - Ship partial if beneficial
   - Track closely

### Handling Rework

**When Defects Are Found:**

1. **Stop Work** (if in progress)
   - Don't make more bad parts
   - Place hold if needed

2. **Document Issue**
   - Take photos
   - Create change request if systemic
   - Record what's wrong

3. **Determine Cause**
   - Why did it happen?
   - First time or recurring?
   - Process or design issue?

4. **Plan Correction**
   - How to fix defective parts
   - Prevent making more
   - Update process if needed

5. **Create Rework Order**
   - Define rework operations
   - Assign to work center
   - Set priority

6. **Perform Rework**
   - Follow rework plan
   - Inspect carefully
   - Verify fix worked

7. **Learn & Improve**
   - Update procedures
   - Train as needed
   - Implement prevention

### Managing Customer Changes

**Customer Wants to Change Order:**

1. **Capture Change Request**
   - What do they want changed?
   - Why the change?
   - When do they need it?

2. **Assess Impact**
   - What work is already done?
   - Can we accommodate?
   - Cost impact?
   - Schedule impact?

3. **Quote the Change**
   - Additional cost
   - Time extension needed
   - Any credits if scope reduced

4. **Get Approval**
   - Customer approves cost/time
   - Document agreement
   - Update paperwork

5. **Create Change Request** (if needed)
   - Formal CR in system
   - Link to job
   - Track implementation

6. **Update Job**
   - Modify work orders
   - Adjust quantities
   - Update drawings
   - Revise schedule

7. **Communicate**
   - Alert production
   - Update sales order
   - Adjust invoicing

### End of Day Checklist

**For Production Supervisors:**

- ✅ All employees clocked out
- ✅ Active work closed out properly
- ✅ Quantities recorded
- ✅ Any problems documented
- ✅ Hot jobs status checked
- ✅ Materials staged for tomorrow
- ✅ Work orders printed for next day
- ✅ Equipment shut down safely
- ✅ Area cleaned and organized

**For Planners/Schedulers:**

- ✅ New jobs entered
- ✅ Priority changes noted
- ✅ Work released for tomorrow
- ✅ Material shortages identified
- ✅ Schedule updated
- ✅ Customer requests handled

---

## Tips & Best Practices

### General Best Practices

✅ **Enter Data Promptly** - Don't wait until end of day  
✅ **Be Accurate** - Garbage in, garbage out  
✅ **Add Notes** - Future you will thank you  
✅ **Upload Documents** - Keep everything together  
✅ **Communicate Changes** - Don't assume others know  
✅ **Review Before Releasing** - Catch problems early  
✅ **Close Completed Work** - Keep lists clean  
✅ **Use Filters** - Find what you need fast

### Data Entry Tips

✅ **Use Consistent Naming** - Makes searching easier  
✅ **Fill in All Fields** - More information is better  
✅ **Double-Check Numbers** - Quantities, dates, costs  
✅ **Save Frequently** - Don't lose work  
✅ **Verify Customer Info** - Avoid shipping errors

### Communication Best Practices

✅ **Document Verbal Agreements** - Add notes  
✅ **Update Status** - Keep everyone informed  
✅ **Respond to Notifications** - People are waiting  
✅ **Escalate Problems** - Don't hide issues  
✅ **Share Knowledge** - Help others learn

### Quality Best Practices

✅ **Follow Change Request Process** - Don't skip it  
✅ **Document Problems** - Help prevent recurrence  
✅ **Complete Root Cause** - Fix it permanently  
✅ **Verify Drawings** - Always use latest revision  
✅ **Inspect Work** - Quality is everyone's job

### Efficiency Tips

✅ **Use Search** - Faster than scrolling  
✅ **Save Favorite Filters** - Reuse common searches  
✅ **Keyboard Shortcuts** - Learn them  
✅ **Batch Similar Tasks** - Enter all jobs at once  
✅ **Keep Notes Template** - Copy and modify

### Security & Safety

✅ **Log Out When Done** - Protect data  
✅ **Don't Share Passwords** - Security requirement  
✅ **Verify Before Deleting** - Can't always undo  
✅ **Back Up Important Work** - Save copies  
✅ **Report Suspicious Activity** - Security matters

---

## Troubleshooting

### Common Issues and Solutions

#### "I Can't Find My Job"

**Try These:**
1. Check your filters - might be filtered out
2. Clear all filters and search again
3. Try searching by customer name
4. Check if job was closed
5. Verify you're in right company (tenant)

#### "I Can't Edit Something"

**Possible Reasons:**
- You don't have permission (contact admin)
- Item is locked (already shipped, closed, etc.)
- Someone else is editing it
- Your session timed out (log out and back in)

#### "Work Order Won't Release"

**Check:**
- Materials available?
- Previous operations complete?
- Quality hold present?
- Drawings attached?
- Work center assigned?

#### "Can't Clock Into Work Order"

**Verify:**
- Work order is released
- Your employee record is set up
- Work center is correct
- No one else clocked into same operation
- Work order not on hold

#### "Job Is Missing Information"

**To Fix:**
- Open job in edit mode
- Fill in missing fields
- Save changes
- If can't edit, contact job creator or supervisor

#### "Wrong Due Date"

**To Update:**
- Open job or work order
- Edit due date
- System may recalculate other dates
- Check that all dates make sense
- Save changes

#### "Scrap Not Recording"

**Make Sure:**
- Entering scrap during receive operation
- Selecting scrap reason
- Quantity is positive number
- You have permission to record scrap
- Clicking save

#### "Can't Upload Files"

**Check:**
- File size not too large (typically 10-50MB limit)
- File type is supported
- Internet connection working
- Browser is up to date
- Have permission to upload

#### "Report Shows No Data"

**Verify:**
- Date range includes data
- Filters not too restrictive
- You have permission to see data
- Data has been entered
- Try broader search first

### Getting Help

**If You're Stuck:**

1. **Check This Guide** - Answers might be here
2. **Ask a Coworker** - Someone may know
3. **Try the Help Button** - System may have help text
4. **Contact Your Supervisor** - They can assist
5. **Submit IT Ticket** - For technical issues
6. **Contact System Admin** - For permissions or setup

### Performance Issues

**If System is Slow:**

- Close unnecessary browser tabs
- Clear browser cache
- Check internet connection
- Try different browser
- Report persistent issues to IT

---

## Quick Reference Guide

### Common Actions

| What You Want to Do | Where to Go |
|---------------------|-------------|
| Create a new job | Workflow → Manage Jobs → + Add |
| Find a job | Workflow → Manage Jobs → Search |
| Release work to production | Workflow → Release Work |
| See what's being worked on | Workflow → Active Work |
| Create change request | Workflow → Change Requests → + Add |
| Upload a drawing | Open job → Attachments → Upload |
| Add a note | Open job/work order → Notes → + Add |
| Check job status | Workflow → Manage Jobs → Click job |
| Print work order | Workflow → Work Orders → Print |
| Close a work order | Inventory → Close Work Order |
| View reports | Workflow → Workflow Reports |

### Key Terms

| Term | What It Means |
|------|---------------|
| **Job** | Customer order or project |
| **Work Order** | Manufacturing instructions for a job |
| **Operation** | Single manufacturing step |
| **Release** | Give permission to start work |
| **WIP** | Work In Process - partially completed |
| **Router** | Sequence of operations to make something |
| **CR** | Change Request - formal change documentation |
| **MPT** | Make-to-Print - build to customer drawings |
| **Shipper** | Shipping order/documentation |
| **Clock In** | Start time tracking on work |
| **Issue Material** | Assign materials to work order |
| **Receive** | Record operation completion |

### Status Indicators

Different colors and icons indicate status (varies by configuration):

- **Green** - Good, on track
- **Yellow** - Warning, attention needed
- **Red** - Problem, late, or blocked
- **Blue** - Information
- **Gray** - Inactive or closed

### Keyboard Shortcuts (Common)

- **Ctrl+F** or **Cmd+F** - Search page
- **Ctrl+S** or **Cmd+S** - Save (if supported)
- **Escape** - Close dialog
- **Tab** - Move to next field
- **Shift+Tab** - Move to previous field

---

## Conclusion

The Workflow module is your central tool for managing manufacturing operations from customer order through shipping. This guide covered the main features and common tasks.

### Remember:

- **Data Quality Matters** - Accurate information leads to better decisions
- **Communicate Changes** - Keep everyone informed
- **Follow Processes** - They exist for good reasons
- **Document Everything** - You'll thank yourself later
- **Ask Questions** - Better to ask than guess
- **Continuous Improvement** - Always look for ways to do better

### Keep Learning

- Attend training sessions
- Read system updates
- Share tips with coworkers
- Suggest improvements
- Stay curious

---

**Document Version:** 1.0  
**Created:** November 2025  
**For:** Verax Workflow Module Users  
**File:** `WORKFLOW_MODULE_GUIDE.md`

**End of Guide**

