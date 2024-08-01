const { app, BrowserWindow, dialog, ipcMain } = require("electron");
const path = require("path");
const { exec } = require("child_process");

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      enableRemoteModule: false,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile("index.html");
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (mainWindow === null) createWindow();
});

ipcMain.handle("select-directory", async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ["openDirectory"],
  });

  if (!result.canceled) {
    const selectedPath = result.filePaths[0];
    mainWindow.webContents.send("show-status", "Processing..."); // Show status bar with message
    runPythonScript(selectedPath);
    return selectedPath;
  }
});

const runPythonScript = (dirPath) => {
  const pythonScriptPath = path.join(__dirname, "python", "organize_movies.py");
  const pythonExe = "python"; // Adjust if using a different Python executable

  exec(
    `${pythonExe} ${pythonScriptPath} "${dirPath}"`,
    (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing Python script: ${error}`);
        return;
      }
      console.log(`Python script output: ${stdout}`);
      if (stderr) {
        console.error(`Python script stderr: ${stderr}`);
      }
      mainWindow.webContents.send("hide-status"); // Hide status bar when processing is complete
    }
  );
};
