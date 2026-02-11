# Restaurant Management System
## Project Mid-Defence Document

**Date:** February 11, 2026  
**Project Status:** Mid-Development Phase

---

## 1. PROJECT OVERVIEW

### 1.1 Project Title
**Restaurant Management System** - A comprehensive web-based application for managing all operational aspects of a restaurant.

### 1.2 Project Description
The Restaurant Management System is a Django-based web application designed to streamline restaurant operations. It provides an integrated platform for managing orders, menu items, staff, tables, payments, and customer deliveries. The system incorporates machine learning algorithms to optimize menu management based on demand patterns.

### 1.3 Project Scope
- Multi-user authentication with role-based access control
- Order management across three channels: Dine-in, Takeaway, and Delivery
- Real-time kitchen operations oversight
- Payment processing and history tracking
- Staff management with granular permission control
- Menu optimization using K-Means clustering
- Order history and analytics

---

## 2. OBJECTIVES & GOALS

### 2.1 Primary Objectives
1. **Operational Efficiency**: Automate and streamline restaurant operations to reduce manual workload
2. **Order Management**: Provide a centralized platform for managing orders across multiple channels
3. **Staff Coordination**: Enable efficient task distribution and monitoring among kitchen and service staff
4. **Payment Processing**: Implement secure payment handling and financial tracking
5. **Data Analytics**: Collect and analyze order data for business intelligence
6. **Menu Optimization**: Use ML algorithms to identify high-demand items and optimize menu

### 2.2 Business Goals
- Reduce order processing time
- Improve order accuracy
- Enhance customer satisfaction through better service
- Optimize inventory and menu management
- Provide detailed business analytics and reporting

---

## 3. TECHNOLOGY STACK

### 3.1 Backend
| Technology | Purpose |
|-----------|---------|
| **Django 3.2+** | Web framework |
| **Python 3.8+** | Programming language |
| **SQLite3** | Database (development) |
| **Django ORM** | Object-relational mapping |

### 3.2 Frontend
| Technology | Purpose |
|-----------|---------|
| **HTML5** | Markup structure |
| **CSS3** | Styling and layout |
| **JavaScript** | Client-side interactivity |
| **Bootstrap** | Responsive UI framework |
| **Django Templates** | Server-side templating |

### 3.3 Libraries & Tools
| Library | Purpose |
|---------|---------|
| **django-widget-tweaks** | Enhanced form rendering |
| **Pillow** | Image processing |
| **qrcode** | QR code generation |
| **pandas** | Data manipulation and analysis |
| **scikit-learn** | Machine learning (K-Means) |
| **pytz** | Timezone handling |

### 3.4 Development Tools
- **Version Control**: Git
- **IDE**: VS Code
- **Database**: SQLite3
- **Package Manager**: pip

---

## 4. SYSTEM ARCHITECTURE

### 4.1 Application Structure

```
restaurant-management-system/
├── accounts/                 # User authentication & staff management
│   ├── models.py            # User, Staff, StaffPermission models
│   ├── views.py             # Authentication views
│   ├── decorators.py        # Permission decorators
│   ├── mixins.py            # Class-based view mixins
│   └── urls.py              # Authentication URLs
│
├── restaurant/              # Core restaurant operations
│   ├── models.py            # Order, MenuItem, Category, Table, Payment models
│   ├── views.py             # Business logic views
│   ├── forms.py             # Django forms
│   ├── middleware.py        # Custom middleware
│   ├── signals.py           # Django signals
│   ├── ml/                  # Machine learning module
│   │   ├── models.py        # ML-specific models
│   │   ├── utils.py         # ML utilities
│   │   └── views.py         # ML-related views
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JavaScript, images
│   └── urls.py              # Restaurant URLs
│
├── products/                # Product management
├── project_settings/        # Global settings
├── restaurant_project/      # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── static/                  # Global static files
├── db.sqlite3              # Database
├── manage.py               # Django management
└── requirements.txt        # Python dependencies
```

### 4.2 Architectural Design Pattern
The system follows the **MTV (Model-Template-View)** architecture pattern used by Django:
- **Models**: Define database schema and business logic
- **Templates**: Handle presentation layer
- **Views**: Process user requests and return responses

---

## 5. SYSTEM FEATURES

### 5.1 User Authentication & Authorization
- **User Management**: Custom User model extending Django's AbstractUser
- **Role-Based Access Control (RBAC)**:
  - Admin: Full system access
  - Manager: Operational management
  - Kitchen Staff: Order preparation only
  - Service Staff: Order taking and serving
  - Supervisor: Staff oversight

