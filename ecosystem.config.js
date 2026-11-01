module.exports = {
  apps: [
    {
      name: "rightfit-backend",
      cwd: __dirname,
      script: "./venv/bin/python",
      args: "-m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 2",
      env: {
        APP_ENV: "production",
        DEBUG: "false",
        PORT: "8000"
      },
      restart_delay: 3000,
      max_restarts: 15,
      autorestart: true
    },
    {
      name: "rightfit-startup-intel",
      cwd: __dirname + "/services/startup_intelligence",
      script: __dirname + "/venv/bin/python",
      args: "-m uvicorn main:app --host 127.0.0.1 --port 8002 --workers 1",
      env: {
        PORT: "8002"
      },
      restart_delay: 3000,
      max_restarts: 15,
      autorestart: true
    },
    {
      name: "rightfit-frontend",
      cwd: __dirname + "/frontend",
      script: "npm",
      args: "start -- -p 3000",
      env: {
        NODE_ENV: "production",
        PORT: "3000"
      },
      restart_delay: 3000,
      max_restarts: 15,
      autorestart: true
    }
  ]
};
