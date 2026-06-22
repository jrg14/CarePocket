export type IncomeCategory = {
  id: number;
  name: string;
  slug: string;
  icon: string;
  color: string;
};

export type Income = {
  id: number;
  user_id: number;
  category_id: number;
  amount: number;
  description: string;
  source: string;
  received_on: string;
  note: string | null;
  created_at: string;
  updated_at: string;
  category: IncomeCategory;
};

export type IncomeCreateInput = {
  category_id: number;
  amount: number;
  description: string;
  source: string;
  received_on: string;
  note?: string | null;
};

export type IncomeUpdateInput = Partial<IncomeCreateInput>;

export type IncomeListResponse = {
  items: Income[];
  total: number;
};

export type IncomeSummaryCategoryBreakdown = {
  category: IncomeCategory;
  amount: number;
  percentage: number;
};

export type IncomeSummary = {
  period_start: string;
  period_end: string;
  today_total: number;
  week_total: number;
  month_total: number;
  average_daily: number;
  total_incomes: number;
  top_category: IncomeSummaryCategoryBreakdown | null;
  category_breakdown: IncomeSummaryCategoryBreakdown[];
  recent_incomes: Income[];
};
