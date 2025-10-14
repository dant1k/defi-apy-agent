export function formatLabel(value: string): string {
  if (!value) {
    return value;
  }
  return value
    .split(/[-_\s]/)
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join(" ");
}

export function formatNumber(value?: number, fractionDigits = 2): string {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "-";
  }
  return value.toLocaleString("ru-RU", { maximumFractionDigits: fractionDigits });
}

export function formatPercent(value?: number | null, fractionDigits = 2): string {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "-";
  }
  return `${value.toFixed(fractionDigits)}%`;
}

export function formatLockup(days?: number): string {
  if (days === undefined || days === null) {
    return "-";
  }
  if (days === 0) {
    return "нет";
  }
  if (days % 30 === 0) {
    return `${days / 30} мес.`;
  }
  if (days % 7 === 0) {
    return `${days / 7} нед.`;
  }
  return `${days} дней`;
}
