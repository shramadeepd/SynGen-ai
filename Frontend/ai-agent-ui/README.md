# SynGen AI Frontend

A modern Vue.js frontend for the SynGen AI intelligent Text-to-SQL platform.

## Features

- 🤖 **Intelligent Chat Interface** - Natural language queries with real-time responses
- 📊 **Analytics Dashboard** - Interactive data visualizations and insights
- 📄 **Document Search** - AI-powered document retrieval and Q&A
- 🔐 **Authentication** - Secure JWT-based authentication
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎨 **Modern UI** - Built with Tailwind CSS and Heroicons
- ⚡ **Fast Performance** - Optimized with Vite and Vue 3

## Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Axios** - HTTP client for API calls
- **Tailwind CSS** - Utility-first CSS framework
- **Heroicons** - Beautiful SVG icons
- **Chart.js** - Data visualization
- **Vue Toastification** - Toast notifications
- **Vite** - Fast build tool

## Quick Start

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Frontend/ai-agent-ui
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   ```
   http://localhost:3000
   ```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ChatWindow/     # Chat-related components
│   └── HeaderBar.vue   # Application header
├── views/              # Page components
│   ├── LoginView.vue   # Authentication page
│   ├── DashboardView.vue # Main dashboard
│   ├── ChatView.vue    # Chat interface
│   ├── AnalyticsView.vue # Analytics dashboard
│   ├── DocumentsView.vue # Document search
│   └── SettingsView.vue # User settings
├── stores/             # Pinia state management
│   ├── auth.js         # Authentication store
│   └── api.js          # API interaction store
├── router/             # Vue Router configuration
│   └── index.js        # Route definitions
├── App.vue             # Root component
├── main.js             # Application entry point
└── style.css           # Global styles
```

## Key Features

### 🔐 Authentication

- JWT-based authentication
- Role-based access control
- Persistent login sessions
- Secure token management

### 💬 Chat Interface

- Real-time query processing
- Support for SQL and document queries
- Query history and management
- Auto-scroll and loading states
- Query type selection (auto-detect, SQL, document)

### 📊 Analytics Dashboard

- Real-time database statistics
- Interactive data visualizations
- Quick analytics queries
- Top customers and recent orders
- Performance metrics

### 📄 Document Management

- AI-powered document search
- Document upload and categorization
- Semantic and keyword search
- Source attribution and metadata
- Search result highlighting

### ⚙️ Settings & Preferences

- User profile management
- Application preferences
- Query statistics
- Data export functionality
- System information

## API Integration

The frontend integrates with the SynGen AI backend through RESTful APIs:

### Authentication Endpoints
- `POST /auth/token` - User login
- `GET /auth/me` - Get user info
- `POST /auth/register` - User registration

### Query Endpoints
- `POST /api/query` - Unified query processing
- `POST /api/sql` - SQL-specific queries
- `POST /api/rag/query` - Document search
- `POST /api/rag/ingest` - Document upload

### System Endpoints
- `GET /api/stats` - Database statistics
- `GET /health` - Health check

## State Management

### Auth Store (`stores/auth.js`)
- User authentication state
- Login/logout functionality
- Token management
- User profile data

### API Store (`stores/api.js`)
- Query execution and history
- Loading states
- Error handling
- Data caching

## Styling

The application uses Tailwind CSS for styling with:

- **Responsive Design** - Mobile-first approach
- **Dark/Light Theme** - User preference support
- **Custom Components** - Reusable UI patterns
- **Animations** - Smooth transitions and loading states

## Development

### Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Environment Variables

Create a `.env` file in the project root:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=SynGen AI
VITE_APP_VERSION=1.0.0
```

### Code Style

- Use Vue 3 Composition API
- Follow Vue.js style guide
- Use TypeScript for type safety (optional)
- Implement proper error handling
- Write meaningful component names

## Production Deployment

### Build for Production

```bash
npm run build
```

This creates a `dist/` directory with optimized files.

### Deployment Options

1. **Static Hosting** (Netlify, Vercel, GitHub Pages)
2. **CDN** (AWS CloudFront, Cloudflare)
3. **Docker Container**
4. **Traditional Web Server** (Nginx, Apache)

### Docker Deployment

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Performance Optimization

- **Code Splitting** - Automatic route-based splitting
- **Lazy Loading** - Components loaded on demand
- **Image Optimization** - Compressed and responsive images
- **Caching** - API response and asset caching
- **Bundle Analysis** - Monitor bundle size

## Security

- **XSS Protection** - Input sanitization
- **CSRF Protection** - Token-based requests
- **Secure Headers** - Content Security Policy
- **Authentication** - JWT token validation
- **HTTPS** - Secure communication

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the documentation
- Open an issue on GitHub
- Contact the development team 