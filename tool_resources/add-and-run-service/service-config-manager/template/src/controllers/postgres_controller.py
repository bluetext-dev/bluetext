import psycopg2
import time
from utils.logger import get_logger

class PostgresController:
    """Manages Postgres configuration and SQL execution."""

    def __init__(self, environment, config):
        self.environment = environment
        self.config = config
        self.logger = get_logger('postgres')
        self.host = self._get_env('POSTGRES_HOST')
        self.database = self._get_env('POSTGRES_DB')
        self.user = self._get_env('POSTGRES_USER')
        self.password = self._get_env('POSTGRES_PASSWORD')

    def _get_env(self, key):
        import os
        val = os.environ.get(key)
        if not val:
            raise ValueError(f"Missing environment variable: {key}")
        return val

    def wait_for_connection(self, max_retries=10, delay=5):
        """Wait for Postgres to be ready."""
        for i in range(max_retries):
            try:
                conn = psycopg2.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
                conn.close()
                self.logger.info("✅ Connected to Postgres")
                return True
            except psycopg2.OperationalError as e:
                self.logger.warning(f"⏳ Waiting for Postgres... ({i+1}/{max_retries}): {e}")
                time.sleep(delay)
        return False

    def run_ops(self):
        """Run Postgres configuration operations."""
        self.logger.info("🚀 Starting Postgres operations...")
        
        if not self.wait_for_connection():
            self.logger.error("❌ Failed to connect to Postgres")
            return

        # Load SQL script
        sql_script_path = self.config.load_target_config('postgres')
        if not sql_script_path:
            self.logger.warning("⚠️ No postgres.sql config found")
            return
            
        self.execute_script(sql_script_path)

    def execute_script(self, script_path):
        """Execute a SQL script file."""
        self.logger.info(f"📜 Executing SQL script: {script_path}")
        
        try:
            with open(script_path, 'r') as f:
                sql = f.read()

            conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            # Enable autocommit or handle transactions
            conn.autocommit = True
            
            with conn.cursor() as cursor:
                # Basic execution, might need splitting by ; for large scripts if driver doesn't handle it
                # psycopg2 usually handles multiple statements in one execute call
                cursor.execute(sql)
            
            conn.close()
            self.logger.info("✅ SQL script executed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute SQL script: {e}")
