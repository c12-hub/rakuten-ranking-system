(function () {
  window.exportRakutenJson = function exportRakutenJson(payload) {
    if (!payload) {
      alert("No JSON data to export yet.");
      return;
    }

    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "downloaded_rakuten.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };
})();
