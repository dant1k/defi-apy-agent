export function HomeSkeleton(): JSX.Element {
  return (
    <section className="page">
      <StrategiesSkeleton />
      <AnalyticsSkeleton />
    </section>
  );
}

export function StrategiesSkeleton(): JSX.Element {
  return (
    <div className="skeleton-card">
      <div className="skeleton-row skeleton-row--wide" />
      <div className="skeleton-row skeleton-row--medium" />
      <div className="skeleton-row skeleton-row--full" />
    </div>
  );
}

export function AnalyticsSkeleton(): JSX.Element {
  return (
    <div className="skeleton-card">
      <div className="skeleton-row skeleton-row--wide" />
      <div className="skeleton-row skeleton-row--chips">
        {Array.from({ length: 3 }).map((_, index) => (
          <span key={index} className="skeleton-chip" />
        ))}
      </div>
      <div className="skeleton-table">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="skeleton-row skeleton-row--full" />
        ))}
      </div>
    </div>
  );
}
