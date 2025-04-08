const { spawn } = require("child_process");

const shell = process.env.SHELL || "/bin/bash";
const cmd = ". .venv/bin/activate && uvicorn main:app --reload --env-file=.env";

const child = spawn(shell, ["-c", cmd], {
  stdio: "inherit",
  cwd: __dirname,
});

child.on("exit", (code, signal) => {
  // 👇 Exit cleanly even on Ctrl+C
  if (signal === "SIGINT" || code === 0) {
    process.exit(0);
  } else {
    console.error(`FastAPI exited with code ${code} or signal ${signal}`);
    process.exit(code || 1);
  }
});