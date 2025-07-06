## SE-Project-Frontend

This template should help get you started developing with Vue 3 in Vite.

### Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

### Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

### Project Setup

```sh
npm install
```

#### Compile and Hot-Reload for Development

```sh
npm run dev
```

#### Compile and Minify for Production

```sh
npm run build
```

#### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

---

### Project Structure

The frontend is organized for scalability and maintainability, following common Vue 3 and Vite best practices. Below is an overview of the main folders and files:

```
frontend/
├── public/           # Static assets (favicon, images, demo data)
├── src/              # Main source code
│   ├── assets/       # Styles (SCSS, Tailwind), images, and other static resources
│   ├── components/   # Vue components (UI elements, dashboards, registration, etc.)
│   ├── layout/       # Layout components (sidebar, topbar, footer, menu)
│   ├── router/       # Vue Router configuration
│   ├── service/      # API service modules for backend communication
│   ├── store/        # State management (e.g., Vuex or Pinia)
│   └── views/        # Page-level Vue components
├── index.html        # Main HTML entry point
├── package.json      # Project metadata and dependencies
├── vite.config.mjs   # Vite configuration
└── ...
```

#### Key Folders and Files

- **public/**: Contains static files served directly, such as images and demo data. The `images/` folder holds icons and branding assets.
- **src/assets/**: Includes global stylesheets (`styles.scss`, `tailwind.css`) and additional static resources.
- **src/components/**: Houses reusable Vue components, organized by feature (e.g., `doctorDashboard/`, `landing/`, `Registration/`, `seniorDashboard/`).
- **src/layout/**: Contains layout-related components for consistent app structure (sidebar, topbar, footer, etc.).
- **src/router/index.js**: Configures application routes using Vue Router.
- **src/service/**: Provides modules for API calls and business logic, such as `DoctorService.js`, `AppointmentService.js`, and others for handling appointments, notifications, reviews, etc.
- **src/store/**: Intended for state management (e.g., Vuex or Pinia stores).
- **src/views/**: Contains main page components for different routes/views.
- **index.html**: The main HTML template for the app.
- **package.json**: Lists dependencies, scripts, and project metadata.
- **vite.config.mjs**: Vite build and dev server configuration.

#### Main Functionalities

- **User Registration & Authentication**: Components and services for user sign-up, login, and profile management.
- **Doctor & Senior Dashboards**: Dedicated dashboard components for doctors and seniors, providing tailored interfaces and features.
- **Appointment Management**: Services and components for booking, viewing, and managing appointments.
- **Notifications**: Real-time or scheduled notifications for users.
- **Peer Groups & Reviews**: Functionality for managing peer groups and submitting/viewing reviews.
- **Responsive Design**: Utilizes Tailwind CSS and custom SCSS for a modern, responsive UI.

#### Customization & Extensibility

- Easily add new components in `src/components/` and new pages in `src/views/`.
- API endpoints and business logic can be extended in `src/service/`.
- Layout and navigation can be customized via `src/layout/` and `src/router/`.

---

For more details, refer to the inline comments in the source files and the [Vite Documentation](https://vite.dev/).

