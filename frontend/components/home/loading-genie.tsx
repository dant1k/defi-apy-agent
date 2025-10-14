type LoadingGenieProps = {
  mode: "search" | "refresh";
  etaSeconds?: number | null;
};

export function LoadingGenie({ mode, etaSeconds }: LoadingGenieProps): JSX.Element {
  const message =
    mode === "search"
      ? "Джин ищет лучшие стратегии..."
      : "Джин обновляет список, держись!";

  const etaLabel =
    typeof etaSeconds === "number"
      ? etaSeconds > 0
        ? `≈ ${etaSeconds} с`
        : "почти готово"
      : null;

  return (
    <div className="genie-container" role="status" aria-live="polite">
      <div className="genie-figure">
        <span className="genie-emoji" aria-hidden="true">
          🧞‍♂️
        </span>
        <span className="genie-shadow" aria-hidden="true" />
        <span className="genie-spark spark-1" aria-hidden="true" />
        <span className="genie-spark spark-2" aria-hidden="true" />
        <span className="genie-spark spark-3" aria-hidden="true" />
      </div>
      <p>
        {message}
        {etaLabel && <span className="genie-eta">{etaLabel}</span>}
      </p>
    </div>
  );
}
