window.onload = () => {
  document.getElementById("select-directory").addEventListener("click", () => {
    window.electron
      .selectDirectory()
      .then((selectedPath) => {
        console.log(`Selected directory: ${selectedPath}`);
      })
      .catch((err) => {
        console.error("Error handling directory selection:", err);
      });
  });

  window.electron.on("show-status", (message) => {
    const statusBar = document.getElementById("statusBar");
    statusBar.textContent = message;
    statusBar.style.display = "block";
  });

  window.electron.on("hide-status", () => {
    document.getElementById("statusBar").style.display = "none";
  });
};
