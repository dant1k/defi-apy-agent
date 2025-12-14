"use client";

export default function LoadingState() {
  return (
    <div className="bg-white p-12 rounded-lg shadow text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
      <p className="mt-4 text-gray-500">Loading...</p>
    </div>
  );
}

