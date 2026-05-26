(function () {
  const COLUMNS = [
    ["itemName", "商品名"],
    ["itemPrice", "价格"],
    ["shopName", "店铺"],
    ["reviewCount", "评论数"],
    ["reviewAverage", "评分"],
    ["itemUrl", "商品URL"],
    ["mainImageUrl", "主图URL"],
    ["rank", "排名"],
    ["genreId", "类目ID"],
    ["fetchedAt", "抓取时间"],
  ];

  window.exportRakutenCsv = function exportRakutenCsv(items) {
    if (!Array.isArray(items) || items.length === 0) {
      alert("No ranking data to export yet.");
      return;
    }

    const header = COLUMNS.map((column) => csvCell(column[1])).join(",");
    const rows = items.map((item) =>
      COLUMNS.map((column) => csvCell(item[column[0]] ?? "")).join(",")
    );
    const csv = "\ufeff" + [header, ...rows].join("\r\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const date = new Date().toISOString().slice(0, 10).replaceAll("-", "");
    link.href = url;
    link.download = `ranking_100371_${date}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  function csvCell(value) {
    const text = String(value ?? "");
    return `"${text.replaceAll('"', '""')}"`;
  }
})();
