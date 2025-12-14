"use client";

interface KPIHeaderProps {
  title: string;
  updatedAt?: string;
  warning?: boolean;
}

export default function KPIHeader({ title, updatedAt, warning }: KPIHeaderProps) {
  const formatDate = (dateString?: string): string => {
    if (!dateString) return "—";
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">{title}</h1>
        <div className="text-right">
          {warning && (
            <div className="text-yellow-600 text-sm mb-1">⚠️ Stale data</div>
          )}
          <div className="text-sm text-gray-500">
            Updated: {formatDate(updatedAt)}
          </div>
        </div>
      </div>
    </div>
  );
}

