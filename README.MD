# SolarRally - EV Charging Station Management System

## Overview
SolarRally is a comprehensive EV charging station management system designed for solar-powered charging infrastructure. The platform provides real-time monitoring, user management, session tracking, and IoT integration for electric vehicle charging stations.

## 🚀 Features

### Core Functionality
- **Real-time EVSE Monitoring**: Live telemetry data from charging stations
- **User Authentication & Management**: Secure user registration, login, and profile management
- **Charging Session Management**: Track charging sessions, energy consumption, and costs
- **Dashboard Analytics**: Comprehensive dashboard with real-time metrics and historical data
- **IoT Integration**: MQTT-based communication with charging hardware
- **Solar Integration**: Monitor solar energy production and grid/solar energy switching

### Technical Features
- **WebSocket Support**: Real-time data streaming to frontend
- **RESTful API**: Comprehensive API for all system operations
- **Database Management**: PostgreSQL with proper migrations and relationships
- **Authentication**: JWT-based authentication with refresh tokens
- **Device Simulation**: Mock EVSE publishers for development and testing
- **Cloud Deployment**: Production-ready AWS deployment configuration

## 🏗️ Architecture

### Backend (FastAPI)
- **API Server**: FastAPI with automatic OpenAPI documentation
- **Authentication**: JWT tokens with bcrypt password hashing
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-time**: WebSocket connections for live data
- **MQTT Integration**: Paho MQTT client for device communication

### Frontend (React)
- **UI Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: React hooks and context
- **Real-time Updates**: WebSocket integration
- **Responsive Design**: Mobile-first responsive layout

### Database Schema
- **Users**: User accounts with authentication
- **EVSE Units**: Charging station configuration
- **Charging Sessions**: Session tracking and billing
- **Telemetry**: Real-time device data storage

## 🛠️ Technologies

### Backend Stack
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - Python ORM
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Paho MQTT** - IoT messaging
- **Uvicorn** - ASGI server

### Frontend Stack
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library

### DevOps & Cloud
- **Docker** - Containerization
- **AWS** - Cloud infrastructure
- **Terraform** - Infrastructure as Code
- **GitHub Actions** - CI/CD pipeline

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Docker (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/SolarRally.git
   cd SolarRally
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup environment variables
   cp .env.example .env
   # Edit .env with your database credentials
   
   # Run database migrations
   alembic upgrade head
   
   # Start the backend server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   ```

4. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb solarrally
   
   # The backend will automatically create tables on first run
   ```

5. **MQTT Broker (Optional)**
   ```bash
   # Install Mosquitto MQTT broker
   # Ubuntu/Debian:
   sudo apt-get install mosquitto mosquitto-clients
   
   # macOS:
   brew install mosquitto
   
   # Windows: Download from https://mosquitto.org/download/
   
   # Start broker
   mosquitto -v
   ```

## 🚀 Quick Start

1. **Start all services**
   ```bash
   # Terminal 1: Backend
   cd backend && uvicorn app.main:app --reload
   
   # Terminal 2: Frontend  
   cd frontend && npm run dev
   
   # Terminal 3: MQTT Broker
   mosquitto -v
   
   # Terminal 4: Mock EVSE (optional)
   cd backend && python mock_evse_publisher.py
   ```

2. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. **Create your first user**
   - Navigate to the frontend
   - Click "Register" to create an account
   - Login and start monitoring your charging stations

## 🌐 AWS Deployment

SolarRally includes production-ready AWS deployment configuration using Terraform.

### Quick AWS Deployment
```bash
# Configure AWS CLI
aws configure

# Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# Deploy application
cd ..
./scripts/deploy_to_aws.sh deploy prod us-east-1 default
```

### AWS Architecture
- **IoT Core**: Managed MQTT broker for device communication
- **ECS Fargate**: Containerized backend deployment
- **RDS PostgreSQL**: Managed database service
- **S3 + CloudFront**: Static frontend hosting with CDN
- **Application Load Balancer**: High availability and SSL termination
- **VPC**: Secure network isolation

For detailed deployment instructions, see [AWS_GETTING_STARTED.md](docs/AWS_GETTING_STARTED.md)

## 📖 API Documentation

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user profile

### EVSE Management
- `GET /api/v1/evse/units` - List all EVSE units
- `POST /api/v1/evse/units` - Create new EVSE unit
- `GET /api/v1/evse/units/{unit_id}` - Get specific EVSE unit
- `PUT /api/v1/evse/units/{unit_id}` - Update EVSE unit

### Charging Sessions
- `GET /api/v1/sessions` - List charging sessions
- `POST /api/v1/sessions/start` - Start charging session
- `POST /api/v1/sessions/stop` - Stop charging session
- `GET /api/v1/sessions/{session_id}` - Get session details

### Real-time Data
- `WebSocket /ws` - Real-time telemetry data stream
- `GET /api/v1/telemetry/latest` - Latest telemetry readings

Full API documentation available at `/docs` when running the backend.

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://username:password@localhost/solarrally

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# Application
DEBUG=True
CORS_ORIGINS=["http://localhost:5173"]
```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Start all services first
npm run test:integration
```

## 🐳 Docker Deployment

### Development
```bash
docker-compose up --build
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring & Analytics

### Metrics Available
- **Real-time Charging Data**: Voltage, current, power, energy
- **Session Analytics**: Duration, energy consumed, cost
- **User Analytics**: Active users, session frequency
- **System Health**: API response times, error rates
- **IoT Metrics**: Device connectivity, message throughput

### Dashboards
- **Operations Dashboard**: Real-time system overview
- **Business Dashboard**: Revenue and usage analytics
- **Technical Dashboard**: System performance metrics

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt rounds
- **CORS Protection**: Configurable cross-origin policies
- **Input Validation**: Pydantic models for API validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **Rate Limiting**: API endpoint rate limiting
- **HTTPS**: SSL/TLS encryption in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` directory for detailed guides
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions and community support

## 🗺️ Roadmap

### Phase 7 (Planned)
- [ ] Mobile application (React Native)
- [ ] Advanced analytics and reporting
- [ ] Multi-tenant support
- [ ] Payment gateway integration
- [ ] Load balancing and auto-scaling

### Phase 8 (Future)
- [ ] Machine learning for predictive analytics
- [ ] Integration with renewable energy forecasting
- [ ] Fleet management for commercial users
- [ ] API marketplace for third-party integrations

## 🙏 Acknowledgments

- FastAPI team for the excellent web framework
- React team for the powerful UI library
- PostgreSQL community for the robust database
- AWS for comprehensive cloud services
- All contributors and users of SolarRally

---

**Built with ❤️ for the future of sustainable transportation**
