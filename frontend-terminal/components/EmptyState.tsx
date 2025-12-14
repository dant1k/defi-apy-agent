"use client";

interface EmptyStateProps {
  message: string;
}

export default function EmptyState({ message }: EmptyStateProps) {
  return (
    <div className="bg-white p-12 rounded-lg shadow text-center">
      <p className="text-gray-500">{message}</p>
    </div>
  );
}