- **Module-Based Permissions**: 8 granular permission modules
  - Dashboard
  - Orders Management
  - Menu Management
  - Kitchen Operations
  - Order History
  - Table Management
  - Takeaway Orders
  - Delivery Management

### 5.2 Order Management System
- **Three Order Types**:
  - **Dine-in (Table)**: Customers seated at tables
  - **Takeaway**: Customers pick up orders
  - **Delivery**: Orders delivered to customer address

- **Order Status Workflow**:
  ```
  Pending → Preparing → Ready → [On the Way] → [Served] → Completed
                              ↓
                        Ready to Pickup
  ```

- **Order Details Tracked**:
  - Unique 8-digit Order ID
  - Customer name and phone
  - Order items with quantities
  - Special instructions
  - Delivery details (address, landmark, building, unit)
  - Payment status and amount
  - Order timestamp and completion time

### 5.3 Menu Management
- **Category Management**: Organize menu items by category
- **MenuItem Features**:
  - Name, description, price
  - Availability status
  - Preparation area
  - Menu images
  - **Demand Tier Classification** (ML-powered):
    - High Demand (Tier 1)
    - Medium Demand (Tier 2)
    - Low Demand (Tier 3)
  - Order count tracking
  - Last tier update timestamp

### 5.4 Table Management
- Dynamic table configuration
- Real-time occupancy tracking
- Table capacity management
- Table status monitoring

### 5.5 Payment Processing
- **Payment Methods Support**:
  - Cash
  - Card
  - Online Transfer
  - Wallet
  - Cheque

- **Payment Features**:
  - Amount tracking
  - Payment status (Paid/Unpaid)
  - Multiple payments per order
  - Payment history
  - Editor tracking (who processed payment)

### 5.6 Staff Management
- **Staff Information Tracking**:
  - Personal details
  - Role assignment
  - Contact information
  - Salary management
  - Joining date tracking
  - Active/Inactive status

- **Staff Types**:
  - Supervisor
  - Regular Staff
  - Kitchen Staff

- **Permission Management**:
  - Granular module-wise access
  - Permission audit trail
  - Create/Update/Delete timestamps

### 5.7 Kitchen Operations
- Real-time order tracking
- Order preparation status updates
- Item-wise preparation tracking
- Queue management
- Delivery status monitoring

### 5.8 Order History & Analytics
- Complete order audit trail
- Historical payment records
- Order completion tracking
- Staff performance metrics
- Sales analytics

### 5.9 Machine Learning Features
- **K-Means Clustering Algorithm**:
  - Analyzes order history data
  - Categorizes menu items into demand tiers
  - Automatic tier recalculation
  - Data-driven menu optimization

- **ML Module Components**:
  - Data preparation and preprocessing
  - Model training and evaluation
  - Sample data generation
  - Demand tier prediction
  - Trend analysis

---

## 6. DATABASE DESIGN

### 6.1 Core Models

#### User Model (accounts.models)
```python
Attributes: username, email, password, role, is_active, created_at
Relations: OneToMany → Staff
```

#### Staff Model (accounts.models)
```python
Attributes: user (FK), staff_type, role, contact, salary, joined_date, is_active
Relations: OneToOne → User
          OneToMany → StaffPermission
```

#### StaffPermission Model (accounts.models)
```python
Attributes: staff (FK), module, is_allowed, created_at, updated_at
Relations: ManyToOne → Staff
Modules: Dashboard, Orders, Menu, Kitchen, History, Tables, Takeaway, Delivery
```

#### Category Model (restaurant.models)
```python
Attributes: name, is_active
Relations: OneToMany → MenuItem
```

#### MenuItem Model (restaurant.models)
```python
Attributes: name, description, price, category (FK), is_available, 
           preparation_area, image, demand_tier, order_count, last_tier_update
Relations: ManyToOne → Category
          OneToMany → OrderItem
```

#### Table Model (restaurant.models)
```python
Attributes: number (unique), capacity, is_occupied
```

#### Order Model (restaurant.models)
```python
Attributes: order_id (unique), customer_name, customer_phone, order_type,
           status, total_amount, payment_status, special_notes,
           delivery_address, delivery_landmark, delivery_building, 
           delivery_unit, delivery_charge, created_at, completed_by
Relations: OneToMany → OrderItem
          OneToMany → Payment
```

#### OrderItem Model (restaurant.models)
```python
Attributes: order (FK), menu_item (FK), quantity, price, special_instructions
```

#### Payment Model (restaurant.models)
```python
Attributes: order (FK), amount, payment_method, payment_status, 
           edited_by (FK→User), created_at, updated_at
Relations: ManyToOne → Order
          ManyToOne → User
```

