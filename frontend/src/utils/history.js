const KEY = "diabetes_prediction_history";

export function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "[]");
  } catch {
    return [];
  }
}

export function saveHistory(items) {
  localStorage.setItem(KEY, JSON.stringify(items));
}

export function addHistory(item) {
  const items = loadHistory();
  items.unshift(item);
  saveHistory(items.slice(0, 50));
  return items;
}

export function deleteHistory(id) {
  const items = loadHistory().filter((x) => x.id !== id);
  saveHistory(items);
  return items;
}

export function clearHistory() {
  localStorage.removeItem(KEY);
}
