const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electron", {
  selectDirectory: () => ipcRenderer.invoke("select-directory"),
  on: (channel, callback) =>
    ipcRenderer.on(channel, (event, ...args) => callback(...args)),
});
