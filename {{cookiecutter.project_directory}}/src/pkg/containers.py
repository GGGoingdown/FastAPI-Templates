from dependency_injector import containers, providers

from src.config import Settings
from src.pkg import services, repositories, db


class Gateway(containers.DeclarativeContainer):
    config: Settings = providers.Configuration()

    database_resource = providers.Resource(db.DatabaseResource, dsn=config.pg_dsn)

    cache_resource = providers.Resource(db.CacheResource, dsn=config.redis_dsn)


class Service(containers.DeclarativeContainer):
    config: Settings = providers.Configuration()
    gateway: Gateway = providers.DependenciesContainer()

    logger_resource = providers.Resource(
        services.LoggerInit,
        app_name=config.app_name,
        log_path=config.log_path,
        show_log_level=config.show_log_level,
        write_log_level=config.write_log_level,
    )

    # Authentication and Authorization
    jwt_handler = providers.Singleton(
        services.JWTHandler,
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
        expired_time_minute=config.jwt_expire_min,
    )

    auth_service = providers.Singleton(
        services.AuthService,
        jwt_handler=jwt_handler,
        admin_username=config.admin_username,
        admin_password=config.admin_password,
    )

    # Repositories
    user_repository = providers.Singleton(repositories.UserRepository)

    # Services
    database_service = providers.Singleton(
        services.DBService, user_repo=user_repository
    )
    cache_service = providers.Singleton(
        services.CacheService, client=gateway.cache_resource
    )


class Application(containers.DeclarativeContainer):
    config: Settings = providers.Configuration()
    gateway: Gateway = providers.Container(Gateway, config=config)
    service: Service = providers.Container(Service, config=config, gateway=gateway)
