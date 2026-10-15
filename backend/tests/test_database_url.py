"""Tests for safe database URL parsing, masking, and health endpoint verification."""

import os
import sys
from pathlib import Path
import unittest

from sqlalchemy.exc import ArgumentError
from sqlalchemy.engine.url import make_url

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")

from app.main import app


class TestDatabaseURLValidation(unittest.TestCase):
    """Test suite to validate DATABASE_URL parsing safety without connecting to external DBs."""

    def test_valid_mysqlconnector_url_parsing(self):
        """Verify that a valid mysql+mysqlconnector connection URL parses successfully."""
        url_str = "mysql+mysqlconnector://aqpg_user:SecurePass123!@db-host.render.com:3306/aqpg_production"
        parsed = make_url(url_str)
        self.assertEqual(parsed.drivername, "mysql+mysqlconnector")
        self.assertEqual(parsed.username, "aqpg_user")
        self.assertEqual(parsed.password, "SecurePass123!")
        self.assertEqual(parsed.host, "db-host.render.com")
        self.assertEqual(parsed.port, 3306)
        self.assertEqual(parsed.database, "aqpg_production")

    def test_invalid_docker_command_url_raises_argument_error(self):
        """Verify that a Docker run command string raises ArgumentError when parsed as a database URL."""
        docker_cmd = "$ docker run --name some-mysql -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/mysql-root -d mysql:tag"
        with self.assertRaises(ArgumentError):
            make_url(docker_cmd)

    def test_database_url_password_masking(self):
        """Verify that password is hidden when converting SQLAlchemy URL object to string."""
        url_str = "mysql+mysqlconnector://myuser:SecretPassword99@localhost:3306/mydb"
        parsed = make_url(url_str)
        safe_str = parsed.render_as_string(hide_password=True)
        self.assertNotIn("SecretPassword99", safe_str)
        self.assertIn("***", safe_str)

    def test_health_endpoint_registered(self):
        """Verify that /health endpoint is registered on the FastAPI app."""
        routes = [route.path for route in app.routes]
        self.assertIn("/health", routes)

    def test_production_environment_missing_database_url_raises_value_error(self):
        """When ENVIRONMENT=production, missing or default SQLite database URL must fail startup clearly."""
        from app.core.config import Settings
        with self.assertRaises(ValueError) as ctx:
            # ENVIRONMENT=production without providing an external DATABASE_URL falls back to default SQLite
            Settings(ENVIRONMENT="production")
        self.assertIn("Production environment requires an external DATABASE_URL", str(ctx.exception))

    def test_production_environment_sqlite_database_url_raises_value_error(self):
        """When ENVIRONMENT=production, an explicit SQLite URL must fail startup clearly."""
        from app.core.config import Settings
        with self.assertRaises(ValueError) as ctx:
            Settings(ENVIRONMENT="production", DATABASE_URL="sqlite:///./aqpg.db")
        self.assertIn("SQLite database is not permitted in production", str(ctx.exception))

    def test_production_environment_valid_external_database_url_succeeds(self):
        """When ENVIRONMENT=production, a valid external database URL must be accepted and preserved."""
        from app.core.config import Settings
        valid_url = "mysql+mysqlconnector://prod_user:SuperSecret123!@db.render.internal:3306/aqpg_prod"
        prod_settings = Settings(ENVIRONMENT="production", DATABASE_URL=valid_url)
        self.assertEqual(prod_settings.DATABASE_URL, valid_url)
        self.assertEqual(prod_settings.ENVIRONMENT, "production")

    def test_development_environment_preserves_local_sqlite_database_url(self):
        """When ENVIRONMENT=development, local SQLite canonical URL must be preserved."""
        from app.core.config import Settings
        dev_settings = Settings(ENVIRONMENT="development", DATABASE_URL="sqlite:///./aqpg.db")
        self.assertEqual(dev_settings.ENVIRONMENT, "development")
        self.assertTrue(dev_settings.DATABASE_URL.startswith("sqlite:///"))
        self.assertIn("aqpg.db", dev_settings.DATABASE_URL)


if __name__ == "__main__":
    unittest.main()

