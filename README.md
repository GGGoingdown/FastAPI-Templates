# FastAPI-Templates

## Features

- **RDBMS ORM Integration**: Utilizes Tortoise ORM for efficient and intuitive interaction with relational databases, offering a high-level asynchronous ORM interface.
- **Redis Support**: Implements Redis as a fast, open-source, in-memory data structure store, used as a database, cache, and message broker.
- **Celery Support**: Integrates Celery, an asynchronous task queue based on distributed message passing, for handling real-time operations as well as scheduled tasks, improving application performance and scalability.
- **API Client Support**: Includes built-in support for creating and managing external API clients, facilitating seamless integration with third-party services.
- **Authentication**: Supports both JWT (JSON Web Tokens) and Basic Authentication methods, ensuring secure access to the application's endpoints.
- **Package Management**: Uses PDM for package management, providing a modern and straightforward approach to managing project dependencies and environments.
- **Pre-commit File Support**: Integrates pre-commit hooks to automatically check and fix code before commits, enhancing code quality and consistency.
- **Docker Support**: Fully compatible with Docker, including Docker Compose, for easy deployment and scaling within containerized environments.
- **Unit Testing**: Offers comprehensive unit test support, encouraging test-driven development (TDD) practices to ensure code reliability and functionality.
- **Continuous Integration (CI) Support**: Implements Continuous Integration practices with built-in support for popular CI tools and platforms.
- **GitHub Actions Support**: Leverages GitHub Actions for automation of workflows, including but not limited to, CI/CD, testing, and deployment processes. Utilizes [ACT](https://github.com/nektos/act) for running actions locally, facilitating development and testing of workflows.

## Getting Started

Generate project:
```
cookiecutter https://github.com/GGGoingdown/FastAPI-Templates.git
```

## License
MIT