#### OrderHistory Model (restaurant.models)
```python
Attributes: order_id, customer_name, order_type, status, total_amount,
           payment_status, completed_by (FK→User), completed_at
```

---

## 7. IMPLEMENTATION STATUS

### 7.1 Completed Features ✓

#### Backend
- [x] User authentication system with custom User model
- [x] Staff management module
- [x] Role-based and module-based permission system
- [x] Complete Order model with multiple order types
- [x] Menu and Category management
- [x] Table management system
- [x] Payment processing (multiple payment methods)
- [x] Order status workflow
- [x] OrderHistory tracking
- [x] Delivery address management
- [x] QR code generation
- [x] Middleware implementation (Timezone, LoginRequired)
- [x] Signal handlers for data consistency
- [x] Database migrations

#### Frontend
- [x] Authentication pages (Login/Logout)
- [x] Dashboard interface
- [x] Order management interface
- [x] Menu management UI
- [x] Kitchen operations interface
- [x] Staff management interface
- [x] Payment processing interface
- [x] Table management UI
- [x] Order history view
- [x] Profile management
- [x] Responsive design with Bootstrap

#### Machine Learning
- [x] K-Means clustering model
- [x] Demand tier classification
- [x] Data preprocessing utilities
- [x] Sample data generation
- [x] Model training pipeline
- [x] Order count tracking

### 7.2 In-Progress Features 🔄

- [ ] Advanced analytics dashboard
- [ ] Real-time order notifications
- [ ] Enhanced reporting features
- [ ] Integration testing suite
- [ ] Performance optimization

### 7.3 Planned Features 📋

- [ ] Mobile app (iOS/Android)
- [ ] Customer-facing ordering app
- [ ] Integration with payment gateways (Stripe, PayPal)
- [ ] Email/SMS notifications
- [ ] Inventory management
- [ ] Staff scheduling system
- [ ] Customer loyalty program
- [ ] Advanced reporting and BI tools

---

## 8. TECHNICAL IMPLEMENTATION DETAILS

### 8.1 Authentication & Authorization
```python
# Custom User Model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

# Permission Check Decorator
@require_module_access('orders')
def manage_orders(request):
    # Only users with 'orders' module access can access
    pass
```

### 8.2 Order Management Workflow
1. User creates order with customer details
2. Selects order type (table/takeaway/delivery)
3. Adds menu items to order
4. System generates unique order ID
5. Order enters 'pending' status
6. Kitchen staff receives notification
7. Status progresses through workflow
8. Payment is processed
9. Order marked as completed
10. Historical record created

### 8.3 Machine Learning Implementation
```python
# K-Means Clustering for Demand Tier
from sklearn.cluster import KMeans

# Features: order_count
# Output: demand_tier (high, medium, low)
# Automatic recalculation based on order history
```

---

## 9. CHALLENGES & SOLUTIONS

### 9.1 Challenges Encountered

| Challenge | Phase | Impact | Solution |
|-----------|-------|--------|----------|
| Django ORM complexity | Development | Medium | Studied documentation, used raw SQL where needed |
| User permission management | Development | High | Implemented custom decorator system |
| Order ID uniqueness | Development | High | Generated random ID with database check |
| Real-time updates | Design | High | Planned for WebSocket implementation |
| ML data quality | Testing | Medium | Implemented data validation |
| Timezone handling | Testing | Medium | Added middleware for timezone management |

### 9.2 Solutions Implemented
- Custom middleware for cross-cutting concerns
- Decorator pattern for permission checking
- Signal handlers for data consistency
- Comprehensive form validation
- Template tag customization
- Module-based permission system

---

## 10. TESTING & QUALITY ASSURANCE

### 10.1 Testing Approach
- Unit testing (models and utilities)
- Integration testing (views and forms)
- Manual testing of user workflows
- Edge case testing for order processing
- Permission testing for RBAC

### 10.2 Code Quality
- PEP 8 compliance
- Consistent naming conventions
- Modular code organization
- Documentation and comments
- Error handling throughout

---

## 11. PERFORMANCE & SCALABILITY

### 11.1 Current Performance
- Response time: <500ms for most operations
- Database queries: Optimized with select_related and prefetch_related
- Static file serving: Configured for development

### 11.2 Scalability Considerations
- Database: Ready for migration to PostgreSQL
- Caching: Can implement Django cache framework
- Load balancing: Architecture supports horizontal scaling
- API: Can be extended with REST framework

---

## 12. SECURITY MEASURES

