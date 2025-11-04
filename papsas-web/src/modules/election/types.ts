export type AnalyticsDTO = {
  election?: { id: number; title?: string };
  positions: {
    id: number;
    title: string;
    totals: { candidacy_id: number; name: string; count: number; share: number }[];
  }[];
  meta: { totalVotes: number };
};

export type ExplainDTO = { short: string; long: string; text?: string };