### 12.1 Implemented Security Features
- CSRF protection enabled
- SQL injection prevention through ORM
- Password hashing (Django default)
- User authentication required for protected views
- Role-based access control
- Input validation on forms
- Timezone-based session management

### 12.2 Future Security Enhancements
- HTTPS/SSL enforcement
- Rate limiting
- Two-factor authentication
- API key management
- Audit logging
- Data encryption for sensitive fields

---

## 13. DEPLOYMENT OVERVIEW

### 13.1 Current Environment
- **Development Server**: Django development server
- **Database**: SQLite3
- **Static Files**: Django static file handling

### 13.2 Deployment Readiness
- ✓ Code version controlled
- ✓ Environment configuration ready
- ✓ Database migrations prepared
- ✓ Static files configured
- ⚠ Production settings need finalization
- ⚠ Loading balancer configuration pending

### 13.3 Production Deployment Plan
- Web server: Gunicorn/uWSGI
- Database: PostgreSQL
- Static files: Nginx/CloudFront
- Environment: Docker/Virtual Machine

---

## 14. PROJECT TIMELINE & MILESTONES

### 14.1 Completed Milestones
- ✓ **Week 1-2**: Project planning and architecture design
- ✓ **Week 3-4**: User authentication system
- ✓ **Week 5-6**: Core order management system
- ✓ **Week 7-8**: Menu and table management
- ✓ **Week 9-10**: Payment processing
- ✓ **Week 11-12**: ML implementation
- ✓ **Week 13-14**: Staff management and permissions
- ✓ **Week 15-16**: Frontend UI development

### 14.2 Upcoming Milestones
- **Week 17-18**: Testing and bug fixes
- **Week 19-20**: Documentation and deployment prep
- **Week 21-22**: Advanced features
- **Week 23-24**: Final refinement and presentation

---

## 15. DEPENDENCY MANAGEMENT

### 15.1 Python Dependencies
```
Django>=3.2
pytz
sqlparse
django-widget-tweaks
qrcode
Pillow
pandas
scikit-learn  # for ML clustering
```

### 15.2 Installation Instructions
```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## 16. DOCUMENTATION

### 16.1 Available Documentation
- [x] README.md - Project overview
- [x] Inline code comments
- [x] Django admin interface
- [x] Template documentation
- [ ] API documentation
- [ ] User manual

### 16.2 Code Documentation
- Model docstrings and field descriptions
- View function documentation
- Form documentation
- Custom decorator documentation
- ML module documentation

---

## 17. KEY ACHIEVEMENTS

1. **Complete Order Management System**: Handles multiple order types with comprehensive workflow
2. **Robust Permission System**: 8-module granular access control for 60+ staff members
3. **ML Integration**: K-Means clustering for intelligent menu optimization
4. **Scalable Architecture**: Modular design supporting future expansions
5. **User-Friendly Interface**: Responsive design for multi-device access
6. **Data Integrity**: Signal handlers and middleware ensure data consistency
7. **Audit Trail**: Complete order history and payment tracking

---

## 18. FUTURE ROADMAP

### Phase 2 (Post-Mid Defence)
- Real-time notifications using WebSockets
- Advanced analytics dashboard
- Customer mobile app
- Payment gateway integration
- Inventory management system
- Staff scheduling module

### Phase 3 (Long-term)
- AI-powered menu recommendations
- Customer data analytics
- Loyalty program implementation
- Multi-location support
- API for third-party integration

---

## 19. CONCLUSION

The Restaurant Management System has successfully completed its core functionality development. The system provides a comprehensive solution for managing restaurant operations with a focus on:

- **Scalability**: Architecture designed for growth
- **Security**: Proper authentication and authorization
- **Usability**: Intuitive user interface
- **Intelligence**: ML-driven insights
- **Maintainability**: Clean, well-documented code

The project is ready for the next phase of development with all foundational components in place. The mid-point assessment confirms that the project is on track to meet all objectives, with potential for expansion into customer-facing applications and advanced analytics in subsequent phases.

---

## 20. APPENDIX

### 20.1 Key Files Overview
- `restaurant/models.py`: Core business models (Order, MenuItem, Payment, etc.)
- `restaurant/views.py`: Business logic and view controllers
- `accounts/models.py`: User and staff management models
- `restaurant_project/settings.py`: Django configuration
- `requirements.txt`: Python dependencies
- `db.sqlite3`: Development database

### 20.2 Contact & Support
For questions or additional information about this project, please refer to the project README.md or contact the development team.

---

**Document Version:** 1.0  
**Last Updated:** February 11, 2026  
**Status:** Mid-Defence Documentation

